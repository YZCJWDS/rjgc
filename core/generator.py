import random

class MathGenerator:
    def __init__(self, difficulty=1):
        self.number_range = {
            1: (0, 10),   # 初级难度
            2: (0, 100),  # 中级难度
            3: (0, 1000)  # 高级难度
        }[difficulty]
        
    def generate_question(self, operator='+'):
        a = random.randint(*self.number_range)
        b = random.randint(*self.number_range)
        
        # 处理减法避免负数结果
        if operator == '-' and a < b:
            a, b = b, a
        # 处理除法保证能整除
        elif operator == '/':
            if a > 0:
                b = random.choice([i for i in range(1, a+1) if a % i == 0])
            
        return {
            'question': f"{a} {operator} {b} = ?",
            'answer': eval(f"{a}{operator}{b}")
        }