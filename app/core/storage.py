# app/core/storage.py
#
# Модуль хранения профиля и прогресса (Flet 1.0.5).
# Использует SharedPreferences.

import json
import flet as ft


async def load_profile() -> str:
    """Загружает имя профиля."""
    try:
        prefs = ft.SharedPreferences()
        name = await prefs.get("profile_name")
        return str(name) if name else ""
    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
        return ""


async def save_profile(name: str):
    """Сохраняет имя профиля."""
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("profile_name", name)
    except Exception as e:
        print(f"Ошибка сохранения профиля: {e}")


async def load_progress() -> dict:
    """
    Загружает прогресс из SharedPreferences (в виде JSON-строки).
    Возвращает словарь {case_id: {"status": "passed", "time": 45}}.
    """
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
    """Сохраняет прогресс в виде JSON-строки."""
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("progress_data", json.dumps(progress))
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")
