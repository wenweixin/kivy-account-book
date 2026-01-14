import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.config import Config
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

# 定义颜色常量
PRIMARY_COLOR = (0.2, 0.6, 0.9, 1)  # 主色调 - 蓝色
SUCCESS_COLOR = (0.2, 0.8, 0.2, 1)  # 成功 - 绿色
WARNING_COLOR = (0.9, 0.6, 0.2, 1)  # 警告 - 橙色
ERROR_COLOR = (0.9, 0.3, 0.3, 1)  # 错误 - 红色
BACKGROUND_COLOR = (0.95, 0.95, 0.95, 1)  # 背景色
TEXT_COLOR = (0.2, 0.2, 0.2, 1)  # 文字色
TAB_BG_COLOR = (0.85, 0.85, 0.85, 1)  # Tab背景色

# 添加字体大小常量（针对移动设备优化）
TITLE_FONT_SIZE = 36  # 标题字体 - 增加到36
HEADER_FONT_SIZE = 36  # 表头字体 - 增加到36
LABEL_FONT_SIZE = 32  # 标签字体 - 增加到32
BUTTON_FONT_SIZE = 32  # 按钮字体 - 增加到32
CONTENT_FONT_SIZE = 32  # 内容字体 - 增加到32
SMALL_CONTENT_FONT_SIZE = 32  # 小内容字体 - 增加到32

# ======== 核心修复：解决中文乱码 ========
# 1. 设置Kivy默认编码为UTF-8
os.environ['KIVY_TEXT'] = 'utf8'
Config.set('kivy', 'default_encoding', 'utf-8')


# 2. 注册中文字体（自动适配Windows/Linux/安卓）
def register_chinese_font():
    """注册中文字体（优先本地simhei.ttf，兼容Windows/Linux/安卓）"""
    # 1. 优先读取代码目录下的simhei.ttf（关键！适配打包场景）
    local_font = "simhei.ttf"
    if os.path.exists(local_font):
        LabelBase.register(DEFAULT_FONT, local_font)
        print(f"[表情] 成功加载本地中文字体：{local_font}")
        return

    # 2. 备用：读取系统字体（仅本地运行时生效）
    # Windows系统默认中文字体路径
    windows_fonts = [
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
    ]
    # Linux/WSL系统中文字体路径
    linux_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]

    # 优先选择系统中存在的字体
    font_path = None
    if sys.platform == 'win32':
        for font in windows_fonts:
            if os.path.exists(font):
                font_path = font
                break
    else:
        for font in linux_fonts:
            if os.path.exists(font):
                font_path = font
                break

    # 注册字体
    if font_path:
        LabelBase.register(DEFAULT_FONT, font_path)
        print(f"[表情] 成功加载系统中文字体：{font_path}")
    else:
        print("[表情] 未找到中文字体，仍可能出现乱码，但已启用UTF-8编码")


# 执行字体注册
register_chinese_font()

# ======== 适配修改：指定兼容的Kivy版本 ========
kivy.require('2.1.0')  # 改为2.1.0（和打包时安装的版本一致）
Window.softinput_mode = "below_target"


# ======== 核心适配：安卓数据存储路径（关键修改） ========
def get_data_file_path():
    """适配安卓/PC的文件存储路径"""
    if 'android' in sys.modules:  # 检测是否在安卓环境运行
        from android.storage import app_storage_path
        # 安卓：使用应用私有存储目录（可读写）
        data_dir = app_storage_path()
        return os.path.join(data_dir, "advanced_account_records.json")
    else:
        # PC：使用当前目录
        return "advanced_account_records.json"


# 数据存储路径（适配安卓）
DATA_FILE = get_data_file_path()
# 支出分类选项
EXPENSE_CATEGORIES = ["购物", "吃饭", "房租", "交通", "礼物"]
# 时间筛选类型（扩展为年、月、日）
TIME_FILTER_TYPES = ["今日", "本月", "本年", "自定义日期", "按月统计"]
# 添加总和选项
EXPENSE_CATEGORIES_WITH_TOTAL = EXPENSE_CATEGORIES + ["总和"]


# ==================== 数据处理函数（强化编码） ====================
def init_data():
    """初始化数据文件（强制UTF-8编码）"""
    if not os.path.exists(DATA_FILE):
        # 强制指定encoding='utf-8'，确保中文写入正常
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)  # ensure_ascii=False保留中文


