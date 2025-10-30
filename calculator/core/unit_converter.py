class UnitConverter:
    """单位换算器类，提供各种常用单位之间的换算功能"""
    
    # 长度单位换算系数（以米为基准）
    LENGTH_UNITS = {
        'meter': 1.0,              # 米
        'kilometer': 1000.0,       # 千米
        'centimeter': 0.01,        # 厘米
        'millimeter': 0.001,       # 毫米
        'inch': 0.0254,            # 英寸
        'foot': 0.3048,            # 英尺
        'yard': 0.9144,            # 码
        'mile': 1609.344           # 英里
    }
    
    # 重量单位换算系数（以克为基准）
    WEIGHT_UNITS = {
        'gram': 1.0,               # 克
        'kilogram': 1000.0,        # 千克
        'milligram': 0.001,        # 毫克
        'metric_ton': 1000000.0,   # 吨
        'pound': 453.59237,        # 磅
        'ounce': 28.349523125      # 盎司
    }
    
    # 体积单位换算系数（以升为基准）
    VOLUME_UNITS = {
        'liter': 1.0,              # 升
        'milliliter': 0.001,       # 毫升
        'cubic_meter': 1000.0,     # 立方米
        'gallon_us': 3.785411784,  # 美制加仑
        'gallon_uk': 4.54609,      # 英制加仑
        'fluid_ounce_us': 0.0295735295625,  # 美制液盎司
        'fluid_ounce_uk': 0.0284130625      # 英制液盎司
    }
    
    # 温度单位换算
    @staticmethod
    def convert_temperature(value, from_unit, to_unit):
        """温度单位换算
        
        Args:
            value: 温度值
            from_unit: 源单位 ('celsius', 'fahrenheit', 'kelvin')
            to_unit: 目标单位 ('celsius', 'fahrenheit', 'kelvin')
        """
        if from_unit == to_unit:
            return value
        
        # 先转换为摄氏度
        if from_unit == 'fahrenheit':
            celsius = (value - 32) * 5 / 9
        elif from_unit == 'kelvin':
            celsius = value - 273.15
        else:  # celsius
            celsius = value
        
        # 再从摄氏度转换为目标单位
        if to_unit == 'fahrenheit':
            return celsius * 9 / 5 + 32
        elif to_unit == 'kelvin':
            return celsius + 273.15
        else:  # celsius
            return celsius
    
    @staticmethod
    def convert_length(value, from_unit, to_unit):
        """长度单位换算
        
        Args:
            value: 长度值
            from_unit: 源单位
            to_unit: 目标单位
        """
        if from_unit not in UnitConverter.LENGTH_UNITS:
            raise ValueError(f"不支持的源长度单位: {from_unit}")
        if to_unit not in UnitConverter.LENGTH_UNITS:
            raise ValueError(f"不支持的目标长度单位: {to_unit}")
        
        # 先转换为米，再转换为目标单位
        meters = value * UnitConverter.LENGTH_UNITS[from_unit]
        return meters / UnitConverter.LENGTH_UNITS[to_unit]
    
    @staticmethod
    def convert_weight(value, from_unit, to_unit):
        """重量单位换算
        
        Args:
            value: 重量值
            from_unit: 源单位
            to_unit: 目标单位
        """
        if from_unit not in UnitConverter.WEIGHT_UNITS:
            raise ValueError(f"不支持的源重量单位: {from_unit}")
        if to_unit not in UnitConverter.WEIGHT_UNITS:
            raise ValueError(f"不支持的目标重量单位: {to_unit}")
        
        # 先转换为克，再转换为目标单位
        grams = value * UnitConverter.WEIGHT_UNITS[from_unit]
        return grams / UnitConverter.WEIGHT_UNITS[to_unit]
    
    @staticmethod
    def convert_volume(value, from_unit, to_unit):
        """体积单位换算
        
        Args:
            value: 体积值
            from_unit: 源单位
            to_unit: 目标单位
        """
        if from_unit not in UnitConverter.VOLUME_UNITS:
            raise ValueError(f"不支持的源体积单位: {from_unit}")
        if to_unit not in UnitConverter.VOLUME_UNITS:
            raise ValueError(f"不支持的目标体积单位: {to_unit}")
        
        # 先转换为升，再转换为目标单位
        liters = value * UnitConverter.VOLUME_UNITS[from_unit]
        return liters / UnitConverter.VOLUME_UNITS[to_unit]
    
    @staticmethod
    def get_available_length_units():
        """获取所有可用的长度单位"""
        return list(UnitConverter.LENGTH_UNITS.keys())
    
    @staticmethod
    def get_available_weight_units():
        """获取所有可用的重量单位"""
        return list(UnitConverter.WEIGHT_UNITS.keys())
    
    @staticmethod
    def get_available_volume_units():
        """获取所有可用的体积单位"""
        return list(UnitConverter.VOLUME_UNITS.keys())
    
    @staticmethod
    def get_available_temperature_units():
        """获取所有可用的温度单位"""
        return ['celsius', 'fahrenheit', 'kelvin']