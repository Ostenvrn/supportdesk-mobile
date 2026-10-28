# app/ui/about.py
#
# Экран "О программе".

import flet as ft
from app.ui.theme_colors import text_primary, text_secondary, text_accent, text_error


class AboutScreen:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        self.container.content = ft.Column(
            controls=[
                ft.Icon(ft.Icons.SUPPORT_AGENT, size=80, color=text_accent(self.page)),
                ft.Text("SupportDesk Mobile", size=24, weight=ft.FontWeight.BOLD, color=text_accent(self.page)),
                ft.Text("Версия 1.0.0", size=14, color=text_secondary(self.page)),
                ft.Divider(),
                ft.Text("Автор проекта:", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                ft.Text("А.Д. Чернов", size=16, color=text_primary(self.page)),
                ft.Container(height=10),
                ft.Text(
                    "Мобильный тренажёр для инженеров технической поддержки. "
                    "Позволяет отрабатывать навыки диагностики сетевых проблем (L1/L2/L3), "
                    "изучать базовые команды и готовиться к собеседованиям.",
                    size=12,
                    color=text_secondary(self.page),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(
                        "⚠️ Внимание: это тренажёр. Он не выполняет реальных сетевых запросов к оборудованию провайдера.",
                        size=12,
                        color=text_error(self.page),
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=10,
                    bgcolor="#FFF3CD" if not self.page.theme_mode == ft.ThemeMode.DARK else "#3D3D1C",
                    border_radius=8,
                    width=350,
                ),
                ft.Container(height=20),
                ft.Text("© 2026. Все права защищены.", size=10, color=text_secondary(self.page)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return self.container
