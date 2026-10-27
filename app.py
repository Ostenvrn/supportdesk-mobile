# app.py
#
# Точка входа SupportDesk Mobile (Flet 1.0.5).
# Этап 1: профиль + заглушка главного экрана.

import flet as ft

import app.state as state
from app.core.storage import load_profile, save_profile


def main(page: ft.Page):
    # --- Настройки страницы (фиолетовая тема) ---
    page.title = "SupportDesk Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F4F6F9"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # --- Загружаем профиль при старте ---
    saved_name = load_profile()
    if saved_name:
        state.profile_name = saved_name
        state.profile_created = True

    # --- Контейнер для экранов ---
    screen_container = ft.Container(expand=True)

    def show_profile_screen():
        """Экран профиля (если не создан)."""
        name_input = ft.TextField(
            label="Ваше имя",
            hint_text="Например, Александр",
            width=300,
            autofocus=True,
            border_color="#5A00FF",
            focused_border_color="#5A00FF",
        )

        def save_and_continue(e):
            name = name_input.value.strip() if name_input.value else ""
            if not name:
                name_input.error_text = "Введите имя"
                page.update()
                return
            state.profile_name = name
            state.profile_created = True
            save_profile(name)
            show_main_screen()

        save_btn = ft.Button(
            content=ft.Text("Сохранить и продолжить", color=ft.Colors.WHITE),
            bgcolor="#5A00FF",
            on_click=save_and_continue,
            width=300,
            height=45,
        )

        screen_container.content = ft.Column(
            controls=[
                ft.Icon(icon=ft.Icons.SUPPORT_AGENT, size=80, color="#5A00FF"),
                ft.Text("SupportDesk Mobile", size=28, weight=ft.FontWeight.BOLD, color="#5A00FF"),
                ft.Text("Твой помощник в поддержке", size=14, color="#666666"),
                ft.Container(height=20),
                name_input,
                ft.Container(height=10),
                save_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
        page.update()

    def show_main_screen():
        """Главный экран (заглушка с карточками)."""

        def go_to_section(e):
            section = e.control.data
            page.snack_bar = ft.SnackBar(ft.Text(f"Раздел '{section}' в разработке"))
            page.snack_bar.open = True
            page.update()

        def make_card(title: str, icon, color: str, section: str):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(icon=icon, size=40, color=color),
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="#333333"),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                bgcolor="#FFFFFF",
                border_radius=12,
                padding=20,
                width=140,
                height=140,
                alignment=ft.Alignment.CENTER,
                on_click=go_to_section,
                data=section,
                shadow=ft.BoxShadow(blur_radius=4, color="#00000010"),
            )

        cards_row = ft.Row(
            controls=[
                make_card("Справочник", ft.Icons.MENU_BOOK, "#5A00FF", "Справочник"),
                make_card("Тренажёр", ft.Icons.SCHOOL, "#5A00FF", "Тренажёр"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        cards_row2 = ft.Row(
            controls=[
                make_card("Прогресс", ft.Icons.BAR_CHART, "#5A00FF", "Прогресс"),
                make_card("Профиль", ft.Icons.PERSON, "#5A00FF", "Профиль"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        screen_container.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(f"👋 Привет, {state.profile_name}!", size=20, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=20),
                cards_row,
                ft.Container(height=10),
                cards_row2,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        page.update()

    # --- Стартуем с нужного экрана ---
    page.add(screen_container)

    if state.profile_created:
        show_main_screen()
    else:
        show_profile_screen()


if __name__ == "__main__":
    ft.run(main)
