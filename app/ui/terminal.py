# app/ui/terminal.py
#
# Экран "Свободный терминал" (Песочница).

import random
import flet as ft

from app.core.terminal_emulator import execute_command
from app.core.storage import load_progress, save_progress
from app.core.achievements import get_all_achievements, save_achievements
from app.ui.theme_colors import text_primary, text_secondary

EXAMPLE_COMMANDS = [
    "ping 8.8.8.8",
    "ping ya.ru",
    "ipconfig",
    "ipconfig /all",
    "tracert ya.ru",
    "nslookup ya.ru",
    "netstat -an",
    "arp -a",
    "route print",
    "tasklist",
    "help",
]

IGNORED_FOR_COUNTER = {"help", "cls", ""}


class TerminalScreen:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.output_list = None  # Теперь это ListView
        self.input_field = None
        self.session_command_count = 0
        self.container = ft.Container(expand=True)

    def build(self) -> ft.Control:
        # --- Список вывода (замена TextField на ListView) ---
        self.output_list = ft.ListView(
            expand=True,
            spacing=5,
            auto_scroll=True,  # Встроенная автопрокрутка Flet
            padding=10,
        )
        
        # Добавляем приветствие
        welcome_text = (
            "Добро пожаловать в песочницу SupportDesk!\n"
            "Введите команду и нажмите Enter.\n"
            "Например: ping 8.8.8.8, ipconfig, tracert ya.ru\n"
            "Введите help — чтобы увидеть список всех команд.\n"
            "Введите cls — чтобы очистить экран.\n"
            "----------------------------------------"
        )
        self._add_text_to_console(welcome_text, "#00FF66")

        # Обертка для списка (чтобы был черный фон и рамки)
        console_container = ft.Container(
            content=self.output_list,
            bgcolor="#000000",
            border_radius=8,
            expand=True,
        )

        # --- Поле ввода ---
        self.input_field = ft.TextField(
            hint_text="Введите команду...",
            expand=True,
            autofocus=True,
            text_style=ft.TextStyle(font_family="Courier New", size=13),
            on_submit=self._on_command_submit,
        )

        # --- Кнопки ---
        run_button = ft.Button(
            content=ft.Text("Выполнить", color="#FFFFFF"),
            bgcolor="#5A00FF",
            on_click=self._on_command_submit,
        )

        copy_button = ft.IconButton(
            icon=ft.Icons.COPY,
            tooltip="Скопировать весь вывод",
            on_click=self._on_copy_click,
        )

        clear_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            tooltip="Очистить экран (cls)",
            on_click=self._on_clear_click,
        )

        random_button = ft.IconButton(
            icon=ft.Icons.CASINO,
            tooltip="Случайная команда",
            on_click=self._on_random_click,
        )

        back_button = ft.TextButton(
            content=ft.Text("← Назад"),
            on_click=self._on_back_click,
        )

        # --- Чипы-примеры ---
        chips_row = ft.Row(
            controls=[self._make_chip(cmd) for cmd in EXAMPLE_COMMANDS],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
        )

        # --- Предупреждение ---
        warning = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#E63946", size=18),
                    ft.Text(
                        "Это тренажёр. Команды выполняются в песочнице, реальные сетевые запросы не отправляются.",
                        size=11,
                        color=text_secondary(self.page),
                        expand=True,
                    ),
                ],
                spacing=8,
            ),
            padding=8,
            bgcolor=("#FFF3CD" if self.page.theme_mode != ft.ThemeMode.DARK else "#3D3D1C"),
            border_radius=8,
        )

        input_row = ft.Row(controls=[self.input_field, run_button], spacing=8)
        bottom_row = ft.Row(controls=[back_button, random_button, copy_button, clear_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.container.content = ft.Column(
            controls=[
                warning,
                console_container,  # Теперь здесь контейнер со списком
                chips_row,
                input_row,
                bottom_row,
            ],
            spacing=10,
            expand=True,
        )
        self.container.padding = 10
        self.container.expand = True

        self.page.run_task(self._load_counter)

        return self.container

    def _add_text_to_console(self, text: str, color: str = "#00FF66"):
        """Добавляет текст в ListView."""
        if self.output_list is not None:
            self.output_list.controls.append(
                ft.Text(text, size=13, color=color, font_family="Courier New", selectable=True)
            )
            # Принудительная прокрутка вниз после добавления
            self.output_list.auto_scroll = True
            self.page.update()

    def _make_chip(self, command: str) -> ft.Control:
        return ft.Container(
            content=ft.Text(command, size=12, font_family="Courier New", color=text_primary(self.page)),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            bgcolor=ft.Colors.with_opacity(0.1, "#5A00FF"),
            border_radius=16,
            on_click=lambda e, c=command: self._on_chip_click(c),
            ink=True,
        )

    async def _load_counter(self):
        try:
            progress = await load_progress()
            self.session_command_count = int(progress.get("__cmd_master_count__", 0))
        except Exception as e:
            print(f"Ошибка загрузки счётчика: {e}")
            self.session_command_count = 0

    def _on_chip_click(self, command: str):
        if self.input_field is not None:
            self.input_field.value = command
            self.page.update()

    def _on_random_click(self, e):
        if self.input_field is not None:
            self.input_field.value = random.choice(EXAMPLE_COMMANDS)
            self.page.update()

    def _on_copy_click(self, e):
        if self.output_list is not None:
            # Собираем весь текст из Text-компонентов списка
            full_text = "\n".join([ctrl.value for ctrl in self.output_list.controls if isinstance(ctrl, ft.Text)])
            self.page.set_clipboard(full_text)
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Вывод скопирован в буфер обмена"),
                duration=1500,
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _on_clear_click(self, e):
        self._clear_output()

    def _on_back_click(self, e):
        if self.on_back is not None:
            self.on_back()

    def _clear_output(self):
        if self.output_list is not None:
            self.output_list.controls.clear()
            self._add_text_to_console("----------------------------------------")

    def _on_command_submit(self, e):
        if self.input_field is None or self.output_list is None:
            return

        command = (self.input_field.value or "").strip()
        if not command:
            return

        if command.lower() == "cls":
            self.input_field.value = ""
            self._clear_output()
            return

        # Добавляем эхо команды в консоль (белым цветом)
        self._add_text_to_console(f"\n> {command}", "#FFFFFF")

        try:
            result = execute_command(command)
        except Exception as error:
            result = f"Ошибка эмулятора: {error}"

        # Добавляем результат (зеленым)
        self._add_text_to_console(result)

        self.input_field.value = ""
        self.page.update()

        if command.lower() not in IGNORED_FOR_COUNTER:
            self.page.run_task(self._increment_counter)

    async def _increment_counter(self):
        try:
            progress = await load_progress()
            count = int(progress.get("__cmd_master_count__", 0)) + 1
            progress["__cmd_master_count__"] = count

            earned = progress.get("__achievements__", [])
            earned_ids = [a["id"] for a in earned]
            new_achievements = []

            if count >= 10 and "cmd_master" not in earned_ids:
                for ach in get_all_achievements():
                    if ach["id"] == "cmd_master":
                        new_achievements.append(ach)
                        break

            if new_achievements:
                progress = await save_achievements(progress, new_achievements)

            await save_progress(progress)
            self.session_command_count = count

            if new_achievements:
                names = ", ".join([f"{a['icon']} {a['title']}" for a in new_achievements])
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"🏆 Получено достижение: {names}", color=ft.Colors.WHITE),
                    bgcolor="#5A00FF",
                    duration=2500,
                )
                self.page.snack_bar.open = True
                self.page.update()

        except Exception as e:
            print(f"Ошибка счётчика: {e}")
