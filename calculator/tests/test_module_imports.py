import sys
import os

# 添加包含calculator包的项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_core_imports():
    """测试核心模块导入"""
    try:
        from calculator.core.arithmetic import ArithmeticCalculator
        from calculator.core.scientific import ScientificCalculator
        from calculator.core.unit_converter import UnitConverter
        from calculator.core.base_converter import BaseConverter
        print("✅ 核心模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 核心模块导入失败: {e}")
        return False

def test_ui_imports():
    """测试UI模块导入"""
    try:
        from calculator.ui.main_window import CalculatorMainWindow
        print("✅ UI模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ UI模块导入失败: {e}")
        return False

def test_data_imports():
    """测试数据模块导入"""
    try:
        from calculator.data.history_manager import HistoryManager
        from calculator.data.config_manager import ConfigManager
        print("✅ 数据模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 数据模块导入失败: {e}")
        return False

def test_calculator_functionality():
    """测试计算器基本功能"""
    try:
        from calculator.core.arithmetic import ArithmeticCalculator
        calc = ArithmeticCalculator()
        result = calc.add(5, 3)
        assert result == 8, f"加法测试失败: 期望8, 得到{result}"
        print("✅ 计算器功能测试成功")
        return True
    except Exception as e:
        print(f"❌ 计算器功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始模块导入测试...")
    
    core_result = test_core_imports()
    ui_result = test_ui_imports()
    data_result = test_data_imports()
    func_result = test_calculator_functionality()
    
    print("\n测试结果汇总:")
    print(f"核心模块: {'通过' if core_result else '失败'}")
    print(f"UI模块: {'通过' if ui_result else '失败'}")
    print(f"数据模块: {'通过' if data_result else '失败'}")
    print(f"功能测试: {'通过' if func_result else '失败'}")
    
    if core_result and data_result and func_result:
        print("\n✅ 基本模块结构和功能测试通过!")
        print("注意: UI模块测试可能需要安装PyQt6")
    else:
        print("\n❌ 部分测试失败，请检查代码")