# animego_parser.py
"""
Парсер для AnimeGo (animego.me)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import json
import logging

logger = logging.getLogger(__name__)


class AnimeGoParser(AnimeSource):
    def __init__(self):
        super().__init__("AnimeGo", "https://animego.me")

    def search(self, query: str) -> List[Anime]:
        """Поиск аниме"""
        try:
            url = f"{self.base_url}/search/anime?q={query}"
            response = self.session.get(url, timeout=15)
            html = response.text
            
            results = []
            # Парсим результаты
            blocks = re.findall(
                r'class="p-poster__stack"(.*?)class="card-title text-truncate"><a [^>]+>([^<]+)</a>',
                html, re.DOTALL
            )
            
            for block, title in blocks:
                pid_match = re.search(r'data-ajax-url="/[^"]+-([0-9]+)"', block)
                pid = pid_match.group(1) if pid_match else None
                
                year_match = re.search(r'class="anime-year"><a [^>]+>([0-9]{4})<', block)
                year = int(year_match.group(1)) if year_match else None
                
                img_match = re.search(r'data-original="([^"]+)"', block)
                img = img_match.group(1) if img_match else None
                
                if pid:
                    anime = Anime(
                        id=pid,
                        title=title.strip(),
                        poster=img,
                        year=year,
                        translation="AnimeGo",
                        source="animego",
                        url=f"{self.base_url}/anime/{pid}"
                    )
                    results.append(anime)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска AnimeGo: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды через API плеера"""
        try:
            # Получаем данные плеера
            player_url = f"{self.base_url}/anime/{anime.id}/player?_allow=true"
            headers = {
                'cache-control': 'no-cache',
                'dnt': '1',
                'pragma': 'no-cache',
                'referer': f"{self.base_url}/",
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'XMLHttpRequest'
            }
            
            response = self.session.get(player_url, headers=headers, timeout=15)
            data = response.json()
            content = data.get('content', '')
            
            if not content:
                return []
            
            # Парсим эпизоды
            episodes = []
            ep_matches = re.findall(r'data-episode="([0-9]+)"', content)
            
            # Получаем хост и токен
            host_match = re.search(
                r'data-player="(https?:)?//(aniboom\.[^/]+)/embed/([^"\?&]+)\?episode=1\&amp;translation=([0-9]+)"',
                content
            )
            
            if not host_match:
                return []
            
            host = host_match.group(2)
            token = host_match.group(3)
            translation = host_match.group(4)
            
            for ep_num in ep_matches:
                episode = Episode(
                    number=ep_num,
                    url=f"https://{host}/embed/{token}?episode={ep_num}&translation={translation}",
                    translation="AnimeGo",
                    quality="1080p"
                )
                episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов AnimeGo: {e}")
            return []