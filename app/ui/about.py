# app/ui/about.py
#
# Экран "О программе" с соглашением и дисклеймером.

import flet as ft
from app.state import APP_VERSION
from app.ui.theme_colors import text_primary, text_secondary, text_accent, text_error


class AboutScreen:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        # Функция для показа пользовательского соглашения
        def show_agreement(e):
            agreement_text = (
                "ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ\n\n"
                "1. Настоящее приложение является исключительно обучающим тренажёром.\n"
                "2. Все данные (имена, адреса, номера заявок, IP-адреса) являются вымышленными. "
                "Любые совпадения с реальными людьми или организациями случайны.\n"
                "3. Приложение не собирает, не хранит и не передает персональные данные третьим лицам. "
                "Вся информация (имя профиля, прогресс) хранится локально на вашем устройстве.\n"
                "4. Приложение не выполняет реальных сетевых запросов к оборудованию провайдеров."
            )

            dialog = ft.AlertDialog(
                title=ft.Text("Пользовательское соглашение", color=text_primary(self.page)),
                content=ft.Container(
                    content=ft.Text(agreement_text, size=14, color=text_primary(self.page)),
                    width=400,
                    padding=10,
                ),
                bgcolor=text_secondary(self.page) if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1E1E1E",
                actions=[
                    ft.TextButton("Закрыть", on_click=lambda _: self.page.pop_dialog(), style=ft.ButtonStyle(color=text_accent(self.page)))
                ],
            )
            self.page.show_dialog(dialog)

        self.container.content = ft.Column(
            controls=[
                ft.Icon(ft.Icons.SUPPORT_AGENT, size=80, color=text_accent(self.page)),
                ft.Text("SupportDesk Mobile", size=24, weight=ft.FontWeight.BOLD, color=text_accent(self.page)),
                ft.Text(f"Версия {APP_VERSION}", size=14, color=text_secondary(self.page)),
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
                        "⚠️ Внимание: это тренажёр. Все имена, адреса и ситуации вымышлены, "
                        "любые совпадения случайны. Приложение не выполняет реальных сетевых запросов.",
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
                ft.TextButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.DESCRIPTION, color=text_accent(self.page)),
                            ft.Text("Пользовательское соглашение", color=text_accent(self.page)),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    on_click=show_agreement,
                ),
                ft.Container(height=10),
                ft.Text("© 2026. Все права защищены.", size=10, color=text_secondary(self.page)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return self.container
