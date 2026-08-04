# main.py
"""
Главное приложение с KivyMD интерфейсом
"""

import os
import sys
import threading
import json

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.list import MDList, OneLineListItem, TwoLineAvatarListItem, ImageLeftWidget
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.chip import MDChip

from parsers import *
from utils.export_manager import ExportManager

# KV строка для интерфейса
KV = '''
<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "🎬 Anime Parser Pro"
            elevation: 4
            right_action_items: [["export", lambda x: app.show_export_dialog()], ["cog", lambda x: app.show_settings()]]
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(16)
            spacing: dp(12)
            
            MDTextField:
                id: search_field
                hint_text: "Введите название аниме..."
                helper_text: "Например: Атака титанов"
                helper_text_mode: "on_focus"
                icon_right: "magnify"
                on_text_validate: app.on_search(self.text)
            
            MDBoxLayout:
                size_hint_y: None
                height: dp(50)
                spacing: dp(8)
                
                MDRaisedButton:
                    id: source_btn
                    text: "Источник: AniLibria"
                    on_release: app.show_source_menu(self)
                
                MDRaisedButton:
                    text: "🔍 Искать"
                    on_release: app.on_search(search_field.text)
            
            MDProgressBar:
                id: progress_bar
                value: 0
                opacity: 0
            
            MDLabel:
                id: status_label
                text: "Готов к работе"
                halign: "center"
                size_hint_y: None
                height: dp(30)
            
            MDScrollView:
                MDList:
                    id: results_list

<AnimeDetailScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Детали аниме"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.back_to_main()]]
            right_action_items: [["download", lambda x: app.load_episodes()], ["export", lambda x: app.export_current()]]
        
        MDScrollView:
            MDBoxLayout:
                id: detail_content
                orientation: 'vertical'
                padding: dp(16)
                spacing: dp(12)
                size_hint_y: None
                height: self.minimum_height
                
                AsyncImage:
                    id: poster_img
                    size_hint_y: None
                    height: dp(200)
                    allow_stretch: True
                    keep_ratio: True
                
                MDLabel:
                    id: title_label
                    text: ""
                    halign: "center"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDLabel:
                    id: info_label
                    text: ""
                    halign: "center"
                    theme_text_color: "Secondary"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDLabel:
                    id: desc_label
                    text: ""
                    halign: "left"
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDBoxLayout:
                    id: episodes_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                
                MDRaisedButton:
                    text: "📥 Загрузить эпизоды"
                    on_release: app.load_episodes()
                    size_hint_x: 1
                    md_bg_color: app.theme_cls.primary_color

<LoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(32)
        spacing: dp(16)
        
        MDLabel:
            text: "🔐 Авторизация"
            halign: "center"
            font_style: "H4"
            size_hint_y: None
            height: dp(60)
        
        MDLabel:
            text: "Требуется для Anime365"
            halign: "center"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: dp(30)
        
        MDTextField:
            id: login_field
            hint_text: "Логин / Email"
            icon_right: "account"
        
        MDTextField:
            id: pass_field
            hint_text: "Пароль"
            password: True
            icon_right: "lock"
        
        MDRaisedButton:
            text: "Войти"
            size_hint_x: 1
            on_release: app.do_login(login_field.text, pass_field.text)
        
        MDFlatButton:
            text: "Пропустить"
            size_hint_x: 1
            on_release: app.skip_login()
        
        MDLabel:
            id: login_status
            text: ""
            halign: "center"
            theme_text_color: "Error"
            size_hint_y: None
            height: dp(30)
'''

class MainScreen(Screen):
    pass

class AnimeDetailScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class AnimeParserApp(MDApp):
    current_anime = ObjectProperty(None, allownone=True)
    search_results = ListProperty([])
    collected_anime = ListProperty([])
    current_source = StringProperty("anilibria")
    is_loading = BooleanProperty(False)
    
    # Парсеры
    parsers = {}
    active_parser = ObjectProperty(None, allownone=True)
    
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Dark"
        
        # Инициализация парсеров
        self.parsers = {
            'anilibria': AniLibriaParser(),
            'animevost': AnimeVostParser(),
            'ailiberty': AiLibertyParser(),
            'animedia': AniMediaParser(),
            'animego': AnimeGoParser(),
            'animebesst': AnimeBesstParser(),
            'dreamerscast': DreamersCastParser(),
            'mikai': MikaiParser(),
            'moonanime': MoonAnimeParser(),
        }
        self.active_parser = self.parsers['anilibria']
        
        # Экран менеджер
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(AnimeDetailScreen(name='detail'))
        
        # Загрузка KV
        Builder.load_string(KV)
        
        # Показываем экран логина только для Anime365
        self.sm.current = 'main'
        
        return self.sm
    
    def show_source_menu(self, button):
        """Показать меню выбора источника"""
        menu_items = [
            {"text": "AniLibria", "on_release": lambda x="anilibria": self.set_source(x)},
            {"text": "AnimeVost", "on_release": lambda x="animevost": self.set_source(x)},
            {"text": "AiLiberty", "on_release": lambda x="ailiberty": self.set_source(x)},
            {"text": "AniMedia", "on_release": lambda x="animedia": self.set_source(x)},
            {"text": "AnimeGo", "on_release": lambda x="animego": self.set_source(x)},
            {"text": "AnimeBesst", "on_release": lambda x="animebesst": self.set_source(x)},
            {"text": "DreamersCast", "on_release": lambda x="dreamerscast": self.set_source(x)},
            {"text": "Mikai", "on_release": lambda x="mikai": self.set_source(x)},
            {"text": "MoonAnime", "on_release": lambda x="moonanime": self.set_source(x)},
        ]
        
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()
    
    def set_source(self, source_name):
        """Установить активный источник"""
        self.current_source = source_name
        self.active_parser = self.parsers[source_name]
        
        # Обновляем текст кнопки
        main_screen = self.sm.get_screen('main')
        source_names = {
            'anilibria': 'AniLibria',
            'animevost': 'AnimeVost',
            'ailiberty': 'AiLiberty',
            'animedia': 'AniMedia',
            'animego': 'AnimeGo',
            'animebesst': 'AnimeBesst',
            'dreamerscast': 'DreamersCast',
            'mikai': 'Mikai',
            'moonanime': 'MoonAnime',
        }
        main_screen.ids.source_btn.text = f"Источник: {source_names.get(source_name, source_name)}"
        
        # Показываем экран логина если нужно
        if source_name == 'anime365' and not getattr(self.parsers.get('anime365'), 'logged_in', False):
            self.sm.current = 'login'
        
        if self.menu:
            self.menu.dismiss()
    
    def on_search(self, query):
        """Поиск аниме"""
        if self.is_loading or not query.strip():
            return
        
        self.is_loading = True
        main_screen = self.sm.get_screen('main')
        main_screen.ids.status_label.text = f"🔍 Ищем: {query}..."
        main_screen.ids.progress_bar.opacity = 1
        main_screen.ids.progress_bar.start()
        
        # Очищаем список
        main_screen.ids.results_list.clear_widgets()
        
        # Запускаем поиск в потоке
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()
    
    def _search_thread(self, query):
        """Поиск в фоновом потоке"""
        try:
            results = self.active_parser.search(query)
            self.search_results = results
            
            Clock.schedule_once(lambda dt: self._display_results(results), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(str(e)), 0)
        finally:
            self.is_loading = False
            Clock.schedule_once(lambda dt: self._stop_progress(), 0)
    
    def _display_results(self, results):
        """Отобразить результаты поиска"""
        main_screen = self.sm.get_screen('main')
        results_list = main_screen.ids.results_list
        
        if not results:
            main_screen.ids.status_label.text = "❌ Ничего не найдено"
            return
        
        main_screen.ids.status_label.text = f"✅ Найдено: {len(results)} результатов"
        
        for anime in results:
            item = TwoLineAvatarListItem(
                text=anime.title,
                secondary_text=f"{anime.year or 'N/A'} | {anime.translation}",
                on_release=lambda x, a=anime: self.show_anime_detail(a)
            )
            
            if anime.poster:
                item.add_widget(ImageLeftWidget(source=anime.poster))
            
            results_list.add_widget(item)
    
    def _stop_progress(self):
        """Остановить прогресс"""
        main_screen = self.sm.get_screen('main')
        main_screen.ids.progress_bar.stop()
        main_screen.ids.progress_bar.opacity = 0
    
    def show_anime_detail(self, anime):
        """Показать детали аниме"""
        self.current_anime = anime
        self.sm.current = 'detail'
        
        detail_screen = self.sm.get_screen('detail')
        detail_screen.ids.title_label.text = anime.title
        
        info_parts = []
        if anime.year:
            info_parts.append(f"Год: {anime.year}")
        info_parts.append(f"Источник: {anime.translation}")
        detail_screen.ids.info_label.text = " | ".join(info_parts)
        
        detail_screen.ids.desc_label.text = anime.description or "Описание отсутствует"
        
        if anime.poster:
            detail_screen.ids.poster_img.source = anime.poster
    
    def load_episodes(self):
        """Загрузить эпизоды"""
        if not self.current_anime or self.is_loading:
            return
        
        self.is_loading = True
        detail_screen = self.sm.get_screen('detail')
        detail_screen.ids.episodes_container.clear_widgets()
        
        threading.Thread(target=self._load_episodes_thread, daemon=True).start()
    
    def _load_episodes_thread(self):
        """Загрузка эпизодов в потоке"""
        try:
            episodes = self.active_parser.get_episodes(self.current_anime)
            self.current_anime.episodes = episodes
            
            Clock.schedule_once(lambda dt: self._display_episodes(episodes), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(str(e)), 0)
        finally:
            self.is_loading = False
    
    def _display_episodes(self, episodes):
        """Отобразить эпизоды"""
        detail_screen = self.sm.get_screen('detail')
        container = detail_screen.ids.episodes_container
        
        if not episodes:
            label = MDLabel(
                text="❌ Не удалось получить эпизоды",
                halign="center",
                theme_text_color="Error"
            )
            container.add_widget(label)
            return
        
        # Добавляем в собранные
        if self.current_anime not in self.collected_anime:
            self.collected_anime.append(self.current_anime)
        
        label = MDLabel(
            text=f"📺 Эпизодов: {len(episodes)}",
            halign="center",
            font_style="H6"
        )
        container.add_widget(label)
        
        for ep in episodes:
            chip = MDChip(
                text=f"EP{ep.number} ({ep.quality})",
                icon="play-circle",
                on_release=lambda x, e=ep: self.show_episode_info(e)
            )
            container.add_widget(chip)
    
    def show_episode_info(self, episode):
        """Показать информацию об эпизоде"""
        self.show_snackbar(f"Ссылка: {episode.url[:50]}...")
    
    def export_current(self):
        """Экспорт текущего аниме"""
        if not self.current_anime or not self.current_anime.episodes:
            self.show_error("Сначала загрузите эпизоды")
            return
        
        self._do_export([self.current_anime])
    
    def show_export_dialog(self):
        """Показать диалог экспорта"""
        if not self.collected_anime:
            self.show_error("Нет собранных аниме для экспорта")
            return
        
        content = MDBoxLayout(orientation='vertical', spacing=12, size_hint_y=None, height=120)
        
        content.add_widget(MDLabel(text=f"Аниме для экспорта: {len(self.collected_anime)}"))
        
        dialog = MDDialog(
            title="📤 Экспорт",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="M3U + JSON", on_release=lambda x: [self._do_export(self.collected_anime), dialog.dismiss()])
            ]
        )
        dialog.open()
    
    def _do_export(self, anime_list):
        """Выполнить экспорт"""
        try:
            # Определяем путь
            if platform == 'android':
                try:
                    from android.permissions import request_permissions, Permission
                    from android.storage import app_storage_path
                    request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
                    path = app_storage_path()
                except:
                    path = os.path.expanduser('~')
            else:
                path = os.path.expanduser('~')
            
            m3u_file, json_file = ExportManager.export_both(anime_list, path)
            
            msg = "✅ Экспорт завершен!\n\n"
            if m3u_file:
                msg += f"M3U: {os.path.basename(m3u_file)}\n"
            if json_file:
                msg += f"JSON: {os.path.basename(json_file)}"
            
            self.show_snackbar(msg)
            
        except Exception as e:
            self.show_error(f"Ошибка экспорта: {e}")
    
    def do_login(self, login, password):
        """Авторизация в Anime365"""
        if not login or not password:
            return
        
        parser = Anime365Parser()
        success = parser.login(login, password)
        
        if success:
            self.parsers['anime365'] = parser
            self.show_snackbar("✅ Авторизация успешна!")
            self.sm.current = 'main'
        else:
            login_screen = self.sm.get_screen('login')
            login_screen.ids.login_status.text = "❌ Неверный логин или пароль"
    
    def skip_login(self):
        """Пропустить авторизацию"""
        self.sm.current = 'main'
    
    def back_to_main(self):
        """Вернуться на главный экран"""
        self.sm.current = 'main'
    
    def show_settings(self):
        """Показать настройки"""
        self.show_snackbar("Настройки в разработке")
    
    def show_error(self, message):
        """Показать ошибку"""
        dialog = MDDialog(
            title="❌ Ошибка",
            text=str(message),
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def show_snackbar(self, message):
        """Показать уведомление"""
        MDSnackbar(
            MDLabel(text=str(message)),
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5}
        ).open()


if __name__ == '__main__':
    AnimeParserApp().run()
