# app/ui/simulator.py
#
# Симулятор входящих заявок с консолью команд.
#
# Особенности:
# - В консоли сначала выводится команда (как в реальном терминале),
#   затем её вывод.
# - На финальном экране рекомендации на светлом фоне (не сливаются).

import json
import random
import threading
from importlib import resources

import flet as ft


class SimulatorScreen:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back

        self.all_cases = self._load_cases()
        self.remaining_ids = [c["id"] for c in self.all_cases]

        self.current_case = None
        self.current_command_idx = 0

        self.timer_seconds = 0
        self.timer_running = False

        # Консольный вывод (список строк)
        self.console_lines = []

        self.container = ft.Container(expand=True)
        self.console_output = None
        self.timer_text = None

    def _load_cases(self) -> list:
        try:
            data_file = resources.files("assets").joinpath("cases_simulator.json")
            with data_file.open("r", encoding="utf-8") as f:
                return json.load(f).get("cases", [])
        except Exception as e:
            print(f"Ошибка загрузки кейсов: {e}")
            return []

    def build(self) -> ft.Control:
        self._show_next_case()
        return ft.Column(controls=[self.container], expand=True)

    # ---------- Экран 1: карточка заявки ----------

    def _show_next_case(self):
        if not self.remaining_ids:
            self.remaining_ids = [c["id"] for c in self.all_cases]

        case_id = random.choice(self.remaining_ids)
        self.remaining_ids.remove(case_id)

        case = next((c for c in self.all_cases if c["id"] == case_id), None)
        if not case:
            self.container.content = ft.Text("Ошибка: заявка не найдена.")
            self.page.update()
            return

        self.current_case = case
        self.current_command_idx = 0
        self.timer_seconds = 0
        self.timer_running = False
        self.console_lines = []

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
        return ft.Row(
            controls=[
                ft.Text(label, size=13, color="#666666", width=90),
                ft.Text(value, size=13, color="#333333", expand=True),
            ],
            spacing=5,
        )

    # ---------- Экран 2: консоль ----------

    def _start_case(self):
        self.timer_running = True
        self.current_command_idx = 0
        self.console_lines = []
        self._start_timer()
        self._show_console()

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

    def _show_console(self):
        commands = self.current_case.get("commands", [])
        if self.current_command_idx >= len(commands):
            self._show_solution()
            return

        cmd = commands[self.current_command_idx]
        if cmd.get("is_final"):
            self._show_solution()
            return

        # Текст консоли: если пусто — приглашение
        console_text = "\n".join(self.console_lines) if self.console_lines else "Microsoft Windows [Version 10.0.19045.3803]\n(c) Корпорация Майкрософт. Все права защищены.\n\nC:\\Users\\support>"

        self.console_output = ft.Text(
            value=console_text,
            size=12,
            color="#00FF00",
            font_family="Courier New",
            selectable=True,
        )

        self.timer_text = ft.Text(
            f"⏱ {self.timer_seconds // 60:02d}:{self.timer_seconds % 60:02d}",
            size=14, color="#5A00FF", weight=ft.FontWeight.BOLD,
        )

        # Кнопка текущей команды
        cmd_buttons = [
            ft.Button(
                content=ft.Text(f"▶ {cmd['name']}", size=13, color="#FFFFFF"),
                bgcolor="#333333",
                width=500,
                height=40,
                on_click=lambda e, c=cmd: self._execute_command(c),
            )
        ]

        self.interpret_container = ft.Column(controls=[], spacing=8)

        console_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(f"Заявка {self.current_case['number']}", size=13, color="#666666"),
                            ft.Container(expand=True),
                            self.timer_text,
                        ],
                    ),
                    ft.Container(height=5),
                    ft.Container(
                        content=self.console_output,
                        bgcolor="#1E1E1E",
                        border_radius=8,
                        padding=15,
                        height=250,
                    ),
                    ft.Container(height=10),
                    ft.Text("Доступные команды:", size=13, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Column(controls=cmd_buttons, spacing=8),
                    self.interpret_container,
                ],
                spacing=8,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
        )

        self.container.content = ft.Column(
            controls=[console_card],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.update()

    def _execute_command(self, cmd: dict):
        """Имитация выполнения команды: выводим команду + её результат."""
        # Добавляем в консоль "ввод" команды (как в терминале) и её вывод.
        # Формат: "C:\Users\support> <команда>" и следом вывод.
        prompt_line = f"C:\\Users\\support> {cmd['name']}"
        output = cmd.get("output", "Команда выполнена.")

        self.console_lines.append(prompt_line)
        self.console_lines.append(output)

        if self.console_output is not None:
            self.console_output.value = "\n".join(self.console_lines) + "\n\nC:\\Users\\support>"
            self.page.update()

        # Показываем вопрос-интерпретацию
        self._show_interpretation(cmd)

    def _show_interpretation(self, cmd: dict):
        question = cmd.get("question", "")
        answers = cmd.get("answers", [])

        if not question or not answers:
            self.current_command_idx += 1
            self._show_console()
            return

        answer_buttons = []
        for ans in answers:
            answer_buttons.append(
                ft.Button(
                    content=ft.Text(ans["text"], size=13, color="#333333", text_align=ft.TextAlign.LEFT),
                    bgcolor="#F8F9FA",
                    width=500,
                    height=45,
                    on_click=lambda e, a=ans: self._on_interpret(a),
                )
            )

        self.interpret_container.controls = [
            ft.Divider(height=1, color="#CED4DA"),
            ft.Text(f"❓ {question}", size=14, weight=ft.FontWeight.BOLD, color="#333333"),
            ft.Column(controls=answer_buttons, spacing=8),
        ]
        self.page.update()

    def _on_interpret(self, ans: dict):
        if ans.get("correct"):
            self.current_command_idx += 1
            self.interpret_container.controls = []
            self._show_console()
        else:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("❌ Неверно. Подумайте ещё раз.", color=ft.Colors.WHITE),
                bgcolor="#E63946",
                duration=3000,
            )
            self.page.snack_bar.open = True
            self.page.update()

    # ---------- Экран 3: решение ----------

    def _show_solution(self):
        self.timer_running = False

        commands = self.current_case.get("commands", [])
        final_cmd = None
        for c in commands:
            if c.get("is_final"):
                final_cmd = c
                break

        if not final_cmd:
            final_cmd = {"name": "Закрыть заявку", "output": "Заявка закрыта."}

        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60

        # --- Рекомендация на СВЕТЛОМ фоне (чтобы текст не сливался) ---
        final_output_text = final_cmd.get("output", "")

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
                    ft.Text("Финальный шаг:", size=14, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(
                        content=ft.Text(
                            final_output_text,
                            size=13,
                            color="#333333",          # ТЁМНЫЙ текст
                            selectable=True,
                            font_family="Courier New",
                        ),
                        padding=ft.Padding.all(12),
                        bgcolor="#F8F9FA",             # СВЕТЛЫЙ фон
                        border=ft.Border.all(1, "#CED4DA"),
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
        self.page.update()
