# app/ui/screens.py
#
# Экраны приложения.
# Справочник: список категорий -> список статей -> текст статьи.

import flet as ft

from app.core.knowledge import get_categories, get_category_by_id


class KnowledgeScreen:
    """
    Экран "Справочник".
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_category = None
        self.container = ft.Container(expand=True)

    def build(self) -> ft.Control:
        self.show_categories()
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(icon=ft.Icons.MENU_BOOK, color="#5A00FF", size=28),
                        ft.Text("Справочник", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                    ],
                    spacing=10,
                ),
                ft.Container(height=10),
                self.container,
            ],
            expand=True,
        )

    def show_categories(self):
        categories = get_categories()

        if not categories:
            self.container.content = ft.Text(
                "База знаний пуста.", color="#666666", italic=True
            )
            self.page.update()
            return

        cards = []
        for cat in categories:
            cards.append(self._make_category_card(cat))

        self.container.content = ft.Column(
            controls=[
                ft.Text("Выберите раздел:", size=14, color="#666666"),
                ft.Container(height=8),
                ft.Column(controls=cards, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            expand=True,
        )
        self.page.update()

    def _make_category_card(self, category: dict) -> ft.Control:
        def on_click(e):
            self.show_articles(category["id"])

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.ARTICLE, color="#5A00FF", size=24),
                    ft.Column(
                        controls=[
                            ft.Text(category["name"], size=16, weight=ft.FontWeight.BOLD, color="#333333"),
                            ft.Text(category.get("description", ""), size=12, color="#666666"),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(icon=ft.Icons.CHEVRON_RIGHT, color="#999999", size=20),
                ],
                spacing=12,
            ),
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=15,
            on_click=on_click,
            shadow=ft.BoxShadow(blur_radius=3, color="#00000010"),
        )

    def show_articles(self, category_id: str):
        category = get_category_by_id(category_id)
        if not category:
            return

        self.current_category = category
        articles = category.get("articles", [])
        if not articles:
            self.container.content = ft.Text("В этой категории пока нет статей.", color="#666666", italic=True)
            self.page.update()
            return

        cards = []
        for idx, article in enumerate(articles):
            cards.append(self._make_article_card(category_id, idx, article))

        back_btn = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color="#5A00FF"),
                    ft.Text("К разделам", color="#5A00FF", size=14),
                ],
                spacing=5,
            ),
            on_click=lambda e: self.show_categories(),
        )

        self.container.content = ft.Column(
            controls=[
                back_btn,
                ft.Text(category["name"], size=18, weight=ft.FontWeight.BOLD, color="#333333"),
                ft.Container(height=5),
                ft.Column(controls=cards, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
            ],
            expand=True,
        )
        self.page.update()

    def _make_article_card(self, category_id: str, idx: int, article: dict) -> ft.Control:
        def on_click(e):
            self.show_article_text(category_id, idx)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.DESCRIPTION, color="#5A00FF", size=22),
                    ft.Text(article["title"], size=14, color="#333333", expand=True),
                    ft.Icon(icon=ft.Icons.CHEVRON_RIGHT, color="#999999", size=18),
                ],
                spacing=10,
            ),
            bgcolor="#FFFFFF",
            border_radius=8,
            padding=12,
            on_click=on_click,
        )

    def show_article_text(self, category_id: str, article_idx: int):
        category = get_category_by_id(category_id)
        if not category:
            return
        articles = category.get("articles", [])
        if article_idx >= len(articles):
            return

        article = articles[article_idx]

        back_btn = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.ARROW_BACK, size=18, color="#5A00FF"),
                    ft.Text(f"К разделу «{category['name']}»", color="#5A00FF", size=13),
                ],
                spacing=5,
            ),
            on_click=lambda e: self.show_articles(category_id),
        )

        # ВАЖНО: ft.padding.all() удалён в Flet 0.85+.
        # Используем ft.Padding.all() (класс, не модуль).
        self.container.content = ft.Column(
            controls=[
                back_btn,
                ft.Text(article["title"], size=18, weight=ft.FontWeight.BOLD, color="#333333"),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text(article["content"], size=14, color="#333333", selectable=True),
                    padding=ft.Padding.all(15),
                    bgcolor="#FFFFFF",
                    border_radius=10,
                    expand=True,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.page.update()