def load_records() -> List[Dict]:
    """加载所有记账记录（强制UTF-8编码）"""
    init_data()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_record(category: str, remark: str, amount: float) -> bool:
    """保存支出记录（强制UTF-8编码）"""
    try:
        records = load_records()
        current_time = datetime.now()
        record = {
            "time": current_time.strftime("%Y-%m-%d %H:%M"),
            "date": current_time.strftime("%Y-%m-%d"),
            "month": current_time.strftime("%Y-%m"),
            "year": current_time.strftime("%Y"),
            "category": category,
            "remark": remark,
            "amount": round(float(amount), 2)
        }
        records.append(record)
        # 关键：ensure_ascii=False 保留中文，encoding='utf-8' 确保编码正确
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存记录失败: {e}")
        return False


def filter_records_by_time(records: List[Dict], filter_type: str, target_value: str = "") -> List[Dict]:
    """按时间筛选记录"""
    if filter_type == "今日":
        today = datetime.now().strftime("%Y-%m-%d")
        return [r for r in records if r["date"] == today]
    elif filter_type == "本月":
        current_month = datetime.now().strftime("%Y-%m")
        return [r for r in records if r["month"] == current_month]
    elif filter_type == "本年":
        current_year = datetime.now().strftime("%Y")
        return [r for r in records if r["year"] == current_year]
    elif filter_type == "自定义日期":
        # target_value 应该是 YYYY-MM-DD 格式的字符串
        if target_value:
            return [r for r in records if r["date"] == target_value]
        return records
    elif filter_type == "按月统计":
        return records
    else:
        return records


def search_records(records: List[Dict], keyword: str) -> List[Dict]:
    """模糊搜索记录（匹配分类/备注，支持中文）"""
    if not keyword:
        return records

    # 中文不区分大小写，直接匹配原字符
    keyword = keyword.strip()
    matched = []
    for record in records:
        if (keyword in record["category"]) or (keyword in record["remark"]):
            matched.append(record)
    return matched


def calculate_total(records: List[Dict]) -> float:
    """计算记录总金额"""
    total = sum([record["amount"] for record in records])
    return round(total, 2)


def get_monthly_statistics(records: List[Dict], category_filter: str):
    """获取月度统计数据（只统计当前年份）"""
    # 首先根据分类过滤数据
    if category_filter != "总和":
        filtered_records = [r for r in records if r["category"] == category_filter]
    else:
        filtered_records = records

    # 获取当前年份
    current_year = datetime.now().year

    # 按月份聚合数据
    monthly_totals = defaultdict(float)

    for record in filtered_records:
        # 只统计当前年份的数据
        if record["year"] == str(current_year):
            month = record["month"].split("-")[1]  # 获取月份部分（MM）
            monthly_totals[int(month)] += record["amount"]

    # 返回1-12月的数据，如果没有数据则为0
    result = []
    for month in range(1, 13):
        result.append((f"{month}月", monthly_totals[month]))

    return result


def get_daily_statistics(records: List[Dict], category_filter: str):
    """获取每日统计数据（最近20天）"""
    # 首先根据分类过滤数据
    if category_filter != "总和":
        filtered_records = [r for r in records if r["category"] == category_filter]
    else:
        filtered_records = records

    # 计算最近20天的日期
    daily_totals = defaultdict(float)
    for i in range(20):  # 修改为20天
        day_ago = datetime.now() - timedelta(days=i)
        day_str = day_ago.strftime("%m-%d")
        daily_totals[day_str] = 0.0

    # 聚合数据
    for record in filtered_records:
        date = record["date"]
        date_part = date.split("-")[1] + "-" + date.split("-")[2]  # MM-DD
        if date_part in daily_totals:
            daily_totals[date_part] += record["amount"]

    # 生成结果，从最近一天开始
    result = []
    for i in range(20):  # 修改为20天
        day_ago = datetime.now() - timedelta(days=i)
        day_str = day_ago.strftime("%m-%d")
        result.append((f"{day_str}", daily_totals[day_str]))

    return result


def get_yearly_statistics(records: List[Dict], category_filter: str):
    """获取年度统计数据（最近10年）"""
    # 首先根据分类过滤数据
    if category_filter != "总和":
        filtered_records = [r for r in records if r["category"] == category_filter]
    else:
        filtered_records = records

    # 计算最近10年的年份
    current_year = datetime.now().year
    yearly_totals = {}
    for i in range(10):
        year = current_year - i
        yearly_totals[str(year)] = 0.0

    # 聚合数据
    for record in filtered_records:
        year = record["year"]
        if year in yearly_totals:
            yearly_totals[year] += record["amount"]

    # 生成结果，从最近一年开始
    result = []
    for i in range(10):
        year = str(current_year - i)
        result.append((f"{year}", yearly_totals[year]))

    return result


# 自定义按钮类
class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  # 移除默认背景
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
            self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# 自定义柱状图组件
