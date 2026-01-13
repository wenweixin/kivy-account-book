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
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
import json
import os
import sys
from datetime import datetime
from typing import List, Dict

# 定义颜色常量
PRIMARY_COLOR = (0.2, 0.6, 0.9, 1)  # 主色调 - 蓝色
SUCCESS_COLOR = (0.2, 0.8, 0.2, 1)  # 成功 - 绿色
WARNING_COLOR = (0.9, 0.6, 0.2, 1)  # 警告 - 橙色
ERROR_COLOR = (0.9, 0.3, 0.3, 1)  # 错误 - 红色
BACKGROUND_COLOR = (0.95, 0.95, 0.95, 1)  # 背景色
TEXT_COLOR = (0.2, 0.2, 0.2, 1)  # 文字色
TAB_BG_COLOR = (0.85, 0.85, 0.85, 1)  # Tab背景色

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
        print(f"✅ 成功加载本地中文字体：{local_font}")
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
        print(f"✅ 成功加载系统中文字体：{font_path}")
    else:
        print("❌ 未找到中文字体，仍可能出现乱码，但已启用UTF-8编码")


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
EXPENSE_CATEGORIES = ["购物", "吃饭", "房租", "交通", "礼物", "借钱"]
# 时间筛选类型
TIME_FILTER_TYPES = ["全部", "按日", "按月", "按年"]


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
    if filter_type == "全部" or not target_value:
        return records

    filtered = []
    for record in records:
        if filter_type == "按日" and record["date"] == target_value:
            filtered.append(record)
        elif filter_type == "按月" and record["month"] == target_value:
            filtered.append(record)
        elif filter_type == "按年" and record["year"] == target_value:
            filtered.append(record)
    return filtered


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

