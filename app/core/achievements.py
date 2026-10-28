# app/core/achievements.py
#
# Система достижений (ачивок).
# Проверяет условия и сохраняет полученные ачивки.

import flet as ft


# Список всех доступных ачивок.
ALL_ACHIEVEMENTS = [
    {"id": "first_blood", "title": "Первая кровь", "description": "Решил первую заявку", "icon": "🩸"},
    {"id": "speed_demon", "title": "Скорострел", "description": "Решил заявку быстрее чем за 1 минуту", "icon": "⚡"},
    {"id": "expert_l2", "title": "Эксперт L2", "description": "Решил 10 заявок", "icon": "🧠"},
    {"id": "gov_master", "title": "Госсектор", "description": "Прошёл 3 заявки из госучреждений", "icon": "🛡️"},
    {"id": "perfect_run", "title": "Безупречно", "description": "Решил заявку без единой ошибки", "icon": "✨"},
    
    # Новые ачивки
    {"id": "veteran_5", "title": "Пятерня", "description": "Решил 5 заявок", "icon": "🖐️"},
    {"id": "veteran_25", "title": "Ветеран", "description": "Решил 25 заявок", "icon": "🎖️"},
    {"id": "net_guru", "title": "Сетевой гуру", "description": "Решил 5 заявок по теме интернета", "icon": "🌐"},
    {"id": "tv_master", "title": "Телемастер", "description": "Решил 3 заявки по теме ТВ", "icon": "📺"},
    {"id": "eye_of_falcon", "title": "Глаз-алмаз", "description": "Решил 3 заявки по видеонаблюдению", "icon": "👁️"},
    {"id": "survivor", "title": "Выживший", "description": "Допустил 5 ошибок в одной заявке, но довёл её до конца", "icon": "💀"},
    {"id": "fast_learner", "title": "Схватываю на лету", "description": "Решил 3 заявки подряд без ошибок", "icon": "🚀"}
]


async def check_achievements(progress: dict, current_case: dict, time_spent: int, errors_count: int = 0) -> list:
    """
    Проверяет, какие ачивки нужно выдать после решения текущей заявки.
    """
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]
    new_achievements = []

    # Собираем статистику по всем пройденным заявкам (исключая служебные ключи)
    all_cases = {k: v for k, v in progress.items() if not k.startswith("__")}
    solved_count = len(all_cases)

    # Считаем количество по темам
    topic_counts = {}
    for k, v in all_cases.items():
        if isinstance(v, dict):
            topic = v.get("topic", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # 1. Первая кровь (если решена хотя бы одна заявка)
    if solved_count >= 1 and "first_blood" not in earned_ids:
        new_achievements.append(_get_ach_by_id("first_blood"))

    # 2. Скорострел (меньше 60 секунд)
    if time_spent < 60 and "speed_demon" not in earned_ids:
        new_achievements.append(_get_ach_by_id("speed_demon"))

    # 3. Пятерня (5 заявок)
    if solved_count >= 5 and "veteran_5" not in earned_ids:
        new_achievements.append(_get_ach_by_id("veteran_5"))

    # 4. Эксперт L2 (10 заявок)
    if solved_count >= 10 and "expert_l2" not in earned_ids:
        new_achievements.append(_get_ach_by_id("expert_l2"))

    # 5. Ветеран (25 заявок)
    if solved_count >= 25 and "veteran_25" not in earned_ids:
        new_achievements.append(_get_ach_by_id("veteran_25"))

    # 6. Госсектор (3 заявки из gov)
    if topic_counts.get("gov", 0) >= 3 and "gov_master" not in earned_ids:
        new_achievements.append(_get_ach_by_id("gov_master"))
        
    # 7. Сетевой гуру (5 заявок из internet)
    if topic_counts.get("internet", 0) >= 5 and "net_guru" not in earned_ids:
        new_achievements.append(_get_ach_by_id("net_guru"))

    # 8. Телемастер (3 заявки из tv)
    if topic_counts.get("tv", 0) >= 3 and "tv_master" not in earned_ids:
        new_achievements.append(_get_ach_by_id("tv_master"))

    # 9. Глаз-алмаз (3 заявки из cameras)
    if topic_counts.get("cameras", 0) >= 3 and "eye_of_falcon" not in earned_ids:
        new_achievements.append(_get_ach_by_id("eye_of_falcon"))

    # 10. Безупречно (продвинутый режим, 0 ошибок)
    if errors_count == 0 and "perfect_run" not in earned_ids:
        if current_case.get("advanced"):
            new_achievements.append(_get_ach_by_id("perfect_run"))

    # 11. Выживший (5 ошибок, но заявка решена)
    if errors_count >= 5 and "survivor" not in earned_ids:
        new_achievements.append(_get_ach_by_id("survivor"))

    # 12. Схватываю на лету (3 заявки подряд без ошибок)
    # Для этого нам нужно знать историю последних заявок. 
    # Так как мы сохраняем прогресс, добавим флаг "no_errors" для каждой заявки.
    if errors_count == 0:
        # Считаем, сколько последних заявок были без ошибок
        no_error_streak = 0
        for k, v in all_cases.items():
            if isinstance(v, dict) and v.get("no_errors"):
                no_error_streak += 1
            else:
                no_error_streak = 0 # Сбрасываем, если была ошибка
        
        # Текущая заявка тоже без ошибок
        if no_error_streak >= 2 and "fast_learner" not in earned_ids:
            new_achievements.append(_get_ach_by_id("fast_learner"))

    return new_achievements


def _get_ach_by_id(ach_id: str) -> dict:
    for a in ALL_ACHIEVEMENTS:
        if a["id"] == ach_id:
            return a
    return {}


async def save_achievements(progress: dict, new_achievements: list) -> dict:
    if not new_achievements:
        return progress

    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]

    for a in new_achievements:
        if a and a["id"] not in earned_ids:
            earned.append(a)

    progress["__achievements__"] = earned
    return progress


def get_all_achievements() -> list:
    return ALL_ACHIEVEMENTS
