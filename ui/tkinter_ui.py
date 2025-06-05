import tkinter as tk
from tkinter import ttk, messagebox
import random
import os
import json  # Added for leaderboard

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[警告] Pillow library not found. Images will not be loaded.")

class EnhancedMathTrainerUI:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("小学生速算乐园 🎉") # More engaging title
        self.window.geometry("800x650") # Slightly taller for more space
        self.window.resizable(False, False)

        # --- Color Palette ---
        self.bg_color = "#E0F7FA"  # Light Cyan - Softer background
        self.primary_color = "#00796B"  # Teal - For primary actions and accents
        self.accent_color = "#FF8A65"  # Deep Orange - For secondary actions/emphasis
        self.text_color = "#263238"    # Blue Grey - For general text
        self.correct_color = "#4CAF50" # Green - For correct answers
        self.error_color = "#F44336"   # Red - For errors/incorrect answers
        self.input_bg_color = "#FFFFFF" # White for input field

        self.current_answer = None
        self.question_active = False # To track if a question is currently displayed
        self.selected_difficulty = tk.StringVar(value="中等") # Default difficulty

        self.score = 0
        self.lives = 3
        self.leaderboard_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'leaderboard.json')
        self.leaderboard_data = self._load_leaderboard()

        self._load_assets()
        self._setup_styles()
        self._create_main_layout()
        self._create_header()
        self._create_question_area()
        self._create_input_area()
        self._create_feedback_area()
        # self._create_star_animation_canvas() # Keep the star animation # 去掉星星动画

        print("[调试信息] UI初始化完成")
        self.show_initial_message()

    def _load_assets(self):
        self.images = {}
        if not PIL_AVAILABLE:
            messagebox.showwarning("Pillow缺失", "Python Pillow库未安装，无法加载图片资源。程序将不显示图片。")
            return

        # 配置PIL日志级别以抑制libpng警告
        import logging
        pil_logger = logging.getLogger('PIL')
        pil_logger.setLevel(logging.WARNING)

        # 修改图片文件名以匹配实际文件
        # Paths are relative to the 'images' subdirectory
        image_files = {
            "background": "background.png", # 修改为实际存在的文件名
            "start_button": "btn_start.png",    # 修改为实际存在的文件名
            "submit_button": "btn_submit.png",  # 修改为实际存在的文件名
            "correct_icon": "btn_start.png",   # 临时使用已有图片
            "incorrect_icon": "btn_submit.png"    # 临时使用已有图片
        }
        base_path = os.path.join(os.path.dirname(__file__), 'images')

        for name, filename in image_files.items():
            path = os.path.join(base_path, filename)
            try:
                if name == "background":
                    img = Image.open(path)
                    self.images[name] = ImageTk.PhotoImage(img.resize((800, 650), Image.Resampling.LANCZOS))
                else: # Icons
                    img = Image.open(path)
                    # Standard icon size, adjust as needed
                    icon_size = (40, 40) if "button" in name else (50, 50)
                    self.images[name] = ImageTk.PhotoImage(img.resize(icon_size, Image.Resampling.LANCZOS))
                print(f"[调试信息] 成功加载图片: {name} from {path}")
            except Exception as e:
                print(f"[错误] 加载图片失败 '{name}': {e}")
                self.images[name] = None # Explicitly set to None if loading fails

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') # clam is a good base for custom styling

        # --- General Styles ---
        style.configure(".",
                        background=self.bg_color,
                        foreground=self.text_color,
                        font=("Segoe UI", 12)) # Using a more modern font
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)

        # --- Button Styles ---
        # Base button style
        style.configure("App.TButton",
                        font=("Segoe UI", 14, "bold"),
                        padding=(10, 8), # Horizontal, vertical padding
                        borderwidth=0,
                        relief=tk.FLAT, # Flat modern look
                        foreground="white")
        style.map("App.TButton",
                  background=[("active", self.primary_color), # Keep consistent on active
                              ("disabled", "#BDBDBD")], # Grey out when disabled
                  relief=[("pressed", tk.SUNKEN), ("!pressed", tk.FLAT)])

        style.configure("Primary.TButton", background=self.primary_color)
        style.map("Primary.TButton",
                  background=[("active", "#005A4B"), # Darker shade on hover/active
                              ("disabled", "#BDBDBD")])

        style.configure("Accent.TButton", background=self.accent_color)
        style.map("Accent.TButton",
                  background=[("active", "#E67E22"), # Darker shade for accent
                              ("disabled", "#BDBDBD")])

        # --- Label Styles ---
        style.configure("Header.TLabel",
                        font=("Comic Sans MS", 28, "bold"), # Fun font for kids
                        foreground=self.primary_color)
        style.configure("Question.TLabel",
                        font=("Segoe UI", 38, "bold"), # Larger font for question
                        foreground=self.text_color)
        style.configure("Feedback.TLabel",
                        font=("Segoe UI", 16),
                        padding=10)
        style.configure("Correct.Feedback.TLabel", foreground=self.correct_color)
        style.configure("Error.Feedback.TLabel", foreground=self.error_color)

        # --- Entry Style ---
        style.configure("TEntry",
                        font=("Segoe UI", 24),
                        padding=10,
                        relief=tk.SOLID, # Clear border
                        fieldbackground=self.input_bg_color,
                        foreground=self.text_color,
                        borderwidth=1)
        style.map("TEntry",
                  bordercolor=[('focus', self.primary_color), ('!focus', '#CCCCCC')],
                  borderwidth=[('focus', 2), ('!focus', 1)])

        # 为排行榜对话框添加特定样式
        style.configure("Leaderboard.TLabel",
                        background="#F0F4C3",  # 淡黄色背景
                        foreground="#33691E",  # 深绿色文字
                        font=("Segoe UI", 14, "bold"),
                        padding=10)

    def _create_main_layout(self):
        # Background Canvas (full window)
        self.background_canvas = tk.Canvas(self.window, highlightthickness=0)
        if self.images.get("background"):
            self.background_canvas.create_image(0, 0, image=self.images["background"], anchor='nw')
        else:
            self.background_canvas.config(bg=self.bg_color) # Fallback color
        self.background_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Main content frame - slightly offset from edges for a "floating" feel
        self.main_frame = ttk.Frame(self.window, style="TFrame", padding=20)
        # self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=700, height=550)
        # Using pack to center the main content area, allowing background to show around it
        self.main_frame.pack(expand=True, fill=tk.NONE, pady=(20,0)) # pady to push it down a bit from top

    def _create_header(self):
        header_frame = ttk.Frame(self.main_frame, style="TFrame")
        header_frame.pack(pady=(10, 20), fill=tk.X)

        title_label = ttk.Label(header_frame, text="小学生速算乐园 🎉", style="Header.TLabel")
        title_label.pack()

        # Score and Lives display
        info_frame = ttk.Frame(header_frame, style="TFrame")
        info_frame.pack(pady=(5,0), fill=tk.X)

        self.score_label = ttk.Label(info_frame, text=f"分数: {self.score}", font=("Segoe UI", 14))
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.lives_label = ttk.Label(info_frame, text=f"生命: {self.lives * '❤️'}", font=("Segoe UI", 14), foreground=self.error_color)
        self.lives_label.pack(side=tk.RIGHT, padx=20)

    def _create_question_area(self):
        question_frame = ttk.Frame(self.main_frame, style="TFrame")
        question_frame.pack(pady=20)

        self.question_label = ttk.Label(question_frame, text="点击开始按钮吧！", style="Question.TLabel")
        self.question_label.pack()
        # Store original properties for animations
        self.question_label_orig_fg = self.question_label.cget("foreground")

    def _create_input_area(self):
        input_controls_frame = ttk.Frame(self.main_frame, style="TFrame")
        input_controls_frame.pack(pady=10) # Reduced pady to make space for difficulty

        # Difficulty Selection
        difficulty_frame = ttk.Frame(input_controls_frame, style="TFrame")
        difficulty_frame.pack(pady=(0, 10)) # Space below difficulty selection

        ttk.Label(difficulty_frame, text="选择难度:", style="TLabel").pack(side=tk.LEFT, padx=(0, 5))
        difficulty_options = ["简单", "中等", "困难"]
        self.difficulty_combobox = ttk.Combobox(
            difficulty_frame,
            textvariable=self.selected_difficulty,
            values=difficulty_options,
            state="readonly", # Prevent manual text input
            width=8,
            font=("Segoe UI", 12)
        )
        self.difficulty_combobox.pack(side=tk.LEFT)
        self.difficulty_combobox.bind("<<ComboboxSelected>>", self._on_difficulty_change)

        # Entry field
        self.answer_entry = ttk.Entry(input_controls_frame, width=10, style="TEntry", justify=tk.CENTER)
        self.answer_entry.pack(pady=(0, 15)) # Space below entry
        self.answer_entry.bind("<Return>", lambda event: self._check_answer()) # Submit on Enter

        # Buttons Frame (for side-by-side layout)
        buttons_frame = ttk.Frame(input_controls_frame, style="TFrame")
        buttons_frame.pack(pady=(10,0)) # Add some padding above buttons

        self.start_btn = ttk.Button(
            buttons_frame,
            text=" 开始练习",
            image=self.images.get("start_button"),
            compound=tk.LEFT,
            command=self._start_practice,
            style="Primary.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.submit_btn = ttk.Button(
            buttons_frame,
            text=" 提交答案",
            image=self.images.get("submit_button"),
            compound=tk.LEFT,
            command=self._check_answer,
            style="Accent.TButton"
        )
        self.submit_btn.pack(side=tk.LEFT, padx=10)
        self.submit_btn.config(state=tk.DISABLED)

        self.leaderboard_btn = ttk.Button(
            buttons_frame,
            text="排行榜",
            command=self._show_leaderboard_ui,
            style="App.TButton" # Using a general app button style
        )
        self.leaderboard_btn.pack(side=tk.LEFT, padx=10)

    def _create_feedback_area(self):
        self.feedback_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.feedback_frame.pack(pady=20, fill=tk.X) # Fill horizontally to center text

        self.feedback_icon_label = ttk.Label(self.feedback_frame, style="TLabel") # For correct/incorrect icon
        self.feedback_icon_label.pack(pady=(0,5))

        self.feedback_text_label = ttk.Label(self.feedback_frame, text="", style="Feedback.TLabel", anchor=tk.CENTER)
        self.feedback_text_label.pack(fill=tk.X)

    def _on_difficulty_change(self, event=None):
        print(f"[调试信息] 难度已更改为: {self.selected_difficulty.get()}")

    def _update_score_lives_labels(self):
        self.score_label.config(text=f"分数: {self.score}")
        self.lives_label.config(text=f"生命: {self.lives * '❤️'}")

    def _game_over(self):
        self.question_active = False
        messagebox.showinfo("游戏结束", f"游戏结束！\n你的最终得分是: {self.score}")
        self._add_score_to_leaderboard(self.score)

        # Reset UI for new game
        self.start_btn.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.DISABLED)
        self.difficulty_combobox.config(state="readonly")
        self.question_label.config(text="点击开始按钮吧！")
        self.answer_entry.delete(0, tk.END)
        self.show_initial_message() # Clear feedback

        self._show_leaderboard_ui() # Show leaderboard after game over

    def _load_leaderboard(self):
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
                        return data
                    else:
                        print("[警告] 排行榜文件格式不正确，将使用空排行榜。")
                        return []
            else:
                os.makedirs(os.path.dirname(self.leaderboard_file), exist_ok=True)
                return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"[错误] 加载排行榜失败: {e}")
            return []

    def _save_leaderboard(self):
        try:
            os.makedirs(os.path.dirname(self.leaderboard_file), exist_ok=True)
            with open(self.leaderboard_file, 'w', encoding='utf-8') as f:
                json.dump(self.leaderboard_data, f, indent=4)
        except IOError as e:
            print(f"[错误] 保存排行榜失败: {e}")

    def _add_score_to_leaderboard(self, new_score):
        if not isinstance(new_score, (int, float)):
            print(f"[警告] 无效的分数类型: {new_score}")
            return

        self.leaderboard_data.append(new_score)
        self.leaderboard_data.sort(reverse=True)
        self.leaderboard_data = self.leaderboard_data[:3]
        self._save_leaderboard()

    def _show_leaderboard_ui(self):
        # 创建一个自定义的排行榜窗口，而不是使用messagebox
        leaderboard_window = tk.Toplevel(self.window)
        leaderboard_window.title("排行榜 - 前三名")
        leaderboard_window.geometry("350x250")
        leaderboard_window.resizable(False, False)
        leaderboard_window.configure(bg="#F0F4C3")  # 淡黄色背景

        # 窗口设置为模态，必须关闭此窗口才能操作主窗口
        leaderboard_window.transient(self.window)
        leaderboard_window.grab_set()

        # 标题标签
        title_label = ttk.Label(
            leaderboard_window,
            text="🏆 最高分记录 🏆",
            style="Leaderboard.TLabel",
            anchor=tk.CENTER
        )
        title_label.pack(pady=(20, 10), fill=tk.X)

        # 排行榜内容
        content_frame = ttk.Frame(leaderboard_window, style="TFrame")
        content_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        content_frame.configure(style="TFrame")

        if not self.leaderboard_data:
            ttk.Label(
                content_frame,
                text="排行榜为空！\n开始挑战以创造记录吧！",
                style="Leaderboard.TLabel",
                anchor=tk.CENTER
            ).pack(pady=20, fill=tk.X)
        else:
            for i, score in enumerate(self.leaderboard_data):
                # 使用不同的颜色和图标来突出显示不同的排名
                if i == 0:
                    prefix = "🥇"  # 金牌
                    frame_bg = "#FFD700"  # 金色
                elif i == 1:
                    prefix = "🥈"  # 银牌
                    frame_bg = "#C0C0C0"  # 银色
                elif i == 2:
                    prefix = "🥉"  # 铜牌
                    frame_bg = "#CD7F32"  # 铜色
                else:
                    prefix = "🎖️"  # 普通奖牌
                    frame_bg = "#F0F4C3"  # 淡黄色

                rank_frame = tk.Frame(content_frame, bg=frame_bg, bd=1, relief=tk.RAISED)
                rank_frame.pack(fill=tk.X, padx=20, pady=5)

                rank_label = tk.Label(
                    rank_frame,
                    text=f"{prefix} 第 {i+1} 名: {score}分",
                    font=("Segoe UI", 14, "bold"),
                    bg=frame_bg,
                    fg="#33691E"  # 深绿色文字
                )
                rank_label.pack(pady=8, padx=5)

        # 关闭按钮
        close_button = ttk.Button(
            leaderboard_window,
            text="关闭",
            command=leaderboard_window.destroy,
            style="Primary.TButton"
        )
        close_button.pack(pady=(5, 20))

        # 设置窗口在屏幕中央
        leaderboard_window.update_idletasks()
        width = leaderboard_window.winfo_width()
        height = leaderboard_window.winfo_height()
        x = (leaderboard_window.winfo_screenwidth() // 2) - (width // 2)
        y = (leaderboard_window.winfo_screenheight() // 2) - (height // 2)
        leaderboard_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # 等待此窗口关闭
        leaderboard_window.wait_window()

    def _clear_feedback(self):
        if self.question_active:
            self.feedback_text_label.config(text="")
            self.feedback_icon_label.config(image='')

    def _start_practice(self):
        self.score = 0
        self.lives = 3
        self._update_score_lives_labels()
        self.question_active = True
        self._clear_feedback()
        self._generate_new_question()
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()
        self.start_btn.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.NORMAL)

    def _generate_new_question(self):
        difficulty = self.selected_difficulty.get()

        if difficulty == "简单":
            operators = ['+', '-']
        elif difficulty == "中等":
            operators = ['+', '-', '*']
        else: # 困难
            operators = ['+', '-', '*', '/']

        selected_operator = random.choice(operators)
        question_data = self.controller.generate_question(selected_operator, difficulty)
        self.question_label.config(text=question_data['question'])
        self.current_answer = question_data['answer']

    def _check_answer(self):
        if not self.question_active:
            return

        user_input = self.answer_entry.get().strip()
        if not user_input:
            self.feedback_text_label.config(text="请输入答案哦！", style="Error.Feedback.TLabel")
            self.feedback_icon_label.config(image='')
            return

        try:
            user_answer = float(user_input)
            is_correct = self.controller.check_answer(user_answer, self.current_answer)

            if is_correct:
                self.score += 10
                self._update_score_lives_labels()
                self.show_feedback(is_correct)
                self.window.after(1500, lambda: [
                    self.answer_entry.delete(0, tk.END),
                    self._generate_new_question()
                ])
            else:
                self.lives -= 1
                self._update_score_lives_labels()
                self.show_feedback(is_correct)
                if self.lives <= 0:
                    self._game_over()
                else:
                    self.answer_entry.delete(0, tk.END)
                    self.answer_entry.focus()

        except ValueError:
            self.feedback_text_label.config(text="请输入有效的数字！", style="Error.Feedback.TLabel")
            self.feedback_icon_label.config(image=self.images.get("incorrect_icon"))
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()
            self.window.after(3000, self._clear_feedback)

    def show_initial_message(self):
        self.feedback_icon_label.config(image='') # Clear icon
        self.feedback_text_label.config(text="准备好了吗？点击开始按钮进行速算练习！", style="Feedback.TLabel")

    def show_feedback(self, is_correct):
        icon = None
        if is_correct:
            self.feedback_text_label.config(text="太棒了，回答正确！", style="Correct.Feedback.TLabel")
            icon = self.images.get("correct_icon")
            self._play_correct_animation()
        else:
            self.feedback_text_label.config(text=f"别灰心，正确答案是: {self.current_answer}", style="Error.Feedback.TLabel")
            icon = self.images.get("incorrect_icon")
            self._play_wrong_animation()

        if icon:
            self.feedback_icon_label.config(image=icon)
        else:
            self.feedback_icon_label.config(image='')
            
        self.window.update()
        self.window.after(3000, self._clear_feedback)

    def _play_correct_animation(self):
        original_color = self.question_label_orig_fg
        self.question_label.config(foreground=self.correct_color)
        self.window.after(150, lambda: self.question_label.config(font=("Segoe UI", 40, "bold")))
        self.window.after(300, lambda: self.question_label.config(font=("Segoe UI", 38, "bold")))
        self.window.after(450, lambda: self.question_label.config(foreground=original_color))

    def _play_wrong_animation(self):
        try:
            has_focus = self.answer_entry == self.window.focus_get()
            entry_x = self.answer_entry.winfo_x()
            entry_y = self.answer_entry.winfo_y()
            entry_width = self.answer_entry.winfo_width()
            entry_height = self.answer_entry.winfo_height()

            self.answer_entry.pack_forget()
            self.answer_entry.place(x=entry_x, y=entry_y, width=entry_width, height=entry_height)

            def animate_shake(count):
                if count > 0:
                    offset = 5 if count % 2 == 0 else -5
                    self.answer_entry.place(x=entry_x + offset, y=entry_y)
                    self.window.after(50, lambda: animate_shake(count - 1))
                else:
                    self.answer_entry.place_forget()
                    self.answer_entry.pack(pady=(0,15))
                    if has_focus:
                        self.answer_entry.focus_set()

            animate_shake(6)

        except Exception as e:
            print(f"[错误] 动画效果出错: {e}")
            self.answer_entry.place_forget()
            self.answer_entry.pack(pady=(0,15))
            self.answer_entry.focus_set()

    def run(self):
        self.window.mainloop()

# Dummy Controller for testing purposes
class DummyController:
    def generate_question(self, operator, difficulty="中等"): # Add difficulty parameter
        num1, num2 = self._get_numbers_for_difficulty(operator, difficulty)

        if operator == '/': # Basic division, ensure num1 is multiple of num2
            if num2 == 0: num2 = 1
            num1 = num2 * random.randint(1, difficulty_settings[difficulty]['div_multiplier_max'])
        elif operator == '-': # Ensure positive result for simplicity
            if num1 < num2:
                num1, num2 = num2, num1

        question = f"{num1} {operator} {num2} = ?"
        answer = eval(str(num1) + operator + str(num2))
        if operator == '/':
            answer = int(answer)
        return {'question': question, 'answer': answer}

    def _get_numbers_for_difficulty(self, operator, difficulty):
        config = difficulty_settings.get(difficulty, difficulty_settings["中等"])

        if operator == '*':
            num1 = random.randint(config['mult_min'], config['mult_max'])
            num2 = random.randint(config['mult_min'], config['mult_max'])
        elif operator == '/':
            num1 = random.randint(config['add_sub_min'], config['add_sub_max'])
            num2 = random.randint(config['div_divisor_min'], config['div_divisor_max'])
            if num2 == 0: num2 = 1
        else:
            num1 = random.randint(config['add_sub_min'], config['add_sub_max'])
            num2 = random.randint(config['add_sub_min'], config['add_sub_max'])
        return num1, num2

    def check_answer(self, user_answer, correct_answer):
        try:
            return float(user_answer) == float(correct_answer)
        except ValueError:
            return False

# Difficulty settings
difficulty_settings = {
    "简单": {
        "add_sub_min": 1, "add_sub_max": 10,
        "mult_min": 1, "mult_max": 5,
        "div_divisor_min": 1, "div_divisor_max": 5, "div_multiplier_max": 5,
        "operators": ['+', '-']
    },
    "中等": {
        "add_sub_min": 1, "add_sub_max": 50,
        "mult_min": 1, "mult_max": 12,
        "div_divisor_min": 1, "div_divisor_max": 10, "div_multiplier_max": 10,
        "operators": ['+', '-', '*']
    },
    "困难": {
        "add_sub_min": 1, "add_sub_max": 100,
        "mult_min": 1, "mult_max": 20,
        "div_divisor_min": 2, "div_divisor_max": 12, "div_multiplier_max": 12,
        "operators": ['+', '-', '*', '/']
    }
}

if __name__ == '__main__':
    if not PIL_AVAILABLE:
        print("---------------------------------------------------------")
        print("Pillow library is not installed. Images will not be loaded.")
        print("Please install it by running: pip install Pillow")
        print("---------------------------------------------------------")

    controller = DummyController()
    app_ui = EnhancedMathTrainerUI(controller)
    app_ui.run()

