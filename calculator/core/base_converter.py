class BaseConverter:
    """进制转换器类，提供不同进制之间的数值转换功能"""
    
    @staticmethod
    def decimal_to_binary(decimal_num):
        """十进制转换为二进制
        
        Args:
            decimal_num: 十进制数
        
        Returns:
            二进制字符串
        """
        if decimal_num == 0:
            return "0"
        
        # 处理负数
        is_negative = decimal_num < 0
        decimal_num = abs(decimal_num)
        
        result = []
        while decimal_num > 0:
            result.append(str(decimal_num % 2))
            decimal_num = decimal_num // 2
        
        if is_negative:
            return "-" + "".join(reversed(result))
        return "".join(reversed(result))
    
    @staticmethod
    def decimal_to_octal(decimal_num):
        """十进制转换为八进制
        
        Args:
            decimal_num: 十进制数
        
        Returns:
            八进制字符串
        """
        if decimal_num == 0:
            return "0"
        
        # 处理负数
        is_negative = decimal_num < 0
        decimal_num = abs(decimal_num)
        
        result = []
        while decimal_num > 0:
            result.append(str(decimal_num % 8))
            decimal_num = decimal_num // 8
        
        if is_negative:
            return "-" + "".join(reversed(result))
        return "".join(reversed(result))
    
    @staticmethod
    def decimal_to_hexadecimal(decimal_num):
        """十进制转换为十六进制
        
        Args:
            decimal_num: 十进制数
        
        Returns:
            十六进制字符串
        """
        if decimal_num == 0:
            return "0"
        
        # 处理负数
        is_negative = decimal_num < 0
        decimal_num = abs(decimal_num)
        
        hex_chars = "0123456789ABCDEF"
        result = []
        while decimal_num > 0:
            result.append(hex_chars[decimal_num % 16])
            decimal_num = decimal_num // 16
        
        if is_negative:
            return "-" + "".join(reversed(result))
        return "".join(reversed(result))
    
    @staticmethod
    def binary_to_decimal(binary_str):
        """二进制转换为十进制
        
        Args:
            binary_str: 二进制字符串
        
        Returns:
            十进制整数
        """
        try:
            return int(binary_str, 2)
        except ValueError:
            raise ValueError("无效的二进制字符串")
    
    @staticmethod
    def octal_to_decimal(octal_str):
        """八进制转换为十进制
        
        Args:
            octal_str: 八进制字符串
        
        Returns:
            十进制整数
        """
        try:
            return int(octal_str, 8)
        except ValueError:
            raise ValueError("无效的八进制字符串")
    
    @staticmethod
    def hexadecimal_to_decimal(hex_str):
        """十六进制转换为十进制
        
        Args:
            hex_str: 十六进制字符串
        
        Returns:
            十进制整数
        """
        try:
            return int(hex_str, 16)
        except ValueError:
            raise ValueError("无效的十六进制字符串")
    
    @staticmethod
    def convert(number_str, from_base, to_base):
        """通用进制转换函数
        
        Args:
            number_str: 数字字符串
            from_base: 源进制 (2, 8, 10, 16)
            to_base: 目标进制 (2, 8, 10, 16)
        
        Returns:
            转换后的数字字符串
        """
        # 验证进制范围
        if from_base not in [2, 8, 10, 16] or to_base not in [2, 8, 10, 16]:
            raise ValueError("进制必须是2、8、10或16")
        
        # 转换为十进制
        try:
            decimal_num = int(number_str, from_base)
        except ValueError:
            raise ValueError(f"无效的{from_base}进制数字字符串")
        
        # 从十进制转换为目标进制
        if to_base == 2:
            return BaseConverter.decimal_to_binary(decimal_num)
        elif to_base == 8:
            return BaseConverter.decimal_to_octal(decimal_num)
        elif to_base == 10:
            return str(decimal_num)
        elif to_base == 16:
            return BaseConverter.decimal_to_hexadecimal(decimal_num)
    
    @staticmethod
    def validate_number(number_str, base):
        """验证数字字符串是否符合指定进制
        
        Args:
            number_str: 数字字符串
            base: 进制
        
        Returns:
            bool: 是否有效
        """
        try:
            int(number_str, base)
            return True
        except ValueError:
            return False