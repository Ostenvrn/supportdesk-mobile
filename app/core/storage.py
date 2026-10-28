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
        await prefs.set("quiz_results", "[]")
        await prefs.set("articles_read", "[]")
    except Exception as e:
        print(f"Ошибка сброса данных: {e}")


async def load_quiz_results() -> list:
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


# --- Учёт прочитанных статей ---

async def load_articles_read() -> list:
    """Возвращает список ID прочитанных статей (category_id + article_idx)."""
    try:
        prefs = ft.SharedPreferences()
        raw = await prefs.get("articles_read")
        if raw:
            return json.loads(raw)
        return []
    except Exception:
        return []


async def mark_article_read(category_id: str, article_idx: int):
    """Отмечает статью как прочитанную."""
    try:
        read_list = await load_articles_read()
        article_id = f"{category_id}_{article_idx}"
        if article_id not in read_list:
            read_list.append(article_id)
            prefs = ft.SharedPreferences()
            await prefs.set("articles_read", json.dumps(read_list))
    except Exception as e:
        print(f"Ошибка сохранения прочитанной статьи: {e}")
