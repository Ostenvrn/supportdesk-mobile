# app/core/achievements.py
#
# Система достижений (ачивок).
# Проверяет условия и сохраняет полученные ачивки.

import flet as ft


# Список всех доступных ачивок.
# id: уникальный ключ
# title: название
# description: описание
# icon: иконка (emoji или ft.Icons)
ALL_ACHIEVEMENTS = [
    {
        "id": "first_blood",
        "title": "Первая кровь",
        "description": "Решил первую заявку",
        "icon": "🩸",
    },
    {
        "id": "speed_demon",
        "title": "Скорострел",
        "description": "Решил заявку быстрее чем за 1 минуту",
        "icon": "⚡",
    },
    {
        "id": "expert",
        "title": "Эксперт L2",
        "description": "Решил 10 заявок",
        "icon": "🧠",
    },
    {
        "id": "gov_master",
        "title": "Госсектор",
        "description": "Прошёл 3 заявки из госучреждений",
        "icon": "🛡️",
    },
    {
        "id": "perfect_run",
        "title": "Безупречно",
        "description": "Решил заявку без единой ошибки (в продвинутом режиме)",
        "icon": "✨",
    }
]


async def check_achievements(progress: dict, current_case: dict, time_spent: int, errors_count: int = 0) -> list:
    """
    Проверяет, какие ачивки нужно выдать после решения текущей заявки.
    Возвращает список новых ачивок (которые ещё не были получены).
    
    progress — текущий словарь прогресса (загруженный из SharedPreferences).
    current_case — данные текущей заявки (id, topic и т.д.).
    time_spent — время решения в секундах.
    errors_count — количество ошибок в продвинутом режиме (для ачивки "Безупречно").
    """
    # Получаем список уже полученных ачивок из прогресса (или пустой список).
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]
    new_achievements = []

    # 1. Первая кровь (если это первая решённая заявка)
    # Считаем общее количество решённых заявок (исключая служебный ключ __achievements__)
    solved_count = len([k for k in progress.keys() if not k.startswith("__")])
    if solved_count == 1 and "first_blood" not in earned_ids:
        new_achievements.append(_get_ach_by_id("first_blood"))

    # 2. Скорострел (меньше 60 секунд)
    if time_spent < 60 and "speed_demon" not in earned_ids:
        new_achievements.append(_get_ach_by_id("speed_demon"))

    # 3. Эксперт L2 (10 заявок)
    if solved_count >= 10 and "expert" not in earned_ids:
        new_achievements.append(_get_ach_by_id("expert"))

    # 4. Госсектор (3 заявки из topic == "gov")
    if "gov_master" not in earned_ids:
        gov_count = 0
        for k, v in progress.items():
            if not k.startswith("__") and isinstance(v, dict) and v.get("topic") == "gov":
                gov_count += 1
        if gov_count >= 3:
            new_achievements.append(_get_ach_by_id("gov_master"))

    # 5. Безупречно (продвинутый режим, 0 ошибок)
    if errors_count == 0 and "perfect_run" not in earned_ids:
        # Добавляем только если это была продвинутая заявка (проверяем по id или флагу)
        if current_case.get("advanced"):
            new_achievements.append(_get_ach_by_id("perfect_run"))

    return new_achievements


def _get_ach_by_id(ach_id: str) -> dict:
    """Возвращает объект ачивки по её id."""
    for a in ALL_ACHIEVEMENTS:
        if a["id"] == ach_id:
            return a
    return {}


async def save_achievements(progress: dict, new_achievements: list) -> dict:
    """
    Добавляет новые ачивки в прогресс и возвращает обновлённый словарь.
    """
    if not new_achievements:
        return progress

    # Получаем уже имеющиеся
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]

    for a in new_achievements:
        if a and a["id"] not in earned_ids:
            earned.append(a)

    progress["__achievements__"] = earned
    return progress


def get_all_achievements() -> list:
    """Возвращает список всех ачивок (для отображения в профиле)."""
    return ALL_ACHIEVEMENTS
