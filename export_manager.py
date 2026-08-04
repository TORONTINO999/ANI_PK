# export_manager.py
"""
Менеджер для экспорта в M3U и JSON
"""

import json
import os
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExportManager:
    @staticmethod
    def export_m3u(anime_list: List, filepath: str) -> bool:
        """Экспортировать в M3U плейлист"""
        try:
            lines = ['#EXTM3U']
            
            for anime in anime_list:
                for ep in anime.episodes:
                    if not ep.url:
                        continue
                    
                    title = f"{anime.title} - Эпизод {ep.number}"
                    if ep.title:
                        title += f" - {ep.title}"
                    title += f" ({ep.translation}) [{ep.quality}]"
                    
                    lines.append(f'#EXTINF:-1,{title}')
                    if ep.subtitles:
                        lines.append(f'#EXTSUB:{ep.subtitles}')
                    lines.append(ep.url)
                    lines.append('')  # Пустая строка между записями
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            logger.info(f"M3U экспортирован в {filepath}")
            return True
        except Exception as e:
            logger.error(f"Ошибка экспорта M3U: {e}")
            return False

    @staticmethod
    def export_json(anime_list: List, filepath: str) -> bool:
        """Экспортировать в JSON"""
        try:
            data = [anime.to_dict() for anime in anime_list]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON экспортирован в {filepath}")
            return True
        except Exception as e:
            logger.error(f"Ошибка экспорта JSON: {e}")
            return False

    @staticmethod
    def export_both(anime_list: List, base_path: str, filename: str = None) -> tuple:
        """Экспортировать и в M3U, и в JSON"""
        if not filename:
            filename = f'anime_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        m3u_file = os.path.join(base_path, f"{filename}.m3u")
        json_file = os.path.join(base_path, f"{filename}.json")
        
        m3u_ok = ExportManager.export_m3u(anime_list, m3u_file)
        json_ok = ExportManager.export_json(anime_list, json_file)
        
        return (m3u_file if m3u_ok else None, json_file if json_ok else None)
