# app/ui/about.py
#
# Экран "О программе" с соглашением и списком изменений.

import flet as ft
from app.state import APP_VERSION
from app.ui.theme_colors import text_primary, text_secondary, text_accent, text_error, bg_card


class AboutScreen:
    def __init__(self, page: ft.Page, on_back):
        self.page = page
        self.on_back = on_back
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        def show_changelog(e):
            # === СЮДА ДОБАВЛЯЕМ ИЗМЕНЕНИЯ ПЕРЕД КАЖДЫМ ПУШЕМ ===
            changes = [
                "✅ Исправлена системная кнопка «Назад» (приложение больше не закрывается).",
                "✅ Добавлен индикатор загрузки при переходе между экранами.",
                "✅ В Справочнике появилась кнопка очистки поиска и дублирующая кнопка возврата внизу статьи.",
                "✅ В тестах: счетчик правильных ответов и предупреждение при досрочном выходе.",
                "✅ В терминале: история команд, новые команды, фокус и позиционирование курсора.",
                "✅ В профиле: счетчик достижений, кнопка смены профиля, график последних тестов.",
                "✅ Каскадная анимация карточек и плавное закрытие заявок.",
                "✅ Устранено мерцание темы при запуске приложения.",
            ]
            
            changelog_content = ft.Column(
                controls=[ft.Text(change, size=13, color=text_primary(self.page)) for change in changes],
                spacing=8,
            )
            
            dialog = ft.AlertDialog(
                title=ft.Text(f"Что нового в {APP_VERSION}?", color=text_primary(self.page), weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=ft.Column([changelog_content], scroll=ft.ScrollMode.AUTO),
                    width=500,
                    height=400,
                    padding=10,
                ),
                bgcolor=bg_card(self.page),
                shape=ft.RoundedRectangleBorder(radius=16),
                actions=[
                    ft.Button(
                        content=ft.Text("Круто!", color="#FFFFFF"),
                        bgcolor="#5A00FF",
                        on_click=lambda _: self.page.pop_dialog(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ],
            )
            self.page.show_dialog(dialog)

        def show_agreement(e):
            dialog_bg = "#FFFFFF" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1E1E1E"
            dialog_text = "#333333" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#E0E0E0"
            dialog_subtext = "#666666" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#AAAAAA"

            items = [
                (ft.Icons.SCHOOL, "1. Обучающий тренажёр", "Настоящее приложение является исключительно обучающим тренажёром для инженеров поддержки."),
                (ft.Icons.DATA_OBJECT, "2. Вымышленные данные", "Все данные (имена, адреса, номера заявок, IP-адреса) являются вымышленными. Любые совпадения с реальными людьми или организациями случайны."),
                (ft.Icons.SECURITY, "3. Конфиденциальность", "Приложение не собирает и не передает персональные данные третьим лицам. Вся информация (имя профиля, прогресс) хранится только локально на вашем устройстве."),
                (ft.Icons.WIFI_OFF, "4. Нет реальных запросов", "Приложение не выполняет реальных сетевых запросов к оборудованию провайдеров. Все команды эмулируются внутри приложения."),
            ]

            content_controls = []
            for icon, title, desc in items:
                content_controls.append(
                    ft.Column(
                        controls=[
                            ft.Row(controls=[
                                ft.Icon(icon, color="#5A00FF" if self.page.theme_mode == ft.ThemeMode.LIGHT else "#B388FF", size=24),
                                ft.Text(title, weight=ft.FontWeight.BOLD, color=dialog_text, size=16)
                            ], spacing=10),
                            ft.Text(desc, size=14, color=dialog_subtext),
                            ft.Divider(height=10, color="transparent"),
                        ],
                        spacing=5
                    )
                )

            dialog = ft.AlertDialog(
                title=ft.Text("Пользовательское соглашение", color=dialog_text, weight=ft.FontWeight.BOLD, size=20),
                content=ft.Container(
                    content=ft.Column(controls=content_controls, scroll=ft.ScrollMode.AUTO, spacing=10),
                    width=500,
                    height=400,
                ),
                bgcolor=dialog_bg,
                shape=ft.RoundedRectangleBorder(radius=16),
                actions=[
                    ft.Button(
                        content=ft.Text("Понятно", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                        bgcolor="#5A00FF",
                        on_click=lambda _: self.page.pop_dialog(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ],
            )
            self.page.show_dialog(dialog)

        def open_rustore(e):
            # Открываем реальную ссылку на RuStore
            self.page.launch_url("https://www.rustore.ru/catalog/app/com.ostenvrn.supportdesk_mobile")

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
                        "⚠️ Внимание: это тренажёр. Все имена, адреса и ситуации вымышлены. "
                        "Приложение не выполняет реальных сетевых запросов.",
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
                
                # --- Ссылки ---
                ft.Text("Полезные ссылки:", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.SHOP,
                            icon_color=text_accent(self.page),
                            tooltip="RuStore",
                            on_click=open_rustore # Теперь открывает реальную ссылку
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                ft.Container(height=20),
                ft.TextButton(
                    content=ft.Row(
                        controls=[ft.Icon(ft.Icons.NEW_RELEASES, color=text_accent(self.page)), ft.Text(f"Что нового в {APP_VERSION}?", color=text_accent(self.page))],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    on_click=show_changelog,
                ),
                ft.TextButton(
                    content=ft.Row(
                        controls=[ft.Icon(ft.Icons.DESCRIPTION, color=text_accent(self.page)), ft.Text("Пользовательское соглашение", color=text_accent(self.page))],
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