class BarChartWidget(FloatLayout):
    def __init__(self, data=[], **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.bind(size=self.draw_chart, pos=self.draw_chart)
        self.draw_chart()

    def draw_chart(self, *args):
        # 清除之前的绘制
        self.canvas.clear()

        # 移除之前添加的所有标签
        for child in list(self.children):
            if isinstance(child, Label):
                self.remove_widget(child)

        if not self.data:
            # 显示无数据提示
            no_data_label = Label(
                text="暂无统计数据",
                font_size=SMALL_CONTENT_FONT_SIZE,
                color=TEXT_COLOR,
                halign="center",
                valign="middle",
                center_x=self.center_x,
                center_y=self.center_y,
                font_name=DEFAULT_FONT
            )
            self.add_widget(no_data_label)
            return

        # 获取最大值用于缩放
        max_amount = max([item[1] for item in self.data]) if self.data else 1
        if max_amount == 0:
            max_amount = 1

        # 设置图表区域 - 使用整个组件的空间，并留出适当边距
        margin_left = 150  # 左边距，为月份标签预留空间
        margin_right = 50  # 右边距
        margin_top = 50  # 上边距
        margin_bottom = 80  # 下边距，为年份标签预留空间

        chart_left = self.x + margin_left
        chart_right = self.right - margin_right
        chart_top = self.top - margin_top
        chart_bottom = self.y + margin_bottom
        chart_width = chart_right - chart_left
        chart_height = chart_top - chart_bottom

        # 绘制背景
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=(chart_left, chart_bottom), size=(chart_width, chart_height))

            # 绘制网格线（垂直线）
            Color(0.9, 0.9, 0.9, 1)
            for i in range(5):
                x_pos = chart_left + (chart_width / 4) * i
                Line(points=[x_pos, chart_bottom, x_pos, chart_top], width=1)

        # 绘制水平柱状图
        num_bars = len(self.data)
        if num_bars > 0:
            # 计算柱子高度，确保所有柱子都能完整显示
            bar_height = chart_height / num_bars * 0.8  # 每个柱子占用80%的分配空间
            space_between_bars = chart_height / num_bars * 0.2  # 柱子之间的间距

            for i, (time_period, amount) in enumerate(self.data):
                bar_width = (amount / max_amount) * chart_width * 0.9  # 水平方向的宽度
                bar_x = chart_left  # 从左边开始
                # 从上到下排列，注意索引顺序
                bar_y = chart_bottom + chart_height - (i + 1) * (
                        bar_height + space_between_bars) + space_between_bars / 2

                # 绘制柱子
                with self.canvas:
                    Color(0.2, 0.6, 0.9, 1)  # 使用主色调
                    Rectangle(pos=(bar_x, bar_y), size=(bar_width, bar_height))

                    # 绘制柱子边框
                    Color(0.1, 0.4, 0.7, 1)
                    Line(rectangle=(bar_x, bar_y, bar_width, bar_height), width=1)

                # 创建标签显示金额（在柱子右侧）
                amount_label = Label(
                    text=f"{amount:.2f}元",
                    font_size=SMALL_CONTENT_FONT_SIZE - 7,  # 与月份标签字体大小相同
                    size_hint=(None, None),
                    width=100,
                    height=min(bar_height, 60),
                    halign='left',
                    font_name=DEFAULT_FONT,
                    color=TEXT_COLOR
                )
                amount_label.x = bar_x + bar_width + 5
                amount_label.center_y = bar_y + bar_height / 2
                self.add_widget(amount_label)

                # 创建标签显示时间（在柱子左侧，固定在最左边）
                time_label = Label(
                    text=time_period,
                    font_size=SMALL_CONTENT_FONT_SIZE - 7,  # 月份标签字体大小
                    size_hint=(None, None),
                    width=120,
                    height=min(bar_height, 60),
                    halign='right',
                    shorten=True,
                    text_size=(120, min(bar_height, 60)),
                    font_name=DEFAULT_FONT,
                    color=TEXT_COLOR
                )
                time_label.x = self.x + 10  # 固定在最左边，而不是柱子的左边
                time_label.center_y = bar_y + bar_height / 2
                self.add_widget(time_label)

                # 绘制Y轴标签线（连接月份标签和柱子）
                with self.canvas:
                    Color(0.5, 0.5, 0.5, 1)
                    Line(points=[time_label.right, time_label.center_y, bar_x, bar_y + bar_height / 2], width=1)

            # 添加当前年份显示
            current_year = datetime.now().year
            year_label = Label(
                text=f"{current_year}年",
                font_size=SMALL_CONTENT_FONT_SIZE,
                size_hint=(None, None),
                width=100,
                height=30,
                halign='center',
                font_name=DEFAULT_FONT,
                color=TEXT_COLOR
            )
            year_label.center_x = self.center_x
            year_label.y = self.y + 20  # 在底部边缘上方
            self.add_widget(year_label)


