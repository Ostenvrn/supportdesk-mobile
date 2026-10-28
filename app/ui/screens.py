# app/ui/screens.py

import flet as ft
from app.core.knowledge import get_categories, get_category_by_id, search_knowledge


class KnowledgeScreen:
    # ... (код без изменений, как в предыдущем шаге) ...
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_category = None
        self.container = ft.Container(expand=True)
        self.search_results_container = ft.Column(visible=False, expand=True)
        self.categories_container = ft.Column(expand=True)

    def build(self) -> ft.Control:
        self.show_categories()
        search_input = ft.TextField(
            hint_text="Поиск по справочнику...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            bgcolor="#FFFFFF",
            height=50,
            on_change=self._on_search_change,
        )
        return ft.Column(
            controls=[
                ft.Row(controls=[ft.Icon(icon=ft.Icons.MENU_BOOK, color="#5A00FF", size=28), ft.Text("Справочник", size=22, weight=ft.FontWeight.BOLD, color="#333333")], spacing=10),
                ft.Container(height=10),
                search_input,
                ft.Container(height=15),
                self.search_results_container, 
                self.categories_container,      
            ],
            expand=True,
        )
    # ... (остальные методы KnowledgeScreen без изменений) ...


class SimulatorSelectionScreen:
    # ... (код без изменений) ...
    def __init__(self, page: ft.Page, on_start_simulator):
        self.page = page
        self.on_start_simulator = on_start_simulator
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)
    # ... (остальные методы SimulatorSelectionScreen без изменений) ...


class QuizSelectionScreen:
    """Экран выбора уровня для теста."""
    def __init__(self, page: ft.Page, on_start_quiz):
        self.page = page
        self.on_start_quiz = on_start_quiz
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        def start_quiz(level: int):
            self.on_start_quiz(level)

        card_l1 = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOOKS_ONE, size=40, color="#00A896"),
                    ft.Text("Тест L1", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Базовые знания", size=12, color="#666666"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#FFFFFF", padding=20, border_radius=14, width=160, height=140,
            on_click=lambda e: start_quiz(1),
            shadow=ft.BoxShadow(blur_radius=4, color="#00000015"),
        )

        card_l2 = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOOKS_TWO, size=40, color="#5A00FF"),
                    ft.Text("Тест L2", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Сетевые технологии", size=12, color="#666666"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#FFFFFF", padding=20, border_radius=14, width=160, height=140,
            on_click=lambda e: start_quiz(2),
            shadow=ft.BoxShadow(blur_radius=4, color="#00000015"),
        )

        card_l3 = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOOKS_3, size=40, color="#E63946"),
                    ft.Text("Тест L3", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Инфраструктура", size=12, color="#666666"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#FFFFFF", padding=20, border_radius=14, width=160, height=140,
            on_click=lambda e: start_quiz(3),
            shadow=ft.BoxShadow(blur_radius=4, color="#00000015"),
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Выберите уровень теста", size=22, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Row(controls=[card_l1, card_l2, card_l3], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
                ft.Text("Каждый тест содержит вопросы только для выбранного уровня.", size=12, color="#666666"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
        return self.container
