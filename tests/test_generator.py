import unittest
from core.generator import MathGenerator

class TestGenerator(unittest.TestCase):
    def setUp(self):
        """初始化测试环境"""
        self.generator = MathGenerator()

    def test_addition(self):
        """测试加法题目生成"""
        for _ in range(100):
            q = self.generator.generate_question('+')
            a, b = map(int, q['question'].split(' ')[0::2])
            self.assertEqual(a + b, q['answer'])

    def test_subtraction(self):
        """测试减法题目生成"""
        for _ in range(100):
            q = self.generator.generate_question('-')
            a, b = map(int, q['question'].split(' ')[0::2])
            self.assertGreaterEqual(a, b)  # 确保没有负数结果
            self.assertEqual(a - b, q['answer'])

    def test_multiplication(self):
        """测试乘法题目生成"""
        for _ in range(100):
            q = self.generator.generate_question('*')
            a, b = map(int, q['question'].split(' ')[0::2])
            self.assertEqual(a * b, q['answer'])

    def test_division(self):
        """测试除法题目生成"""
        for _ in range(100):
            q = self.generator.generate_question('/')
            a, b = map(int, q['question'].split(' ')[0::2])
            self.assertEqual(a % b, 0)  # 确保可以整除
            self.assertEqual(a / b, q['answer'])

    def test_difficulty_level(self):
        """测试不同难度级别"""
        # 测试初级难度
        gen1 = MathGenerator(difficulty=1)
        for _ in range(100):
            q = gen1.generate_question()
            a, b = map(int, q['question'].split(' ')[0::2])
            self.assertTrue(0 <= a <= 10 and 0 <= b <= 10)
            
        # 测试中级难度
        gen2 = MathGenerator(difficulty=2)
        for _ in range(100):
            q = gen2.generate_question()
            a, b = map(int, q['question'].split(' ')[0::2])
            self.assertTrue(0 <= a <= 100 and 0 <= b <= 100)
            
        # 测试高级难度
        gen3 = MathGenerator(difficulty=3)
        for _ in range(100):
            q = gen3.generate_question()
            a, b = map(int, q['question'].split(' ')[0::2])
            self.assertTrue(0 <= a <= 1000 and 0 <= b <= 1000)

if __name__ == '__main__':
    unittest.main()