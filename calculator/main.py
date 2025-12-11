import sys
import os

# 添加项目根目录到Python路径，确保可以导入calculator包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream
from PyQt6.QtGui import QIcon
from calculator.ui.main_window import CalculatorMainWindow
from calculator.data.config_manager import ConfigManager

def apply_theme(app, theme_name, resources_dir):
    """应用主题样式表
    
    Args:
        app: QApplication实例
        theme_name: 主题名称 (light 或 dark)
        resources_dir: 资源文件夹路径
    """
    # 构建样式表文件路径
    styles_dir = os.path.join(resources_dir, 'styles')
    if theme_name == 'dark':
        style_file = os.path.join(styles_dir, 'dark.qss')
    else:
        style_file = os.path.join(styles_dir, 'default.qss')  # 使用default.qss作为浅色主题文件
    
    # 加载样式表
    try:
        if os.path.exists(style_file):
            file = QFile(style_file)
            if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
                stream = QTextStream(file)
                app.setStyleSheet(stream.readAll())
                file.close()
                return True
        return False
    except Exception as e:
        print(f"加载样式表失败: {e}")
        return False

def set_application_icon(app, resources_dir):
    """设置应用程序图标
    
    Args:
        app: QApplication实例
        resources_dir: 资源文件夹路径
    """
    try:
        icon_path = os.path.join(resources_dir, 'icons', 'calculator.svg')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            return True
        return False
    except Exception as e:
        print(f"设置图标失败: {e}")
        return False

def main():
    """主程序入口"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    
    # 获取资源文件夹路径（resources文件夹位于calculator目录内）
    calculator_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(calculator_dir, 'resources')
    
    # 加载配置
    config_manager = ConfigManager()
    
    # 应用主题
    theme = config_manager.get_theme()
    apply_theme(app, theme, resources_dir)
    
    # 设置应用程序图标
    set_application_icon(app, resources_dir)
    
    # 创建主窗口实例
    window = CalculatorMainWindow()
    
    # 应用配置
    font_size = config_manager.get_font_size()
    window_size = config_manager.get_window_size()
    
    # 设置窗口大小
    window.resize(window_size["width"], window_size["height"])
    
    # 显示主窗口
    window.show()
    
    # 定义主题切换处理函数
    def handle_theme_change(theme_name):
        # 保存主题设置
        config_manager.set_theme(theme_name)
        # 重新应用主题
        apply_theme(app, theme_name, resources_dir)
    
    # 设置窗口的主题切换处理函数
    window.set_theme_changed_handler(handle_theme_change)
    
    # 记录窗口关闭事件，保存配置
    original_close_event = window.closeEvent
    
    def save_config_on_close(event):
        # 保存窗口大小
        window_size = window.size()
        config_manager.set_window_size(window_size.width(), window_size.height())
        # 调用原始的closeEvent处理函数
        original_close_event(event)
    
    # 连接关闭信号
    window.closeEvent = save_config_on_close
    
    # 运行应用程序主循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()