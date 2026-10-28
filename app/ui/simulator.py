# app/ui/simulator.py

import json
import random
import threading
from importlib import resources

import flet as ft
from app.core.storage import load_progress, save_progress
from app.core.achievements import check_achievements, save_achievements
from app.ui.theme_colors import (
    text_primary, text_secondary, text_accent, text_error, 
    bg_card, bg_card_alt, border_color
)


class SimulatorScreen:
    def __init__(self, page: ft.Page, on_back, level: int = 1, is_advanced: bool = False):
        self.page = page
        self.on_back = on_back
        self.level = level
        self.is_advanced = is_advanced

        self.all_cases = self._load_all_cases()
        if self.is_advanced:
            self.all_cases = [c for c in self.all_cases if c.get("advanced")]
        else:
            self.all_cases = [c for c in self.all_cases if not c.get("advanced")]
        self.all_cases = [c for c in self.all_cases if c.get("level") == self.level]

        self.remaining_ids = [c["id"] for c in self.all_cases]
        self.current_case = None
        self.current_command_idx = 0
        self.timer_seconds = 0
        self.timer_running = False
        self.console_logs = []
        self.errors_count = 0

        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
        self.console_list = None
        self.timer_text = None

    def _load_all_cases(self) -> list:
        cases = []
        try:
            data_file = resources.files("assets").joinpath("cases_simulator.json")
            with data_file.open("r", encoding="utf-8") as f:
                cases.extend(json.load(f).get("cases", []))
        except Exception as e:
            print(f"Ошибка загрузки основного файла: {e}")
        try:
            extra_file = resources.files("assets").joinpath("cases_advanced_batch.json")
            with extra_file.open("r", encoding="utf-8") as f:
                cases.extend(json.load(f).get("cases", []))
        except Exception:
            pass
        return cases

    def build(self) -> ft.Control:
        self._show_next_case()
        return ft.Column(controls=[self.container], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _show_next_case(self):
        if not self.remaining_ids:
            self.remaining_ids = [c["id"] for c in self.all_cases]

        if not self.remaining_ids:
            self.container.content = ft.Column(
                controls=[
                    ft.Icon(ft.Icons.INFO, size=50, color="orange"),
                    ft.Text(f"Нет заявок для уровня L{self.level} в этом режиме.", size=18, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                    ft.Button("Назад", on_click=lambda e: self.on_back())
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            )
            self.page.update()
            return

        case_id = random.choice(self.remaining_ids)
        self.remaining_ids.remove(case_id)

        case = next((c for c in self.all_cases if c["id"] == case_id), None)
        if not case:
            self.container.content = ft.Text("Ошибка: заявка не найдена.", color=text_error(self.page))
            self.page.update()
            return

        self.current_case = case
        self.current_command_idx = 0
        self.timer_seconds = 0
        self.timer_running = False
        self.console_logs = []
        self.errors_count = 0

        mode_text = f"Уровень L{self.level} | " + ("Продвинутый режим" if self.is_advanced else "Обычный режим")

        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(mode_text, size=12, color=text_secondary(self.page), weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            ft.Icon(icon=ft.Icons.ASSIGNMENT, color=text_accent(self.page), size=28),
                            ft.Text(f"Заявка {case['number']}", size=18, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=border_color(self.page)),
                    self._row_info("Источник:", case.get("source", "—")),
                    self._row_info("Абонент:", case["subscriber"].get("name", "—")),
                    self._row_info("Адрес:", case["subscriber"].get("address", "—")),
                    self._row_info("Тариф:", case["subscriber"].get("tariff", "—")),
                    ft.Divider(height=1, color=border_color(self.page)),
                    ft.Text("Жалоба:", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                    ft.Container(
                        content=ft.Text(case["complaint"], size=14, color=text_primary(self.page), selectable=True),
                        padding=ft.Padding.all(12),
                        bgcolor=bg_card_alt(self.page),
                        border_radius=8,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=bg_card(self.page),
            border_radius=14,
            padding=20,
            width=600,
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
                ft.Text("Входящая заявка", size=22, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                ft.Container(height=10),
                card,
                ft.Container(height=20),
                ft.Row(controls=[take_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()

    def _row_info(self, label: str, value: str) -> ft.Control:
        return ft.Row(
            controls=[
                ft.Text(label, size=13, color=text_secondary(self.page), width=90),
                ft.Text(value, size=13, color=text_primary(self.page), expand=True),
            ],
            spacing=5,
        )

    def _start_case(self):
        self.timer_running = True
        self.current_command_idx = 0
        self.console_logs = []
        self.errors_count = 0
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

    def _add_console_line(self, text: str, color: str = "#00FF00"):
        self.console_logs.append(ft.Text(text, size=12, color=color, font_family="Courier New", selectable=True))
        if self.console_list:
            self.console_list.controls.append(self.console_logs[-1])
            self.page.update()

    def _show_ticket_info(self, e):
        case = self.current_case
        if not case:
            return

        billing = case.get("billing", {})
        ip = billing.get("ip", "Не назначен")
        session = billing.get("session_status", "Неизвестно")
        balance = billing.get("balance", "0.00 руб.")
        services = billing.get("services", "—")

        crm_content = ft.Column(
            controls=[
                ft.Text("💳 Биллинг / CRM", size=18, weight=ft.FontWeight.BOLD, color=text_accent(self.page)),
                ft.Divider(color=border_color(self.page)),
                self._row_info("IP-адрес:", ip),
                self._row_info("Сессия:", session),
                self._row_info("Баланс:", balance),
                self._row_info("Услуги:", services),
            ],
            spacing=10,
        )

        def open_crm(e):
            self.page.pop_dialog()
            crm_dialog = ft.AlertDialog(
                title=ft.Text("CRM: Личный кабинет абонента", color=text_primary(self.page)),
                content=ft.Container(content=crm_content, width=400, padding=10, bgcolor=bg_card(self.page)),
                bgcolor=bg_card(self.page),
                actions=[ft.TextButton("Закрыть", on_click=lambda _: self.page.pop_dialog())],
            )
            self.page.show_dialog(crm_dialog)

        bs = ft.BottomSheet(
            ft.Container(
                padding=20,
                bgcolor=bg_card(self.page),
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(icon=ft.Icons.ASSIGNMENT, color=text_accent(self.page)),
                                ft.Text(f"Заявка {case['number']}", size=18, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                            ],
                        ),
                        ft.Divider(color=border_color(self.page)),
                        ft.Text(f"Абонент: {case['subscriber'].get('name', '—')}", size=14, color=text_primary(self.page)),
                        ft.Text(f"Адрес: {case['subscriber'].get('address', '—')}", size=14, color=text_primary(self.page)),
                        ft.Text(f"Тариф: {case['subscriber'].get('tariff', '—')}", size=14, color=text_primary(self.page)),
                        ft.Divider(color=border_color(self.page)),
                        ft.Text("Жалоба:", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                        ft.Text(case["complaint"], size=14, color=text_primary(self.page)),
                        ft.Container(height=20),
                        ft.Row(
                            controls=[
                                ft.Button("Посмотреть CRM", icon=ft.Icons.STOREFRONT, bgcolor="#00A896", color=ft.Colors.WHITE, on_click=open_crm),
                                ft.Button("Закрыть", bgcolor="#555555", color=ft.Colors.WHITE, on_click=lambda _: self.page.pop_dialog())
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO
                )
            ),
            open=True,
        )
        self.page.show_dialog(bs)

    def _show_console(self):
        commands = self.current_case.get("commands", [])
        if self.current_command_idx >= len(commands):
            self._show_solution()
            return

        cmd = commands[self.current_command_idx]
        if cmd.get("is_final"):
            self._show_solution()
            return

        self.console_list = ft.ListView(expand=True, spacing=5, auto_scroll=True)

        if not self.console_logs:
            self.console_logs.append(ft.Text("Microsoft Windows [Version 10.0.19045.3803]", size=12, color="#00FF00", font_family="Courier New"))
            self.console_logs.append(ft.Text("(c) Корпорация Майкрософт. Все права защищены.\n", size=12, color="#00FF00", font_family="Courier New"))
        
        for log in self.console_logs:
            self.console_list.controls.append(log)

        self.timer_text = ft.Text(
            f"⏱ {self.timer_seconds // 60:02d}:{self.timer_seconds % 60:02d}",
            size=14, color=text_accent(self.page), weight=ft.FontWeight.BOLD,
        )

        controls_panel = []

        if self.is_advanced:
            cmd_input = ft.TextField(
                hint_text="Введите команду (например: ping 8.8.8.8)",
                expand=True,
                bgcolor="#2D2D2D",
                color="#FFFFFF",
                border_color="#555555",
                height=45,
                text_style=ft.TextStyle(font_family="Courier New", size=13),
            )

            def submit_cmd(e):
                user_cmd = cmd_input.value.strip()
                if not user_cmd:
                    return
                
                if user_cmd == cmd["name"]:
                    self._execute_command(cmd)
                    cmd_input.value = ""
                    self.page.update()
                else:
                    self._add_console_line(f"C:\\Users\\support> {user_cmd}", color="#FFFFFF")
                    self._add_console_line("Команда не распознана или неверна для этой ситуации.", color="#FF5555")
                    self.errors_count += 1
                    cmd_input.value = ""
                    self.page.update()

            cmd_input.on_submit = submit_cmd
            
            controls_panel.append(
                ft.Row(
                    controls=[
                        ft.Text(">", size=16, color="#FFFFFF", font_family="Courier New"),
                        cmd_input
                    ],
                    spacing=5,
                )
            )
            controls_panel.append(ft.Text(f"Подсказка: проверьте логи и введите нужную команду.", size=12, italic=True, color=text_secondary(self.page)))
        else:
            cmd_btn = ft.Button(
                content=ft.Text(f"▶ Выполнить: {cmd['name']}", size=13, color="#FFFFFF"),
                bgcolor="#333333",
                width=500,
                height=40,
                on_click=lambda e, c=cmd: self._execute_command(c),
            )
            controls_panel.append(
                ft.Column(
                    controls=[
                        ft.Text(f"Доступная команда:", size=13, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                        cmd_btn
                    ],
                    spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        self.interpret_container = ft.Column(controls=[], spacing=8)
        self.interpret_buttons = []

        top_panel = ft.Row(
            controls=[
                ft.Text(f"Заявка {self.current_case['number']}", size=13, color=text_secondary(self.page)),
                ft.TextButton(
                    "Посмотреть заявку",
                    icon=ft.Icons.VISIBILITY,
                    style=ft.ButtonStyle(color=text_accent(self.page)),
                    on_click=self._show_ticket_info
                ),
                ft.Container(expand=True),
                self.timer_text,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        console_card = ft.Container(
            content=ft.Column(
                controls=[
                    top_panel,
                    ft.Container(height=5),
                    ft.Container(
                        content=self.console_list,
                        bgcolor="#1E1E1E",
                        border_radius=8,
                        padding=15,
                        height=200,
                        width=600,
                    ),
                    ft.Container(height=10),
                    ft.Column(controls=controls_panel, spacing=10),
                    self.interpret_container,
                ],
                spacing=8,
            ),
            bgcolor=bg_card(self.page),
            border_radius=14,
            padding=20,
            width=650,
            shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
        )

        self.container.content = ft.Column(
            controls=[console_card],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()

    def _execute_command(self, cmd: dict):
        prompt_line = f"C:\\Users\\support> {cmd['name']}"
        output = cmd.get("output", "Команда выполнена.")

        self._add_console_line(prompt_line, color="#FFFFFF")
        self._add_console_line(output)

        if not self.is_advanced:
            explanation = cmd.get("explanation", "")
            if explanation:
                self._show_interpretation(cmd, explanation)
            else:
                self._show_interpretation(cmd, None)
        else:
            self.current_command_idx += 1
            self.page.update()
            self._show_console()

    def _show_interpretation(self, cmd: dict, explanation: str):
        question = cmd.get("question", "")
        answers = cmd.get("answers", [])

        controls = []
        
        if explanation:
            controls.append(
                ft.Container(
                    content=ft.Text(f"💡 {explanation}", size=13, color=text_primary(self.page), selectable=True),
                    padding=ft.Padding.all(10),
                    bgcolor=bg_card_alt(self.page),
                    border_radius=8,
                    width=500
                )
            )

        if question and answers:
            answer_buttons = []
            for ans in answers:
                btn = ft.Button(
                    content=ft.Text(ans["text"], size=13, color=text_primary(self.page), text_align=ft.TextAlign.LEFT),
                    bgcolor=bg_card_alt(self.page),
                    width=500,
                    height=40,
                    on_click=lambda e, a=ans: self._on_interpret(a, e.control),
                )
                answer_buttons.append(btn)

            controls.append(
                ft.Column(
                    controls=[
                        ft.Text(f"❓ {question}", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                        ft.Column(controls=answer_buttons, spacing=8),
                    ],
                    spacing=8
                )
            )
        else:
            if answers:
                pass
            else:
                next_btn = ft.Button(
                    content=ft.Text("Продолжить →", color=ft.Colors.WHITE),
                    bgcolor="#5A00FF",
                    width=200,
                    on_click=lambda e: self._next_step()
                )
                controls.append(ft.Row([next_btn], alignment=ft.MainAxisAlignment.CENTER))

        self.interpret_container.controls = [
            ft.Divider(height=1, color=border_color(self.page)),
        ] + controls
        self.page.update()

    def _next_step(self):
        self.current_command_idx += 1
        self.interpret_container.controls = []
        self._show_console()

    def _on_interpret(self, ans: dict, button: ft.Control):
        if ans.get("correct"):
            self.current_command_idx += 1
            self.interpret_container.controls = []
            self._show_console()
        else:
            self.errors_count += 1
            button.bgcolor = "#E63946"
            button.content.color = ft.Colors.WHITE
            self.page.update()

    def _show_solution(self):
        self.timer_running = False

        commands = self.current_case.get("commands", [])
        final_cmd = None
        for c in commands:
            if c.get("is_final"):
                final_cmd = c
                break

        if not final_cmd:
            final_cmd = {"name": "close_ticket", "output": "Заявка закрыта."}

        async def save_result_and_check_achievements():
            progress = await load_progress()
            
            progress[self.current_case["id"]] = {
                "status": "passed",
                "time": self.timer_seconds,
                "number": self.current_case["number"],
                "topic": self.current_case["topic"],
                "no_errors": self.errors_count == 0
            }
            
            new_achievements = await check_achievements(
                progress, 
                self.current_case, 
                self.timer_seconds,
                self.errors_count
            )
            
            if new_achievements:
                progress = await save_achievements(progress, new_achievements)
                self.new_achievements_to_show = new_achievements
            else:
                self.new_achievements_to_show = []
            
            await save_progress(progress)
            
            if self.new_achievements_to_show:
                ach_names = ", ".join([f"{a['icon']} {a['title']}" for a in self.new_achievements_to_show])
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"🏆 Получены достижения: {ach_names}", color=ft.Colors.WHITE),
                    bgcolor="#5A00FF",
                    duration=2000, # 2 секунды
                )
                self.page.snack_bar.open = True
                self.page.update()

        self.page.run_task(save_result_and_check_achievements)

        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60

        final_output_text = final_cmd.get("output", "")
        explanation = final_cmd.get("explanation", "")

        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon=ft.Icons.CHECK_CIRCLE, color="#00A896", size=36),
                            ft.Text("Заявка закрыта!", size=20, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Text(f"Заявка {self.current_case['number']}", size=13, color=text_secondary(self.page)),
                    ft.Text(f"Время решения: {mins:02d}:{secs:02d}", size=14, color=text_accent(self.page), weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color=border_color(self.page)),
                    ft.Text("Финальный шаг:", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                    ft.Container(
                        content=ft.Text(
                            final_output_text,
                            size=13,
                            color=text_primary(self.page),
                            selectable=True,
                            font_family="Courier New",
                        ),
                        padding=ft.Padding.all(12),
                        bgcolor=bg_card_alt(self.page),
                        border=ft.Border.all(1, border_color(self.page)),
                        border_radius=8,
                        width=550,
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Text(
                            f"💡 {explanation}" if explanation else "",
                            size=13,
                            color=text_primary(self.page),
                            selectable=True,
                        ),
                        padding=ft.Padding.all(10),
                        bgcolor=bg_card_alt(self.page),
                        border_radius=8,
                        width=550,
                        visible=bool(explanation)
                    ),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=bg_card(self.page),
            border_radius=14,
            padding=20,
            width=600,
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
                    ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(self.page)),
                    ft.Text("На главную", color=text_accent(self.page), size=14),
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
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()
