# app/core/storage.py
#
# Модуль хранения профиля (Flet 1.0.5).
# SharedPreferences в 1.0 — асинхронный сервис: методы нужно await-ить.

import flet as ft


async def load_profile() -> str:
    """
    Загружает имя профиля из SharedPreferences.
    Возвращает "" если профиль не создан.
    """
    try:
        prefs = ft.SharedPreferences()
        name = await prefs.get("profile_name")
        return str(name) if name else ""
    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
        return ""


async def save_profile(name: str):
    """
    Сохраняет имя профиля в SharedPreferences.
    """
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("profile_name", name)
    except Exception as e:
        print(f"Ошибка сохранения профиля: {e}")


async def load_progress() -> dict:
    """Заглушка прогресса."""
    return {}


async def save_progress(progress: dict):
    """Заглушка сохранения прогресса."""
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("progress", "{}")
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")
