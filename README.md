# 🎬 Anime Parser Pro

Мульти-источниковое Android-приложение для парсинга аниме-сайтов с экспортом в M3U и JSON.

## ✨ Поддерживаемые источники

| Источник | Поиск | Эпизоды | Авторизация | Качество |
|----------|-------|---------|-------------|----------|
| ✅ AniLibria | API | API | Нет | ~1080p |
| ✅ AnimeVost | Парсинг | Парсинг | Нет | ~720p |
| ✅ AiLiberty | Парсинг | PlayerJS | Нет | ~1080p |
| ✅ AniMedia | Парсинг | Парсинг | Нет | ~720p |
| ✅ AnimeGo | Парсинг + API | API | Нет | ~1080p |
| ✅ AnimeBesst | Парсинг | Парсинг | Нет | ~720p |
| ✅ DreamersCast | Парсинг | PlayerJS | Нет | ~1080p |
| ✅ Mikai | API | API | Нет | ~1080p |
| ✅ MoonAnime | API | API | Токен | ~1080p |
| ⚙️ Anime365 | API | API | Да | ~720p |

## 📱 Установка

1. Скачайте APK из [Releases](../../releases)
2. Установите на Android 5.0+

## 🚀 Сборка через GitHub Actions

1. Форкните репозиторий
2. Включите Actions в настройках
3. Push в main — APK соберётся автоматически
4. Скачайте артефакт из последнего workflow

## 🛠️ Локальная сборка

```bash
pip install buildozer
buildozer android debug
