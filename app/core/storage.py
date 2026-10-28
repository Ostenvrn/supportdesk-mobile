# app/core/storage.py
#
# Модуль хранения профиля, прогресса и темы.

import json
import flet as ft


async def load_profile() -> str:
    try:
        prefs = ft.SharedPreferences()
        name = await prefs.get("profile_name")
        return str(name) if name else ""
    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
        return ""


async def save_profile(name: str):
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("profile_name", name)
    except Exception as e:
        print(f"Ошибка сохранения профиля: {e}")


async def load_progress() -> dict:
    try:
        prefs = ft.SharedPreferences()
        raw = await prefs.get("progress_data")
        if raw:
            return json.loads(raw)
        return {}
    except Exception as e:
        print(f"Ошибка загрузки прогресса: {e}")
        return {}


async def save_progress(progress: dict):
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("progress_data", json.dumps(progress))
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")


async def load_theme() -> bool:
    try:
        prefs = ft.SharedPreferences()
        is_dark = await prefs.get("dark_theme")
        return bool(is_dark)
    except Exception:
        return False


async def save_theme(is_dark: bool):
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("dark_theme", is_dark)
    except Exception as e:
        print(f"Ошибка сохранения темы: {e}")


async def reset_all_data():
    """Сбрасывает профиль, прогресс и тему."""
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("profile_name", "")
        await prefs.set("progress_data", "{}")
        await prefs.set("dark_theme", False)
    except Exception as e:
        print(f"Ошибка сброса данных: {e}")
