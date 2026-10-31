# main.py
#
# Точка входа SupportDesk Mobile (Flet 1.0.5).

import flet as ft
import flet.canvas as cv

import app.state as state
from app.core.storage import load_profile, save_profile, load_theme, load_progress
from app.ui.screens import KnowledgeScreen, SimulatorSelectionScreen, QuizSelectionScreen
from app.ui.simulator import SimulatorScreen
from app.ui.progress import ProgressScreen
from app.ui.profile import ProfileScreen
from app.ui.about import AboutScreen
from app.ui.quiz import QuizScreen
from app.ui.terminal import TerminalScreen
from app.ui.theme_colors import (
    text_primary, text_secondary, text_accent, text_error, bg_primary, bg_card, bg_card_alt
)


def build_logo(size: int = 80, page: ft.Page = None) -> ft.Control:
    s = size
    accent = text_accent(page) if page else "#5A00FF"
    bg = bg_card(page) if page else "#FFFFFF"
    
    return ft.Stack(width=s, height=s, controls=[
        ft.Container(width=s, height=s, border_radius=s // 2, bgcolor=accent, opacity=0.12),
        ft.Container(width=s * 0.7, height=s * 0.75, left=s * 0.15, top=s * 0.08, bgcolor=bg, border=ft.Border.all(3, accent), border_radius=ft.BorderRadius.only(top_left=(s * 0.7) // 2, top_right=(s * 0.7) // 2, bottom_left=(s * 0.7) // 2, bottom_right=(s * 0.7) // 2)),
        ft.Container(width=s * 0.15, height=s * 0.15, left=s * 0.425, top=s * 0.35, border_radius=(s * 0.15) // 2, bgcolor=accent),
        ft.Container(width=s * 0.2, height=2, left=s * 0.22, top=s * 0.42, bgcolor=accent),
        ft.Container(width=s * 0.2, height=2, left=s * 0.58, top=s * 0.42, bgcolor=accent),
        ft.Container(width=2, height=s * 0.2, left=s * 0.49, top=s * 0.48, bgcolor=accent),
        ft.Container(width=s * 0.1, height=s * 0.1, left=s * 0.2, top=s * 0.38, border_radius=(s * 0.1) // 2, bgcolor=accent),
        ft.Container(width=s * 0.1, height=s * 0.1, left=s * 0.7, top=s * 0.38, border_radius=(s * 0.1) // 2, bgcolor=accent),
        ft.Container(width=s * 0.1, height=s * 0.1, left=s * 0.45, top=s * 0.65, border_radius=(s * 0.1) // 2, bgcolor=accent),
    ])


def build_background() -> ft.Control:
    nodes = [(30, 40), (110, 20), (190, 80), (280, 30), (370, 100), (450, 50), (50, 170), (140, 230), (230, 160), (320, 240), (410, 170), (480, 220), (20, 310), (100, 380), (200, 320), (290, 400), (380, 320), (460, 390), (60, 470), (150, 530), (250, 480), (340, 550), (420, 470), (490, 540), (40, 600), (130, 660), (230, 610), (320, 670), (410, 600), (480, 660)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (6, 12), (7, 13), (8, 14), (9, 15), (10, 16), (11, 17), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (12, 18), (13, 19), (14, 20), (15, 21), (16, 22), (17, 23), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23), (18, 24), (19, 25), (20, 26), (21, 27), (22, 28), (23, 29), (24, 25), (25, 26), (26, 27), (27, 28), (28, 29)]
    shapes = []
    for a, b in edges:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        shapes.append(cv.Line(x1=x1, y1=y1, x2=x2, y2=y2, paint=ft.Paint(color="#5A00FF", stroke_width=1, style=ft.PaintingStyle.STROKE)))
    for (x, y) in nodes:
        shapes.append(cv.Circle(x=x, y=y, radius=5, paint=ft.Paint(color="#5A00FF", style=ft.PaintingStyle.FILL)))
        shapes.append(cv.Circle(x=x, y=y, radius=12, paint=ft.Paint(color="#5A00FF", stroke_width=0.5, style=ft.PaintingStyle.STROKE)))
    return ft.Stack(controls=[ft.Container(content=cv.Canvas(shapes=shapes, width=520, height=700), opacity=0.10)], expand=True)


async def main(page: ft.Page):
    page.title = "SupportDesk Mobile"
    
    # --- НАСТРОЙКА СОВРЕМЕННОЙ ТЕМЫ ---
    page.fonts = {
        "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
    }
    page.theme = ft.Theme(
        font_family="Inter",
        color_scheme=ft.ColorScheme(primary="#5A00FF", secondary="#00A896"),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.dark_theme = ft.Theme(
        font_family="Inter",
        color_scheme=ft.ColorScheme(primary="#B388FF", secondary="#69DB7C"),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    is_dark = await load_theme()
    if is_dark:
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = bg_primary(page)
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = bg_primary(page)

    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    saved_name = await load_profile()
    if saved_name:
        state.profile_name = saved_name
        state.profile_created = True

    switcher = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=300, reverse_duration=300,
        switch_in_curve=ft.AnimationCurve.EASE_IN,
        switch_out_curve=ft.AnimationCurve.EASE_OUT,
        expand=True,
    )

    def set_screen(control: ft.Control):
        switcher.content = control
        page.update()

    def show_profile_screen():
        name_input = ft.TextField(
            label="Ваше имя", hint_text="Например, Александр", width=300, autofocus=True,
            border=ft.InputBorder.OUTLINE, color=text_primary(page), label_style=ft.TextStyle(color=text_secondary(page)),
        )

        async def save_and_continue(e):
            name = name_input.value.strip() if name_input.value else ""
            if not name:
                name_input.error_text = "Введите имя"
                page.update()
                return
            state.profile_name = name
            state.profile_created = True
            await save_profile(name)
            page.run_task(show_main_screen)

        save_btn = ft.Button(
            content=ft.Text("Сохранить и продолжить", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), 
            bgcolor="#5A00FF", on_click=save_and_continue, width=300, height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )

        screen = ft.Column(
            controls=[
                build_logo(100, page),
                ft.Text("SupportDesk Mobile", size=28, weight=ft.FontWeight.BOLD, color=text_accent(page)),
                ft.Text("Твой помощник в поддержке", size=14, color=text_secondary(page)),
                ft.Container(height=20), name_input, ft.Container(height=10), save_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5, expand=True, alignment=ft.MainAxisAlignment.CENTER,
        )
        set_screen(screen)

    async def show_main_screen():
        progress = await load_progress()
        solved_count = len([k for k in progress.keys() if not k.startswith("__")])

        def open_section(section: str):
            try:
                if section == "Справочник":
                    body = KnowledgeScreen(page).build()
                    back_btn = ft.TextButton(
                        content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("На главную", color=text_accent(page), size=14)], spacing=5),
                        on_click=lambda e: page.run_task(show_main_screen)
                    )
                    set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))

                elif section == "Тренажёры":
                    def start_sim(level: int, is_advanced: bool):
                        sim = SimulatorScreen(page, on_back=lambda: page.run_task(show_main_screen), level=level, is_advanced=is_advanced)
                        body = sim.build()
                        back_btn = ft.TextButton(
                            content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("К выбору тренажёра", color=text_accent(page), size=14)], spacing=5),
                            on_click=lambda e: open_section("Тренажёры")
                        )
                        set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))
                    
                    def start_terminal():
                        term = TerminalScreen(page, on_back=lambda: open_section("Тренажёры"))
                        body = term.build()
                        back_btn = ft.TextButton(
                            content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("К выбору тренажёра", color=text_accent(page), size=14)], spacing=5),
                            on_click=lambda e: open_section("Тренажёры")
                        )
                        set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))

                    body = SimulatorSelectionScreen(page, on_start_simulator=start_sim, on_start_terminal=start_terminal).build()
                    back_btn = ft.TextButton(
                        content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("На главную", color=text_accent(page), size=14)], spacing=5),
                        on_click=lambda e: page.run_task(show_main_screen)
                    )
                    set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))

                elif section == "Тесты":
                    def start_quiz(level: int):
                        quiz = QuizScreen(page, level=level, on_back=lambda: page.run_task(show_main_screen))
                        body = quiz.build()
                        back_btn = ft.TextButton(
                            content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("К выбору теста", color=text_accent(page), size=14)], spacing=5),
                            on_click=lambda e: open_section("Тесты")
                        )
                        set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))
                    
                    body = QuizSelectionScreen(page, on_start_quiz=start_quiz).build()
                    back_btn = ft.TextButton(
                        content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("На главную", color=text_accent(page), size=14)], spacing=5),
                        on_click=lambda e: page.run_task(show_main_screen)
                    )
                    set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))

                elif section == "Прогресс":
                    progress_screen = ProgressScreen(page, on_start_training=lambda: open_section("Тренажёры"))
                    async def load_progress_screen():
                        body = await progress_screen.build()
                        back_btn = ft.TextButton(
                            content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("На главную", color=text_accent(page), size=14)], spacing=5),
                            on_click=lambda e: page.run_task(show_main_screen)
                        )
                        set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))
                    page.run_task(load_progress_screen)

                elif section == "Профиль":
                    # Передаем функцию для открытия прогресса
                    body = ProfileScreen(page, on_show_progress=lambda: open_section("Прогресс")).build()
                    back_btn = ft.TextButton(
                        content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("На главную", color=text_accent(page), size=14)], spacing=5),
                        on_click=lambda e: page.run_task(show_main_screen)
                    )
                    set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))

                elif section == "О программе":
                    body = AboutScreen(page, on_back=lambda: page.run_task(show_main_screen)).build()
                    back_btn = ft.TextButton(
                        content=ft.Row(controls=[ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color=text_accent(page)), ft.Text("На главную", color=text_accent(page), size=14)], spacing=5),
                        on_click=lambda e: page.run_task(show_main_screen)
                    )
                    set_screen(ft.Column(controls=[body, ft.Row(controls=[back_btn], alignment=ft.MainAxisAlignment.CENTER)], expand=True))

                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Раздел '{section}' в разработке"))
                    page.snack_bar.open = True
                    page.update()
            except Exception as ex:
                print(f"Ошибка при открытии раздела {section}: {ex}")
                error_screen = ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color="red", size=50), 
                        ft.Text(f"Ошибка: {ex}", color="red", selectable=True), 
                        ft.TextButton(content=ft.Text("Назад"), on_click=lambda e: page.run_task(show_main_screen))
                    ], 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
                set_screen(error_screen)

        def make_card(title: str, subtitle: str, icon, color: str, section: str):
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(content=ft.Icon(icon=icon, size=32, color=color), width=56, height=56, bgcolor="#F4F0FF" if not page.theme_mode == ft.ThemeMode.DARK else "#3D3D1C", border_radius=28, alignment=ft.Alignment.CENTER),
                        ft.Column(controls=[ft.Text(title, size=17, weight=ft.FontWeight.BOLD, color=text_primary(page)), ft.Text(subtitle, size=12, color=text_secondary(page))], spacing=2, expand=True),
                        ft.Icon(icon=ft.Icons.CHEVRON_RIGHT, color=text_secondary(page), size=22),
                    ],
                    spacing=15,
                ),
                bgcolor=bg_card(page), border_radius=16, padding=ft.Padding.symmetric(vertical=15, horizontal=20),
                col={"xs": 12, "sm": 6},
                on_click=lambda e: open_section(section), shadow=ft.BoxShadow(blur_radius=10, color="#00000015", offset=ft.Offset(0, 4)),
                ink=True,
            )

        # Убрали карточку "Прогресс", теперь их 5
        cards_column = ft.ResponsiveRow(
            controls=[
                make_card("Справочник", "База знаний и статьи", ft.Icons.MENU_BOOK, text_accent(page), "Справочник"),
                make_card("Тренажёры", "L1, L2, L3 — симулятор заявок", ft.Icons.SCHOOL, text_accent(page), "Тренажёры"),
                make_card("Тесты", "Проверка знаний (25 вопросов)", ft.Icons.QUIZ, text_accent(page), "Тесты"),
                make_card("Профиль", "Настройки, прогресс и история тестов", ft.Icons.PERSON, text_accent(page), "Профиль"),
                make_card("О программе", "Информация об авторе и версии", ft.Icons.INFO, text_accent(page), "О программе"),
            ],
            spacing=15, run_spacing=15,
        )

        content_column = ft.Column(
            controls=[
                build_logo(70, page), ft.Container(height=10),
                ft.Text(f"👋 Привет, {state.profile_name}!", size=22, weight=ft.FontWeight.BOLD, color=text_primary(page)),
                ft.Text(f"Решено заявок: {solved_count}", size=14, color=text_accent(page), weight=ft.FontWeight.BOLD),
                ft.Text("Выбери раздел, чтобы начать", size=13, color=text_secondary(page)),
                ft.Container(height=20), cards_column,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, expand=True,
        )

        main_screen = ft.Stack(controls=[build_background(), ft.Container(content=content_column, expand=True, alignment=ft.Alignment.CENTER)], expand=True)
        set_screen(main_screen)

    page.add(switcher)
    if state.profile_created:
        page.run_task(show_main_screen)
    else:
        show_profile_screen()


if __name__ == "__main__":
    ft.run(main)
