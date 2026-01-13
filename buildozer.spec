[app]
# 应用标题
title = 记账本
# 应用版本（必填项，解决报错的核心）
version = 0.1
# 包名（小写，无特殊字符）
package.name = accountbook
# 包域名（反向域名格式）
package.domain = org.example
# 源码目录（当前目录）
source.dir = .
# 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,ttf
# 必须包含的文件
source.include_files = main.py,account_book.py,simhei.ttf
# 依赖库（和打包环境匹配）
requirements = python3,kivy==2.1.0,pyjnius,plyer
# Android NDK版本
android.ndk = 21e
# Android API版本
android.api = 21
# Android Build Tools版本
android.build_tools = 30.0.3
# NDK API版本
android.ndk_api = 21
# 支持的CPU架构
android.arch = armeabi-v7a,arm64-v8a
# 安卓权限（读写存储）
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# 入口文件
main.py = main.py
# 日志级别
log_level = 2

[buildozer]
# 全局日志级别
log_level = 2
# 根用户警告
warn_on_root = 1
