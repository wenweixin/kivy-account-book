# -*- coding: utf-8 -*-
# @Author: wenweixin
# @Date:   2026/1/13 12:39
# @File:   main.py
# main.py - 安卓打包强制要求的入口文件
# 直接导入并运行记账本应用
import account_book

# 调用应用的主入口（匹配你的代码结构）
if __name__ == '__main__':
    account_book.AdvancedAccountBookApp().run()