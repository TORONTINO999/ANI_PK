[app]

# ===== Основное =====
title = Anime Parser Pro
package.name = animeparserpro
package.domain = org.animeparser

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,md

version = 1.0.0

# ===== Зависимости =====
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,requests,beautifulsoup4,html5lib,urllib3,charset-normalizer,idna,certifi

# ===== Ориентация и экран =====
orientation = portrait
fullscreen = 0

# ===== Android =====
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.named_permissions = android.permission.MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25c
android.arch = arm64-v8a,armeabi-v7a
android.allow_backup = True

# ===== Графика =====
# android.presplash = presplash.png
# android.icon = icon.png

# ===== Для работы с сетью =====
android.gradle_dependencies = 'com.android.support:localbroadcastmanager:28.0.0'

# ===== Опции сборки =====
android.ignore_apk = True
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 1