# 第一页：记账输入页面（优化版）
class InputPage(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super().__init__(**kwargs)
        self.parent_app = parent_app
        self.orientation = "vertical"
        self.padding = 20  # 增加内边距
        self.spacing = 10  # 增加间距

        # 设置整体背景
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # ========== 1. 记账输入区域 - 优化样式 ==========
        input_layout = self.create_input_section()
        input_layout.size_hint_y = 0.6  # 增加到60%高度
        self.add_widget(input_layout)

        # ========== 2. 时间筛选统计区域 ==========
        filter_layout = self.create_stats_section()
        filter_layout.size_hint_y = 0.25  # 调整到25%高度
        self.add_widget(filter_layout)

        # ========== 3. 统计结果展示 ==========
        self.result_label = Label(
            text="总支出：0.00 元",
            font_size=TITLE_FONT_SIZE,
            color=ERROR_COLOR,
            size_hint_y=0.15,  # 调整到15%高度
            halign="center",
            bold=True,
            font_name=DEFAULT_FONT
        )
        self.add_widget(self.result_label)

        # 初始化加载记录
        self.current_records = load_records()

    def create_input_section(self):
        # 创建带边框的卡片式布局
        card_layout = BoxLayout(orientation='vertical', padding=20)  # 增加内边距
        # 设置为动态大小，根据分配的高度调整
        with card_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.card_bg = RoundedRectangle(pos=card_layout.pos, size=card_layout.size,
                                            radius=[20])  # 增加圆角半径
            card_layout.bind(pos=self._update_card_bg, size=self._update_card_bg)

        # 标题
        header = Label(text="[b]记账输入[/b]", markup=True, size_hint_y=None, height=70,  # 增加标题高度
                       color=PRIMARY_COLOR, font_size=TITLE_FONT_SIZE, font_name=DEFAULT_FONT)
        card_layout.add_widget(header)

        # 输入网格 - 使用3行布局以获得更好的对称性
        input_grid = GridLayout(cols=2, spacing=15, padding=[0, 15, 0, 0])  # 增加间距

        # 1.1 时间（自动显示）
        input_grid.add_widget(
            Label(text="时间：", font_size=LABEL_FONT_SIZE, halign="right", color=TEXT_COLOR, size_hint_y=None,
                  height=70))  # 增加高度
        self.time_label = Label(text=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                font_size=CONTENT_FONT_SIZE, color=PRIMARY_COLOR, size_hint_y=None, height=70)
        input_grid.add_widget(self.time_label)

        # 1.2 支出分类（下拉选择，修复中文显示）
        input_grid.add_widget(
            Label(text="分类：", font_size=LABEL_FONT_SIZE, halign="right", color=TEXT_COLOR, size_hint_y=None,
                  height=70))
        self.category_spinner = Spinner(
            text=EXPENSE_CATEGORIES[0],
            values=EXPENSE_CATEGORIES,
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            # 强制指定字体渲染中文
            font_name=DEFAULT_FONT
        )
        input_grid.add_widget(self.category_spinner)

        # 1.3 具体备注（可空，支持中文输入）- 移除错误的input_encoding参数
        input_grid.add_widget(
            Label(text="备注：", font_size=LABEL_FONT_SIZE, halign="right", color=TEXT_COLOR, size_hint_y=None,
                  height=70))
        self.remark_input = TextInput(
            hint_text="例如：麦当劳/地铁3号线",
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            multiline=False,  # 单行输入
            background_color=(0.98, 0.98, 0.98, 1),  # 浅灰色背景
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT
        )
        input_grid.add_widget(self.remark_input)

        # 1.4 金额（元）
        input_grid.add_widget(
            Label(text="金额（元）：", font_size=LABEL_FONT_SIZE, halign="right", color=TEXT_COLOR, size_hint_y=None,
                  height=70))
        self.amount_input = TextInput(
            hint_text="请输入数字",
            font_size=CONTENT_FONT_SIZE,
            input_filter="float",
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT
        )
        input_grid.add_widget(self.amount_input)

        # 1.5 保存按钮
        input_grid.add_widget(Label(size_hint_y=None, height=70))
        save_btn = StyledButton(
            text="保存支出记录",
            font_size=BUTTON_FONT_SIZE,
            background_color=SUCCESS_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=80,  # 进一步增加按钮高度
            font_name=DEFAULT_FONT
        )
        save_btn.bind(on_press=self.save_record_handler)
        input_grid.add_widget(save_btn)

        card_layout.add_widget(input_grid)
        return card_layout

    def create_stats_section(self):
        stats_layout = GridLayout(cols=4, spacing=15, padding=15)  # 增加间距和内边距

        # 添加圆角背景
        with stats_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.stats_bg = RoundedRectangle(pos=stats_layout.pos, size=stats_layout.size, radius=[15])
            stats_layout.bind(pos=self._update_stats_bg, size=self._update_stats_bg)

        # 统计区域控件
        stats_layout.add_widget(
            Label(text="时间筛选：", font_size=LABEL_FONT_SIZE, halign="center", color=TEXT_COLOR, size_hint_y=None,
                  height=70))  # 增加高度
        self.filter_spinner = Spinner(
            text=TIME_FILTER_TYPES[0],
            values=TIME_FILTER_TYPES,
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            font_name=DEFAULT_FONT
        )
        # 添加筛选类型变化事件监听
        self.filter_spinner.bind(text=self.on_filter_type_change)
        stats_layout.add_widget(self.filter_spinner)

        # 创建日期输入框容器 - 使用水平布局放置年月日输入框
        self.date_input_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=70)  # 增加高度

        # 年输入框
        self.year_input = TextInput(
            hint_text="年",
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT,
            input_filter='int'  # 只允许输入整数
        )

        # 月输入框
        self.month_input = TextInput(
            hint_text="月",
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT,
            input_filter='int'  # 只允许输入整数
        )

        # 日输入框
        self.day_input = TextInput(
            hint_text="日",
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT,
            input_filter='int'  # 只允许输入整数
        )

        # 初始状态下不添加输入框，只有在选择"自定义日期"时才添加
        self.date_input_container.add_widget(self.year_input)
        self.date_input_container.add_widget(self.month_input)
        self.date_input_container.add_widget(self.day_input)
        self.date_input_container.clear_widgets()  # 初始清空，稍后根据选择决定是否添加

        stats_layout.add_widget(self.date_input_container)

        filter_btn = StyledButton(
            text="统计",
            font_size=BUTTON_FONT_SIZE,
            background_color=PRIMARY_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=70,  # 增加高度
            font_name=DEFAULT_FONT
        )
        filter_btn.bind(on_press=self.filter_and_calculate)
        stats_layout.add_widget(filter_btn)

        return stats_layout

    # ========== 核心功能函数 ==========
    def save_record_handler(self, instance):
        """保存支出记录处理"""
        amount_text = self.amount_input.text.strip()
        if not amount_text or float(amount_text) <= 0:
            self.result_label.text = "错误：金额必须是大于0的数字！"
            self.result_label.color = ERROR_COLOR
            return

        category = self.category_spinner.text
        remark = self.remark_input.text.strip()
        amount = float(amount_text)

        if save_record(category, remark, amount):
            self.remark_input.text = ""
            self.amount_input.text = ""
            self.time_label.text = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.current_records = load_records()
            self.parent_app.refresh_all_pages()  # 通知其他页面更新数据
            self.result_label.text = f"保存成功！累计支出：{calculate_total(self.current_records)} 元"
            self.result_label.color = SUCCESS_COLOR
        else:
            self.result_label.text = "保存失败！请检查输入"
            self.result_label.color = ERROR_COLOR

    def filter_and_calculate(self, instance):
        """按时间筛选并计算总支出"""
        filter_type = self.filter_spinner.text
        filter_value = ""

        # 根据筛选类型获取正确的筛选值
        if filter_type == "自定义日期":
            year = self.year_input.text.strip()
            month = self.month_input.text.strip()
            day = self.day_input.text.strip()

            # 验证输入是否完整且有效
            if not year or not month or not day:
                self.result_label.text = "错误：请输入完整的年月日！"
                self.result_label.color = ERROR_COLOR
                return

            # 验证年月日的有效性
            try:
                # 将月份和日期转换为两位数格式
                month_int = int(month)
                day_int = int(day)

                if month_int < 1 or month_int > 12:
                    self.result_label.text = "错误：月份应在1-12之间！"
                    self.result_label.color = ERROR_COLOR
                    return

                if day_int < 1 or day_int > 31:
                    self.result_label.text = "错误：日期应在1-31之间！"
                    self.result_label.color = ERROR_COLOR
                    return

                # 组合日期字符串
                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

                if not self.validate_date_format(formatted_date):
                    self.result_label.text = "错误：日期格式无效！"
                    self.result_label.color = ERROR_COLOR
                    return

                filter_value = formatted_date
            except ValueError:
                self.result_label.text = "错误：年月日必须是数字！"
                self.result_label.color = ERROR_COLOR
                return
        # 其他类型无需额外输入值

        filtered_records = filter_records_by_time(self.current_records, filter_type, filter_value)
        total = calculate_total(filtered_records)

        self.parent_app.refresh_all_pages()

        # 根据筛选类型显示不同的结果文本
        display_text = self.get_filter_display_text(filter_type, filter_value)
        self.result_label.text = f"{display_text}支出：{total} 元"
        self.result_label.color = PRIMARY_COLOR

    def on_filter_type_change(self, spinner, text):
        """处理筛选类型变化"""
        if text == "自定义日期":
            # 显示年月日输入框
            self.date_input_container.clear_widgets()
            self.date_input_container.add_widget(self.year_input)
            self.date_input_container.add_widget(self.month_input)
            self.date_input_container.add_widget(self.day_input)
        else:
            # 对于"今日"、"本月"、"本年"，不需要额外输入
            self.date_input_container.clear_widgets()
            placeholder_label = Label(
                text="自动选择",
                font_size=CONTENT_FONT_SIZE,
                size_hint_x=1,
                size_hint_y=None,
                height=70,  # 增加高度
                color=TEXT_COLOR,
                halign="left",
                font_name=DEFAULT_FONT
            )
            self.date_input_container.add_widget(placeholder_label)

    def validate_date_format(self, date_str):
        """验证日期格式是否为 YYYY-MM-DD"""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_filter_display_text(self, filter_type, filter_value=""):
        """获取筛选类型的显示文本"""
        if filter_type == "自定义日期":
            return f"日期({filter_value})"
        elif filter_type == "今日":
            return "今日"
        elif filter_type == "本月":
            return "本月"
        elif filter_type == "本年":
            return "本年"
        elif filter_type == "按月统计":
            return "累计"
        else:
            return filter_type

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_card_bg(self, instance, value):
        self.card_bg.pos = instance.pos
        self.card_bg.size = instance.size

    def _update_stats_bg(self, instance, value):
        self.stats_bg.pos = instance.pos
        self.stats_bg.size = instance.size


