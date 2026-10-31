# app/ui/profile.py

import flet as ft
import app.state as state
from app.core.storage import save_profile, reset_all_data, load_quiz_results
from app.ui.theme_colors import text_primary, text_secondary, text_accent, text_error, bg_card


class ProfileScreen:
    def __init__(self, page: ft.Page, on_show_progress=None):
        self.page = page
        self.on_show_progress = on_show_progress # Функция перехода в прогресс
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        name_input = ft.TextField(
            label="Имя пользователя",
            value=state.profile_name,
            width=300,
            border_color=text_accent(self.page),
            focused_border_color=text_accent(self.page),
            color=text_primary(self.page),
            label_style=ft.TextStyle(color=text_secondary(self.page)),
            border_radius=12,
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
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )

        # --- Кнопка перехода в Прогресс ---
        progress_btn = ft.Container()
        if self.on_show_progress:
            progress_btn = ft.Button(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.BAR_CHART, color="#FFFFFF"),
                        ft.Text("Посмотреть мой прогресс", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                bgcolor="#00A896", # Зеленый цвет
                width=300,
                height=50,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                on_click=lambda e: self.on_show_progress(),
            )

        # --- Блок достижений ---
        async def load_achievements_count():
            from app.core.storage import load_progress
            from app.core.achievements import get_all_achievements
            progress = await load_progress()
            earned = progress.get("__achievements__", [])
            all_ach = get_all_achievements()
            ach_text.value = f"🏆 Получено достижений: {len(earned)} из {len(all_ach)}"
            self.page.update()

        ach_text = ft.Text("🏆 Загрузка достижений...", size=14, weight=ft.FontWeight.BOLD, color=text_accent(self.page))
        self.page.run_task(load_achievements_count)

        # --- Смена профиля ---
        def confirm_change_profile(e):
            def do_change_profile(e):
                async def _change():
                    state.profile_name = ""
                    state.profile_created = False
                    await save_profile("") 
                    self.page.pop_dialog()
                    self.page.window.reload()
                self.page.run_task(_change)

            dialog = ft.AlertDialog(
                title=ft.Text("Смена профиля"),
                content=ft.Text("Вы уверены? Текущее имя будет сброшено, но весь ваш прогресс и достижения сохранятся."),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog()),
                    ft.Button(content=ft.Text("Сменить имя"), bgcolor="#5A00FF", color="#FFFFFF", on_click=do_change_profile),
                ],
            )
            self.page.show_dialog(dialog)

        change_profile_btn = ft.OutlinedButton(
            content=ft.Text("Сменить профиль", color=text_accent(self.page)),
            width=300,
            height=45,
            on_click=confirm_change_profile,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
        )

        # --- История тестов ---
        quiz_history_container = ft.Column()

        async def load_history():
            history = await load_quiz_results()
            if not history:
                quiz_history_container.controls = [ft.Text("Вы ещё не проходили тесты.", color=text_secondary(self.page), italic=True)]
            else:
                for res in reversed(history[-5:]):
                    quiz_history_container.controls.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Text(f"L{res['level']}", size=14, weight=ft.FontWeight.BOLD, color=text_accent(self.page)),
                                    ft.Text(f"{res['date']}", size=12, color=text_secondary(self.page)),
                                    ft.Container(expand=True),
                                    ft.Text(f"{res['correct']}/{res['total']}", size=14, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                                ]
                            ),
                            padding=10,
                            bgcolor=bg_card(self.page),
                            border_radius=8,
                        )
                    )
            self.page.update()

        self.page.run_task(load_history)

        # --- Сброс прогресса ---
        def confirm_reset(e):
            def do_reset(e):
                async def _reset():
                    await reset_all_data()
                    state.profile_name = ""
                    state.profile_created = False
                    state.progress = {}
                    self.page.pop_dialog()
                    self.page.window.reload()
                self.page.run_task(_reset)

            dialog = ft.AlertDialog(
                title=ft.Text("Сброс прогресса"),
                content=ft.Text("Вы уверены? Все достижения, история, результаты тестов и имя будут удалены."),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog()),
                    ft.Button(content=ft.Text("Да, удалить"), bgcolor="#E63946", color="#FFFFFF", on_click=do_reset),
                ],
            )
            self.page.show_dialog(dialog)

        reset_btn = ft.Button(
            content=ft.Text("🗑 Сбросить весь прогресс", color=ft.Colors.WHITE),
            bgcolor="#E63946",
            width=300,
            height=45,
            on_click=confirm_reset,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
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
                ft.Text("Профиль", size=22, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                ft.Container(height=10),
                ft.Icon(icon=ft.Icons.PERSON, size=80, color=text_accent(self.page)),
                ft.Container(height=10),
                name_input,
                ft.Container(height=10),
                save_btn,
                ft.Container(height=5),
                success_text,
                change_profile_btn,
                ft.Container(height=15),
                progress_btn, # Кнопка перехода в прогресс
                ft.Container(height=15),
                ach_text,
                ft.Divider(),
                theme_switch,
                ft.Divider(),
                ft.Text("Последние тесты:", size=16, weight=ft.FontWeight.BOLD, color=text_primary(self.page)),
                quiz_history_container,
                ft.Container(height=20),
                reset_btn,
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        return self.container
