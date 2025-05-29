import json
import os

class DataHandler:
    def __init__(self, config_path='config/settings.json'):
        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果文件不存在或格式错误，返回默认配置
            return {
                "current_user": "",
                "difficulty_level": 1,
                "practice_history": []
            }

    def save_score(self, total, correct, time_used):
        """保存练习记录"""
        record = {
            "date": self._get_current_date(),
            "total": total,
            "correct": correct,
            "time_used": time_used
        }
        self.data['practice_history'].append(record)
        self._save_config()

    def _save_config(self):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def _get_current_date(self):
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')