# parsers/__init__.py
from parsers.anime_sources import AnimeSource, Anime, Episode
from parsers.aniliberia_parser import AniLibriaParser
from parsers.anime365_parser import Anime365Parser
from parsers.animevost_parser import AnimeVostParser
from parsers.ailiberty_parser import AiLibertyParser
from parsers.animedia_parser import AniMediaParser
from parsers.animego_parser import AnimeGoParser
from parsers.animebesst_parser import AnimeBesstParser
from parsers.dreamerscast_parser import DreamersCastParser
from parsers.mikai_parser import MikaiParser
from parsers.moonanime_parser import MoonAnimeParser

__all__ = [
    'AnimeSource', 'Anime', 'Episode',
    'AniLibriaParser', 'Anime365Parser', 'AnimeVostParser',
    'AiLibertyParser', 'AniMediaParser', 'AnimeGoParser',
    'AnimeBesstParser', 'DreamersCastParser', 'MikaiParser',
    'MoonAnimeParser'
]
