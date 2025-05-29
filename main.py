from core.generator import MathGenerator
from core.evaluator import Evaluator
from core.data_handler import DataHandler
from ui.tkinter_ui import MathTrainerUI

class MathTrainerApp:
    def __init__(self):
        # 初始化核心组件
        self.generator = MathGenerator(difficulty=1)  # 默认初级难度
        self.evaluator = Evaluator()
        self.data_handler = DataHandler()
        
        # 创建UI
        self.ui = MathTrainerUI(self)
        
    def generate_question(self, operator='+'):
        """生成题目（供UI调用）"""
        return self.generator.generate_question(operator)
        
    def check_answer(self, user_answer, correct_answer):
        """检查答案（供UI调用）"""
        return self.evaluator.check_answer(user_answer, correct_answer)
        
    def run(self):
        """启动应用"""
        self.ui.run()

if __name__ == "__main__":
    app = MathTrainerApp()
    app.run()