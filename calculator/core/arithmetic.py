import re
import ast

class ArithmeticCalculator:
    """算术运算计算器类，提供基本的数学运算功能"""
    
    @staticmethod
    def add(a, b):
        """加法运算"""
        return a + b
    
    @staticmethod
    def subtract(a, b):
        """减法运算"""
        return a - b
    
    @staticmethod
    def multiply(a, b):
        """乘法运算"""
        return a * b
    
    @staticmethod
    def divide(a, b):
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    
    @staticmethod
    def power(a, b):
        """幂运算"""
        return a ** b
    
    @staticmethod
    def square_root(a):
        """平方根运算"""
        if a < 0:
            raise ValueError("不能对负数求平方根")
        return a ** 0.5
    
    @staticmethod
    def cube_root(a):
        """立方根运算"""
        return a ** (1/3)
    
    @staticmethod
    def reciprocal(a):
        """倒数运算"""
        if a == 0:
            raise ValueError("零没有倒数")
        return 1 / a
    
    @staticmethod
    def factorial(n):
        """阶乘运算"""
        if not isinstance(n, int) or n < 0:
            raise ValueError("阶乘只能计算非负整数")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    @staticmethod
    def evaluate_expression(expression):
        """计算带括号的表达式
        
        Args:
            expression: 字符串形式的数学表达式，支持+、-、*、/、()
            
        Returns:
            计算结果
            
        Raises:
            ValueError: 表达式无效或包含不支持的操作
        """
        # 验证表达式只包含允许的字符
        if not re.match(r'^[0-9\s\+\-\*/\.\(\)]*$', expression):
            raise ValueError("表达式包含不支持的字符")
        
        # 检查括号是否匹配
        open_brackets = expression.count('(')
        close_brackets = expression.count(')')
        if open_brackets != close_brackets:
            raise ValueError("括号不匹配")
        
        try:
            # 使用ast.literal_eval计算表达式 - 更安全的方式
            # 先将表达式转换为可安全计算的形式
            # 替换乘法符号以避免解释为元组
            expression = expression.replace('*', '*')
            
            # 定义安全的计算函数
            def safe_eval(node):
                if isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.BinOp):
                    left = safe_eval(node.left)
                    right = safe_eval(node.right)
                    if isinstance(node.op, ast.Add):
                        return left + right
                    elif isinstance(node.op, ast.Sub):
                        return left - right
                    elif isinstance(node.op, ast.Mult):
                        return left * right
                    elif isinstance(node.op, ast.Div):
                        if right == 0:
                            raise ValueError("除数不能为零")
                        return left / right
                    else:
                        raise ValueError(f"不支持的操作符: {type(node.op).__name__}")
                elif isinstance(node, ast.UnaryOp):
                    operand = safe_eval(node.operand)
                    if isinstance(node.op, ast.USub):
                        return -operand
                    elif isinstance(node.op, ast.UAdd):
                        return operand
                    else:
                        raise ValueError(f"不支持的一元操作符: {type(node.op).__name__}")
                else:
                    raise ValueError(f"不支持的表达式节点: {type(node).__name__}")
            
            # 解析表达式
            tree = ast.parse(expression, mode='eval')
            # 计算表达式
            result = safe_eval(tree.body)
            
            return result
        except SyntaxError:
            raise ValueError("表达式语法错误")
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"计算错误: {str(e)}")