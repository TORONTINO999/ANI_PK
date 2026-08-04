# anime365_parser.py
"""
Парсер для Anime365 (smotret-anime.com)
"""

from parsers.anime_sources import AnimeSource, Anime, Episode
from typing import List, Optional
import re
import json
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Anime365Parser(AnimeSource):
    def __init__(self, login: Optional[str] = None, password: Optional[str] = None):
        super().__init__("Anime365", "https://smotret-anime.com")
        self.logged_in = False
        self.local_type = "voiceRu"
        
        if login and password:
            self.login(login, password)

    def login(self, login: str, password: str) -> bool:
        """Авторизация на Anime365"""
        try:
            login_page = self.session.get(f"{self.base_url}/users/login", timeout=10)
            soup = BeautifulSoup(login_page.text, 'html.parser')
            csrf_input = soup.find('input', {'type': 'hidden'})
            if not csrf_input:
                logger.error("CSRF токен не найден")
                return False
            
            csrf = csrf_input.get('value', '')
            
            data = {
                'csrf': csrf,
                'LoginForm[username]': login,
                'LoginForm[password]': password,
                'yt0': '',
                'dynpage': 1
            }
            
            response = self.session.post(f"{self.base_url}/users/login", data=data, timeout=10)
            self.logged_in = 'E-mail' not in response.text
            
            if self.logged_in:
                logger.info("Авторизация Anime365 успешна")
            else:
                logger.warning("Авторизация Anime365 не удалась")
            
            return self.logged_in
        except Exception as e:
            logger.error(f"Ошибка при логине Anime365: {e}")
            return False

    def search(self, query: str) -> List[Anime]:
        """Поиск аниме"""
        if not self.logged_in:
            logger.warning("Не авторизован на Anime365")
            return []
        
        try:
            url = f"{self.base_url}/api/series?query={query}"
            response = self.session.get(url, timeout=10)
            data = response.json().get('data', [])
            
            results = []
            for item in data:
                titles = item.get('titles', {})
                descriptions = item.get('descriptions', [{}])
                desc = descriptions[0].get('value', '') if descriptions else ''
                
                anime = Anime(
                    id=str(item.get('id')),
                    title=titles.get('ru', titles.get('romaji', 'Unknown')),
                    original_title=titles.get('romaji'),
                    poster=item.get('posterUrl'),
                    description=desc,
                    year=None,
                    translation="Anime365",
                    source="anime365",
                    url=f"{self.base_url}/api/series?id={item.get('id')}"
                )
                results.append(anime)
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска Anime365: {e}")
            return []

    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить эпизоды"""
        if not self.logged_in:
            return []
        
        try:
            url = f"{self.base_url}/api/translations?seriesId={anime.id}&type={self.local_type}"
            response = self.session.get(url, timeout=10)
            data = response.json().get('data', [])
            
            episodes = []
            if data:
                # Группируем по авторам перевода
                translations_by_author = {}
                for trans in data:
                    author = trans.get('authorsSummary', 'Unknown')
                    if author not in translations_by_author:
                        translations_by_author[author] = []
                    
                    ep = trans.get('episode', {})
                    translations_by_author[author].append({
                        'episode': ep.get('episodeInt', '1'),
                        'embedUrl': trans.get('embedUrl', ''),
                        'author': author
                    })
                
                # Выбираем перевод с наибольшим количеством эпизодов
                best_author = max(translations_by_author.keys(), 
                                 key=lambda k: len(translations_by_author[k]))
                
                for ep_data in translations_by_author[best_author]:
                    video_data = self._extract_video_data(ep_data['embedUrl'])
                    if video_data:
                        episode = Episode(
                            number=str(ep_data['episode']),
                            url=video_data.get('video'),
                            subtitles=video_data.get('sub'),
                            translation=best_author,
                            quality="720p"
                        )
                        episodes.append(episode)
            
            return sorted(episodes, key=lambda x: int(x.number) if x.number.isdigit() else 0)
        except Exception as e:
            logger.error(f"Ошибка получения эпизодов Anime365: {e}")
            return []

    def _extract_video_data(self, url: str) -> Optional[dict]:
        """Извлечь видео из страницы"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            video = soup.find('video', {'id': 'main-video'})
            
            if not video:
                return None
            
            sources = json.loads(video.get('data-sources', '[]'))
            video_url = sources[0]['urls'][0] if sources else None
            sub_url = video.get('data-subtitles', '')
            if sub_url:
                sub_url = sub_url.replace('?willcache', '')
                if not sub_url.startswith('http'):
                    sub_url = self.base_url + sub_url
            
            return {
                'video': video_url,
                'sub': sub_url if sub_url else None
            }
        except Exception as e:
            logger.error(f"Ошибка извлечения видео: {e}")
            return None

    def get_user_list(self) -> dict:
        """Получить списки пользователя"""
        if not self.logged_in:
            return {}
        
        try:
            # Получаем ID пользователя
            main_page = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(main_page.text, 'html.parser')
            user_link = soup.select_one('#top-dropdown2 > li:nth-child(2) > a[href]')
            if not user_link:
                return {}
            
            match = re.search(r'users/([0-9]+)/list', str(user_link))
            if not match:
                return {}
            
            acc_id = match.group(1)
            
            user_list = {
                'watching': [], 
                'completed': [],
                'onhold': [],
                'dropped': [],
                'planned': []
            }
            
            for list_type in user_list.keys():
                response = self.session.get(f"{self.base_url}/users/{acc_id}/list/{list_type}", timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                anime_items = soup.find_all("tr", class_="m-animelist-item")
                
                for anime in anime_items:
                    anime_id = anime.get('data-id')
                    if anime_id:
                        user_list[list_type].append(anime_id)
            
            return user_list
        except Exception as e:
            logger.error(f"Ошибка получения списка пользователя: {e}")
            return {}

    def get_ongoing_list(self) -> List[str]:
        """Получить список онгоингов"""
        try:
            response = self.session.get(f"{self.base_url}/ongoing?view=big-list", timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            animes = soup.find_all("h2", class_="line-1")
            
            anime_list = []
            for anime in animes:
                link = anime.find("a")
                if link:
                    anime_id = link.get('href', '').split("-")[-1]
                    if anime_id:
                        anime_list.append(anime_id)
            
            return anime_list
        except Exception as e:
            logger.error(f"Ошибка получения онгоингов: {e}")
            return []

    def get_random_list(self) -> List[str]:
        """Получить случайный список"""
        try:
            response = self.session.get(f"{self.base_url}/random?view=big-list", timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            animes = soup.find_all("h2", class_="line-1")
            
            anime_list = []
            for anime in animes:
                link = anime.find("a")
                if link:
                    anime_id = link.get('href', '').split("-")[-1]
                    if anime_id:
                        anime_list.append(anime_id)
            
            return anime_list
        except Exception as e:
            logger.error(f"Ошибка получения случайного списка: {e}")
            return []