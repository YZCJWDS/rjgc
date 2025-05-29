import tkinter as tk
from tkinter import ttk
import random
import os

class MathTrainerUI:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("小学生速算练习")
        self.window.geometry("800x600")
        self.window.resizable(False, False)

        # 设置背景色
        self.bg_color = "#F0F4F8"  # 浅灰蓝色背景

        # 初始化主题颜色
        self.primary_color = "#4A90E2"
        self.accent_color = "#FF6B6B"

        self._load_background_image()
        print("[调试信息] 开始初始化UI组件...")
        self._setup_styles()
        print("[调试信息] 样式配置完成")
        self._setup_ui()
        print("[调试信息] UI布局初始化完成")

        self.current_answer = None
        self._create_animation()

    def _load_background_image(self):
        try:
            from PIL import Image, ImageTk
            # 创建画布
            self.bg_canvas = tk.Canvas(self.window, highlightthickness=0)
            self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

            # 加载背景图片
            bg_path = os.path.join(os.path.dirname(__file__), 'images', 'background.png')
            print(f"[调试信息] 加载背景图片: {bg_path}")
            
            pil_image = Image.open(bg_path)
            self.background_image = ImageTk.PhotoImage(pil_image.resize((800, 600), Image.Resampling.LANCZOS))
            self.bg_canvas.create_image(0, 0, image=self.background_image, anchor='nw')
            
        except Exception as e:
            print(f"背景图加载失败: {str(e)}")
            self.bg_canvas = tk.Canvas(self.window, bg=self.bg_color)
            self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def _create_animation(self):
        self.canvas = tk.Canvas(self.window, width=800, height=100, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(y=500)

        self.stars = []
        for _ in range(20):
            x = random.randint(0, 800)
            y = random.randint(0, 100)
            size = random.randint(2, 4)
            self.stars.append({
                'id': self.canvas.create_oval(x, y, x + size, y + size, fill=self.primary_color, outline=""),
                'speed': random.uniform(0.5, 1.5)
            })

        self._animate_stars()

    def _animate_stars(self):
        for star in self.stars:
            self.canvas.move(star['id'], -star['speed'], 0)
            coords = self.canvas.coords(star['id'])
            if coords[0] < -5:
                self.canvas.coords(star['id'], 800, coords[1], 800 + coords[2] - coords[0], coords[3])
        self.window.after(50, self._animate_stars)

    def show_feedback(self, is_correct):
        if is_correct:
            self.feedback_label.config(text="正确！", foreground="green")
            self._play_correct_animation()
        else:
            self.feedback_label.config(text=f"错误！正确答案是: {self.current_answer}", foreground="red")
            self._play_wrong_animation()

    def _play_correct_animation(self):
        font_size = 28

        def animate(i):
            if i < 5:
                self.question_label.config(font=("Arial", font_size + i * 2))
                self.window.after(50, animate, i + 1)
            else:
                self.question_label.config(font=("Arial", font_size))

        animate(0)

    def _play_wrong_animation(self):
        original_x = self.answer_entry.winfo_x()

        def animate(i):
            if i < 5:
                offset = 5 if i % 2 == 0 else -5
                self.answer_entry.place_configure(x=original_x + offset)
                self.window.after(50, animate, i + 1)
            else:
                self.answer_entry.place_configure(x=original_x)

        animate(0)

    def _start_practice(self):
        self._generate_new_question()
        self.answer_entry.focus()
        self.start_btn.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.NORMAL)

    def _generate_new_question(self):
        operators = ['+', '-', '*', '/']
        selected_operator = random.choice(operators)
        question_data = self.controller.generate_question(selected_operator)
        self.question_label.config(text=question_data['question'])
        self.current_answer = question_data['answer']

    def _check_answer(self):
        user_input = self.answer_entry.get()
        if not user_input:
            return

        try:
            user_answer = float(user_input)
            is_correct = self.controller.check_answer(user_answer, self.current_answer)

            if is_correct:
                self.show_feedback(True)
                self._generate_new_question()
            else:
                self.show_feedback(False)

            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()

        except ValueError:
            self.feedback_label.config(text="请输入有效数字！", foreground="red")
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # 通用样式设置
        style.configure(".", background=self.bg_color)
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, font=("Arial", 12))
        style.configure("TButton", background=self.bg_color)

        # 输入框样式
        style.configure("TEntry",
                       font=("Arial", 18),
                       padding=10,
                       background='white',
                       fieldbackground='white',
                       foreground='black')

        # 主按钮样式
        style.configure("Primary.TButton",
                       foreground="white",
                       background=self.primary_color,
                       font=("Arial", 14, "bold"),
                       borderwidth=0)
        style.map("Primary.TButton",
                 background=[("active", "#357ABD"), ("disabled", "#CCCCCC")])

        # 强调按钮样式
        style.configure("Accent.TButton",
                       foreground="white",
                       background=self.accent_color,
                       font=("Arial", 14, "bold"),
                       borderwidth=0)
        style.map("Accent.TButton",
                 background=[("active", "#E55959"), ("disabled", "#CCCCCC")])

        # 标题样式
        style.configure("Title.TLabel",
                       font=("Arial", 24, "bold"),
                       foreground=self.primary_color)

        # 题目样式
        style.configure("Question.TLabel",
                       font=("Arial", 28),
                       foreground="#333333")

        # 反馈样式
        style.configure("Feedback.TLabel",
                       font=("Arial", 18),
                       anchor=tk.CENTER)

    def _setup_ui(self):
        # 主容器使用窗口背景色
        main_container = tk.Frame(self.window, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 内容容器
        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=500)

        # 标题
        title_label = ttk.Label(
            content_frame,
            text="小学生速算练习",
            style="Title.TLabel"
        )
        title_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # 题目显示
        self.question_label = ttk.Label(
            content_frame,
            text="点击开始练习",
            style="Question.TLabel"
        )
        self.question_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        # 答案输入区
        input_frame = ttk.Frame(content_frame)
        input_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.answer_entry = ttk.Entry(
            input_frame,
            style="TEntry",
            width=15
        )
        self.answer_entry.pack(pady=(0, 10))

        # 按钮区
        button_frame = ttk.Frame(content_frame)
        button_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        try:
            from PIL import Image, ImageTk
            self.start_icon = ImageTk.PhotoImage(
                Image.open(os.path.join(os.path.dirname(__file__), 'images', 'btn_start.png')).resize((32, 32), Image.Resampling.LANCZOS))
            self.submit_icon = ImageTk.PhotoImage(
                Image.open(os.path.join(os.path.dirname(__file__), 'images', 'btn_submit.png')).resize((32, 32), Image.Resampling.LANCZOS))
        except Exception as e:
            print(f"按钮图标加载失败: {str(e)}")
            self.start_icon = self.submit_icon = None

        self.start_btn = ttk.Button(
            button_frame,
            text=" 开始练习",
            image=self.start_icon,
            compound=tk.LEFT,
            command=self._start_practice,
            style="Primary.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.submit_btn = ttk.Button(
            button_frame,
            text=" 提交答案",
            image=self.submit_icon,
            compound=tk.LEFT,
            command=self._check_answer,
            style="Accent.TButton"
        )
        self.submit_btn.pack(side=tk.LEFT, padx=5)
        self.submit_btn.config(state=tk.DISABLED)

        # 反馈标签
        self.feedback_label = ttk.Label(
            content_frame,
            text="",
            style="Feedback.TLabel"
        )
        self.feedback_label.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

    def run(self):
        self.window.mainloop()

