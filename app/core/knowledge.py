# app/core/knowledge.py
#
# Загрузка базы знаний из assets/knowledge.json.
# Добавлен поиск по категориям и статьям.

import json
from importlib import resources


def load_knowledge() -> dict:
    """Загружает базу знаний из assets/knowledge.json."""
    try:
        data_file = resources.files("assets").joinpath("knowledge.json")
        with data_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки базы знаний: {e}")
        return {"categories": []}


def get_categories() -> list:
    """Возвращает список категорий из базы знаний."""
    db = load_knowledge()
    return db.get("categories", [])


def get_category_by_id(category_id: str) -> dict:
    """Возвращает категорию по её id."""
    for cat in get_categories():
        if cat.get("id") == category_id:
            return cat
    return {}


def search_knowledge(query: str) -> list:
    """
    Ищет совпадения по названиям категорий и статей.
    Возвращает список словарей {"type": "category"/"article", "category_id": ..., "article_index": ..., "title": ..., "text": ...}.
    """
    query = query.lower().strip()
    if not query:
        return []

    results = []
    categories = get_categories()

    for cat in categories:
        # Поиск по названию категории
        if query in cat["name"].lower():
            results.append({
                "type": "category",
                "category_id": cat["id"],
                "title": cat["name"],
                "text": cat.get("description", "")
            })

        # Поиск по статьям внутри категории
        for idx, article in enumerate(cat.get("articles", [])):
            if query in article["title"].lower() or query in article.get("content", "").lower():
                results.append({
                    "type": "article",
                    "category_id": cat["id"],
                    "article_index": idx,
                    "title": article["title"],
                    "text": article.get("content", "")[:100] + "..." # Превью
                })

    return results
