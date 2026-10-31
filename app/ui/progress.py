# app/ui/progress.py

import flet as ft
from app.core.storage import load_progress, load_quiz_results
from app.core.achievements import get_all_achievements
from app.ui.theme_colors import (
    text_primary, text_secondary, text_accent, text_error, text_success, 
    bg_card, bg_card_alt, border_color
)


class ProgressScreen:
    def __init__(self, page: ft.Page, on_start_training=None):
        self.page = page
        self.on_start_training = on_start_training
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
            start_btn = ft.Button(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PLAY_ARROW, color="#FFFFFF"),
                        ft.Text("Начать тренировку", color="#FFFFFF", weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                bgcolor="#5A00FF",
                width=250,
                height=50,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                on_click=lambda e: self.on_start_training() if self.on_start_training else None
            )

            cases_section = ft.Column(
                controls=[
                    ft.Icon(icon=ft.Icons.INSIGHTS, size=80, color=ft.Colors.with_opacity(0.5, "#5A00FF")),
                    ft.Text("Здесь пока пусто", size=20, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                    ft.Text("Реши свою первую заявку, чтобы увидеть статистику и прогресс!", size=14, color=text_secondary(self.page), text_align=ft.TextAlign.CENTER),
                    ft.Container(height=20),
                    start_btn
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        else:
            total_time = 0
            best_time = 999999
            list_items = [] # Сюда соберем список для модального окна

            for case_id, data in cases_data.items():
                time_spent = data.get("time", 0)
                total_time += time_spent
                if time_spent < best_time:
                    best_time = time_spent

                mins = time_spent // 60
                secs = time_spent % 60
                
                # Элемент списка для модального окна
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
                        shadow=ft.BoxShadow(blur_radius=2, color="#00000010"),
                    )
                )

            avg_time = total_time // total_cases
            avg_mins = avg_time // 60
            avg_secs = avg_time % 60
            best_mins = best_time // 60
            best_secs = best_time % 60

            # Красивая карточка со статистикой
            stats_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(controls=[ft.Text(str(total_cases), size=24, weight=ft.FontWeight.BOLD, color=text_accent(self.page)), ft.Text("Решено", size=10, color=text_secondary(self.page), text_align=ft.TextAlign.CENTER)], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(width=1, height=40, bgcolor=border_color(self.page)),
                        ft.Column(controls=[ft.Text(f"{avg_mins:02d}:{avg_secs:02d}", size=24, weight=ft.FontWeight.BOLD, color=text_accent(self.page)), ft.Text("Среднее", size=10, color=text_secondary(self.page), text_align=ft.TextAlign.CENTER)], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(width=1, height=40, bgcolor=border_color(self.page)),
                        ft.Column(controls=[ft.Text(f"{best_mins:02d}:{best_secs:02d}", size=24, weight=ft.FontWeight.BOLD, color=text_success(self.page)), ft.Text("Лучшее", size=10, color=text_secondary(self.page), text_align=ft.TextAlign.CENTER)], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
                bgcolor=bg_card(self.page), padding=15, border_radius=14, shadow=ft.BoxShadow(blur_radius=6, color="#00000015"),
            )

            # Функция открытия истории заявок в модальном окне
            def show_cases_history(e):
                dialog = ft.AlertDialog(
                    title=ft.Text("История заявок", color=text_primary(self.page)),
                    content=ft.Container(
                        content=ft.Column(
                            controls=list_items,
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        width=500,
                        height=400,
                    ),
                    bgcolor=text_secondary(self.page) if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1E1E1E",
                    actions=[
                        ft.TextButton("Закрыть", on_click=lambda _: self.page.pop_dialog(), style=ft.ButtonStyle(color=text_accent(self.page)))
                    ],
                )
                self.page.show_dialog(dialog)

            history_btn = ft.Button(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LIST_ALT, color=text_accent(self.page)),
                        ft.Text("Посмотреть историю заявок", color=text_accent(self.page), weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                bgcolor="transparent",
                height=45,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=12),
                    side=ft.BorderSide(1, text_accent(self.page))
                ),
                on_click=show_cases_history,
            )

            cases_section = ft.Column(
                controls=[
                    stats_card, 
                    ft.Container(height=10), 
                    history_btn
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        # --- Кнопка "Достижения" (вызывает модальное окно) ---
        def show_achievements(e):
            earned_ids = [a["id"] for a in earned_achievements]
            ach_cards = []
            for ach in all_achievements:
                is_earned = ach["id"] in earned_ids
                card = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(ach["icon"], size=24, color=None if is_earned else "#555555"),
                                    ft.Text(ach["title"], size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page) if is_earned else text_secondary(self.page), expand=True),
                                ],
                                spacing=10,
                            ),
                            ft.Text(ach["description"], size=11, color=text_secondary(self.page) if is_earned else "#777777"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    bgcolor=bg_card(self.page) if is_earned else bg_card_alt(self.page),
                    padding=12, border_radius=8,
                    col={"xs": 12, "sm": 6},
                    opacity=1.0 if is_earned else 0.5,
                )
                ach_cards.append(card)

            dialog = ft.AlertDialog(
                title=ft.Text("🏆 Достижения", color=text_primary(self.page)),
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(f"Получено: {len(earned_achievements)} из {len(all_achievements)}", size=14, color=text_secondary(self.page)),
                            ft.Container(height=10),
                            ft.ResponsiveRow(controls=ach_cards, spacing=10, run_spacing=10),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    width=600,
                    height=500,
                ),
                bgcolor=text_secondary(self.page) if self.page.theme_mode == ft.ThemeMode.LIGHT else "#1E1E1E",
                actions=[
                    ft.TextButton("Закрыть", on_click=lambda _: self.page.pop_dialog(), style=ft.ButtonStyle(color=text_accent(self.page)))
                ],
            )
            self.page.show_dialog(dialog)

        ach_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.WHITE),
                    ft.Text("Посмотреть достижения", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor="#5A00FF",
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=show_achievements,
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
                        bgcolor=bg_card(self.page), padding=15, border_radius=8, shadow=ft.BoxShadow(blur_radius=2, color="#00000010"),
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
            bgcolor=bg_card_alt(self.page), padding=15, border_radius=10,
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Мой прогресс", size=22, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                ft.Container(height=10),
                cases_section,
                ft.Container(height=20),
                quiz_section,
                ft.Container(height=20),
                ach_button,
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return self.container
