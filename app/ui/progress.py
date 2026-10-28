# app/ui/progress.py

import flet as ft
from app.core.storage import load_progress, load_quiz_results
from app.core.achievements import get_all_achievements
from app.ui.theme_colors import (
    text_primary, text_secondary, text_accent, text_error, text_success, 
    bg_card, bg_card_alt, border_color
)


class ProgressScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
        self.progress_data = {}

    async def build(self) -> ft.Control:
        self.progress_data = await load_progress()
        quiz_results = await load_quiz_results()

        cases_data = {k: v for k, v in self.progress_data.items() if not k.startswith("__")}
        total_cases = len(cases_data)
        earned_achievements = self.progress_data.get("__achievements__", [])
        all_achievements = get_all_achievements()

        # --- Блок заявок ---
        if total_cases == 0:
            cases_section = ft.Column(
                controls=[
                    ft.Icon(icon=ft.Icons.INSIGHTS, size=60, color=text_secondary(self.page)),
                    ft.Text("Пока нет пройденных заявок", size=18, weight=ft.FontWeight.BOLD, color=text_secondary(self.page)),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        else:
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
                
                list_items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(icon=ft.Icons.CHECK_CIRCLE, color=text_success(self.page), size=24),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"Заявка {data.get('number', case_id)}", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                                        ft.Text(f"Тема: {data.get('topic', '—')}", size=12, color=text_secondary(self.page)),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Text(f"{mins:02d}:{secs:02d}", size=14, color=text_accent(self.page), weight=ft.FontWeight.BOLD),
                            ],
                        ),
                        bgcolor=bg_card(self.page),
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

            stats_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(controls=[ft.Text(str(total_cases), size=28, weight=ft.FontWeight.BOLD, color=text_accent(self.page)), ft.Text("Решено заявок", size=12, color=text_secondary(self.page))], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(width=1, height=40, bgcolor=border_color(self.page)),
                        ft.Column(controls=[ft.Text(f"{avg_mins:02d}:{avg_secs:02d}", size=28, weight=ft.FontWeight.BOLD, color=text_accent(self.page)), ft.Text("Среднее время", size=12, color=text_secondary(self.page))], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(width=1, height=40, bgcolor=border_color(self.page)),
                        ft.Column(controls=[ft.Text(f"{best_mins:02d}:{best_secs:02d}", size=28, weight=ft.FontWeight.BOLD, color=text_success(self.page)), ft.Text("Лучшее время", size=12, color=text_secondary(self.page))], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
                bgcolor=bg_card(self.page), padding=20, border_radius=14, width=600, shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
            )

            list_card = ft.Container(
                content=ft.Column(controls=[ft.Text("История решений:", size=16, weight=ft.FontWeight.BOLD, color=text_primary(self.page)), ft.Container(height=10), ft.Column(controls=list_items, spacing=10, scroll=ft.ScrollMode.AUTO)]),
                bgcolor=bg_card_alt(self.page), width=600, padding=15, border_radius=10,
            )

            cases_section = ft.Column(controls=[stats_card, ft.Container(height=20), list_card])

        # --- Блок ачивок ---
        earned_ids = [a["id"] for a in earned_achievements]
        ach_cards = []
        for ach in all_achievements:
            is_earned = ach["id"] in earned_ids
            ach_cards.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(ach["icon"], size=30, color=None if is_earned else "#555555"),
                            ft.Text(ach["title"], size=12, weight=ft.FontWeight.BOLD, color=text_primary(self.page) if is_earned else text_secondary(self.page), text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    bgcolor=bg_card(self.page) if is_earned else bg_card_alt(self.page),
                    padding=10, border_radius=8, width=100, height=100,
                    alignment=ft.Alignment.CENTER, opacity=1.0 if is_earned else 0.5,
                )
            )

        ach_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🏆 Достижения", size=16, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                    ft.Container(height=10),
                    ft.Row(controls=ach_cards, wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                ]
            ),
            bgcolor=bg_card_alt(self.page), width=600, padding=15, border_radius=10,
        )

        # --- Блок тестов ---
        quiz_items = []
        if not quiz_results:
            quiz_items.append(ft.Text("Тесты ещё не проходились.", color=text_secondary(self.page), italic=True))
        else:
            for res in reversed(quiz_results):
                is_passed = res["correct"] >= 15
                color = text_success(self.page) if is_passed else text_error(self.page)
                icon = ft.Icons.CHECK_CIRCLE if is_passed else ft.Icons.CANCEL
                quiz_items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(icon=icon, color=color, size=24),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"Тест L{res['level']}", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                                        ft.Text(f"{res['date']}", size=12, color=text_secondary(self.page)),
                                    ],
                                    spacing=2, expand=True,
                                ),
                                ft.Text(f"{res['correct']}/{res['total']}", size=14, weight=ft.FontWeight.BOLD, color=color),
                            ],
                        ),
                        bgcolor=bg_card(self.page), padding=15, border_radius=8, width=500, shadow=ft.BoxShadow(blur_radius=2, color="#00000010"),
                    )
                )

        quiz_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("📝 Результаты тестов", size=16, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                    ft.Container(height=10),
                    ft.Column(controls=quiz_items, spacing=10),
                ]
            ),
            bgcolor=bg_card_alt(self.page), width=600, padding=15, border_radius=10,
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Мой прогресс", size=22, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                ft.Container(height=10),
                cases_section,
                ft.Container(height=20),
                quiz_section,
                ft.Container(height=20),
                ach_section,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return self.container
