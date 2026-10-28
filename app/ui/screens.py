# app/ui/screens.py
#
# Экраны приложения.
# Справочник (с поиском) + Экран выбора тренажёра.

import flet as ft

from app.core.knowledge import get_categories, get_category_by_id, search_knowledge


class KnowledgeScreen:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_category = None
        self.container = ft.Container(expand=True)
        self.search_results_container = ft.Column(visible=False)
        self.categories_container = ft.Column()

    def build(self) -> ft.Control:
        self.show_categories()

        # Поле поиска
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
                ft.Row(
                    controls=[
                        ft.Icon(icon=ft.Icons.MENU_BOOK, color="#5A00FF", size=28),
                        ft.Text("Справочник", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                    ],
                    spacing=10,
                ),
                ft.Container(height=10),
                search_input,
                ft.Container(height=15),
                self.search_results_container, # Контейнер для результатов поиска
                self.categories_container,      # Контейнер для обычного списка
            ],
            expand=True,
        )

    def _on_search_change(self, e):
        query = e.control.value.strip()
        if not query:
            # Если пусто — показываем категории
            self.search_results_container.visible = False
            self.categories_container.visible = True
            self.page.update()
            return

        # Выполняем поиск
        results = search_knowledge(query)
        
        # Скрываем категории, показываем результаты
        self.categories_container.visible = False
        self.search_results_container.visible = True
        self.search_results_container.controls.clear()

        if not results:
            self.search_results_container.controls.append(
                ft.Text("Ничего не найдено.", color="#666666", italic=True)
            )
        else:
            for res in results:
                if res["type"] == "category":
                    btn = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.FOLDER, color="#5A00FF"),
                                ft.Column(
                                    controls=[
                                        ft.Text(res["title"], size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text("Категория", size=10, color="#888888")
                                    ],
                                    spacing=0
                                )
                            ]
                        ),
                        padding=10,
                        bgcolor="#FFFFFF",
                        border_radius=8,
                        on_click=lambda e, cat_id=res["category_id"]: self.show_articles(cat_id)
                    )
                    self.search_results_container.controls.append(btn)

                elif res["type"] == "article":
                    btn = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ARTICLE, color="#5A00FF"),
                                ft.Column(
                                    controls=[
                                        ft.Text(res["title"], size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text(res["text"], size=12, color="#666666", max_lines=2)
                                    ],
                                    spacing=0,
                                    expand=True
                                )
                            ]
                        ),
                        padding=10,
                        bgcolor="#FFFFFF",
                        border_radius=8,
                        on_click=lambda e, cat_id=res["category_id"], idx=res["article_index"]: self.show_article_text(cat_id, idx)
                    )
                    self.search_results_container.controls.append(btn)

        self.page.update()

    def show_categories(self):
        categories = get_categories()
        if not categories:
            self.categories_container.controls.append(ft.Text("База знаний пуста.", color="#666666", italic=True))
            self.page.update()
            return

        self.categories_container.controls.clear()

        cards = []
        for cat in categories:
            cards.append(self._make_category_card(cat))

        self.categories_container.controls = [
            ft.Text("Выберите раздел:", size=14, color="#666666"),
            ft.Container(height=8),
            ft.Column(controls=cards, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True),
        ]
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
        # Скрываем поиск при переходе к статьям
        self.search_results_container.visible = False
        self.categories_container.visible = True

        category = get_category_by_id(category_id)
        if not category:
            return

        self.current_category = category
        articles = category.get("articles", [])
        if not articles:
            self.categories_container.controls = [ft.Text("В этой категории пока нет статей.", color="#666666", italic=True)]
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

        self.categories_container.controls = [
            back_btn,
            ft.Text(category["name"], size=18, weight=ft.FontWeight.BOLD, color="#333333"),
            ft.Container(height=5),
            ft.Column(controls=cards, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True),
        ]
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
        self.search_results_container.visible = False
        self.categories_container.visible = True

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

        self.categories_container.controls = [
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
        ]
        self.page.update()


class SimulatorSelectionScreen:
    """Экран выбора уровня (L1, L2, L3) и режима (Обычный/Продвинутый)."""
    def __init__(self, page: ft.Page, on_start_simulator):
        self.page = page
        self.on_start_simulator = on_start_simulator # callback (level, is_advanced)
        self.container = ft.Container(expand=True, alignment=ft.Alignment.CENTER)

    def build(self) -> ft.Control:
        def make_level_card(level: int, title: str, desc: str, color: str):
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(icon=ft.Icons.LAYERS, size=40, color=color),
                        ft.Text(f"Уровень L{level}", size=18, weight=ft.FontWeight.BOLD, color="#333333"),
                        ft.Text(title, size=14, color=color, weight=ft.FontWeight.BOLD),
                        ft.Text(desc, size=12, color="#666666", text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                bgcolor="#FFFFFF",
                padding=20,
                border_radius=14,
                width=160,
                height=160,
                shadow=ft.BoxShadow(blur_radius=4, color="#00000015"),
            )

        card_l1 = make_level_card(1, "Базовая диагностика", "Кабель, роутер, DNS, простые сбои", "#00A896")
        card_l2 = make_level_card(2, "Сетевые проблемы", "Wi-Fi, VLAN, скорость, маршруты", "#5A00FF")
        card_l3 = make_level_card(3, "Инфраструктура", "B2B, VPN, госучреждения, ЭЦП", "#E63946")

        def start_level(level: int, is_advanced: bool):
            self.on_start_simulator(level, is_advanced)

        card_l1.on_click = lambda e: start_level(1, False)
        card_l2.on_click = lambda e: start_level(2, False)
        card_l3.on_click = lambda e: start_level(3, False)

        mode_label = ft.Text("Режим прохождения:", size=16, weight=ft.FontWeight.BOLD, color="#333333")
        
        normal_btn = ft.Button(
            content=ft.Text("Обычный режим (с подсказками)", color="#FFFFFF"),
            bgcolor="#333333",
            width=300,
            height=45,
            on_click=lambda e: self._show_mode_selection(start_level, is_advanced=False),
        )
        
        advanced_btn = ft.Button(
            content=ft.Text("Продвинутый режим (ручной ввод)", color="#FFFFFF"),
            bgcolor="#5A00FF",
            width=300,
            height=45,
            on_click=lambda e: self._show_mode_selection(start_level, is_advanced=True),
        )

        self.container.content = ft.Column(
            controls=[
                ft.Text("Выберите уровень поддержки", size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                ft.Container(height=20),
                ft.Row(controls=[card_l1, card_l2, card_l3], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
                ft.Container(height=30),
                mode_label,
                ft.Container(height=10),
                ft.Row(controls=[normal_btn, advanced_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
        return self.container

    def _show_mode_selection(self, start_callback, is_advanced: bool):
        def make_level_btn(level: int, name: str):
            return ft.Button(
                content=ft.Text(f"Уровень L{level} ({name})", color="#FFFFFF"),
                bgcolor="#5A00FF",
                width=300,
                height=45,
                on_click=lambda e: (self.page.pop_dialog(), start_callback(level, is_advanced)),
            )

        dialog = ft.AlertDialog(
            title=ft.Text("Выберите уровень"),
            content=ft.Column(
                controls=[
                    make_level_btn(1, "Базовая диагностика"),
                    make_level_btn(2, "Сетевые проблемы"),
                    make_level_btn(3, "Инфраструктура"),
                ],
                tight=True,
                spacing=10,
            ),
            actions=[ft.TextButton("Отмена", on_click=lambda _: self.page.pop_dialog())],
        )
        self.page.show_dialog(dialog)
