# animebesst_parser.py
"""
Парсер для AnimeBesst (anime1.best)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import logging

logger = logging.getLogger(__name__)


class AnimeBesstParser(AnimeSource):
    def __init__(self):
        super().__init__("AnimeBesst", "https://anime1.best")

    def search(self, query: str) -> List[Anime]:
        """Поиск аниме"""
        try:
            data = {
                'do': 'search',
                'subaction': 'search',
                'search_start': 0,
                'full_search': 0,
                'result_from': 1,
                'story': query
            }
            
            response = self.session.post(f"{self.base_url}/index.php?do=search", data=data, timeout=15)
            html = response.text
            
            results = []
            # Парсим результаты
            blocks = re.findall(
                r'class="shortstory-listab"(.*?)class="shortstory-listab-title"><a href="(https?://[^"]+\.html)">([^<]+)</a>',
                html, re.DOTALL
            )
            
            for block, url, title in blocks:
                if "Новости" in block:
                    continue
                
                year_match = re.search(r'">([0-9]{4})</a>', block)
                year = int(year_match.group(1)) if year_match else None
                
                img_match = re.search(r'<img class="img-fit lozad" data-src="([^"]+)"', block)
                img = img_match.group(1) if img_match else None
                
                season_match = re.search(r'([0-9]+) сезон', title)
                season = season_match.group(1) if season_match else "1"
                
                anime = Anime(
                    id=url,
                    title=title.strip(),
                    poster=img,
                    year=year,
                    translation="AnimeBesst",
                    source="animebesst",
                    url=url
                )
                results.append(anime)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска AnimeBesst: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды"""
        try:
            response = self.session.get(anime.url, timeout=15)
            html = response.text
            
            # Ищем videoList
            video_list_match = re.search(r'var videoList ?=([^\n\r]+)', html)
            if not video_list_match:
                return []
            
            video_list = video_list_match.group(1)
            
            # Парсим эпизоды
            matches = re.findall(
                r'"id":"([0-9]+)( [^"]+)?","link":"(https?:)?\\\\/\\\\/([^"]+)"',
                video_list
            )
            
            episodes = []
            for ep_id, ep_name, _, ep_url in matches:
                clean_url = ep_url.replace("\\", "")
                if not clean_url.startswith("http"):
                    clean_url = "https://" + clean_url
                
                episode = Episode(
                    number=ep_id,
                    title=ep_name.strip() if ep_name else f"Серия {ep_id}",
                    url=clean_url,
                    translation="AnimeBesst",
                    quality="720p"
                )
                episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов AnimeBesst: {e}")
            return []