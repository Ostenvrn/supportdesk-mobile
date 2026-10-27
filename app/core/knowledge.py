# app/core/knowledge.py
#
# Загрузка базы знаний из assets/knowledge.json.
#
# Используем importlib.resources, чтобы файл находился и при запуске
# из исходников (Linux), и внутри APK на Android.

import json
from importlib import resources


def load_knowledge() -> dict:
    """
    Загружает базу знаний из assets/knowledge.json.
    Возвращает словарь с ключом "categories".
    При ошибке возвращает пустой словарь.
    """
    try:
        # resources.files("assets") находит пакет/папку assets.
        # На Android Flet упаковывает assets в приложение.
        data_file = resources.files("assets").joinpath("knowledge.json")
        with data_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки базы знаний: {e}")
        return {"categories": []}


def get_categories() -> list:
    """
    Возвращает список категорий из базы знаний.
    """
    db = load_knowledge()
    return db.get("categories", [])


def get_category_by_id(category_id: str) -> dict:
    """
    Возвращает категорию по её id (или пустой словарь).
    """
    for cat in get_categories():
        if cat.get("id") == category_id:
            return cat
    return {}
