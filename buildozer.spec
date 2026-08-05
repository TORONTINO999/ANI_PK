[app]
title = Anime Parser Pro
package.name = animeparserpro
package.domain = org.animeparser
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,md
version = 1.0.0
requirements = python3==3.11.12,kivy==2.2.1,kivymd==1.1.1,pillow,requests,beautifulsoup4,html5lib,urllib3,charset-normalizer,idna,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25.2.9519653
android.ndk_api = 21
android.archs = arm64-v8a
android.allow_backup = True
android.build_tools = 33.0.2

[buildozer]
log_level = 2
warn_on_root = 1