# 第一页：记账输入页面（优化版）
class InputPage(BoxLayout):
    def __init__(self, parent_app, **kwargs):
        super().__init__(**kwargs)
        self.parent_app = parent_app
        self.orientation = "vertical"
        self.padding = 0  # 改为0，消除内边距
        self.spacing = 0  # 改为0，消除间距

        # 设置整体背景
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)

        # ========== 1. 记账输入区域 - 优化样式 ==========
        input_layout = self.create_input_section()
        input_layout.size_hint_y = 0.5  # 分配50%高度
        self.add_widget(input_layout)

        # ========== 2. 时间筛选统计区域 ==========
        filter_layout = self.create_stats_section()
        filter_layout.size_hint_y = 0.2  # 分配20%高度
        self.add_widget(filter_layout)

        # ========== 3. 统计结果展示 ==========
        self.result_label = Label(
            text="总支出：0.00 元",
            font_size=20,
            color=ERROR_COLOR,
            size_hint_y=0.1,  # 分配10%高度
            halign="center",
            bold=True,
            font_name=DEFAULT_FONT
        )
        self.add_widget(self.result_label)

        # 初始化加载记录
        self.current_records = load_records()

    def create_input_section(self):
        # 创建带边框的卡片式布局
        card_layout = BoxLayout(orientation='vertical', padding=10)
        # 设置为动态大小，根据分配的高度调整
        with card_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.card_bg = RoundedRectangle(pos=card_layout.pos, size=card_layout.size,
                                            radius=[15])
            card_layout.bind(pos=self._update_card_bg, size=self._update_card_bg)

        # 标题
        header = Label(text="[b]记账输入[/b]", markup=True, size_hint_y=None, height=40,
                       color=PRIMARY_COLOR, font_size=18, font_name=DEFAULT_FONT)
        card_layout.add_widget(header)

        # 输入网格 - 使用3行布局以获得更好的对称性
        input_grid = GridLayout(cols=2, spacing=10, padding=[0, 10, 0, 0])

        # 1.1 时间（自动显示）
        input_grid.add_widget(
            Label(text="时间：", font_size=16, halign="right", color=TEXT_COLOR, size_hint_y=None, height=40))
        self.time_label = Label(text=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                font_size=16, color=PRIMARY_COLOR, size_hint_y=None, height=40)
        input_grid.add_widget(self.time_label)

        # 1.2 支出分类（下拉选择，修复中文显示）
        input_grid.add_widget(
            Label(text="分类：", font_size=16, halign="right", color=TEXT_COLOR, size_hint_y=None, height=40))
        self.category_spinner = Spinner(
            text=EXPENSE_CATEGORIES[0],
            values=EXPENSE_CATEGORIES,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None,
            height=40,
            # 强制指定字体渲染中文
            font_name=DEFAULT_FONT
        )
        input_grid.add_widget(self.category_spinner)

        # 1.3 具体备注（可空，支持中文输入）- 移除错误的input_encoding参数
        input_grid.add_widget(
            Label(text="备注：", font_size=16, halign="right", color=TEXT_COLOR, size_hint_y=None, height=40))
        self.remark_input = TextInput(
            hint_text="例如：麦当劳/地铁3号线",
            font_size=16,
            size_hint_x=1,
            size_hint_y=None,
            height=40,
            multiline=False,  # 单行输入
            background_color=(0.98, 0.98, 0.98, 1),  # 浅灰色背景
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT
        )
        input_grid.add_widget(self.remark_input)

        # 1.4 金额（元）
        input_grid.add_widget(
            Label(text="金额（元）：", font_size=16, halign="right", color=TEXT_COLOR, size_hint_y=None, height=40))
        self.amount_input = TextInput(
            hint_text="请输入数字",
            font_size=16,
            input_filter="float",
            size_hint_x=1,
            size_hint_y=None,
            height=40,
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT
        )
        input_grid.add_widget(self.amount_input)

        # 1.5 保存按钮
        input_grid.add_widget(Label(size_hint_y=None, height=40))
        save_btn = StyledButton(
            text="保存支出记录",
            font_size=18,
            background_color=SUCCESS_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=50,  # 增加按钮高度
            font_name=DEFAULT_FONT
        )
        save_btn.bind(on_press=self.save_record_handler)
        input_grid.add_widget(save_btn)

        card_layout.add_widget(input_grid)
        return card_layout

    def create_stats_section(self):
        stats_layout = GridLayout(cols=4, spacing=10, padding=10)

        # 添加圆角背景
        with stats_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.stats_bg = RoundedRectangle(pos=stats_layout.pos, size=stats_layout.size, radius=[10])
            stats_layout.bind(pos=self._update_stats_bg, size=self._update_stats_bg)

        # 统计区域控件
        stats_layout.add_widget(
            Label(text="时间筛选：", font_size=16, halign="center", color=TEXT_COLOR, size_hint_y=None, height=40))
        self.filter_spinner = Spinner(
            text=TIME_FILTER_TYPES[0],
            values=TIME_FILTER_TYPES,
            font_size=16,
            size_hint_x=1,
            size_hint_y=None,
            height=40,
            font_name=DEFAULT_FONT
        )
        stats_layout.add_widget(self.filter_spinner)

        self.filter_input = TextInput(
            hint_text="例：2024-12-01",
            font_size=16,
            size_hint_x=1,
            size_hint_y=None,
            height=40,
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT
        )
        stats_layout.add_widget(self.filter_input)

        filter_btn = StyledButton(
            text="统计",
            font_size=16,
            background_color=PRIMARY_COLOR,
            size_hint_x=1,
            size_hint_y=None,
            height=40,
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
        filter_value = self.filter_input.text.strip()

        filtered_records = filter_records_by_time(self.current_records, filter_type, filter_value)
        total = calculate_total(filtered_records)

        self.parent_app.refresh_all_pages()  # 通知其他页面更新数据
        self.result_label.text = f"{filter_type}支出：{total} 元"
        self.result_label.color = PRIMARY_COLOR

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
            font_size=20,
            color=WARNING_COLOR,
            size_hint_y=None,
            height=50,
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
        search_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=60, padding=10)

        # 添加圆角背景
        with search_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.search_bg = RoundedRectangle(pos=search_layout.pos, size=search_layout.size, radius=[10])
            search_layout.bind(pos=self._update_search_bg, size=self._update_search_bg)

        search_layout.add_widget(Label(text="搜索：", font_size=16, halign="center", color=TEXT_COLOR))
        self.search_input = TextInput(
            hint_text="模糊搜索关键词",
            font_size=16,
            size_hint_x=1,
            background_color=(0.98, 0.98, 0.98, 1),
            foreground_color=TEXT_COLOR,
            font_name=DEFAULT_FONT
        )
        search_layout.add_widget(self.search_input)

        search_btn = StyledButton(
            text="搜索并求和",
            font_size=16,
            background_color=WARNING_COLOR,
            size_hint_x=1,
            font_name=DEFAULT_FONT,
            height=40
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
                font_size=18,
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=40,
                font_name=DEFAULT_FONT
            )
            self.search_record_layout.add_widget(empty_label)
            return

        for i, record in enumerate(reversed(records)):
            # 交替背景色
            bg_color = (1, 1, 1, 1) if i % 2 == 0 else (0.98, 0.98, 0.98, 1)

            record_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10)
            with record_box.canvas.before:
                Color(*bg_color)
                rect = RoundedRectangle(pos=record_box.pos, size=record_box.size, radius=[8])
                record_box.bind(pos=lambda w, x: setattr(rect, 'pos', w.pos),
                                size=lambda w, x: setattr(rect, 'size', w.size))

            record_text = (
                f"[color=#3399CC]{record['time']}[/color] | "
                f"分类：{record['category']} | "
                f"备注：{record['remark'] or '无'} | "
                f"[b]金额：{record['amount']} 元[/b]"
            )

            record_label = Label(
                text=record_text,
                font_size=14,
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
        title_layout = BoxLayout(size_hint_y=None, height=50)
        title_label = Label(
            text="全部记录",
            font_size=24,
            color=PRIMARY_COLOR,
            bold=True,
            font_name=DEFAULT_FONT
        )
        title_layout.add_widget(title_label)
        self.add_widget(title_layout)

        # 总支出统计
        self.total_label = Label(
            text="总支出：0.00 元",
            font_size=18,
            color=ERROR_COLOR,
            size_hint_y=None,
            height=40,
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
                font_size=18,
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=40,
                font_name=DEFAULT_FONT
            )
            self.record_layout.add_widget(empty_label)
            return

        for i, record in enumerate(reversed(records)):
            # 交替背景色
            bg_color = (1, 1, 1, 1) if i % 2 == 0 else (0.98, 0.98, 0.98, 1)

            record_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10)
            with record_box.canvas.before:
                Color(*bg_color)
                rect = RoundedRectangle(pos=record_box.pos, size=record_box.size, radius=[8])
                record_box.bind(pos=lambda w, x: setattr(rect, 'pos', w.pos),
                                size=lambda w, x: setattr(rect, 'size', w.size))

            record_text = (
                f"[color=#3399CC]{record['time']}[/color] | "
                f"分类：{record['category']} | "
                f"备注：{record['remark'] or '无'} | "
                f"[b]金额：{record['amount']} 元[/b]"
            )

            record_label = Label(
                text=record_text,
                font_size=14,
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


# 主应用类
class AdvancedAccountBookApp(App):
    def build(self):
        self.title = "高级记账本"

        # 主布局
        main_layout = BoxLayout(orientation='vertical')

        # 创建Tab面板
        tab_panel = TabbedPanel(do_default_tab=False)

        # 创建三个页面
        self.input_page = InputPage(parent_app=self)
        self.search_page = SearchPage(parent_app=self)
        self.records_page = RecordsPage(parent_app=self)

        # 创建Tab项
        input_tab = TabbedPanelItem(text='记账')
        search_tab = TabbedPanelItem(text='搜索')
        records_tab = TabbedPanelItem(text='记录')

        # 将页面添加到对应Tab
        input_tab.content = self.input_page
        search_tab.content = self.search_page
        records_tab.content = self.records_page

        # 添加Tab到面板
        tab_panel.add_widget(input_tab)
        tab_panel.add_widget(search_tab)
        tab_panel.add_widget(records_tab)

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

        # 刷新各个页面的显示
        self.records_page.refresh_records(records)

        # 更新搜索页面的记录显示
        self.search_page.refresh_search_records(self.search_page.current_records)


if __name__ == "__main__":
    # 最终确保编码正确
    sys.stdout.reconfigure(encoding='utf-8')

    AdvancedAccountBookApp().run()
