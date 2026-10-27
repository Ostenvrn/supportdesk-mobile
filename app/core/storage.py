# app/core/storage.py
#
# Модуль хранения профиля и прогресса.
# Использует SharedPreferences (Flet 1.0.5).

import flet as ft


def load_profile() -> str:
    """
    Загружает имя профиля из SharedPreferences.
    Возвращает "" если профиль не создан.
    """
    try:
        prefs = ft.SharedPreferences()
        name = prefs.get("profile_name") or ""
        return str(name)
    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
        return ""


def save_profile(name: str):
    """
    Сохраняет имя профиля в SharedPreferences.
    """
    try:
        prefs = ft.SharedPreferences()
        prefs.set("profile_name", name)
    except Exception as e:
        print(f"Ошибка сохранения профиля: {e}")


def load_progress() -> dict:
    """
    Загружает прогресс (заглушка — пустой словарь).
    """
    return {}


def save_progress(progress: dict):
    """
    Сохраняет прогресс (заглушка).
    """
    try:
        prefs = ft.SharedPreferences()
        # Пока сохраняем пустую строку (прогресс будет в тренажёре)
        prefs.set("progress", "{}")
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")