# 第二页：搜索页面
class SearchPage(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super().__init__(**kwargs)
        self.parent_app = parent_app
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10

        # 设置整体背景
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # 搜索区域
        search_layout = self.create_search_section()
        self.add_widget(search_layout)

        # 统计结果展示
        self.search_result_label = Label(
            text="搜索结果：0.00 元",
            font_size=TITLE_FONT_SIZE,
            color=WARNING_COLOR,
            size_hint_y=None,
            height=60,
            halign="center",
            bold=True,
            font_name=DEFAULT_FONT
        )
        self.add_widget(self.search_result_label)

        # 搜索结果记录展示区域
        self.search_record_scroll = ScrollView(size_hint_y=0.5)
        self.search_record_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.search_record_layout.bind(minimum_height=self.search_record_layout.setter('height'))
        self.search_record_scroll.add_widget(self.search_record_layout)
        self.add_widget(self.search_record_scroll)

        # 初始化加载记录
        self.current_records = load_records()

    def create_search_section(self):
        search_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=70, padding=10)

        # 添加圆角背景
        with search_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.search_bg = RoundedRectangle(pos=search_layout.pos, size=search_layout.size, radius=[10])
            search_layout.bind(pos=self._update_search_bg, size=self._update_search_bg)

        search_layout.add_widget(Label(text="搜索：", font_size=LABEL_FONT_SIZE, halign="center", color=TEXT_COLOR))
        self.search_input = TextInput(
            hint_text="模糊搜索关键词",
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT
        )
        search_layout.add_widget(self.search_input)

        search_btn = StyledButton(
            text="搜索并求和",
            font_size=BUTTON_FONT_SIZE,
            background_color=WARNING_COLOR,
            size_hint_x=1,
            font_name=DEFAULT_FONT,
            height=50
        )
        search_btn.bind(on_press=self.search_and_calculate)
        search_layout.add_widget(search_btn)

        return search_layout

    def search_and_calculate(self, instance):
        """模糊搜索并计算总支出（支持中文关键词）"""
        keyword = self.search_input.text.strip()
        if not keyword:
            self.search_result_label.text = "错误：请输入搜索关键词！"
            self.search_result_label.color = ERROR_COLOR
            return

        matched_records = search_records(self.current_records, keyword)
        total = calculate_total(matched_records)

        self.refresh_search_records(matched_records)
        self.search_result_label.text = f"搜索「{keyword}」总支出：{total} 元"
        self.search_result_label.color = WARNING_COLOR

    def refresh_search_records(self, records: List[Dict]):
        """刷新搜索记录展示区域"""
        self.search_record_layout.clear_widgets()

        if not records:
            empty_label = Label(
                text="暂无匹配记录",
                font_size=SMALL_CONTENT_FONT_SIZE,
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=40,
                font_name=DEFAULT_FONT
            )
            self.search_record_layout.add_widget(empty_label)
            return

        for i, record in enumerate(reversed(records)):
            # 创建纯内容的BoxLayout，不添加背景色
            record_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10)

            # 不再绘制背景矩形，保持透明

            record_text = (
                f"[color=#3399CC]{record['time']}[/color] | "
                f"分类：{record['category']} | "
                f"备注：{record['remark'] or '无'} | "
                f"[b]金额：{record['amount']} 元[/b]"
            )

            record_label = Label(
                text=record_text,
                font_size=SMALL_CONTENT_FONT_SIZE,
                color=TEXT_COLOR,
                markup=True,
                halign='left',
                valign='middle',
                text_size=(self.width * 0.9, None),
                font_name=DEFAULT_FONT
            )
            record_box.add_widget(record_label)
            self.search_record_layout.add_widget(record_box)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_search_bg(self, instance, value):
        self.search_bg.pos = instance.pos
        self.search_bg.size = instance.size


