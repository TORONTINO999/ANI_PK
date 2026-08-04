# animevost_parser.py
"""
Парсер для AnimeVost (animevost.org)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List
import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class AnimeVostParser(AnimeSource):
    def __init__(self):
        super().__init__("AnimeVost", "https://animevost.org")

    def search(self, query: str) -> List[Anime]:
        """Поиск через POST"""
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
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for item in soup.select('.shortstory'):
                link = item.find('a', href=re.compile(r'\.html'))
                if not link:
                    continue
                
                title = link.text.strip()
                url = link.get('href')
                poster = item.find('img', {'class': 'img-fit'})
                poster_url = None
                if poster:
                    poster_src = poster.get('src', '')
                    if poster_src:
                        poster_url = self.base_url + poster_src if not poster_src.startswith('http') else poster_src
                
                year_match = re.search(r'(\d{4})', item.text)
                year = int(year_match.group(1)) if year_match else None
                
                anime = Anime(
                    id=url,
                    title=title,
                    poster=poster_url,
                    year=year,
                    translation="AnimeVost",
                    source="animevost",
                    url=url
                )
                results.append(anime)
            
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска AnimeVost: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды со страницы"""
        try:
            response = self.session.get(anime.id, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Поиск видео в JavaScript переменной
            script_content = None
            for script in soup.find_all('script'):
                if script.string and 'var data' in script.string:
                    script_content = script.string
                    break
            
            if not script_content:
                # Альтернативный метод - ищем iframe
                iframes = soup.find_all('iframe')
                episodes = []
                for i, iframe in enumerate(iframes):
                    src = iframe.get('src', '')
                    if src:
                        episodes.append(Episode(
                            number=str(i + 1),
                            url=src,
                            translation="AnimeVost",
                            quality="720p"
                        ))
                return episodes
            
            episodes = []
            # Парсим JSON в JavaScript
            match = re.search(r'var data = ({.*?});', script_content, re.DOTALL)
            if match:
                data_str = match.group(1)
                # Заменяем одинарные кавычки на двойные для валидного JSON
                data_str = data_str.replace("'", '"')
                
                # Извлекаем эпизоды
                for ep_match in re.finditer(r'"([^"]+)":"([0-9]+)",', data_str):
                    title = ep_match.group(1)
                    ep_id = ep_match.group(2)
                    
                    episode = Episode(
                        number=ep_id,
                        title=title,
                        url=f"{self.base_url}/frame5.php?play={ep_id}&old=1",
                        translation="AnimeVost",
                        quality="720p"
                    )
                    episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов AnimeVost: {e}")
            return []