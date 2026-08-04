# moonanime_parser.py
"""
Парсер для MoonAnime (api.moonanime.art)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import logging

logger = logging.getLogger(__name__)


class MoonAnimeParser(AnimeSource):
    def __init__(self):
        super().__init__("MoonAnime", "https://api.moonanime.art")
        self.token = "865fEF-E2e1Bc-2ca431-e6A150-780DFD-737C6B"

    def search(self, query: str) -> List[Anime]:
        """Поиск аниме"""
        try:
            # Пробуем поиск по разным параметрам
            search_urls = [
                f"{self.base_url}/api/2.0/titles?api_key={self.token}&limit=20&imdbid={query}",
                f"{self.base_url}/api/2.0/titles?api_key={self.token}&limit=20&title={query}",
            ]
            
            for url in search_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    result = response.json()
                    anime_list = result.get('anime_list', [])
                    
                    if anime_list:
                        results = []
                        for item in anime_list:
                            anime = Anime(
                                id=str(item.get('id')),
                                title=item.get('title', 'Unknown'),
                                poster=item.get('poster'),
                                year=item.get('year'),
                                translation="MoonAnime",
                                source="moonanime",
                                url=f"{self.base_url}/api/2.0/title/{item['id']}"
                            )
                            results.append(anime)
                        return results
                except:
                    continue
            
            return []
        except Exception as e:
            logger.error(f"Ошибка поиска MoonAnime: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды"""
        try:
            url = f"{self.base_url}/api/2.0/title/{anime.id}/videos?api_key={self.token}"
            response = self.session.get(url, timeout=15)
            result = response.json()
            
            # Структура: List[Dict[str, Dict[str, List[Episode]]]]
            episodes = []
            
            for voices in result:
                for voice_name, seasons in voices.items():
                    for season_num, ep_list in seasons.items():
                        for ep in ep_list:
                            if not ep.get('vod'):
                                continue
                            
                            episode = Episode(
                                number=str(ep.get('episode', '1')),
                                url=ep['vod'],
                                translation=voice_name,
                                quality="1080p"
                            )
                            episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов MoonAnime: {e}")
            return []
