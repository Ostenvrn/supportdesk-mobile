# app/ui/theme_colors.py
#
# Модуль для работы с цветами.
# Возвращает цвета в зависимости от текущей темы (светлая/темная).

import flet as ft


def is_dark(page: ft.Page) -> bool:
    """Проверяет, включена ли темная тема."""
    return page.theme_mode == ft.ThemeMode.DARK


# --- Цвета текста ---

def text_primary(page: ft.Page) -> str:
    """Основной текст (заголовки)."""
    return "#FFFFFF" if is_dark(page) else "#333333"


def text_secondary(page: ft.Page) -> str:
    """Второстепенный текст (описания, подсказки)."""
    return "#AAAAAA" if is_dark(page) else "#666666"


def text_muted(page: ft.Page) -> str:
    """Приглушенный текст (серый)."""
    return "#777777" if is_dark(page) else "#888888"


def text_accent(page: ft.Page) -> str:
    """Акцентный текст (фиолетовый)."""
    return "#B388FF" if is_dark(page) else "#5A00FF"


def text_error(page: ft.Page) -> str:
    """Текст ошибки (красный)."""
    return "#FF6B6B" if is_dark(page) else "#E63946"


def text_success(page: ft.Page) -> str:
    """Текст успеха (зеленый)."""
    return "#69DB7C" if is_dark(page) else "#00A896"


def text_info(page: ft.Page) -> str:
    """Текст информации (синий)."""
    return "#74C0FC" if is_dark(page) else "#0056B3"


# --- Цвета фона ---

def bg_primary(page: ft.Page) -> str:
    """Основной фон (самый темный/светлый)."""
    return "#121212" if is_dark(page) else "#F4F6F9"


def bg_card(page: ft.Page) -> str:
    """Фон карточек."""
    return "#1E1E1E" if is_dark(page) else "#FFFFFF"


def bg_card_alt(page: ft.Page) -> str:
    """Альтернативный фон карточек (для контраста)."""
    return "#2D2D2D" if is_dark(page) else "#F8F9FA"


def bg_error(page: ft.Page) -> str:
    """Фон блока ошибки."""
    return "#4A1C1C" if is_dark(page) else "#FFF3F3"


def bg_info(page: ft.Page) -> str:
    """Фон информационного блока."""
    return "#1C2C4A" if is_dark(page) else "#E7F1FF"


# --- Цвета рамок ---

def border_color(page: ft.Page) -> str:
    """Цвет рамок."""
    return "#333333" if is_dark(page) else "#CED4DA"
