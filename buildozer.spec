[app]
title = Anime Parser Pro
package.name = animeparserpro
package.domain = org.animeparser

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,md

version = 1.0.0

requirements = python3,kivy==2.1.0,kivymd==1.1.1,pillow,requests,beautifulsoup4,html5lib,urllib3,charset-normalizer,idna,certifi

orientation = portrait
fullscreen = 0

# Android settings
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a,armeabi-v7a
android.allow_backup = True

# Icon
# android.presplash = presplash.png
# android.icon = icon.png

[buildozer]
log_level = 2
warn_on_root = 1
