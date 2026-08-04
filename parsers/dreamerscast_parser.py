# dreamerscast_parser.py
"""
Парсер для DreamersCast (dreamerscast.com)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import json
import base64
import logging

logger = logging.getLogger(__name__)


class DreamersCastParser(AnimeSource):
    def __init__(self):
        super().__init__("DreamersCast", "https://dreamerscast.com")

    def search(self, query: str) -> List[Anime]:
        """Поиск аниме"""
        try:
            headers = {
                'x-requested-with': 'XMLHttpRequest',
                'referer': self.base_url + '/'
            }
            
            data = {
                'search': query,
                'status': '',
                'pageSize': 16,
                'pageNumber': 1
            }
            
            response = self.session.post(f"{self.base_url}/", data=data, headers=headers, timeout=15)
            result = response.json()
            releases = result.get('releases', [])
            
            results = []
            for item in releases:
                img = item.get('image', '')
                if img.startswith('//'):
                    img = 'https:' + img
                elif img.startswith('/'):
                    img = self.base_url + img
                
                season_match = re.search(r' ([0-9]+)nd ', item.get('original', ''))
                season = season_match.group(1) if season_match else "1"
                
                anime = Anime(
                    id=item.get('url', ''),
                    title=item.get('russian') or item.get('original', 'Unknown'),
                    poster=img,
                    year=item.get('dateissue'),
                    translation="DreamersCast",
                    source="dreamerscast",
                    url=self.base_url + item.get('url', '')
                )
                results.append(anime)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска DreamersCast: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды"""
        try:
            response = self.session.get(anime.url, timeout=15)
            html = response.text
            
            # Ищем base64 данные PlayerJS
            base64_match = re.search(r'Playerjs\("#2(.*?)"\);', html, re.DOTALL)
            if not base64_match:
                return []
            
            base64_data = base64_match.group(1)
            # Убираем комментарии
            clean_base64 = re.sub(r'//[^=]+==', '', base64_data)
            
            try:
                decoded = base64.b64decode(clean_base64).decode('utf-8')
                root = json.loads(decoded)
            except:
                return []
            
            episodes = []
            for item in root.get('file', []):
                file_data = item.get('file', '')
                
                # Ищем HLS ссылку
                hls_match = re.search(r'https?://[^\s]+/hls/[^\s"\',;]+', file_data)
                if not hls_match:
                    continue
                
                hls_url = hls_match.group(0).rstrip(',;')
                
                title = item.get('title', 'Серия')
                ep_match = re.search(r'([0-9]+)', title)
                ep_num = ep_match.group(1) if ep_match else "1"
                
                episode = Episode(
                    number=ep_num,
                    title=title,
                    url=hls_url,
                    translation="DreamersCast",
                    quality="1080p"
                )
                episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов DreamersCast: {e}")
            return []
