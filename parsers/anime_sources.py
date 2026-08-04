# anime_sources.py
"""
Базовый класс для всех парсеров аниме-сайтов.
Все конкретные реализации наследуют этот класс.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """Структура эпизода"""
    number: str
    title: Optional[str] = None
    url: Optional[str] = None
    subtitles: Optional[str] = None
    translation: str = "Оригинал"
    quality: str = "720p"


@dataclass
class Anime:
    """Структура аниме"""
    id: str
    title: str
    original_title: Optional[str] = None
    poster: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    episodes: List[Episode] = field(default_factory=list)
    translation: str = "Unknown"
    source: str = "Unknown"
    url: Optional[str] = None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'original_title': self.original_title,
            'poster': self.poster,
            'description': self.description,
            'year': self.year,
            'translation': self.translation,
            'source': self.source,
            'url': self.url,
            'episodes': [
                {
                    'number': ep.number,
                    'title': ep.title,
                    'url': ep.url,
                    'subtitles': ep.subtitles,
                    'translation': ep.translation,
                    'quality': ep.quality
                }
                for ep in self.episodes
            ]
        }


class AnimeSource(ABC):
    """Абстрактный класс для всех парсеров"""

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    @abstractmethod
    def search(self, query: str) -> List[Anime]:
        """Поиск аниме по названию"""
        pass

    @abstractmethod
    def get_episodes(self, anime: Anime) -> List[Episode]:
        """Получить список эпизодов"""
        pass

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Получить BeautifulSoup объект"""
        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Ошибка при запросе к {url}: {e}")
            return None

    def _post_soup(self, url: str, data: dict) -> Optional[BeautifulSoup]:
        """POST запрос с BeautifulSoup"""
        try:
            response = self.session.post(url, data=data, timeout=15)
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Ошибка при POST запросе к {url}: {e}")
            return None

    def __repr__(self):
        return f"<{self.name}>"
