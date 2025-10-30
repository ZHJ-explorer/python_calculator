import json
import os

class ConfigManager:
    """配置管理器类，负责用户偏好设置的保存和加载"""
    
    def __init__(self, config_file="calculator_config.json"):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        # 获取用户数据目录
        self.config_dir = os.path.join(os.path.expanduser("~"), ".python_calculator")
        self.config_file = os.path.join(self.config_dir, config_file)
        
        # 默认配置
        self.default_config = {
            "theme": "light",  # 主题：light或dark
            "font_size": 14,  # 字体大小
            "remember_history": True,  # 是否记住历史记录
            "max_history_items": 100,  # 最大历史记录数量
            "auto_save": True,  # 是否自动保存
            "recent_tabs": [],  # 最近使用的选项卡
            "window_size": {"width": 450, "height": 600},  # 窗口大小
            "precision": 10,  # 计算精度（小数位数）
            "angle_unit": "radians"  # 角度单位：radians或degrees
        }
        
        # 确保配置目录存在
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # 如果配置文件不存在，创建默认配置文件
        if not os.path.exists(self.config_file):
            self.save_config(self.default_config)
    
    def load_config(self):
        """加载配置
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 合并默认配置，确保所有必要的键都存在
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                
                return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.default_config
    
    def save_config(self, config):
        """保存配置
        
        Args:
            config: 配置字典
        
        Returns:
            是否成功
        """
        try:
            # 合并配置，确保只包含有效的配置项
            merged_config = {}
            for key, default_value in self.default_config.items():
                if key in config:
                    # 验证配置值的类型
                    if isinstance(config[key], type(default_value)) or (isinstance(default_value, int) and isinstance(config[key], float)):
                        merged_config[key] = config[key]
                    else:
                        print(f"配置项 {key} 类型错误，使用默认值")
                        merged_config[key] = default_value
                else:
                    merged_config[key] = default_value
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(merged_config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_config_value(self, key, default=None):
        """获取单个配置值
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        config = self.load_config()
        return config.get(key, default if default is not None else self.default_config.get(key))
    
    def set_config_value(self, key, value):
        """设置单个配置值
        
        Args:
            key: 配置键
            value: 配置值
        
        Returns:
            是否成功
        """
        config = self.load_config()
        config[key] = value
        return self.save_config(config)
    
    def reset_config(self):
        """重置配置为默认值
        
        Returns:
            是否成功
        """
        return self.save_config(self.default_config)
    
    def get_theme(self):
        """获取当前主题
        
        Returns:
            主题名称
        """
        return self.get_config_value("theme")
    
    def set_theme(self, theme):
        """设置主题
        
        Args:
            theme: 主题名称 (light 或 dark)
        
        Returns:
            是否成功
        """
        if theme not in ["light", "dark"]:
            print("无效的主题名称")
            return False
        return self.set_config_value("theme", theme)
    
    def get_font_size(self):
        """获取字体大小
        
        Returns:
            字体大小
        """
        return self.get_config_value("font_size")
    
    def set_font_size(self, font_size):
        """设置字体大小
        
        Args:
            font_size: 字体大小
        
        Returns:
            是否成功
        """
        if not isinstance(font_size, (int, float)) or font_size < 8 or font_size > 72:
            print("无效的字体大小")
            return False
        return self.set_config_value("font_size", int(font_size))
    
    def get_window_size(self):
        """获取窗口大小
        
        Returns:
            窗口大小字典 {"width": int, "height": int}
        """
        return self.get_config_value("window_size")
    
    def set_window_size(self, width, height):
        """设置窗口大小
        
        Args:
            width: 窗口宽度
            height: 窗口高度
        
        Returns:
            是否成功
        """
        if not isinstance(width, int) or not isinstance(height, int) or width < 200 or height < 300:
            print("无效的窗口大小")
            return False
        return self.set_config_value("window_size", {"width": width, "height": height})
    
    def get_angle_unit(self):
        """获取角度单位
        
        Returns:
            角度单位 (radians 或 degrees)
        """
        return self.get_config_value("angle_unit")
    
    def set_angle_unit(self, unit):
        """设置角度单位
        
        Args:
            unit: 角度单位 (radians 或 degrees)
        
        Returns:
            是否成功
        """
        if unit not in ["radians", "degrees"]:
            print("无效的角度单位")
            return False
        return self.set_config_value("angle_unit", unit)
    
    def should_remember_history(self):
        """是否记住历史记录
        
        Returns:
            布尔值
        """
        return self.get_config_value("remember_history")
    
    def set_remember_history(self, value):
        """设置是否记住历史记录
        
        Args:
            value: 布尔值
        
        Returns:
            是否成功
        """
        if not isinstance(value, bool):
            print("无效的值类型")
            return False
        return self.set_config_value("remember_history", value)