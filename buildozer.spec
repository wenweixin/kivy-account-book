[app]
title = 记账本
package.name = accountbook
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.include_files = main.py,account_book.py,simhei.ttf
requirements = python3,kivy==2.1.0,pyjnius,plyer
android.ndk = 21e
android.api = 21
android.build_tools = 30.0.3
android.ndk_api = 21
android.arch = armeabi-v7a,arm64-v8a
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
main.py = main.py
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
