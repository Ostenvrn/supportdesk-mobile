# app/ui/progress.py
#
# Экран "Прогресс" — статистика по пройденным заявкам + ачивки.

import flet as ft
from app.core.storage import load_progress
from app.core.achievements import get_all_achievements


class ProgressScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
        self.progress_data = {}

    async def build(self) -> ft.Control:
        self.progress_data = await load_progress()

        # Исключаем служебный ключ с ачивками
        cases_data = {k: v for k, v in self.progress_data.items() if not k.startswith("__")}
        total_cases = len(cases_data)
        
        # Получаем ачивки
        earned_achievements = self.progress_data.get("__achievements__", [])
        all_achievements = get_all_achievements()

        if total_cases == 0:
            self.container.content = ft.Column(
                controls=[
                    ft.Icon(icon=ft.Icons.INSIGHTS, size=60, color="#CCCCCC"),
                    ft.Text("Пока нет пройденных заявок", size=18, weight=ft.FontWeight.BOLD, color="#666666"),
                    ft.Text("Пройди тренажёр, чтобы здесь появилась статистика.", size=14, color="#888888"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
            return self.container

        # Считаем статистику
        total_time = 0
        best_time = 999999
        
        list_items = []

        for case_id, data in cases_data.items():
            time_spent = data.get("time", 0)
            total_time += time_spent
            
            if time_spent < best_time:
                best_time = time_spent

            mins = time_spent // 60
            secs = time_spent % 60
            
            # Карточка пройденной заявки
            list_items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(icon=ft.Icons.CHECK_CIRCLE, color="#00A896", size=24),
                            ft.Column(
                                controls=[
                                    ft.Text(f"Заявка {data.get('number', case_id)}", size=14, weight=ft.FontWeight.BOLD, color="#333333"),
                                    ft.Text(f"Тема: {data.get('topic', '—')}", size=12, color="#666666"),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Text(f"{mins:02d}:{secs:02d}", size=14, color="#5A00FF", weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    bgcolor="#FFFFFF",
                    padding=15,
                    border_radius=8,
                    width=500,
                    shadow=ft.BoxShadow(blur_radius=2, color="#00000010"),
                )
            )

        avg_time = total_time // total_cases
        avg_mins = avg_time // 60
        avg_secs = avg_time % 60
        
        best_mins = best_time // 60
        best_secs = best_time % 60

        # Блок с общей статистикой
        stats_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(str(total_cases), size=28, weight=ft.FontWeight.BOLD, color="#5A00FF"),
                            ft.Text("Решено заявок", size=12, color="#666666"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(width=1, height=40, bgcolor="#CED4DA"),
                    ft.Column(
                        controls=[
                            ft.Text(f"{avg_mins:02d}:{avg_secs:02d}", size=28, weight=ft.FontWeight.BOLD, color="#5A00FF"),
                            ft.Text("Среднее время", size=12, color="#666666"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(width=1, height=40, bgcolor="#CED4DA"),
                    ft.Column(
                        controls=[
                            ft.Text(f"{best_mins:02d}:{best_secs:02d}", size=28, weight=ft.FontWeight.BOLD, color="#00A896"),
                            ft.Text("Лучшее время", size=12, color="#666666"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
            bgcolor="#FFFFFF",
            padding=20,
            border_radius=14,
            width=600,
            shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
        )

        # Блок с ачивками
        earned_ids = [a["id"] for a in earned_achievements]
        ach_cards = []
        
        for ach in all_achievements:
            is_earned = ach["id"] in earned_ids
            ach_cards.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(ach["icon"], size=30, color=None if is_earned else "#CCCCCC"),
                            ft.Text(ach["title"], size=12, weight=ft.FontWeight.BOLD, 
                                    color="#333333" if is_earned else "#999999",
                                    text_align=ft.TextAlign.CENTER),
                            ft.Text(ach["description"], size=10, color="#666666" if is_earned else "#CCCCCC",
                                    text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    bgcolor="#FFFFFF" if is_earned else "#F0F0F0",
                    padding=10,
                    border_radius=8,
                    width=110,
                    height=110,
                    alignment=ft.Alignment.CENTER,
                    opacity=1.0 if is_earned else 0.6,
                )
            )

        ach_row = ft.Row(controls=ach_cards, wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)

        ach_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🏆 Достижения", size=16, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(height=10),
                    ach_row
                ]
            ),
            bgcolor="#F4F6F9",
            width=600,
        )

        # Список заявок
        list_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("История решений:", size=16, weight=ft.FontWeight.BOLD, color="#333333"),
                    ft.Container(height=10),
                    ft.Column(controls=list_items, spacing=10, scroll=ft.ScrollMode.AUTO),
                ]
            ),
            bgcolor="#F4F6F9",
            width=600,
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Мой прогресс", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                ft.Container(height=10),
                stats_card,
                ft.Container(height=20),
                ach_section,
                ft.Container(height=20),
                list_card,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return self.container
