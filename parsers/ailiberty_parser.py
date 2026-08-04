# ailiberty_parser.py
"""
Парсер для AiLiberty (ailiberty.top)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import json
import logging

logger = logging.getLogger(__name__)


class AiLibertyParser(AnimeSource):
    def __init__(self):
        super().__init__("AiLiberty", "https://ailiberty.top")

    def search(self, query: str) -> List[Anime]:
        """Поиск по сайту"""
        try:
            search_url = f"{self.base_url}/?search={query}"
            response = self.session.get(search_url, timeout=15)
            html = response.text
            
            results = []
            # Парсим ссылки на релизы
            matches = re.findall(
                r'<a[^>]+href="https?://[^/]+/releases/([^"]+)"[^>]*>(.*?)</a>',
                html, re.DOTALL
            )
            
            for uri_id, inner_html in matches:
                title_match = re.search(r'<h3[^>]*>([^<]+)</h3>', inner_html, re.DOTALL)
                title = title_match.group(1).strip() if title_match else "Unknown"
                
                img_match = re.search(r'<img[^>]+src="([^"]+)"', inner_html, re.DOTALL)
                img = img_match.group(1) if img_match else None
                if img and not img.startswith("http"):
                    img = self.base_url + ("/" + img if not img.startswith("/") else img)
                
                year_match = re.search(r'<div[^>]+text-gray-500[^>]*>.*?([0-9]{4}).*?</div>', 
                                       inner_html, re.DOTALL)
                year = int(year_match.group(1)) if year_match else None
                
                anime = Anime(
                    id=uri_id,
                    title=title,
                    poster=img,
                    year=year,
                    translation="AiLiberty",
                    source="ailiberty",
                    url=f"{self.base_url}/releases/{uri_id}"
                )
                results.append(anime)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска AiLiberty: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды"""
        try:
            url = f"{self.base_url}/releases/{anime.id}"
            response = self.session.get(url, timeout=15)
            html = response.text
            
            # Ищем PlayerJS данные
            match = re.search(
                r'file\s*:\s*(\[.*?\])\s*,?\s*default_quality',
                html, re.DOTALL
            )
            if not match:
                match = re.search(r'file\s*:\s*(\[.*?\])\s*\}', html, re.DOTALL)
            
            if not match:
                return []
            
            items = json.loads(match.group(1))
            episodes = []
            
            for item in items:
                title = item.get('title', 'Серия')
                episode_number = re.search(r'([0-9]+)', title)
                ep_num = episode_number.group(1) if episode_number else "1"
                
                file_data = item.get('file', '')
                # Парсим качества
                qualities = re.findall(r'\[(360p|480p|720p|1080p)\]([^\[\,]+)', file_data)
                
                best_url = None
                best_quality = "720p"
                for q, url in qualities:
                    best_url = url.strip().rstrip(',;')
                    best_quality = q
                    if q == "1080p":
                        break
                
                if best_url and not best_url.startswith("http"):
                    best_url = self.base_url + ("/" + best_url if not best_url.startswith("/") else best_url)
                
                episode = Episode(
                    number=ep_num,
                    title=title,
                    url=best_url,
                    translation="AiLiberty",
                    quality=best_quality
                )
                episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов AiLiberty: {e}")
            return []