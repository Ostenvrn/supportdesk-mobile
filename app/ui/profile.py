# app/ui/profile.py
#
# Экран "Профиль" — настройки пользователя.

import flet as ft
import app.state as state
from app.core.storage import save_profile


class ProfileScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        # Поле для ввода имени
        name_input = ft.TextField(
            label="Имя пользователя",
            value=state.profile_name,
            width=300,
            border_color="#5A00FF",
            focused_border_color="#5A00FF",
        )

        # Сообщение об успехе (скрыто по умолчанию)
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
            content=ft.Text("Сохранить", color=ft.Colors.WHITE),
            bgcolor="#5A00FF",
            width=300,
            height=45,
            on_click=save_name,
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Профиль", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                ft.Container(height=20),
                ft.Icon(icon=ft.Icons.PERSON, size=80, color="#5A00FF"),
                ft.Container(height=10),
                name_input,
                ft.Container(height=10),
                save_btn,
                ft.Container(height=10),
                success_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
        )
        return self.container
