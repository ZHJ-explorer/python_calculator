import math

class ScientificCalculator:
    """科学计算器类，提供三角函数、对数函数等科学计算功能"""
    
    @staticmethod
    def sin(x, radians=True):
        """正弦函数
        
        Args:
            x: 角度或弧度值
            radians: True表示输入为弧度，False表示输入为角度
        """
        if not radians:
            x = math.radians(x)
        return math.sin(x)
    
    @staticmethod
    def cos(x, radians=True):
        """余弦函数
        
        Args:
            x: 角度或弧度值
            radians: True表示输入为弧度，False表示输入为角度
        """
        if not radians:
            x = math.radians(x)
        return math.cos(x)
    
    @staticmethod
    def tan(x, radians=True):
        """正切函数
        
        Args:
            x: 角度或弧度值
            radians: True表示输入为弧度，False表示输入为角度
        """
        if not radians:
            x = math.radians(x)
        # 避免除零错误
        if abs(x % math.pi - math.pi/2) < 1e-10:
            raise ValueError("正切函数在90度的奇数倍处无定义")
        return math.tan(x)
    
    @staticmethod
    def asin(x):
        """反正弦函数，返回弧度值"""
        if x < -1 or x > 1:
            raise ValueError("反正弦函数的输入值必须在[-1, 1]范围内")
        return math.asin(x)
    
    @staticmethod
    def acos(x):
        """反余弦函数，返回弧度值"""
        if x < -1 or x > 1:
            raise ValueError("反余弦函数的输入值必须在[-1, 1]范围内")
        return math.acos(x)
    
    @staticmethod
    def atan(x):
        """反正切函数，返回弧度值"""
        return math.atan(x)
    
    @staticmethod
    def log(x, base=math.e):
        """对数函数
        
        Args:
            x: 输入值
            base: 底数，默认为自然对数（e）
        """
        if x <= 0:
            raise ValueError("对数函数的输入值必须大于零")
        if base == math.e:
            return math.log(x)
        elif base == 10:
            return math.log10(x)
        else:
            return math.log(x, base)
    
    @staticmethod
    def log10(x):
        """常用对数（以10为底）"""
        if x <= 0:
            raise ValueError("常用对数的输入值必须大于零")
        return math.log10(x)
    
    @staticmethod
    def exp(x):
        """指数函数（e的x次方）"""
        return math.exp(x)
    
    @staticmethod
    def pi():
        """返回圆周率π"""
        return math.pi
    
    @staticmethod
    def e():
        """返回自然对数的底e"""
        return math.e
    
    @staticmethod
    def radians(degrees):
        """角度转弧度"""
        return math.radians(degrees)
    
    @staticmethod
    def degrees(radians):
        """弧度转角度"""
        return math.degrees(radians)