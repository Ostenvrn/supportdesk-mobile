# app/core/storage.py

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
    try:
        prefs = ft.SharedPreferences()
        await prefs.set("profile_name", "")
        await prefs.set("progress_data", "{}")
        await prefs.set("dark_theme", False)
        await prefs.set("quiz_results", "[]") # Очищаем и тесты
    except Exception as e:
        print(f"Ошибка сброса данных: {e}")


# --- Новые функции для тестов ---

async def load_quiz_results() -> list:
    """Загружает историю результатов тестов."""
    try:
        prefs = ft.SharedPreferences()
        raw = await prefs.get("quiz_results")
        if raw:
            return json.loads(raw)
        return []
    except Exception as e:
        print(f"Ошибка загрузки результатов тестов: {e}")
        return []


async def save_quiz_result(level: int, correct: int, total: int, time_spent: int):
    """Сохраняет результат нового теста."""
    try:
        history = await load_quiz_results()
        from datetime import datetime
        new_result = {
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "level": level,
            "correct": correct,
            "total": total,
            "time": time_spent
        }
        history.append(new_result)
        prefs = ft.SharedPreferences()
        await prefs.set("quiz_results", json.dumps(history))
    except Exception as e:
        print(f"Ошибка сохранения результата теста: {e}")