# 第三页：全部记录页面（修复版）
class RecordsPage(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super().__init__(**kwargs)
        self.parent_app = parent_app
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10

        # 设置整体背景
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # 标题
        title_layout = BoxLayout(size_hint_y=None, height=60)
        title_label = Label(
            text="全部记录",
            font_size=TITLE_FONT_SIZE,
            color=PRIMARY_COLOR,
            bold=True,
            font_name=DEFAULT_FONT
        )
        title_layout.add_widget(title_label)
        self.add_widget(title_layout)

        # 总支出统计
        self.total_label = Label(
            text="总支出：0.00 元",
            font_size=HEADER_FONT_SIZE,
            color=ERROR_COLOR,
            size_hint_y=None,
            height=50,
            halign="center",
            bold=True,
            font_name=DEFAULT_FONT
        )
        self.add_widget(self.total_label)

        # 记录展示区域
        self.record_scroll = ScrollView(size_hint_y=1)
        self.record_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.record_layout.bind(minimum_height=self.record_layout.setter('height'))
        self.record_scroll.add_widget(self.record_layout)
        self.add_widget(self.record_scroll)

        # 初始化加载记录
        self.current_records = load_records()
        self.refresh_records(self.current_records)

    def refresh_records(self, records: List[Dict]):
        """刷新记录展示区域"""
        self.record_layout.clear_widgets()

        if not records:
            empty_label = Label(
                text="暂无记录",
                font_size=SMALL_CONTENT_FONT_SIZE,
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=40,
                font_name=DEFAULT_FONT
            )
            self.record_layout.add_widget(empty_label)
            return

        for i, record in enumerate(reversed(records)):
            # 创建纯内容的BoxLayout，不添加背景色
            record_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10)

            # 不再绘制背景矩形，保持透明

            record_text = (
                f"[color=#3399CC]{record['time']}[/color] | "
                f"分类：{record['category']} | "
                f"备注：{record['remark'] or '无'} | "
                f"[b]金额：{record['amount']} 元[/b]"
            )

            record_label = Label(
                text=record_text,
                font_size=SMALL_CONTENT_FONT_SIZE,  # 调整字体大小
                color=TEXT_COLOR,
                markup=True,
                halign='left',  # 修复：改为左对齐
                valign='middle',
                text_size=(None, None),  # 修复：取消固定宽度，允许自动换行
                font_name=DEFAULT_FONT
            )
            record_box.add_widget(record_label)
            self.record_layout.add_widget(record_box)

        # 更新总金额
        total = calculate_total(records)
        self.total_label.text = f"总支出：{total} 元"

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


