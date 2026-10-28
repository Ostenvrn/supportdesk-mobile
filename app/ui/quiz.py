# app/ui/quiz.py
#
# Экран тестирования (L1, L2, L3).
# Тест состоит из 20 случайных вопросов.
# В конце — разбор ошибок.

import json
import random
import threading
from importlib import resources

import flet as ft
from app.core.storage import save_quiz_result


class QuizScreen:
    def __init__(self, page: ft.Page, level: int, on_back):
        self.page = page
        self.level = level
        self.on_back = on_back

        self.questions = self._load_questions()
        self.current_idx = 0
        self.correct_answers = 0
        
        # Список для хранения истории ответов (для разбора в конце)
        # Формат: {"question": str, "user_answer": str, "correct_answer": str, "is_correct": bool}
        self.answers_history = [] 

        self.timer_seconds = 0
        self.timer_running = True

        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
        self.timer_text = None

    def _load_questions(self) -> list:
        try:
            data_file = resources.files("assets").joinpath("quiz_questions.json")
            with data_file.open("r", encoding="utf-8") as f:
                all_q = json.load(f).get("questions", [])
            
            filtered = [q for q in all_q if q["level"] == self.level]
            random.shuffle(filtered)
            return filtered[:20]
        except Exception as e:
            print(f"Ошибка загрузки вопросов: {e}")
            return []

    def build(self) -> ft.Control:
        if not self.questions:
            self.container.content = ft.Text("Для этого уровня пока нет вопросов.")
            return self.container

        self._start_timer()
        self._show_question()
        return ft.Column(controls=[self.container], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _start_timer(self):
        def tick():
            if self.timer_running:
                self.timer_seconds += 1
                if self.timer_text is not None:
                    mins = self.timer_seconds // 60
                    secs = self.timer_seconds % 60
                    self.timer_text.value = f"⏱ {mins:02d}:{secs:02d}"
                    self.page.update()
                threading.Timer(1.0, tick).start()
        threading.Timer(1.0, tick).start()

    def _show_question(self):
        if self.current_idx >= len(self.questions):
            self._show_results()
            return

        q = self.questions[self.current_idx]

        progress_text = f"Вопрос {self.current_idx + 1} из {len(self.questions)}"
        
        self.timer_text = ft.Text(
            f"⏱ {self.timer_seconds // 60:02d}:{self.timer_seconds % 60:02d}",
            size=14, color="#5A00FF", weight=ft.FontWeight.BOLD,
        )

        answer_buttons = []
        for idx, opt in enumerate(q["options"]):
            btn = ft.Button(
                content=ft.Text(opt, size=14, text_align=ft.TextAlign.LEFT),
                bgcolor="#F8F9FA",
                color="#333333",
                width=500,
                height=50,
                on_click=lambda e, i=idx: self._on_answer(i),
            )
            answer_buttons.append(btn)

        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(progress_text, size=13, color="#666666"),
                            ft.Container(expand=True),
                            self.timer_text,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ProgressBar(value=self.current_idx / len(self.questions), bgcolor="#E9ECEF", color="#5A00FF"),
                    ft.Container(height=20),
                    ft.Text(f"Уровень L{self.level}", size=12, color="#5A00FF", weight=ft.FontWeight.BOLD),
                    ft.Text(q["question"], size=18, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(height=20),
                    ft.Column(controls=answer_buttons, spacing=10),
                ],
                spacing=10,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            padding=20,
            width=600,
            shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
        )

        self.container.content = card
        self.page.update()

    def _on_answer(self, answer_idx: int):
        q = self.questions[self.current_idx]
        is_correct = (answer_idx == q["correct"])
        
        # Записываем в историю
        self.answers_history.append({
            "question": q["question"],
            "user_answer": q["options"][answer_idx],
            "correct_answer": q["options"][q["correct"]],
            "is_correct": is_correct
        })

        if is_correct:
            self.correct_answers += 1
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Верно!", color="white"), bgcolor="#00A896", duration=1000)
        else:
            self.page.snack_bar = ft.SnackBar(ft.Text("❌ Неверно", color="white"), bgcolor="#E63946", duration=1000)
        
        self.page.snack_bar.open = True
        self.page.update()

        self.current_idx += 1
        self._show_question()

    def _show_results(self):
        self.timer_running = False

        async def save_result():
            await save_quiz_result(self.level, self.correct_answers, len(self.questions), self.timer_seconds)

        self.page.run_task(save_result)

        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60

        passed = self.correct_answers >= 15
        
        if passed:
            grade = "Тест сдан! 🏆"
            color = "#00A896"
            icon = ft.Icons.CHECK_CIRCLE
        else:
            grade = "Тест не сдан. 📚"
            color = "#E63946"
            icon = ft.Icons.CANCEL

        score_percent = int((self.correct_answers / len(self.questions)) * 100)

        # --- Собираем блок разбора ошибок ---
        review_controls = []
        for idx, item in enumerate(self.answers_history):
            if not item["is_correct"]:
                # Красная карточка для ошибки
                review_controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(f"Вопрос {idx + 1}: {item['question']}", size=14, weight=ft.FontWeight.BOLD, color="#333333"),
                                ft.Text(f"❌ Ваш ответ: {item['user_answer']}", size=13, color="#E63946"),
                                ft.Text(f"✅ Правильный ответ: {item['correct_answer']}", size=13, color="#00A896", weight=ft.FontWeight.BOLD),
                            ],
                            spacing=5,
                        ),
                        bgcolor="#FFF3F3",
                        padding=12,
                        border_radius=8,
                        width=550,
                        border=ft.Border.all(1, "#E63946")
                    )
                )

        # Если ошибок нет
        if not review_controls:
            review_controls.append(
                ft.Text("🎉 Вы ответили правильно на все вопросы!", size=14, color="#00A896", weight=ft.FontWeight.BOLD)
            )

        review_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("📝 Разбор ответов", size=16, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(height=10),
                    ft.Column(controls=review_controls, spacing=10),
                ]
            ),
            bgcolor="#F4F6F9",
            width=600,
        )

        # --- Основная карточка результата ---
        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon=icon, size=60, color=color),
                    ft.Text("Тест завершён!", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(height=10),
                    ft.Text(f"Правильных ответов: {self.correct_answers} из {len(self.questions)}", size=18),
                    ft.Text(f"Результат: {score_percent}%", size=20, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(grade, size=16, color=color, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(f"Проходной балл: 15 из 20", size=14, color="#666666"),
                    ft.Text(f"Затраченное время: {mins:02d}:{secs:02d}", size=14, color="#666666"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            padding=30,
            width=500,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000020"),
        )

        back_btn = ft.Button(
            content=ft.Text("Вернуться на главную", color="#FFFFFF"),
            bgcolor="#5A00FF",
            width=300,
            height=50,
            on_click=lambda e: self.on_back(),
        )

        # Собираем финальный экран
        self.container.content = ft.Column(
            controls=[
                card,
                ft.Container(height=20),
                review_section,
                ft.Container(height=20),
                back_btn
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START, # Начинаем сверху, чтобы можно было листать
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.update()
