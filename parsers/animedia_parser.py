# animedia_parser.py
"""
Парсер для AniMedia (amd.online)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import logging

logger = logging.getLogger(__name__)


class AniMediaParser(AnimeSource):
    def __init__(self):
        super().__init__("AniMedia", "https://amd.online")

    def search(self, query: str) -> List[Anime]:
        """Поиск аниме"""
        try:
            data = {
                'do': 'search',
                'subaction': 'search',
                'from_page': 0,
                'story': query
            }
            
            response = self.session.post(f"{self.base_url}/index.php?do=search", data=data, timeout=15)
            html = response.text
            
            results = []
            # Парсим результаты поиска
            # Ищем блоки с аниме
            anime_blocks = re.findall(
                r'<a href="https?://[^/]+/([^"]+)" class="poster__link"><h3 class="poster__title line-clamp">([^<]+)</h3></a>',
                html
            )
            
            for url_path, title in anime_blocks:
                img_match = re.search(
                    rf'<a href="https?://[^/]+/{re.escape(url_path)}"[^>]*>.*?<img src="([^"]+)"',
                    html, re.DOTALL
                )
                img = img_match.group(1) if img_match else None
                if img and not img.startswith("http"):
                    img = self.base_url + img
                
                anime = Anime(
                    id=url_path,
                    title=title.strip(),
                    poster=img,
                    translation="AniMedia",
                    source="animedia",
                    url=f"{self.base_url}/{url_path}"
                )
                results.append(anime)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска AniMedia: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды"""
        try:
            response = self.session.get(anime.url, timeout=15)
            html = response.text
            
            # Ищем data-vid и data-vlnk
            matches = re.findall(r'data-vid="([0-9]+)"[\t ]+data-vlnk="([^"]+)"', html)
            
            episodes = []
            seen_episodes = set()
            
            for vid, vod in matches:
                if vod and '/vod/' in vod:
                    ep_num = vid
                    if ep_num not in seen_episodes:
                        seen_episodes.add(ep_num)
                        episode = Episode(
                            number=ep_num,
                            url=vod,
                            translation="AniMedia",
                            quality="720p"
                        )
                        episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов AniMedia: {e}")
            return []