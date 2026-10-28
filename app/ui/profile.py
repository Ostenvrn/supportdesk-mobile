# app/ui/profile.py
#
# Экран "Профиль" — настройки пользователя и сброс прогресса.

import flet as ft
import app.state as state
from app.core.storage import save_profile, reset_all_data


class ProfileScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        name_input = ft.TextField(
            label="Имя пользователя",
            value=state.profile_name,
            width=300,
            border_color="#5A00FF",
            focused_border_color="#5A00FF",
        )

        success_text = ft.Text("", color="#00A896", size=14, weight=ft.FontWeight.BOLD, visible=False)

        async def save_name(e):
            new_name = name_input.value.strip()
            if not new_name:
                name_input.error_text = "Имя не может быть пустым"
                self.page.update()
                return
            
            state.profile_name = new_name
            await save_profile(new_name)
            
            name_input.error_text = None
            success_text.value = "✅ Имя успешно сохранено!"
            success_text.visible = True
            self.page.update()

        save_btn = ft.Button(
            content=ft.Text("Сохранить имя", color=ft.Colors.WHITE),
            bgcolor="#5A00FF",
            width=300,
            height=45,
            on_click=save_name,
        )

        # --- Сброс прогресса ---
        def confirm_reset(e):
            def do_reset(e):
                async def _reset():
                    await reset_all_data()
                    state.profile_name = ""
                    state.profile_created = False
                    state.progress = {}
                    self.page.pop_dialog()
                    # Перенаправляем на экран профиля (через перезагрузку главного экрана)
                    # Проще всего выкинуть пользователя на экран ввода имени
                    self.page.go("/") # Или вызвать callback, но для простоты сделаем так
                    self.page.snack_bar = ft.SnackBar(ft.Text("Прогресс сброшен. Перезапустите приложение."))
                    self.page.snack_bar.open = True
                    self.page.update()
                self.page.run_task(_reset)

            dialog = ft.AlertDialog(
                title=ft.Text("Сброс прогресса"),
                content=ft.Text("Вы уверены? Все достижения, история и имя будут удалены безвозвратно."),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog()),
                    ft.Button("Да, удалить", bgcolor="#E63946", color="#FFFFFF", on_click=do_reset),
                ],
            )
            self.page.show_dialog(dialog)

        reset_btn = ft.Button(
            content=ft.Text("🗑 Сбросить весь прогресс", color=ft.Colors.WHITE),
            bgcolor="#E63946",
            width=300,
            height=45,
            on_click=confirm_reset,
        )

        # --- Тёмная тема ---
        async def toggle_theme(e):
            is_dark = e.control.value
            from app.core.storage import save_theme
            await save_theme(is_dark)
            if is_dark:
                self.page.theme_mode = ft.ThemeMode.DARK
                self.page.bgcolor = "#121212"
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
                self.page.bgcolor = "#F4F6F9"
            self.page.update()

        theme_switch = ft.Switch(
            label="Тёмная тема",
            value=self.page.theme_mode == ft.ThemeMode.DARK,
            on_change=toggle_theme,
            active_color="#5A00FF",
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Профиль", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                ft.Container(height=10),
                ft.Icon(icon=ft.Icons.PERSON, size=80, color="#5A00FF"),
                ft.Container(height=10),
                name_input,
                ft.Container(height=10),
                save_btn,
                ft.Container(height=10),
                success_text,
                ft.Divider(),
                theme_switch,
                ft.Container(height=20),
                reset_btn,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
        )
        return self.container
