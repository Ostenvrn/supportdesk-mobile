# app/ui/simulator.py
#
# Экран "Тренажёр" — симулятор входящих заявок.
#
# Логика:
# 1. Загружаем пул заявок (15 штук).
# 2. Выбираем случайную, не повторяя уже пройденные.
# 3. Показываем карточку заявки (как в CRM).
# 4. Кнопка "Взять в работу" → начинаем таймер.
# 5. Пошагово задаём вопросы. При ошибке — возврат к тому же шагу.
# 6. В конце — решение, таймер останавливается, заявка считается пройденной.

import json
import random
from importlib import resources

import flet as ft


class SimulatorScreen:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back

        # Загружаем кейсы
        self.all_cases = self._load_cases()

        # Пул непройденных (пока просто копия, потом можно сохранять в SharedPreferences)
        self.remaining_ids = [c["id"] for c in self.all_cases]

        # Текущий кейс и шаг
        self.current_case = None
        self.current_step = None
        self.current_step_idx = 0

        # Таймер (секунды)
        self.timer_seconds = 0
        self.timer_running = False

        # Контейнер для контента
        self.container = ft.Container(expand=True)

    def _load_cases(self) -> list:
        """Загружает кейсы из assets/cases_simulator.json."""
        try:
            data_file = resources.files("assets").joinpath("cases_simulator.json")
            with data_file.open("r", encoding="utf-8") as f:
                return json.load(f).get("cases", [])
        except Exception as e:
            print(f"Ошибка загрузки кейсов: {e}")
            return []

    def build(self) -> ft.Control:
        """Корневой контрол экрана."""
        self._show_next_case()
        return ft.Column(controls=[self.container], expand=True)

    # ---------- Экран 1: карточка заявки ----------

    def _show_next_case(self):
        """Берёт случайную непройденную заявку и показывает её карточку."""
        # Если пул пуст — сбрасываем
        if not self.remaining_ids:
            self.remaining_ids = [c["id"] for c in self.all_cases]

        # Случайная заявка из пула
        case_id = random.choice(self.remaining_ids)
        self.remaining_ids.remove(case_id)

        # Находим кейс по id
        case = next((c for c in self.all_cases if c["id"] == case_id), None)
        if not case:
            self.container.content = ft.Text("Ошибка: заявка не найдена.")
            self.page.update()
            return

        self.current_case = case
        self.current_step_idx = 0
        self.timer_seconds = 0
        self.timer_running = False

        # Карточка заявки (как в CRM)
        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon=ft.Icons.ASSIGNMENT, color="#5A00FF", size=28),
                            ft.Text(f"Заявка {case['number']}", size=18, weight=ft.FontWeight.BOLD, color="#333333"),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=1, color="#CED4DA"),
                    self._row_info("Источник:", case.get("source", "—")),
                    self._row_info("Абонент:", case["subscriber"].get("name", "—")),
                    self._row_info("Адрес:", case["subscriber"].get("address", "—")),
                    self._row_info("Тариф:", case["subscriber"].get("tariff", "—")),
                    ft.Divider(height=1, color="#CED4DA"),
                    ft.Text("Жалоба:", size=14, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(
                        content=ft.Text(case["complaint"], size=14, color="#333333", selectable=True),
                        padding=ft.Padding.all(12),
                        bgcolor="#F8F9FA",
                        border_radius=8,
                    ),
                ],
                spacing=8,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
        )

        # Кнопка "Взять в работу"
        take_btn = ft.Button(
            content=ft.Text("Взять в работу →", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
            bgcolor="#5A00FF",
            width=300,
            height=50,
            on_click=lambda e: self._start_case(),
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Входящая заявка", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                ft.Container(height=10),
                card,
                ft.Container(height=20),
                ft.Row(controls=[take_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.update()

    def _row_info(self, label: str, value: str) -> ft.Control:
        """Строка "Метка: Значение"."""
        return ft.Row(
            controls=[
                ft.Text(label, size=13, color="#666666", width=90),
                ft.Text(value, size=13, color="#333333", expand=True),
            ],
            spacing=5,
        )

    # ---------- Экран 2: диагностика ----------

    def _start_case(self):
        """Начинаем прохождение заявки."""
        self.timer_running = True
        self.current_step_idx = 0
        self._start_timer()
        self._show_step()

    def _start_timer(self):
        """Запускаем таймер (обновляем каждую секунду)."""
        def tick():
            if self.timer_running:
                self.timer_seconds += 1
                # Обновляем индикатор времени
                if hasattr(self, "timer_text"):
                    mins = self.timer_seconds // 60
                    secs = self.timer_seconds % 60
                    self.timer_text.value = f"⏱ {mins:02d}:{secs:02d}"
                    self.page.update()
                # Планируем следующий тик
                import threading
                threading.Timer(1.0, tick).start()

        import threading
        threading.Timer(1.0, tick).start()

    def _show_step(self):
        """Показывает текущий шаг диагностики."""
        steps = self.current_case.get("steps", [])
        if self.current_step_idx >= len(steps):
            self._show_solution()
            return

        step = steps[self.current_step_idx]
        self.current_step = step

        # Если шаг содержит "solution" — это финал
        if "solution" in step:
            self._show_solution()
            return

        # Заголовок + индикатор прогресса
        total = len(steps) - 1  # последний шаг — solution
        progress_text = f"Шаг {self.current_step_idx + 1} из {max(total, 1)}"

        # Индикатор времени
        self.timer_text = ft.Text(f"⏱ {self.timer_seconds // 60:02d}:{self.timer_seconds % 60:02d}", size=14, color="#5A00FF", weight=ft.FontWeight.BOLD)

        # Вопрос
        question_text = ft.Text(step["question"], size=16, weight=ft.FontWeight.BOLD, color="#333333")

        # Варианты ответов
        options_controls = []
        for opt in step.get("options", []):
            options_controls.append(self._make_option_button(opt))

        # Карточка шага
        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(f"Заявка {self.current_case['number']}", size=13, color="#666666"),
                            ft.Container(expand=True),
                            self.timer_text,
                        ],
                    ),
                    ft.ProgressBar(value=self.current_step_idx / max(total, 1), bgcolor="#E9ECEF", color="#5A00FF"),
                    ft.Text(progress_text, size=12, color="#666666"),
                    ft.Container(height=10),
                    question_text,
                    ft.Container(height=15),
                    ft.Column(controls=options_controls, spacing=10),
                ],
                spacing=8,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
        )

        self.container.content = ft.Column(controls=[card], expand=True, scroll=ft.ScrollMode.AUTO)
        self.page.update()

    def _make_option_button(self, opt: dict) -> ft.Control:
        """Кнопка варианта ответа с обработкой правильно/неправильно."""
        btn = ft.Button(
            content=ft.Text(opt["text"], size=14, color="#333333", text_align=ft.TextAlign.LEFT),
            bgcolor="#F8F9FA",
            width=500,
            height=50,
            on_click=lambda e: self._on_answer(opt),
        )
        return btn

    def _on_answer(self, opt: dict):
        """Обработка ответа."""
        if opt.get("correct"):
            # Правильно — идём дальше
            self.current_step_idx += 1
            self._show_step()
        else:
            # Неправильно — показываем объяснение и остаёмся на шаге
            explanation = opt.get("explanation", "Неверный ответ.")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ {explanation}", color=ft.Colors.WHITE),
                bgcolor="#E63946",
                duration=4000,
            )
            self.page.snack_bar.open = True
            self.page.update()

    # ---------- Экран 3: решение ----------

    def _show_solution(self):
        """Показывает финальное решение и останавливает таймер."""
        self.timer_running = False

        # Ищем последний шаг с solution
        steps = self.current_case.get("steps", [])
        solution_step = None
        for step in steps:
            if "solution" in step:
                solution_step = step
                break

        if not solution_step:
            solution_step = {"solution": "Решение не найдено.", "recommendation": ""}

        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60

        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon=ft.Icons.CHECK_CIRCLE, color="#00A896", size=36),
                            ft.Text("Заявка закрыта!", size=20, weight=ft.FontWeight.BOLD, color="#333333"),
                        ],
                        spacing=10,
                    ),
                    ft.Text(f"Заявка {self.current_case['number']}", size=13, color="#666666"),
                    ft.Text(f"Время решения: {mins:02d}:{secs:02d}", size=14, color="#5A00FF", weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color="#CED4DA"),
                    ft.Text("Решение:", size=14, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Text(solution_step.get("solution", ""), size=14, color="#333333", selectable=True),
                    ft.Container(height=10),
                    ft.Text("Рекомендация:", size=14, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(
                        content=ft.Text(solution_step.get("recommendation", ""), size=14, color="#0056B3", selectable=True),
                        padding=ft.Padding.all(12),
                        bgcolor="#E7F1FF",
                        border_radius=8,
                    ),
                ],
                spacing=8,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
        )

        next_btn = ft.Button(
            content=ft.Text("Следующая заявка →", color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD),
            bgcolor="#5A00FF",
            width=300,
            height=50,
            on_click=lambda e: self._show_next_case(),
        )

        back_btn = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color="#5A00FF"),
                    ft.Text("На главную", color="#5A00FF", size=14),
                ],
                spacing=5,
            ),
            on_click=lambda e: self.on_back(),
        )

        self.container.content = ft.Column(
            controls=[
                card,
                ft.Container(height=20),
                ft.Row(controls=[next_btn], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.update()# app/ui/simulator.py
#
# Экран "Трена
