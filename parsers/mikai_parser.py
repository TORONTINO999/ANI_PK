# mikai_parser.py
"""
Парсер для Mikai (mikai.me)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import logging

logger = logging.getLogger(__name__)


class MikaiParser(AnimeSource):
    def __init__(self):
        super().__init__("Mikai", "https://api.mikai.me")

    def search(self, query: str) -> List[Anime]:
        """Поиск аниме"""
        try:
            url = f"{self.base_url}/v1/anime/search?page=1&limit=24&sort=year&order=desc&name={query}"
            response = self.session.get(url, timeout=15)
            result = response.json()
            
            items = result.get('result', [])
            results = []
            
            for item in items:
                if not item.get('id'):
                    continue
                
                names = item.get('details', {}).get('names', {})
                title = names.get('name') or names.get('nameEnglish') or names.get('nameNative') or item.get('slug', 'Unknown')
                
                poster = ''
                if item.get('media', {}).get('posterUid'):
                    poster = f"https://images.mikai.me/poster/small/{item['media']['posterUid']}.webp"
                
                anime = Anime(
                    id=str(item['id']),
                    title=title,
                    poster=poster,
                    year=item.get('year'),
                    translation="Mikai (Украинский)",
                    source="mikai",
                    url=f"{self.base_url}/v1/anime/{item['id']}"
                )
                results.append(anime)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска Mikai: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды"""
        try:
            url = f"{self.base_url}/v1/anime/{anime.id}"
            response = self.session.get(url, timeout=15)
            result = response.json()
            
            anime_data = result.get('result', {})
            players = anime_data.get('players', [])
            
            # Ищем ASHDI провайдера
            episodes = []
            for player in players:
                providers = player.get('providers', [])
                for provider in providers:
                    if provider.get('name', '').upper() == 'ASHDI':
                        ep_list = provider.get('episodes', [])
                        team_name = player.get('team', {}).get('name', 'ASHDI')
                        
                        for ep in ep_list:
                            if not ep.get('playLink'):
                                continue
                            
                            episode = Episode(
                                number=str(ep.get('number', '1')),
                                url=ep['playLink'],
                                translation=team_name,
                                quality="1080p"
                            )
                            episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов Mikai: {e}")
            return []