# 第四页：统计页面
class StatisticsPage(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super().__init__(**kwargs)
        self.parent_app = parent_app
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10

        # 设置整体背景
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # 标题
        title_layout = BoxLayout(size_hint_y=None, height=60)
        title_label = Label(
            text="月度统计分析",
            font_size=TITLE_FONT_SIZE,
            color=PRIMARY_COLOR,
            bold=True,
            font_name=DEFAULT_FONT
        )
        title_layout.add_widget(title_label)
        self.add_widget(title_layout)

        # 控制面板
        control_layout = self.create_control_section()
        control_layout.size_hint_y = None
        control_layout.height = 120
        self.add_widget(control_layout)

        # 图表区域
        self.chart_container = BoxLayout(size_hint_y=1)
        self.add_widget(self.chart_container)

        # 初始化加载记录
        self.current_records = load_records()
        self.show_statistics()

    def create_control_section(self):
        control_layout = GridLayout(cols=4, spacing=10, padding=10)

        # 添加圆角背景
        with control_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.control_bg = RoundedRectangle(pos=control_layout.pos, size=control_layout.size, radius=[10])
            control_layout.bind(pos=self._update_control_bg, size=self._update_control_bg)

        # 时间筛选
        control_layout.add_widget(Label(text="时间维度：", font_size=LABEL_FONT_SIZE, halign="center", color=TEXT_COLOR))
        self.time_filter_spinner = Spinner(
            text="按月统计",
            values=["按月统计", "按日统计", "按年统计"],
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=50,
            font_name=DEFAULT_FONT
        )
        control_layout.add_widget(self.time_filter_spinner)

        # 分类筛选
        control_layout.add_widget(Label(text="分类筛选：", font_size=LABEL_FONT_SIZE, halign="center", color=TEXT_COLOR))
        self.category_filter_spinner = Spinner(
            text=EXPENSE_CATEGORIES_WITH_TOTAL[0],
            values=EXPENSE_CATEGORIES_WITH_TOTAL,
            font_size=CONTENT_FONT_SIZE,
            size_hint_x=1,
            size_hint_y=None,
            height=50,
            font_name=DEFAULT_FONT
        )
        control_layout.add_widget(self.category_filter_spinner)

        # 统计按钮
        stats_btn = StyledButton(
            text="生成统计",
            font_size=BUTTON_FONT_SIZE,
            background_color=PRIMARY_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=50,
            font_name=DEFAULT_FONT
        )
        stats_btn.bind(on_press=self.show_statistics)
        control_layout.add_widget(stats_btn)

        # 添加一个空标签占位
        control_layout.add_widget(Label())

        return control_layout

    def show_statistics(self, instance=None):
        """显示统计数据"""
        time_filter = self.time_filter_spinner.text
        category_filter = self.category_filter_spinner.text

        # 根据时间筛选类型获取统计数据
        if time_filter == "按月统计":
            monthly_data = get_monthly_statistics(self.current_records, category_filter)
        elif time_filter == "按日统计":
            monthly_data = get_daily_statistics(self.current_records, category_filter)
        elif time_filter == "按年统计":
            monthly_data = get_yearly_statistics(self.current_records, category_filter)
        else:
            monthly_data = []

        # 清除旧的图表
        self.chart_container.clear_widgets()

        # 创建新的图表
        if monthly_data:
            chart_widget = BarChartWidget(data=monthly_data)
            self.chart_container.add_widget(chart_widget)
        else:
            # 显示无数据提示
            no_data_label = Label(
                text="暂无统计数据",
                font_size=TITLE_FONT_SIZE,
                color=TEXT_COLOR,
                halign="center",
                valign="middle",
                font_name=DEFAULT_FONT
            )
            self.chart_container.add_widget(no_data_label)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_control_bg(self, instance, value):
        self.control_bg.pos = instance.pos
        self.control_bg.size = instance.size


# 主应用类
class AdvancedAccountBookApp(App):
    def build(self):
        self.title = "高级记账本"

        # 主布局
        main_layout = BoxLayout(orientation='vertical')

        # 创建Tab面板
        tab_panel = TabbedPanel(do_default_tab=False)

        # 创建四个页面
        self.input_page = InputPage(parent_app=self)
        self.search_page = SearchPage(parent_app=self)
        self.records_page = RecordsPage(parent_app=self)
        self.statistics_page = StatisticsPage(parent_app=self)

        # 创建Tab项
        input_tab = TabbedPanelItem(text='记账')
        input_tab.font_size = TITLE_FONT_SIZE  # 设置Tab字体大小
        search_tab = TabbedPanelItem(text='搜索')
        search_tab.font_size = TITLE_FONT_SIZE
        records_tab = TabbedPanelItem(text='记录')
        records_tab.font_size = TITLE_FONT_SIZE
        statistics_tab = TabbedPanelItem(text='统计')
        statistics_tab.font_size = TITLE_FONT_SIZE

        # 将页面添加到对应Tab
        input_tab.content = self.input_page
        search_tab.content = self.search_page
        records_tab.content = self.records_page
        statistics_tab.content = self.statistics_page

        # 添加Tab到面板
        tab_panel.add_widget(input_tab)
        tab_panel.add_widget(search_tab)
        tab_panel.add_widget(records_tab)
        tab_panel.add_widget(statistics_tab)

        # 设置默认选中的Tab
        tab_panel.default_tab = input_tab

        # 将Tab面板添加到主布局
        main_layout.add_widget(tab_panel)

        return main_layout

    def refresh_all_pages(self):
        """刷新所有页面的数据"""
        # 重新加载记录
        records = load_records()

        # 更新各个页面的数据
        self.input_page.current_records = records
        self.search_page.current_records = records
        self.records_page.current_records = records
        self.statistics_page.current_records = records

        # 刷新各个页面的显示
        self.records_page.refresh_records(records)

        # 更新搜索页面的记录显示
        self.search_page.refresh_search_records(self.search_page.current_records)


if __name__ == "__main__":
    # 最终确保编码正确
    sys.stdout.reconfigure(encoding='utf-8')

    AdvancedAccountBookApp().run()
