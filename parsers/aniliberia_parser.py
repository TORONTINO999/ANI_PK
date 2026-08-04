# aniliberia_parser.py
"""
Парсер для AniLibria (anilibria.tv)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import requests
import json
import logging

logger = logging.getLogger(__name__)


class AniLibriaParser(AnimeSource):
    def __init__(self):
        super().__init__("AniLibria", "https://api.anilibria.tv")
        self.api_host = "https://api.anilibria.tv"

    def search(self, query: str) -> List[Anime]:
        """Поиск по API AniLibria"""
        try:
            url = f"{self.api_host}/v3/title/search?search={query}&limit=20"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            results = []
            for item in data.get('list', []):
                names = item.get('names', {})
                posters = item.get('posters', {})
                poster_url = None
                if posters and 'small' in posters:
                    poster_url = f"{self.api_host}{posters['small']['url']}"
                
                anime = Anime(
                    id=str(item.get('id')),
                    title=names.get('ru', names.get('en', 'Unknown')),
                    original_title=names.get('en'),
                    poster=poster_url,
                    description=item.get('description'),
                    year=item.get('season', {}).get('year'),
                    translation="AniLibria",
                    source="anilibria",
                    url=f"{self.api_host}/v3/title?id={item.get('id')}"
                )
                results.append(anime)
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска AniLibria: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды из API"""
        try:
            url = f"{self.api_host}/v3/title?id={anime.id}"
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            episodes = []
            player = data.get('player', {})
            playlist = player.get('playlist', {})
            
            for ep_key, ep_data in playlist.items():
                hls = ep_data.get('hls', {})
                best_url = None
                best_quality = "720p"
                
                # Выбираем лучшее качество
                for quality in ['fhd', 'hd', 'sd']:
                    if hls.get(quality):
                        best_url = hls[quality]
                        best_quality = {"fhd": "1080p", "hd": "720p", "sd": "480p"}.get(quality, "720p")
                        break
                
                if best_url:
                    episode = Episode(
                        number=str(ep_data.get('serie', ep_key)),
                        title=ep_data.get('name', f"Серия {ep_key}"),
                        url=best_url,
                        translation="AniLibria",
                        quality=best_quality
                    )
                    episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов AniLibria: {e}")
            return []