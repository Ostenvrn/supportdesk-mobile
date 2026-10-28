# app/ui/about.py
#
# Экран "О программе".

import flet as ft


class AboutScreen:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        self.container.content = ft.Column(
            controls=[
                ft.Icon(ft.Icons.SUPPORT_AGENT, size=80, color="#5A00FF"),
                ft.Text("SupportDesk Mobile", size=24, weight=ft.FontWeight.BOLD, color="#5A00FF"),
                ft.Text("Версия 1.0.0", size=14, color="#888888"),
                ft.Divider(),
                ft.Text("Автор проекта:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("А.Д. Чернов", size=16),
                ft.Container(height=10),
                ft.Text(
                    "Мобильный тренажёр для инженеров технической поддержки. "
                    "Позволяет отрабатывать навыки диагностики сетевых проблем (L1/L2/L3), "
                    "изучать базовые команды и готовиться к собеседованиям.",
                    size=12,
                    color="#666666",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(
                        "⚠️ Внимание: это тренажёр. Он не выполняет реальных сетевых запросов к оборудованию провайдера.",
                        size=12,
                        color="#E63946",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=10,
                    bgcolor="#FFF3CD",
                    border_radius=8,
                    width=350,
                ),
                ft.Container(height=20),
                ft.Text("© 2026. Все права защищены.", size=10, color="#AAAAAA"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return self.container
