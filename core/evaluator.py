class Evaluator:
    def __init__(self):
        pass

    def check_answer(self, user_answer, correct_answer):
        """检查用户答案是否正确"""
        try:
            return float(user_answer) == float(correct_answer)
        except ValueError:
            return False