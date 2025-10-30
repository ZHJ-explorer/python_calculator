import sys
import os

# 添加项目根目录到Python路径，确保当直接运行此文件时也能正确导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QTabWidget, QLabel, QMessageBox,
    QMenuBar, QMenu, QComboBox, QDialog, QScrollArea, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction
import math
from calculator.core.arithmetic import ArithmeticCalculator
from calculator.core.scientific import ScientificCalculator
from calculator.core.unit_converter import UnitConverter
from calculator.core.base_converter import BaseConverter
from calculator.data.config_manager import ConfigManager

class CalculatorMainWindow(QMainWindow):
    """计算器主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python多功能计算器")
        self.resize(450, 600)
        
        # 初始化计算器实例
        self.arithmetic_calc = ArithmeticCalculator()
        self.scientific_calc = ScientificCalculator()
        self.unit_converter = UnitConverter()
        self.base_converter = BaseConverter()
        
        # 计算器状态
        self.clear_flag = False  # 是否需要清除显示
        self.current_operation = None  # 当前操作
        self.first_operand = 0  # 第一个操作数
        self.history = []  # 计算历史
        
        # 保存主题切换信号接收者引用
        self.theme_changed_handler = None
        
        # 先加载配置，设置正确的主题状态
        config_manager = ConfigManager()
        theme = config_manager.get_theme()
        # 当前主题模式
        self.is_dark_theme = (theme == "dark")
        
        # 在设置了正确的主题状态后再初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建选项卡控件
        self.tabs = QTabWidget()
        
        # 添加基本计算器选项卡
        self.basic_calc_widget = QWidget()
        self.create_basic_calculator_ui(self.basic_calc_widget)
        self.tabs.addTab(self.basic_calc_widget, "基本计算")
        
        # 添加科学计算器选项卡
        self.scientific_calc_widget = QWidget()
        self.create_scientific_calculator_ui(self.scientific_calc_widget)
        self.tabs.addTab(self.scientific_calc_widget, "科学计算")
        
        # 添加单位换算选项卡
        self.unit_converter_widget = QWidget()
        self.create_unit_converter_ui(self.unit_converter_widget)
        self.tabs.addTab(self.unit_converter_widget, "单位换算")
        
        # 添加进制转换选项卡
        self.base_converter_widget = QWidget()
        self.create_base_converter_ui(self.base_converter_widget)
        self.tabs.addTab(self.base_converter_widget, "进制转换")
        
        main_layout.addWidget(self.tabs)
        
        # 连接标签页切换信号，确保输入框获得焦点时能响应回车键
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        # 在创建完UI后立即应用当前主题样式
        self.update_theme(self.is_dark_theme)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        # 历史记录动作
        history_action = QAction("历史记录", self)
        history_action.triggered.connect(self.show_history)
        file_menu.addAction(history_action)
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设置菜单 - 添加主题切换功能
        settings_menu = menu_bar.addMenu("设置")
        
        # 主题子菜单
        theme_menu = settings_menu.addMenu("主题")
        
        # 浅色主题动作
        light_theme_action = QAction("浅色主题", self)
        light_theme_action.triggered.connect(lambda: self.on_theme_changed("light"))
        theme_menu.addAction(light_theme_action)
        
        # 深色主题动作
        dark_theme_action = QAction("深色主题", self)
        dark_theme_action.triggered.connect(lambda: self.on_theme_changed("dark"))
        theme_menu.addAction(dark_theme_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        # 使用说明动作
        help_action = QAction("使用说明", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
    def set_theme_changed_handler(self, handler):
        """设置主题切换处理函数
        
        Args:
            handler: 主题切换时调用的函数，接收主题名称参数
        """
        self.theme_changed_handler = handler
        
    def create_button(self, text):
        """创建按钮并设置属性
        
        Args:
            text: 按钮文本
            
        Returns:
            创建好的QPushButton对象
        """
        button = QPushButton(text)
        button.setMinimumHeight(50)
        button.clicked.connect(lambda checked, t=text: self.on_basic_button_clicked(t))
        return button
    
    def create_scientific_button(self, text):
        """为科学计算器创建按钮
        
        Args:
            text: 按钮文本
            
        Returns:
            创建好的QPushButton对象
        """
        button = QPushButton(text)
        button.setMinimumHeight(50)
        button.clicked.connect(lambda checked, t=text: self.on_basic_button_clicked(t, self.scientific_display))
        return button
    
    def create_converter_button(self, text, display, converter_type):
        """为换算器创建按钮
        
        Args:
            text: 按钮文本
            display: 显示控件
            converter_type: 换算器类型
            
        Returns:
            创建好的QPushButton对象
        """
        button = QPushButton(text)
        button.setMinimumHeight(50)
        button.clicked.connect(lambda checked, t=text: self.on_basic_button_clicked(t, display, converter_type))
        return button
    
    def on_theme_changed(self, theme_name):
        """处理主题切换事件
        
        Args:
            theme_name: 主题名称 (light 或 dark)
        """
        # 直接调用update_theme方法设置主题
        self.update_theme(is_dark=(theme_name == "dark"))
        
        # 如果有外部处理函数，也调用它
        if self.theme_changed_handler:
            self.theme_changed_handler(theme_name)
    
    def keyPressEvent(self, event):
        """处理键盘按键事件，实现键盘输入支持"""
        key = event.key()
        key_text = event.text()
        current_tab = self.tabs.currentIndex()
        
        # 基本计算器选项卡 (索引为0)
        if current_tab == 0:
            self._handle_basic_calculator_keys(key, key_text, event)
        # 科学计算器选项卡 (索引为1)
        elif current_tab == 1:
            self._handle_scientific_calculator_keys(key, key_text, event)
        # 单位换算和进制转换选项卡使用标准QLineEdit，已有默认键盘支持
        
        # 调用父类方法确保标准按键行为
        super().keyPressEvent(event)
    
    def _handle_basic_calculator_keys(self, key, key_text, event):
        """处理基本计算器的键盘输入"""
        # 数字键 (0-9)
        if key_text.isdigit():
            self.on_basic_button_clicked(key_text, self.display)
        # 小数点
        elif key_text == '.':
            self.on_basic_button_clicked('.', self.display)
        # 运算符
        elif key_text == '*':
            self.on_basic_button_clicked('×', self.display)
        elif key_text == '/':
            self.on_basic_button_clicked('÷', self.display)
        elif key_text in ['+', '-']:
            self.on_basic_button_clicked(key_text, self.display)
        # 括号
        elif key_text == '(':
            self.on_basic_button_clicked('(', self.display)
        elif key_text == ')':
            self.on_basic_button_clicked(')', self.display)
        # 等号 (Enter/Return)
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.on_basic_button_clicked('=', self.display)
        # 清除 (Escape)
        elif key == Qt.Key.Key_Escape:
            self.on_basic_button_clicked('C', self.display)
        # 正负号 (Space + '-')
        elif key == Qt.Key.Key_Minus and key_text == '-':
            self.on_basic_button_clicked('±', self.display)
        # 百分比 (%)
        elif key_text == '%':
            self.on_basic_button_clicked('%', self.display)
    
    def _handle_scientific_calculator_keys(self, key, key_text, event):
        """处理科学计算器的键盘输入"""
        # 数字键 (0-9)
        if key_text.isdigit():
            self.on_basic_button_clicked(key_text, self.scientific_display)
        # 小数点
        elif key_text == '.':
            self.on_basic_button_clicked('.', self.scientific_display)
        # 运算符 - 单独处理，使用科学计算器的显示
        elif key_text == '*':
            self.on_basic_button_clicked('×', self.scientific_display)
        elif key_text == '/':
            self.on_basic_button_clicked('÷', self.scientific_display)
        elif key_text in ['+', '-']:
            self.on_basic_button_clicked(key_text, self.scientific_display)
        # 括号
        elif key_text == '(':
            self.on_basic_button_clicked('(', self.scientific_display)
        elif key_text == ')':
            self.on_basic_button_clicked(')', self.scientific_display)
        # 等号 (Enter/Return)
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.on_basic_button_clicked('=', self.scientific_display)
        # 清除 (Escape)
        elif key == Qt.Key.Key_Escape:
            self.on_basic_button_clicked('C', self.scientific_display)
        # 正负号 (Space + '-')
        elif key == Qt.Key.Key_Minus and key_text == '-':
            self.on_basic_button_clicked('±', self.scientific_display)
        # 百分比 (%)
        elif key_text == '%':
            self.on_basic_button_clicked('%', self.scientific_display)
        
        # 特殊科学函数键 (需要配合Shift或Alt等组合键)
        # 这里实现一些常用科学函数的键盘快捷键
        if key == Qt.Key.Key_S and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            # Shift+S 对应 sin
            self.on_scientific_button_clicked('sin')
        elif key == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            # Shift+C 对应 cos
            self.on_scientific_button_clicked('cos')
        elif key == Qt.Key.Key_T and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            # Shift+T 对应 tan
            self.on_scientific_button_clicked('tan')
        elif key == Qt.Key.Key_P and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            # Shift+P 对应 pi
            self.on_scientific_button_clicked('pi')
        elif key == Qt.Key.Key_E:
            # E 对应 e
            self.on_scientific_button_clicked('e')
        elif key == Qt.Key.Key_X and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            # Ctrl+X 对应 sqrt
            self.on_scientific_button_clicked('sqrt')
    
    def update_theme(self, is_dark=False):
        """更新计算器主题样式"""
        self.is_dark_theme = is_dark
        
        # 更新基本计算器显示区域样式
        if hasattr(self, 'expression_history'):
            self._update_display_styles()
        
        # 更新科学计算器显示区域样式
        if hasattr(self, 'scientific_expression_history'):
            self._update_scientific_display_styles()
        
        # 更新单位换算器和进制转换器界面样式
        # 检查tab_widget是否已经创建
        if hasattr(self, 'tab_widget'):
            current_index = self.tab_widget.currentIndex()
            # 重新创建单位换算器UI（如果当前在该标签页或已初始化过）
            if (current_index == 2 or hasattr(self, 'unit_converter_widget')) and \
               hasattr(self, 'create_unit_converter_ui') and \
               hasattr(self, 'unit_converter_widget'):
                self.create_unit_converter_ui(self.unit_converter_widget)
            # 重新创建进制转换器UI（如果当前在该标签页或已初始化过）
            if (current_index == 3 or hasattr(self, 'base_converter_widget')) and \
               hasattr(self, 'create_base_converter_ui') and \
               hasattr(self, 'base_converter_widget'):
                self.create_base_converter_ui(self.base_converter_widget)
    
    def _update_display_styles(self):
        """更新基本计算器显示区域样式"""
        if self.is_dark_theme:
            # 深色主题样式
            bg_color = "#3a3a3a"
            text_color = "#ffffff"
            text_color_secondary = "#cccccc"
        else:
            # 浅色主题样式
            bg_color = "#ffffff"
            text_color = "#000000"
            text_color_secondary = "#666666"
        
        # 统一使用透明边框
        border_color = "transparent"
        
        # 历史显示区域 - 透明边框
        self.expression_history.setStyleSheet(
            f"font-size: 16px; color: {text_color_secondary}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid {border_color};"
        )
        
        # 表达式输入区域 - 透明边框
        self.display.setStyleSheet(
            f"font-size: 24px; color: {text_color}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid {border_color};"
        )
        
        # 预计算结果显示区域 - 透明边框
        self.pre_result_display.setStyleSheet(
            f"font-size: 18px; color: {text_color_secondary}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid {border_color};"
        )
    
    def _update_scientific_display_styles(self):
        """更新科学计算器显示区域样式"""
        if self.is_dark_theme:
            # 深色主题样式
            bg_color = "#3a3a3a"  # 中性灰色背景
            text_color = "#ffffff"
            text_color_secondary = "#cccccc"
        else:
            # 浅色主题样式
            bg_color = "#ffffff"
            text_color = "#000000"
            text_color_secondary = "#666666"
        
        # 统一使用透明边框
        border_color = "transparent"
        
        # 科学计算器显示区域样式
        self.scientific_expression_history.setStyleSheet(
            f"font-size: 16px; color: {text_color_secondary}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid {border_color};"
        )
        
        self.scientific_display.setStyleSheet(
            f"font-size: 24px; color: {text_color}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid {border_color};"
        )
        
        # 预处理文本框 - 透明边框
        self.scientific_pre_result_display.setStyleSheet(
            f"font-size: 18px; color: {text_color_secondary}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid {border_color};"
        )
    
    def create_basic_calculator_ui(self, parent_widget):
        """创建基本计算器界面"""
        layout = QVBoxLayout(parent_widget)
        
        # 创建表达式历史显示区域（用于显示上移淡化的表达式）
        self.expression_history = QLineEdit("")
        self.expression_history.setReadOnly(True)
        self.expression_history.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 创建表达式输入区域
        self.display = QLineEdit("")
        self.display.setReadOnly(False)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        # 添加回车键提交计算功能
        self.display.returnPressed.connect(self._handle_enter_key)
        # 添加文本变化监听，确保乘除号正确显示
        self.display.textChanged.connect(lambda text: self._handle_display_text_change(text, self.display))
        
        # 创建预计算结果显示区域（淡化小字号）
        self.pre_result_display = QLineEdit("")
        self.pre_result_display.setReadOnly(True)
        self.pre_result_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 添加控件到布局
        layout.addWidget(self.expression_history)
        layout.addWidget(self.display)
        layout.addWidget(self.pre_result_display)
        
        # 设置初始样式
        self._update_display_styles()
        
        # 立即应用深色主题样式（如果当前是深色主题）
        if self.is_dark_theme:
            bg_color = "#3a3a3a"
            text_color = "#ffffff"
            text_color_secondary = "#cccccc"
            
            # 直接设置各个文本框的样式，统一使用透明边框
            self.expression_history.setStyleSheet(
                f"font-size: 16px; color: {text_color_secondary}; padding: 5px; "
                f"background-color: {bg_color}; border: 1px solid transparent;"
            )
            
            self.display.setStyleSheet(
                f"font-size: 24px; color: {text_color}; padding: 5px; "
                f"background-color: {bg_color}; border: 1px solid transparent;"
            )
            
            # 预处理文本框使用透明边框
            self.pre_result_display.setStyleSheet(
                f"font-size: 18px; color: {text_color_secondary}; padding: 5px; "
                f"background-color: {bg_color}; border: 1px solid transparent;"
            )
        
        # 创建按钮网格布局
        grid_layout = QGridLayout()
        
        # 调整布局间距，移除多余空白
        grid_layout.setSpacing(5)  # 设置按钮间距
        
        # 创建按钮并手动添加，确保正确布局
        # 第一行 - 添加括号按钮
        grid_layout.addWidget(self.create_button('C'), 0, 0)
        grid_layout.addWidget(self.create_button('±'), 0, 1)
        grid_layout.addWidget(self.create_button('%'), 0, 2)
        grid_layout.addWidget(self.create_button('÷'), 0, 3)
        
        # 第二行
        grid_layout.addWidget(self.create_button('7'), 1, 0)
        grid_layout.addWidget(self.create_button('8'), 1, 1)
        grid_layout.addWidget(self.create_button('9'), 1, 2)
        grid_layout.addWidget(self.create_button('×'), 1, 3)
        
        # 第三行
        grid_layout.addWidget(self.create_button('4'), 2, 0)
        grid_layout.addWidget(self.create_button('5'), 2, 1)
        grid_layout.addWidget(self.create_button('6'), 2, 2)
        grid_layout.addWidget(self.create_button('-'), 2, 3)
        
        # 第四行 - 基本计算器布局调整，添加括号按钮
        grid_layout.addWidget(self.create_button('1'), 3, 0)
        grid_layout.addWidget(self.create_button('2'), 3, 1)
        grid_layout.addWidget(self.create_button('3'), 3, 2)
        grid_layout.addWidget(self.create_button('+'), 3, 3)
        
        # 新增一行用于括号按钮
        grid_layout.addWidget(self.create_button('('), 4, 0)
        grid_layout.addWidget(self.create_button('0'), 4, 1)
        grid_layout.addWidget(self.create_button(')'), 4, 2)
        grid_layout.addWidget(self.create_button('='), 4, 3)
        
        # 新增第六行用于小数点
        grid_layout.addWidget(self.create_button('.'), 5, 0, 1, 4)  # 小数点按钮占据整行
        
        layout.addLayout(grid_layout)
    
    def create_scientific_calculator_ui(self, parent_widget):
        """创建科学计算器界面"""
        layout = QVBoxLayout(parent_widget)
        
        # 创建表达式历史显示区域（用于显示上移淡化的表达式）
        self.scientific_expression_history = QLineEdit("")
        self.scientific_expression_history.setReadOnly(True)
        self.scientific_expression_history.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 创建表达式输入区域
        self.scientific_display = QLineEdit("")
        self.scientific_display.setReadOnly(False)
        self.scientific_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        # 添加回车键提交计算功能
        self.scientific_display.returnPressed.connect(self._handle_enter_key)
        # 添加文本变化监听，确保乘除号正确显示
        self.scientific_display.textChanged.connect(lambda text: self._handle_display_text_change(text, self.scientific_display))
        
        # 创建预计算结果显示区域（淡化小字号）
        self.scientific_pre_result_display = QLineEdit("")
        self.scientific_pre_result_display.setReadOnly(True)
        self.scientific_pre_result_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # 添加控件到布局
        layout.addWidget(self.scientific_expression_history)
        layout.addWidget(self.scientific_display)
        layout.addWidget(self.scientific_pre_result_display)
        
        # 设置初始样式
        self._update_scientific_display_styles()
        
        # 立即应用深色主题样式（如果当前是深色主题）
        if self.is_dark_theme:
            bg_color = "#3a3a3a"
            text_color = "#ffffff"
            text_color_secondary = "#cccccc"
            
            # 直接设置各个文本框的样式，统一使用透明边框
            self.scientific_expression_history.setStyleSheet(
                f"font-size: 16px; color: {text_color_secondary}; padding: 5px; "
                f"background-color: {bg_color}; border: 1px solid transparent;"
            )
            
            self.scientific_display.setStyleSheet(
                f"font-size: 24px; color: {text_color}; padding: 5px; "
                f"background-color: {bg_color}; border: 1px solid transparent;"
            )
            
            # 预处理文本框使用透明边框
            self.scientific_pre_result_display.setStyleSheet(
                f"font-size: 18px; color: {text_color_secondary}; padding: 5px; "
                f"background-color: {bg_color}; border: 1px solid transparent;"
            )
        
        # 创建科学函数按钮区域
        scientific_buttons_layout = QGridLayout()
        
        # 科学函数按钮
        scientific_buttons = [
            ['sin', 'cos', 'tan', 'asin'],
            ['acos', 'atan', 'ln', 'log'],
            ['^2', '^3', 'sqrt', 'cbrt'],
            ['exp', 'pi', 'e', '!']
        ]
        
        # 创建科学函数按钮
        for row, button_row in enumerate(scientific_buttons):
            for col, button_text in enumerate(button_row):
                button = QPushButton(button_text)
                button.setMinimumHeight(40)
                button.setStyleSheet("font-size: 16px;")
                button.clicked.connect(lambda checked, text=button_text: self.on_scientific_button_clicked(text))
                scientific_buttons_layout.addWidget(button, row, col)
        
        layout.addLayout(scientific_buttons_layout)
        
        # 创建基本数字按钮区域
        digit_buttons_layout = QGridLayout()
        
        # 调整布局间距，移除多余空白
        digit_buttons_layout.setSpacing(5)  # 设置按钮间距
        
        # 创建按钮并手动添加，确保正确布局
        # 第一行 - 添加括号按钮
        digit_buttons_layout.addWidget(self.create_scientific_button('C'), 0, 0)
        digit_buttons_layout.addWidget(self.create_scientific_button('±'), 0, 1)
        digit_buttons_layout.addWidget(self.create_scientific_button('%'), 0, 2)
        digit_buttons_layout.addWidget(self.create_scientific_button('÷'), 0, 3)
        
        # 第二行
        digit_buttons_layout.addWidget(self.create_scientific_button('7'), 1, 0)
        digit_buttons_layout.addWidget(self.create_scientific_button('8'), 1, 1)
        digit_buttons_layout.addWidget(self.create_scientific_button('9'), 1, 2)
        digit_buttons_layout.addWidget(self.create_scientific_button('×'), 1, 3)
        
        # 第三行
        digit_buttons_layout.addWidget(self.create_scientific_button('4'), 2, 0)
        digit_buttons_layout.addWidget(self.create_scientific_button('5'), 2, 1)
        digit_buttons_layout.addWidget(self.create_scientific_button('6'), 2, 2)
        digit_buttons_layout.addWidget(self.create_scientific_button('-'), 2, 3)
        
        # 第四行 - 添加括号按钮
        digit_buttons_layout.addWidget(self.create_scientific_button('1'), 3, 0)
        digit_buttons_layout.addWidget(self.create_scientific_button('2'), 3, 1)
        digit_buttons_layout.addWidget(self.create_scientific_button('3'), 3, 2)
        digit_buttons_layout.addWidget(self.create_scientific_button('+'), 3, 3)
        
        # 新增一行用于括号按钮
        digit_buttons_layout.addWidget(self.create_scientific_button('('), 4, 0)
        digit_buttons_layout.addWidget(self.create_scientific_button('0'), 4, 1)
        digit_buttons_layout.addWidget(self.create_scientific_button(')'), 4, 2)
        digit_buttons_layout.addWidget(self.create_scientific_button('='), 4, 3)
        
        # 新增第六行用于小数点
        digit_buttons_layout.addWidget(self.create_scientific_button('.'), 5, 0, 1, 4)  # 小数点按钮占据整行
        
        layout.addLayout(digit_buttons_layout)
    
    def create_unit_converter_ui(self, parent_widget):
        """创建单位换算器界面，使用Fluent Design风格并支持深浅色主题"""
        layout = QVBoxLayout(parent_widget)
        
        # 设置布局间距，确保紧凑合理
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 根据当前主题设置颜色方案
        if self.is_dark_theme:
            # 深色主题颜色
            bg_color = "#2d2d2d"
            card_bg = "#3a3a3a"
            text_primary = "#ffffff"
            text_secondary = "#b0b0b0"
            border_color = "#4a4a4a"
            accent_color = "#0078d4"
            accent_hover = "#106ebe"
            input_bg = "#333333"
            disabled_bg = "#303030"
        else:
            # 浅色主题颜色
            bg_color = "#f3f3f3"
            card_bg = "#ffffff"
            text_primary = "#1a1a1a"
            text_secondary = "#666666"
            border_color = "#e0e0e0"
            accent_color = "#0078d7"
            accent_hover = "#106ebe"
            input_bg = "#ffffff"
            disabled_bg = "#f3f3f3"
        
        # 容器背景设置
        parent_widget.setStyleSheet(f"background-color: {bg_color};")
        
        # 单位类型选择
        type_layout = QHBoxLayout()
        type_layout.setSpacing(12)
        type_label = QLabel("单位类型")
        type_label.setStyleSheet(f"color: {text_primary}; font-size: 14px; font-weight: 500;")
        
        self.unit_type_combo = QComboBox()
        self.unit_type_combo.addItems(["长度", "重量", "体积", "温度"])
        self.unit_type_combo.setMinimumHeight(36)
        self.unit_type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {card_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: url(:/icons/down_arrow.png);
                width: 16px;
                height: 16px;
            }}
        """)
        self.unit_type_combo.currentTextChanged.connect(self.on_unit_type_changed)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.unit_type_combo, 1)  # 1表示伸展系数
        layout.addLayout(type_layout)
        
        # 源单位和目标单位选择
        units_layout = QHBoxLayout()
        units_layout.setSpacing(12)
        
        # 源单位 - 移除"从:"标签
        self.from_unit_combo = QComboBox()
        self.from_unit_combo.setMinimumHeight(36)
        self.from_unit_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {card_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
            }}
        """)
        
        # 转换按钮
        convert_button = QPushButton("转换")
        convert_button.setMinimumHeight(36)
        convert_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
        """)
        convert_button.clicked.connect(self.convert_units)
        
        # 目标单位 - 移除"到:"标签
        self.to_unit_combo = QComboBox()
        self.to_unit_combo.setMinimumHeight(36)
        self.to_unit_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {card_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
            }}
        """)
        
        units_layout.addWidget(self.from_unit_combo, 1)  # 1表示伸展系数
        units_layout.addWidget(convert_button)
        units_layout.addWidget(self.to_unit_combo, 1)  # 1表示伸展系数
        layout.addLayout(units_layout)
        
        # 输入和输出 - 使用统一长度规格
        value_layout = QVBoxLayout()
        value_layout.setSpacing(12)
        
        # 输入值 - 修改为"待转换"
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        input_label = QLabel("待转换")
        input_label.setStyleSheet(f"color: {text_primary}; font-size: 14px; font-weight: 500;")
        
        self.input_value = QLineEdit()
        self.input_value.setMinimumHeight(40)
        self.input_value.setStyleSheet(f"""
            QLineEdit {{
                background-color: {input_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {accent_color};
                outline: none;
            }}
        """)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_value, 1)  # 1表示伸展系数
        
        # 输出值 - 保持"结果"提示词
        output_layout = QHBoxLayout()
        output_layout.setSpacing(12)
        output_label = QLabel("结果")
        output_label.setStyleSheet(f"color: {text_primary}; font-size: 14px; font-weight: 500;")
        
        self.output_value = QLineEdit()
        self.output_value.setReadOnly(True)
        self.output_value.setMinimumHeight(40)
        self.output_value.setStyleSheet(f"""
            QLineEdit {{
                background-color: {disabled_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 16px;
            }}
        """)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_value, 1)  # 1表示伸展系数
        
        value_layout.addLayout(input_layout)
        value_layout.addLayout(output_layout)
        layout.addLayout(value_layout)
        
        # 添加额外的底部间距
        layout.addItem(QSpacerItem(0, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # 初始加载长度单位
        self.on_unit_type_changed("长度")
    
    def create_base_converter_ui(self, parent_widget):
        """创建进制转换器界面，使用Fluent Design风格并支持深浅色主题"""
        layout = QVBoxLayout(parent_widget)
        
        # 设置布局间距，确保紧凑合理
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 根据当前主题设置颜色方案
        if self.is_dark_theme:
            # 深色主题颜色
            bg_color = "#2d2d2d"
            card_bg = "#3a3a3a"
            text_primary = "#ffffff"
            text_secondary = "#b0b0b0"
            border_color = "#4a4a4a"
            accent_color = "#0078d4"
            accent_hover = "#106ebe"
            input_bg = "#333333"
            disabled_bg = "#303030"
        else:
            # 浅色主题颜色
            bg_color = "#f3f3f3"
            card_bg = "#ffffff"
            text_primary = "#1a1a1a"
            text_secondary = "#666666"
            border_color = "#e0e0e0"
            accent_color = "#0078d7"
            accent_hover = "#106ebe"
            input_bg = "#ffffff"
            disabled_bg = "#f3f3f3"
        
        # 容器背景设置
        parent_widget.setStyleSheet(f"background-color: {bg_color};")
        
        # 源进制和目标进制选择 - 移除"从:"和"到:"标签
        base_layout = QHBoxLayout()
        base_layout.setSpacing(12)
        
        # 源进制
        self.from_base_combo = QComboBox()
        self.from_base_combo.addItems(["二进制 (2)", "八进制 (8)", "十进制 (10)", "十六进制 (16)"])
        self.from_base_combo.setMinimumHeight(36)
        self.from_base_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {card_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
            }}
        """)
        
        # 转换按钮
        convert_button = QPushButton("转换")
        convert_button.setMinimumHeight(36)
        convert_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
        """)
        convert_button.clicked.connect(self.convert_base)
        
        # 目标进制
        self.to_base_combo = QComboBox()
        self.to_base_combo.addItems(["二进制 (2)", "八进制 (8)", "十进制 (10)", "十六进制 (16)"])
        self.to_base_combo.setMinimumHeight(36)
        self.to_base_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {card_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
            }}
        """)
        
        base_layout.addWidget(self.from_base_combo, 1)  # 1表示伸展系数
        base_layout.addWidget(convert_button)
        base_layout.addWidget(self.to_base_combo, 1)  # 1表示伸展系数
        layout.addLayout(base_layout)
        
        # 输入和输出 - 使用统一长度规格
        number_layout = QVBoxLayout()
        number_layout.setSpacing(12)
        
        # 输入值 - 修改为"待转换"
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        input_label = QLabel("待转换")
        input_label.setStyleSheet(f"color: {text_primary}; font-size: 14px; font-weight: 500;")
        
        self.input_number = QLineEdit()
        self.input_number.setMinimumHeight(40)
        self.input_number.setStyleSheet(f"""
            QLineEdit {{
                background-color: {input_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {accent_color};
                outline: none;
            }}
        """)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_number, 1)  # 1表示伸展系数
        
        # 输出值 - 保持"结果"提示词
        output_layout = QHBoxLayout()
        output_layout.setSpacing(12)
        output_label = QLabel("结果")
        output_label.setStyleSheet(f"color: {text_primary}; font-size: 14px; font-weight: 500;")
        
        self.output_number = QLineEdit()
        self.output_number.setReadOnly(True)
        self.output_number.setMinimumHeight(40)
        self.output_number.setStyleSheet(f"""
            QLineEdit {{
                background-color: {disabled_bg};
                color: {text_primary};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 16px;
            }}
        """)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_number, 1)  # 1表示伸展系数
        
        number_layout.addLayout(input_layout)
        number_layout.addLayout(output_layout)
        layout.addLayout(number_layout)
        
        # 添加额外的底部间距
        layout.addItem(QSpacerItem(0, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
    
    def _on_tab_changed(self, index):
        """标签页切换时的处理"""
        # 确保当前活动标签页的输入框获得焦点
        if index == 0:  # 基本计算
            self.display.setFocus()
        elif index == 1:  # 科学计算
            self.scientific_display.setFocus()
    
    def _handle_enter_key(self):
        """处理回车键提交计算"""
        # 判断当前是哪个标签页，选择对应的输入框
        if self.tabs.currentIndex() == 0:  # 基本计算
            # 模拟点击等号按钮
            self.on_basic_button_clicked('=', self.display)
        elif self.tabs.currentIndex() == 1:  # 科学计算
            # 模拟点击等号按钮
            self.on_basic_button_clicked('=', self.scientific_display)
            
    def _handle_display_text_change(self, text, display):
        """处理输入框文本变化，确保乘除号正确显示，并显示预计算结果"""
        # 检查是否需要替换乘除号
        if '*' in text or '/' in text:
            # 暂时断开信号连接，避免递归调用
            display.blockSignals(True)
            # 替换乘除号
            new_text = text.replace('*', '×').replace('/', '÷')
            # 保存当前光标位置
            cursor_position = display.cursorPosition()
            # 更新文本
            display.setText(new_text)
            # 恢复光标位置
            display.setCursorPosition(cursor_position)
            # 重新连接信号
            display.blockSignals(False)
            text = new_text
        
        # 确保文本立即可见
        display.repaint()
        
        # 显示预计算结果
        self._update_pre_result(text, display)
    
    def _update_pre_result(self, text, display):
        """更新预计算结果显示"""
        # 确定要使用的预结果显示控件
        if display == self.display:
            pre_result_display = self.pre_result_display
        else:
            pre_result_display = self.scientific_pre_result_display
        
        # 只有在表达式看起来完整时才计算（包含运算符和数字）
        if not text or len(text) < 3:
            pre_result_display.setText("")
            return
        
        # 检查是否包含基本运算符
        if not any(op in text for op in ['+', '-', '×', '÷']):
            pre_result_display.setText("")
            return
        
        try:
            # 自动补全未闭合的括号
            expression = text
            open_brackets = expression.count('(')
            close_brackets = expression.count(')')
            if open_brackets > close_brackets:
                expression += ')' * (open_brackets - close_brackets)
            
            # 预处理表达式，替换×为*，÷为/
            processed_expression = expression.replace('×', '*').replace('÷', '/')
            
            # 处理隐式乘法
            processed_expression = re.sub(r'([0-9\)])\s*\(', r'\1*(', processed_expression)
            processed_expression = re.sub(r'\)\s*([0-9])', r')*\1', processed_expression)
            
            # 尝试计算预结果
            result = self.arithmetic_calc.evaluate_expression(processed_expression)
            
            # 格式化结果
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            # 保存新的结果文本
            new_text = str(result)
            
            # 直接更新文本，确保显示正常
            pre_result_display.setText(new_text)
            # 根据当前主题设置适当的样式
            if self.is_dark_theme:
                # 深色主题样式
                bg_color = "#3a3a3a"
                text_color = "#cccccc"
            else:
                # 浅色主题样式
                bg_color = "#ffffff"
                text_color = "#666666"
            
            # 统一使用透明边框
            border_color = "transparent"
            
            # 确保文本可见的样式
            pre_result_display.setStyleSheet(
                f"font-size: 18px; color: {text_color}; padding: 5px; "
                f"background-color: {bg_color}; border: 1px solid {border_color};"
            )
        except:
            # 如果计算失败，直接清空
            pre_result_display.setText("")
    
    def _animate_widget(self, widget, duration, target_alpha, on_finished=None):
        """通用的控件设置函数 - 简化版以确保显示正常"""
        # 直接设置样式，确保文本始终可见
        import re
        current_style = widget.styleSheet()
        font_size_match = re.search(r'font-size:\s*(\d+)px', current_style)
        font_size = font_size_match.group(1) if font_size_match else '16'
        
        # 根据控件类型和当前主题设置适当的样式，统一使用透明边框
        if 'pre_result' in str(widget) or ('pre_result' in widget.__class__.__name__):
            if self.is_dark_theme:
                widget.setStyleSheet(f"font-size: {font_size}px; color: #cccccc; padding: 5px; background-color: #3a3a3a; border: 1px solid transparent;")
            else:
                widget.setStyleSheet(f"font-size: {font_size}px; color: #666666; padding: 5px; background-color: #ffffff; border: 1px solid transparent;")
        else:
            if self.is_dark_theme:
                widget.setStyleSheet(f"font-size: {font_size}px; color: #ffffff; padding: 5px; background-color: #3a3a3a; border: 1px solid transparent;")
            else:
                widget.setStyleSheet(f"font-size: {font_size}px; color: #000000; padding: 5px; background-color: #ffffff; border: 1px solid transparent;")
        
        # 如果有回调，直接调用
        if on_finished:
            on_finished()
    
    def _animate_font_size(self, widget, duration, target_size, on_finished=None):
        """字体大小设置函数 - 简化版以确保显示正常"""
        import re
        current_style = widget.styleSheet()
        
        # 直接设置新的字体大小
        new_style = re.sub(
            r'font-size:\s*(\d+)px',
            f'font-size: {target_size}px',
            current_style
        )
        widget.setStyleSheet(new_style)
        
        # 如果有回调，直接调用
        if on_finished:
            on_finished()
    
    def _move_expression_to_history(self, expression, result, display):
        """将表达式移到历史显示区域，结果显示在当前区域"""
        # 确定要使用的历史显示控件
        if display == self.display:
            history_display = self.expression_history
            pre_result_display = self.pre_result_display
        else:
            history_display = self.scientific_expression_history
            pre_result_display = self.scientific_pre_result_display
        
        # 清空预结果显示
        pre_result_display.setText("")
        
        # 直接更新历史区域文本 - 确保数学表达式在左侧，计算结果在右侧
        # 确保表达式和结果值不同时才显示等号格式
        if str(expression) != str(result):
            history_display.setText(f"{expression} = {result}")
        else:
            # 如果表达式和结果相同，只显示值而不是重复显示
            history_display.setText(str(result))
        
        # 直接显示计算结果
        display.setText(str(result))
        
        # 先获取当前主题设置，然后更新样式
        if self.is_dark_theme:
            # 深色主题样式
            bg_color = "#3a3a3a"
            text_color = "#ffffff"
            text_color_secondary = "#cccccc"
        else:
            # 浅色主题样式
            bg_color = "#ffffff"
            text_color = "#000000"
            text_color_secondary = "#666666"
        
        # 直接设置历史区域样式，确保使用当前主题的背景色
        history_display.setStyleSheet(
            f"font-size: 16px; color: {text_color_secondary}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid transparent;"
        )
        
        # 直接设置显示区域样式，确保使用当前主题的背景色
        display.setStyleSheet(
            f"font-size: 24px; color: {text_color}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid transparent;"
        )
        
        # 直接设置预结果显示区域样式，使用透明边框
        pre_result_display.setStyleSheet(
            f"font-size: 18px; color: {text_color_secondary}; padding: 5px; "
            f"background-color: {bg_color}; border: 1px solid transparent;"
        )
        
        # 强制重绘以确保文本立即可见
        display.repaint()
        history_display.repaint()
        pre_result_display.repaint()
    
    def on_basic_button_clicked(self, button_text, display=None, converter_type=None):
        """处理基本计算器按钮点击事件"""
        if display is None:
            display = self.display
        
        if button_text.isdigit() or button_text == '.':
            # 处理数字和小数点输入
            # 确保即使是首次输入也能正确显示
            current_text = display.text()
            
            if self.clear_flag or current_text == "0":
                display.clear()
                self.clear_flag = False
            
            if button_text == '.' and '.' in display.text():
                return  # 避免多个小数点
            
            # 直接设置新文本，确保实时显示
            new_text = display.text() + button_text
            display.setText(new_text)
            # 强制重绘以确保文本立即可见
            display.repaint()
        elif button_text in ['(', ')']:
            # 处理括号输入 - 不清除输入框，始终追加
            current_text = display.text()
            if (current_text == "0" or not current_text) and button_text == '(':
                # 如果是空或0且输入左括号，替换为左括号
                display.setText('(')
            else:
                # 否则直接追加
                display.setText(current_text + button_text)
            # 括号输入不设置clear_flag为False，保留当前状态
        
        elif button_text == 'C':
            # 清除 - 设置为空字符串而非0
            display.setText("")
            self.current_operation = None
            self.first_operand = 0
            self.clear_flag = False
        
        elif button_text == '±':
            # 正负号切换
            text = display.text()
            if not text or text == "0":
                # 如果是空或0，直接设置为-0
                display.setText("-0")
            elif text.startswith('-'):
                display.setText(text[1:])
            else:
                display.setText("-" + text)
        
        elif button_text == '%':
            # 百分比
            try:
                text = display.text()
                if not text or text == "0":
                    # 如果是空或0，结果仍是0
                    display.setText("0")
                    self.clear_flag = True
                else:
                    value = float(text) / 100
                    display.setText(str(value))
                    self.clear_flag = True
            except ValueError:
                self.show_error("无效输入")
        
        elif button_text in ['+', '-', '×', '÷']:
            # 运算符
            # 检查是否有未闭合的括号或表达式
            current_text = display.text()
            
            # 如果显示的是空或0，直接替换为运算符
            if not current_text or current_text == "0":
                display.setText(button_text)
            else:
                if '(' in current_text and ')' not in current_text:
                    # 自动补全括号
                    display.setText(current_text + ')')
                display.setText(current_text + button_text)
            
            # 移除设置clear_flag=True，避免输入下一个数字时清空表达式
        
        elif button_text == '=':
            # 等于 - 支持带括号的表达式计算
            try:
                expression = display.text()
                
                # 检测输入框内容是否为纯数值（不包含运算符或括号）
                is_pure_number = True
                for char in expression:
                    if char in ['+', '-', '×', '÷', '(', ')', '*', '/']:
                        is_pure_number = False
                        break
                
                # 如果是纯数值，则不执行计算，避免重复计算导致的历史记录问题
                if is_pure_number:
                    try:
                        # 验证是否为有效数字
                        float(expression)
                        # 直接将数值显示为当前结果，但不添加到历史记录
                        display.setText(expression)
                        return
                    except ValueError:
                        # 如果不是有效数字，继续执行正常计算流程
                        pass
                
                # 自动补全未闭合的括号
                open_brackets = expression.count('(')
                close_brackets = expression.count(')')
                if open_brackets > close_brackets:
                    expression += ')' * (open_brackets - close_brackets)
                
                # 预处理表达式，替换×为*，÷为/，处理隐式乘法
                processed_expression = expression.replace('×', '*').replace('÷', '/')
                
                # 处理隐式乘法，如 2(3+4) 或 (3+4)(5+6)
                processed_expression = re.sub(r'([0-9\)])\s*\(', r'\1*(', processed_expression)
                processed_expression = re.sub(r'\)\s*([0-9])', r')*\1', processed_expression)
                
                # 使用算术计算器的evaluate_expression方法处理带括号的表达式
                result = self.arithmetic_calc.evaluate_expression(processed_expression)
                
                # 格式化结果，去除末尾的.0
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                
                # 将表达式移到历史显示区域，结果显示在当前区域
                self._move_expression_to_history(expression, result, display)
                
                # 添加到历史记录
                history_item = f"{expression} = {result}"
                self.history.append(history_item)
                
                # 不清空标志，允许使用计算结果继续计算
                # self.clear_flag = True  # 移除这行，避免清空表达式
            except ValueError as e:
                self.show_error(str(e))
            except Exception as e:
                self.show_error(f"计算错误: {str(e)}")
    
    def on_scientific_button_clicked(self, button_text):
        """处理科学计算器按钮点击事件"""
        try:
            # 获取当前显示的值
            current_text = self.scientific_display.text()
            
            # 特殊处理π和e按钮
            if button_text in ['pi', 'e']:
                if button_text == 'pi':
                    result = self.scientific_calc.pi()
                else:  # 'e'
                    result = self.scientific_calc.e()
                self.clear_flag = False  # 直接显示值，不清空
                
                # 显示结果
                self.scientific_display.setText(str(result))
            else:
                # 对于其他科学函数，需要先获取数值
                value = float(current_text) if current_text else 0
                result = 0
                
                if button_text == 'sin':
                    result = self.scientific_calc.sin(value)
                elif button_text == 'cos':
                    result = self.scientific_calc.cos(value)
                elif button_text == 'tan':
                    result = self.scientific_calc.tan(value)
                elif button_text == 'asin':
                    result = self.scientific_calc.asin(value)
                elif button_text == 'acos':
                    result = self.scientific_calc.acos(value)
                elif button_text == 'atan':
                    result = self.scientific_calc.atan(value)
                elif button_text == 'ln':
                    result = self.scientific_calc.log(value)
                elif button_text == 'log':
                    result = self.scientific_calc.log10(value)
                elif button_text == '^2':
                    result = self.arithmetic_calc.power(value, 2)
                elif button_text == '^3':
                    result = self.arithmetic_calc.power(value, 3)
                elif button_text == 'sqrt':
                    result = self.arithmetic_calc.square_root(value)
                elif button_text == 'cbrt':
                    result = self.arithmetic_calc.cube_root(value)
                elif button_text == 'exp':
                    result = self.scientific_calc.exp(value)
                elif button_text == '!':
                    result = self.arithmetic_calc.factorial(int(value))
            
            # 格式化结果
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            # 对于科学函数，将表达式移到历史显示（例如 sin(30) = 0.5）
            if button_text not in ['pi', 'e']:
                expression = f"{button_text}({current_text})" if current_text else f"{button_text}"
                self._move_expression_to_history(expression, result, self.scientific_display)
                
                # 添加到历史记录
                history_item = f"{expression} = {result}"
                self.history.append(history_item)
            
            self.clear_flag = True
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error("计算错误")
    
    def on_unit_type_changed(self, unit_type):
        """处理单位类型变更事件"""
        self.from_unit_combo.clear()
        self.to_unit_combo.clear()
        
        if unit_type == "长度":
            units = self.unit_converter.get_available_length_units()
            self.from_unit_combo.addItems(units)
            self.to_unit_combo.addItems(units)
        elif unit_type == "重量":
            units = self.unit_converter.get_available_weight_units()
            self.from_unit_combo.addItems(units)
            self.to_unit_combo.addItems(units)
        elif unit_type == "体积":
            units = self.unit_converter.get_available_volume_units()
            self.from_unit_combo.addItems(units)
            self.to_unit_combo.addItems(units)
        elif unit_type == "温度":
            units = self.unit_converter.get_available_temperature_units()
            self.from_unit_combo.addItems(units)
            self.to_unit_combo.addItems(units)
    
    def convert_units(self):
        """执行单位换算"""
        try:
            value = float(self.input_value.text())
            from_unit = self.from_unit_combo.currentText()
            to_unit = self.to_unit_combo.currentText()
            unit_type = self.unit_type_combo.currentText()
            
            result = 0
            if unit_type == "长度":
                result = self.unit_converter.convert_length(value, from_unit, to_unit)
            elif unit_type == "重量":
                result = self.unit_converter.convert_weight(value, from_unit, to_unit)
            elif unit_type == "体积":
                result = self.unit_converter.convert_volume(value, from_unit, to_unit)
            elif unit_type == "温度":
                result = self.unit_converter.convert_temperature(value, from_unit, to_unit)
            
            # 格式化结果
            if abs(result) < 1e-10:
                result = 0
            elif abs(result - int(result)) < 1e-10:
                result = int(result)
            
            self.output_value.setText(str(result))
        except ValueError:
            self.show_error("无效的输入值")
        except Exception as e:
            self.show_error(str(e))
    
    def convert_base(self):
        """执行进制转换"""
        try:
            number_str = self.input_number.text()
            from_base_text = self.from_base_combo.currentText()
            to_base_text = self.to_base_combo.currentText()
            
            # 提取进制数字
            from_base = int(from_base_text.split('(')[1].split(')')[0])
            to_base = int(to_base_text.split('(')[1].split(')')[0])
            
            result = self.base_converter.convert(number_str, from_base, to_base)
            self.output_number.setText(result)
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error("转换错误")
    
    def show_history(self):
        """显示计算历史（Fluent Design风格）"""
        # 根据当前主题设置颜色方案
        if self.is_dark_theme:
            # 深色主题颜色
            dialog_bg = "#2d2d2d"
            card_bg = "#3a3a3a"
            card_hover_bg = "#424242"
            text_primary = "#ffffff"
            text_secondary = "#b0b0b0"
            accent_color = "#0078d4"
            accent_hover = "#106ebe"
            accent_pressed = "#005a9e"
            danger_color = "#f15252"
            danger_hover = "#e03e3e"
        else:
            # 浅色主题颜色
            dialog_bg = "#ffffff"
            card_bg = "#f3f3f3"
            card_hover_bg = "#ebebeb"
            text_primary = "#1a1a1a"
            text_secondary = "#666666"
            accent_color = "#0078d7"
            accent_hover = "#106ebe"
            accent_pressed = "#005a9e"
            danger_color = "#d13438"
            danger_hover = "#a8071a"
        
        if not self.history:
            # 使用Fluent Design风格的无历史记录提示窗口
            no_history_dialog = QDialog(self)
            no_history_dialog.setWindowTitle("历史记录")
            no_history_dialog.setMinimumWidth(360)
            no_history_dialog.setMinimumHeight(220)
            
            # 设置Fluent Design风格
            no_history_dialog.setStyleSheet(f"""
                QDialog {{ 
                    background-color: {dialog_bg}; 
                    border-radius: 8px;
                    border: 1px solid {card_hover_bg};
                }}
            """)
            
            # 创建主布局
            main_layout = QVBoxLayout(no_history_dialog)
            main_layout.setSpacing(24)
            main_layout.setContentsMargins(24, 24, 24, 24)
            
            # 添加图标
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 使用简单的文本图标作为替代
            icon_label.setText("📋")
            icon_label.setFixedHeight(48)
            main_layout.addWidget(icon_label)
            
            # 添加标题标签
            title_label = QLabel("暂无计算历史")
            title_label.setStyleSheet(f"""
                QLabel {{ 
                    color: {text_primary}; 
                    font-size: 18px; 
                    font-weight: 500;
                }}
            """)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title_label)
            
            # 添加说明文本
            hint_label = QLabel("进行计算后，历史记录将显示在这里")
            hint_label.setStyleSheet(f"""
                QLabel {{ 
                    color: {text_secondary}; 
                    font-size: 14px;
                }}
            """)
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(hint_label)
            
            # 添加关闭按钮
            close_button = QPushButton("关闭")
            close_button.setFixedHeight(36)
            close_button.setStyleSheet(f"""
                QPushButton {{ 
                    background-color: {accent_color}; 
                    color: white; 
                    border: none; 
                    border-radius: 4px; 
                    font-size: 14px; 
                    font-weight: 500;
                    padding: 0 16px;
                }}
                QPushButton:hover {{ 
                    background-color: {accent_hover}; 
                }}
                QPushButton:pressed {{ 
                    background-color: {accent_pressed}; 
                }}
            """)
            close_button.clicked.connect(no_history_dialog.accept)
            
            # 创建按钮布局
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            button_layout.addStretch()
            main_layout.addLayout(button_layout)
            
            # 显示对话框
            no_history_dialog.exec()
            return
        
        # 创建历史记录对话框
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("历史记录")
        history_dialog.setMinimumSize(480, 640)
        history_dialog.setStyleSheet(f"QDialog {{ background-color: {dialog_bg}; color: {text_primary}; border-radius: 8px; border: 1px solid {card_hover_bg}; }}")
        
        # 创建主布局
        main_layout = QVBoxLayout(history_dialog)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 创建标题标签
        title_label = QLabel("今天")
        title_label.setStyleSheet(f"color: {text_secondary}; font-size: 14px; font-weight: 500; margin-bottom: 8px;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 设置滚动条样式
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ background-color: transparent; border: none; }}
            QScrollBar:vertical {{ 
                background-color: transparent;
                width: 8px;
                margin: 0 0 0 0;
            }}
            QScrollBar::handle:vertical {{ 
                background-color: {text_secondary};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ 
                background-color: {text_primary};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ 
                height: 0px;
                width: 0px;
            }}
        """)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        
        # 创建内容布局
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(4, 4, 4, 4)
        
        # 处理历史记录，创建分块显示
        for record in reversed(self.history):  # 倒序显示，最新的在最上面
            # 分割表达式和结果
            parts = record.split("=")
            if len(parts) == 2:
                expression = parts[0].strip()
                result = parts[1].strip()
                
                # 创建记录块
                record_block = QFrame()
                record_block.setFrameShape(QFrame.Shape.Panel)
                record_block.setStyleSheet(f"""
                    QFrame {{ 
                        background-color: {card_bg}; 
                        border-radius: 8px; 
                        padding: 16px; 
                        border: 1px solid transparent;
                    }}
                    QFrame:hover {{ 
                        background-color: {card_hover_bg}; 
                        border: 1px solid {accent_color};
                    }}
                """)
                
                # 创建记录块布局
                block_layout = QVBoxLayout(record_block)
                block_layout.setContentsMargins(0, 0, 0, 0)
                block_layout.setSpacing(8)
                
                # 添加表达式标签
                expression_label = QLabel(expression)
                expression_label.setStyleSheet(f"color: {text_secondary}; font-size: 14px;")
                expression_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                block_layout.addWidget(expression_label)
                
                # 添加结果标签
                result_label = QLabel(result)
                result_label.setStyleSheet(f"color: {text_primary}; font-size: 18px; font-weight: 600;")
                result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                block_layout.addWidget(result_label)
                
                # 添加复制按钮
                copy_button = QPushButton("复制")
                copy_button.setFixedHeight(28)
                copy_button.setStyleSheet(f"""
                    QPushButton {{ 
                        background-color: transparent; 
                        color: {accent_color}; 
                        border: 1px solid {accent_color}; 
                        border-radius: 4px; 
                        font-size: 12px;
                        padding: 0 8px;
                    }}
                    QPushButton:hover {{ 
                        background-color: {accent_color};
                        color: white;
                    }}
                """)
                copy_button.clicked.connect(lambda checked, r=result: QApplication.clipboard().setText(r))
                
                # 添加按钮布局
                button_layout = QHBoxLayout()
                button_layout.addStretch()
                button_layout.addWidget(copy_button)
                block_layout.addLayout(button_layout)
                
                # 添加记录块到内容布局
                content_layout.addWidget(record_block)
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 添加滚动区域到主布局
        main_layout.addWidget(scroll_area, 1)  # 1表示伸展系数
        
        # 创建底部布局
        bottom_layout = QHBoxLayout()
        
        # 添加历史记录数量
        count_label = QLabel(f"共 {len(self.history)} 条记录")
        count_label.setStyleSheet(f"color: {text_secondary}; font-size: 12px;")
        bottom_layout.addWidget(count_label)
        
        bottom_layout.addStretch()
        
        # 添加清空按钮
        clear_button = QPushButton("清空历史")
        clear_button.setFixedHeight(32)
        clear_button.setStyleSheet(f"""
            QPushButton {{ 
                background-color: transparent; 
                color: {danger_color}; 
                border: 1px solid {danger_color}; 
                border-radius: 4px; 
                padding: 0 12px; 
                font-size: 14px;
            }}
            QPushButton:hover {{ 
                background-color: {danger_color};
                color: white;
            }}
        """)
        clear_button.clicked.connect(lambda: self.clear_history(history_dialog))
        bottom_layout.addWidget(clear_button)
        
        # 添加底部布局到主布局
        main_layout.addLayout(bottom_layout)
        
        # 显示对话框
        history_dialog.exec()
    
    def clear_history(self, dialog):
        """清空历史记录，使用Fluent Design风格的确认对话框"""
        # 根据当前主题设置颜色方案
        if self.is_dark_theme:
            # 深色主题颜色
            dialog_bg = "#2d2d2d"
            card_hover_bg = "#424242"
            text_primary = "#ffffff"
            text_secondary = "#b0b0b0"
            accent_color = "#0078d4"
            accent_hover = "#106ebe"
            accent_pressed = "#005a9e"
            danger_color = "#f15252"
            danger_hover = "#e03e3e"
            neutral_bg = "#3a3a3a"
            neutral_hover = "#4a4a4a"
        else:
            # 浅色主题颜色
            dialog_bg = "#ffffff"
            card_hover_bg = "#ebebeb"
            text_primary = "#1a1a1a"
            text_secondary = "#666666"
            accent_color = "#0078d7"
            accent_hover = "#106ebe"
            accent_pressed = "#005a9e"
            danger_color = "#d13438"
            danger_hover = "#a8071a"
            neutral_bg = "#f3f3f3"
            neutral_hover = "#e6e6e6"
        
        # 创建自定义的Fluent Design风格确认对话框
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle("确认清空")
        confirm_dialog.setMinimumWidth(420)
        confirm_dialog.setMinimumHeight(220)
        
        # 设置Fluent Design风格
        confirm_dialog.setStyleSheet(f"""
            QDialog {{ 
                background-color: {dialog_bg}; 
                border-radius: 8px;
                border: 1px solid {card_hover_bg};
            }}
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(confirm_dialog)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # 添加图标
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText("⚠️")
        icon_label.setFixedHeight(32)
        main_layout.addWidget(icon_label)
        
        # 添加标题和消息
        title_label = QLabel("确认清空历史记录")
        title_label.setStyleSheet(f"""
            QLabel {{ 
                color: {text_primary}; 
                font-size: 18px; 
                font-weight: 500;
                text-align: center;
            }}
        """)
        main_layout.addWidget(title_label)
        
        message_label = QLabel("确定要清空所有历史记录吗？此操作不可恢复。")
        message_label.setStyleSheet(f"""
            QLabel {{ 
                color: {text_secondary}; 
                font-size: 14px;
            }}
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        main_layout.addWidget(message_label)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setFixedHeight(36)
        cancel_button.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {neutral_bg}; 
                color: {text_primary}; 
                border: 1px solid {card_hover_bg}; 
                border-radius: 4px; 
                font-size: 14px;
                min-width: 80px;
                padding: 0 16px;
            }}
            QPushButton:hover {{ 
                background-color: {neutral_hover}; 
            }}
            QPushButton:pressed {{ 
                background-color: {card_hover_bg}; 
            }}
        """)
        cancel_button.clicked.connect(confirm_dialog.reject)
        button_layout.addWidget(cancel_button)
        
        # 确定按钮
        confirm_button = QPushButton("确定")
        confirm_button.setFixedHeight(36)
        confirm_button.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {danger_color}; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                font-size: 14px;
                min-width: 80px;
                padding: 0 16px;
                margin-left: 12px;
            }}
            QPushButton:hover {{ 
                background-color: {danger_hover}; 
            }}
            QPushButton:pressed {{ 
                background-color: {danger_hover}; 
            }}
        """)
        confirm_button.clicked.connect(lambda: self._confirm_clear_history(confirm_dialog, dialog))
        button_layout.addWidget(confirm_button)
        
        main_layout.addLayout(button_layout)
        
        # 显示对话框
        confirm_dialog.exec()
        
    def _confirm_clear_history(self, confirm_dialog, history_dialog):
        """确认清空历史记录后的操作"""
        self.history = []
        confirm_dialog.accept()
        history_dialog.accept()
    
    def show_help(self):
        """显示使用说明，使用Fluent Design风格的对话框，并支持深色/浅色模式"""
        # 根据当前主题设置颜色方案
        if self.is_dark_theme:
            # 深色主题颜色
            dialog_bg = "#2d2d2d"
            card_bg = "#3a3a3a"
            card_hover_bg = "#424242"
            text_primary = "#ffffff"
            text_secondary = "#b0b0b0"
            text_tertiary = "#e0e0e0"
            accent_color = "#0078d4"
            accent_hover = "#106ebe"
            accent_pressed = "#005a9e"
            border_color = "#4a4a4a"
        else:
            # 浅色主题颜色
            dialog_bg = "#ffffff"
            card_bg = "#f3f3f3"
            card_hover_bg = "#ebebeb"
            text_primary = "#1a1a1a"
            text_secondary = "#444444"
            text_tertiary = "#666666"
            accent_color = "#0078d7"
            accent_hover = "#106ebe"
            accent_pressed = "#005a9e"
            border_color = "#e0e0e0"
        
        # 创建自定义的Fluent Design风格帮助对话框
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("使用说明")
        help_dialog.setMinimumSize(640, 720)  # 略微增加尺寸以确保所有内容可见
        
        # 设置Fluent Design风格
        help_dialog.setStyleSheet(f"""
            QDialog {{ 
                background-color: {dialog_bg}; 
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(help_dialog)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)  # 统一间距
        
        # 添加标题标签
        title_label = QLabel("Python多功能计算器使用说明")
        title_label.setStyleSheet(f"""
            QLabel {{ 
                color: {text_primary}; 
                font-size: 20px; 
                font-weight: 600;
                margin-bottom: 8px;
            }}
        """)
        main_layout.addWidget(title_label)
        
        # 添加版本信息
        version_label = QLabel("版本 1.0")
        version_label.setStyleSheet(f"color: {text_secondary}; font-size: 12px;")
        main_layout.addWidget(version_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 设置滚动条样式
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ background-color: transparent; border: none; }}
            QScrollBar:vertical {{ 
                background-color: transparent;
                width: 8px;
                margin: 0 4px 0 0;
            }}
            QScrollBar::handle:vertical {{ 
                background-color: {text_secondary};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ 
                background-color: {text_primary};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ 
                height: 0px;
                width: 0px;
            }}
        """)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        
        # 创建内容布局
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)  # 增加内容块之间的间距
        content_layout.setContentsMargins(4, 4, 4, 4)
        
        # 帮助内容
        help_sections = [
            {
                "title": "1. 基本计算",
                "content": [
                    "- 数字键 (0-9)：输入数字",
                    "- 运算符键 (+, -, *, /)：输入运算符",
                    "- 小数点 (.)：输入小数点",
                    "- Enter/Return键：计算结果",
                    "- Escape键：清除",
                    "- 减号 (-)：切换正负号",
                    "- 百分号 (%)：转换为百分比",
                    "- 鼠标点击：点击相应按钮"
                ]
            },
            {
                "title": "2. 科学计算",
                "content": [
                    "- 基本功能同基本计算器",
                    "- 键盘快捷键：",
                    "  - Shift+S：sin",
                    "  - Shift+C：cos",
                    "  - Shift+T：tan",
                    "  - Shift+P：π (圆周率)",
                    "  - E：e (自然对数底)",
                    "  - Ctrl+X：平方根",
                    "- 科学函数按钮：点击相应按钮使用所有科学函数"
                ]
            },
            {
                "title": "3. 单位换算",
                "content": [
                    "- 选择单位类型",
                    "- 选择源单位和目标单位",
                    "- 输入要转换的值",
                    "- 点击转换按钮"
                ]
            },
            {
                "title": "4. 进制转换",
                "content": [
                    "- 选择源进制和目标进制",
                    "- 输入要转换的数字",
                    "- 点击转换按钮"
                ]
            },
            {
                "title": "键盘输入支持",
                "content": [
                    "在基本计算器和科学计算器选项卡中可以使用相应的键盘快捷键进行操作，提高计算效率。"
                ]
            },
            {
                "title": "主题设置",
                "content": [
                    "- 浅色/深色主题：在设置菜单中可切换主题",
                    "- 所有界面元素都会根据当前主题自动适配"
                ]
            },
            {
                "title": "历史记录",
                "content": [
                    "- 计算结果会自动保存在历史记录中",
                    "- 点击'历史记录'按钮查看所有计算历史",
                    "- 支持复制历史计算结果"
                ]
            }
        ]
        
        # 创建帮助内容块
        for section in help_sections:
            # 章节标题
            section_title = QLabel(section["title"])
            section_title.setStyleSheet(f"""
                QLabel {{ 
                    color: {text_primary}; 
                    font-size: 16px; 
                    font-weight: 500;
                    margin-bottom: 8px;
                }}
            """)
            content_layout.addWidget(section_title)
            
            # 章节内容容器
            content_frame = QFrame()
            content_frame.setStyleSheet(f"""
                QFrame {{ 
                    background-color: {card_bg}; 
                    border-radius: 8px;
                    padding: 16px;
                    border: 1px solid {border_color};
                }}
            """)
            
            content_block_layout = QVBoxLayout(content_frame)
            content_block_layout.setContentsMargins(0, 0, 0, 0)
            content_block_layout.setSpacing(10)  # 增加内容项之间的间距
            
            # 添加内容项
            for item in section["content"]:
                item_label = QLabel(item)
                item_label.setStyleSheet(f"""
                    QLabel {{ 
                        color: {text_secondary}; 
                        font-size: 14px;
                    }}
                """)
                item_label.setWordWrap(True)
                content_block_layout.addWidget(item_label)
            
            content_layout.addWidget(content_frame)
        
        # 添加底部空白，确保滚动到底部时内容完全可见
        content_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 添加滚动区域到主布局
        main_layout.addWidget(scroll_area, 1)  # 1表示伸展系数
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.setFixedHeight(36)
        close_button.setMinimumWidth(80)  # 设置最小宽度，确保按钮不会太小
        close_button.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {accent_color}; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                font-size: 14px;
                font-weight: 500;
                padding: 0 16px;
            }}
            QPushButton:hover {{ 
                background-color: {accent_hover}; 
            }}
            QPushButton:pressed {{ 
                background-color: {accent_pressed}; 
            }}
        """)
        close_button.clicked.connect(help_dialog.accept)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 16, 0, 0)  # 增加顶部边距，确保按钮不会紧贴内容
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 显示对话框
        help_dialog.exec()
    
    def show_error(self, message):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)