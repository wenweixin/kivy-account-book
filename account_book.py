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
import json
import os
import sys
from datetime import datetime
from typing import List, Dict

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


# ==================== 主界面布局（移除错误的input_encoding参数） ====================
class AdvancedAccountBookLayout(BoxLayout):
    def __init__(self,** kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 10
        self.current_records = load_records()

        # ========== 1. 记账输入区域 ==========
        input_layout = GridLayout(cols=2, spacing=8, size_hint_y=0.35)
        input_layout.row_default_height = 40

        # 1.1 时间（自动显示）
        input_layout.add_widget(Label(text="时间：", font_size=18, halign="right"))
        self.time_label = Label(text=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                font_size=18, color=(0.2, 0.5, 0.8, 1))
        input_layout.add_widget(self.time_label)

        # 1.2 支出分类（下拉选择，修复中文显示）
        input_layout.add_widget(Label(text="分类：", font_size=18, halign="right"))
        self.category_spinner = Spinner(
            text=EXPENSE_CATEGORIES[0],
            values=EXPENSE_CATEGORIES,
            font_size=18,
            size_hint_x=1,
            # 强制指定字体渲染中文
            font_name=DEFAULT_FONT
        )
        input_layout.add_widget(self.category_spinner)

        # 1.3 具体备注（可空，支持中文输入）- 移除错误的input_encoding参数
        input_layout.add_widget(Label(text="备注：", font_size=18, halign="right"))
        self.remark_input = TextInput(hint_text="例如：麦当劳/地铁3号线",
                                      font_size=18, size_hint_x=1,
                                      # 仅保留font_name，移除input_encoding
                                      font_name=DEFAULT_FONT)
        input_layout.add_widget(self.remark_input)

        # 1.4 金额（元）
        input_layout.add_widget(Label(text="金额（元）：", font_size=18, halign="right"))
        self.amount_input = TextInput(hint_text="请输入数字",
                                      font_size=18, input_filter="float", size_hint_x=1,
                                      font_name=DEFAULT_FONT)
        input_layout.add_widget(self.amount_input)

        # 1.5 保存按钮
        input_layout.add_widget(Label())
        save_btn = Button(text="保存支出记录", font_size=18,
                          background_color=(0.2, 0.8, 0.2, 1), size_hint_x=1,
                          font_name=DEFAULT_FONT)
        save_btn.bind(on_press=self.save_record_handler)
        input_layout.add_widget(save_btn)

        self.add_widget(input_layout)

        # ========== 2. 时间筛选统计区域 ==========
        filter_layout = GridLayout(cols=4, spacing=5, size_hint_y=0.15)

        filter_layout.add_widget(Label(text="时间筛选：", font_size=16, halign="center"))
        self.filter_spinner = Spinner(
            text=TIME_FILTER_TYPES[0],
            values=TIME_FILTER_TYPES,
            font_size=16,
            size_hint_x=1,
            font_name=DEFAULT_FONT
        )
        filter_layout.add_widget(self.filter_spinner)

        self.filter_input = TextInput(hint_text="例：2024-12-01",
                                      font_size=16, size_hint_x=1,
                                      font_name=DEFAULT_FONT)
        filter_layout.add_widget(self.filter_input)

        filter_btn = Button(text="统计", font_size=16,
                            background_color=(0.2, 0.5, 0.8, 1), size_hint_x=1,
                            font_name=DEFAULT_FONT)
        filter_btn.bind(on_press=self.filter_and_calculate)
        filter_layout.add_widget(filter_btn)

        self.add_widget(filter_layout)

        # ========== 3. 搜索区域 ==========
        search_layout = GridLayout(cols=3, spacing=5, size_hint_y=0.1)

        search_layout.add_widget(Label(text="搜索：", font_size=16, halign="center"))
        self.search_input = TextInput(hint_text="模糊搜索关键词",
                                      font_size=16, size_hint_x=1,
                                      # 移除错误的input_encoding参数
                                      font_name=DEFAULT_FONT)
        search_layout.add_widget(self.search_input)

        search_btn = Button(text="搜索并求和", font_size=16,
                            background_color=(0.8, 0.5, 0.2, 1), size_hint_x=1,
                            font_name=DEFAULT_FONT)
        search_btn.bind(on_press=self.search_and_calculate)
        search_layout.add_widget(search_btn)

        self.add_widget(search_layout)

        # ========== 4. 统计结果展示 ==========
        self.result_label = Label(text="总支出：0.00 元",
                                  font_size=20, color=(0.8, 0.2, 0.2, 1),
                                  size_hint_y=0.08, halign="center",
                                  font_name=DEFAULT_FONT)
        self.add_widget(self.result_label)

        # ========== 5. 记录展示区域 ==========
        self.record_scroll = ScrollView(size_hint_y=0.32)
        self.record_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.record_layout.bind(minimum_height=self.record_layout.setter('height'))
        self.record_scroll.add_widget(self.record_layout)
        self.add_widget(self.record_scroll)

        # 初始化加载记录
        self.refresh_records(self.current_records)

    # ========== 核心功能函数 ==========
    def save_record_handler(self, instance):
        """保存支出记录处理"""
        amount_text = self.amount_input.text.strip()
        if not amount_text or float(amount_text) <= 0:
            self.result_label.text = "错误：金额必须是大于0的数字！"
            self.result_label.color = (1, 0, 0, 1)
            return

        category = self.category_spinner.text
        remark = self.remark_input.text.strip()
        amount = float(amount_text)

        if save_record(category, remark, amount):
            self.remark_input.text = ""
            self.amount_input.text = ""
            self.time_label.text = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.current_records = load_records()
            self.refresh_records(self.current_records)
            self.result_label.text = f"保存成功！累计支出：{calculate_total(self.current_records)} 元"
            self.result_label.color = (0.2, 0.8, 0.2, 1)
        else:
            self.result_label.text = "保存失败！请检查输入"
            self.result_label.color = (1, 0, 0, 1)

    def filter_and_calculate(self, instance):
        """按时间筛选并计算总支出"""
        filter_type = self.filter_spinner.text
        filter_value = self.filter_input.text.strip()

        filtered_records = filter_records_by_time(self.current_records, filter_type, filter_value)
        total = calculate_total(filtered_records)

        self.refresh_records(filtered_records)
        self.result_label.text = f"{filter_type}支出：{total} 元"
        self.result_label.color = (0.2, 0.5, 0.8, 1)

    def search_and_calculate(self, instance):
        """模糊搜索并计算总支出（支持中文关键词）"""
        keyword = self.search_input.text.strip()
        if not keyword:
            self.result_label.text = "错误：请输入搜索关键词！"
            self.result_label.color = (1, 0, 0, 1)
            return

        matched_records = search_records(self.current_records, keyword)
        total = calculate_total(matched_records)

        self.refresh_records(matched_records)
        self.result_label.text = f"搜索「{keyword}」总支出：{total} 元"
        self.result_label.color = (0.8, 0.5, 0.2, 1)

    def refresh_records(self, records: List[Dict]):
        """刷新记录展示区域（确保中文正常显示）"""
        self.record_layout.clear_widgets()

        if not records:
            self.record_layout.add_widget(Label(text="暂无记录", font_size=16, color=(0.5, 0.5, 0.5, 1),
                                                font_name=DEFAULT_FONT))
            return

        for record in reversed(records):
            record_text = (
                f"[{record['time']}] | 分类：{record['category']} | "
                f"备注：{record['remark'] or '无'} | 金额：{record['amount']} 元"
            )
            # 每条记录的标签都指定中文字体
            self.record_layout.add_widget(Label(text=record_text, font_size=15, color=(0.1, 0.1, 0.1, 1),
                                                font_name=DEFAULT_FONT))


# ==================== APP主类 ====================
class AdvancedAccountBookApp(App):
    def build(self):
        self.title = "高级记账本"
        return AdvancedAccountBookLayout()


if __name__ == "__main__":
    # 最终确保编码正确
    sys.stdout.reconfigure(encoding='utf-8')

    AdvancedAccountBookApp().run()
