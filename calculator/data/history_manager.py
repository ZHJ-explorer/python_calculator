import json
import os
from datetime import datetime

class HistoryManager:
    """历史记录管理器类，负责计算历史的本地存储和读取"""
    
    def __init__(self, history_file="calculator_history.json"):
        """初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
        """
        # 获取用户数据目录
        self.history_dir = os.path.join(os.path.expanduser("~"), ".python_calculator")
        self.history_file = os.path.join(self.history_dir, history_file)
        
        # 确保历史记录目录存在
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
        
        # 如果历史记录文件不存在，创建一个空文件
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def save_history(self, history_items):
        """保存历史记录
        
        Args:
            history_items: 历史记录列表，每个元素是一个字典
        """
        try:
            # 确保每个历史记录项都有时间戳
            for item in history_items:
                if 'timestamp' not in item:
                    item['timestamp'] = datetime.now().isoformat()
            
            # 读取现有历史记录
            existing_history = self.load_history()
            
            # 合并并去重
            all_history = existing_history + history_items
            unique_history = []
            seen = set()
            
            for item in all_history:
                # 创建一个唯一键
                key = f"{item.get('expression', '')}_{item.get('result', '')}_{item.get('timestamp', '')}"
                if key not in seen:
                    seen.add(key)
                    unique_history.append(item)
            
            # 按时间戳排序（最新的在前）
            unique_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # 限制历史记录数量
            if len(unique_history) > 100:
                unique_history = unique_history[:100]
            
            # 保存到文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(unique_history, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            return False
    
    def load_history(self):
        """加载历史记录
        
        Returns:
            历史记录列表
        """
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            return []
    
    def add_history_item(self, expression, result):
        """添加单个历史记录项
        
        Args:
            expression: 表达式字符串
            result: 计算结果
        """
        history_item = {
            'expression': expression,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        # 加载现有历史记录
        existing_history = self.load_history()
        
        # 添加新项到开头
        existing_history.insert(0, history_item)
        
        # 限制历史记录数量
        if len(existing_history) > 100:
            existing_history = existing_history[:100]
        
        # 保存更新后的历史记录
        return self.save_history(existing_history)
    
    def clear_history(self):
        """清空历史记录
        
        Returns:
            是否成功
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"清空历史记录失败: {e}")
            return False
    
    def get_history_by_date(self, start_date=None, end_date=None):
        """按日期范围获取历史记录
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            过滤后的历史记录列表
        """
        all_history = self.load_history()
        
        if not start_date and not end_date:
            return all_history
        
        filtered_history = []
        for item in all_history:
            item_date = datetime.fromisoformat(item.get('timestamp', ''))
            
            if start_date and item_date < start_date:
                continue
            if end_date and item_date > end_date:
                continue
            
            filtered_history.append(item)
        
        return filtered_history
    
    def export_history(self, export_file, format="json"):
        """导出历史记录
        
        Args:
            export_file: 导出文件路径
            format: 导出格式，支持json和txt
        
        Returns:
            是否成功
        """
        history = self.load_history()
        
        try:
            if format.lower() == "json":
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
            elif format.lower() == "txt":
                with open(export_file, 'w', encoding='utf-8') as f:
                    for item in history:
                        timestamp = datetime.fromisoformat(item.get('timestamp', '')).strftime('%Y-%m-%d %H:%M:%S')
                        f.write(f"[{timestamp}] {item.get('expression', '')} = {item.get('result', '')}\n")
            else:
                print(f"不支持的导出格式: {format}")
                return False
            
            return True
        except Exception as e:
            print(f"导出历史记录失败: {e}")
            return False