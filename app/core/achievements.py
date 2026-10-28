# app/core/achievements.py
#
# Система достижений (ачивок).

import flet as ft


ALL_ACHIEVEMENTS = [
    # Базовые
    {"id": "first_blood", "title": "Первая кровь", "description": "Решил первую заявку", "icon": "🩸"},
    {"id": "speed_demon", "title": "Скорострел", "description": "Решил заявку быстрее чем за 1 минуту", "icon": "⚡"},
    {"id": "veteran_5", "title": "Пятерня", "description": "Решил 5 заявок", "icon": "🖐️"},
    {"id": "expert_l2", "title": "Эксперт L2", "description": "Решил 10 заявок", "icon": "🧠"},
    {"id": "veteran_25", "title": "Ветеран", "description": "Решил 25 заявок", "icon": "🎖️"},
    
    # Тематические
    {"id": "gov_master", "title": "Госсектор", "description": "Прошёл 3 заявки из госучреждений", "icon": "🛡️"},
    {"id": "net_guru", "title": "Сетевой гуру", "description": "Решил 5 заявок по теме интернета", "icon": "🌐"},
    {"id": "tv_master", "title": "Телемастер", "description": "Решил 3 заявки по теме ТВ", "icon": "📺"},
    {"id": "eye_of_falcon", "title": "Глаз-алмаз", "description": "Решил 3 заявки по видеонаблюдению", "icon": "👁️"},
    
    # Качество
    {"id": "perfect_run", "title": "Безупречно", "description": "Решил заявку без единой ошибки", "icon": "✨"},
    {"id": "survivor", "title": "Выживший", "description": "Допустил 5 ошибок, но довёл заявку до конца", "icon": "💀"},
    {"id": "fast_learner", "title": "Схватываю на лету", "description": "Решил 3 заявки подряд без ошибок", "icon": "🚀"},
    
    # --- НОВЫЕ АЧИВКИ ---
    {"id": "perfect_test", "title": "Перфекционист", "description": "Сдал тест на 100% (20 из 20)", "icon": "💯"},
    {"id": "theory_master", "title": "Теоретик", "description": "Прошёл тесты L1, L2 и L3", "icon": "🎓"},
    {"id": "bookworm", "title": "Книжный червь", "description": "Прочитал 10 статей в Справочнике", "icon": "📚"},
    {"id": "night_owl", "title": "Ночной инженер", "description": "Пользовался программой в тёмной теме", "icon": "🦉"},
    {"id": "marathon", "title": "Марафонец", "description": "Решил 5 заявок подряд", "icon": "🏃"},
    {"id": "reset_button", "title": "Начать сначала", "description": "Сбросил прогресс, чтобы учиться заново", "icon": "🔄"}
]


async def check_achievements(progress: dict, current_case: dict, time_spent: int, errors_count: int = 0, quiz_results: list = None) -> list:
    """
    Проверяет ачивки для тренажёра.
    """
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]
    new_achievements = []

    all_cases = {k: v for k, v in progress.items() if not k.startswith("__")}
    solved_count = len(all_cases)

    # 1. Первая кровь
    if solved_count >= 1 and "first_blood" not in earned_ids:
        new_achievements.append(_get_ach_by_id("first_blood"))

    # 2. Скорострел
    if time_spent < 60 and "speed_demon" not in earned_ids:
        new_achievements.append(_get_ach_by_id("speed_demon"))

    # 3. Пятерня
    if solved_count >= 5 and "veteran_5" not in earned_ids:
        new_achievements.append(_get_ach_by_id("veteran_5"))

    # 4. Эксперт L2
    if solved_count >= 10 and "expert_l2" not in earned_ids:
        new_achievements.append(_get_ach_by_id("expert_l2"))

    # 5. Ветеран
    if solved_count >= 25 and "veteran_25" not in earned_ids:
        new_achievements.append(_get_ach_by_id("veteran_25"))

    # 6-9. Тематические
    topic_counts = {}
    for k, v in all_cases.items():
        if isinstance(v, dict):
            topic = v.get("topic", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    if topic_counts.get("gov", 0) >= 3 and "gov_master" not in earned_ids:
        new_achievements.append(_get_ach_by_id("gov_master"))
    if topic_counts.get("internet", 0) >= 5 and "net_guru" not in earned_ids:
        new_achievements.append(_get_ach_by_id("net_guru"))
    if topic_counts.get("tv", 0) >= 3 and "tv_master" not in earned_ids:
        new_achievements.append(_get_ach_by_id("tv_master"))
    if topic_counts.get("cameras", 0) >= 3 and "eye_of_falcon" not in earned_ids:
        new_achievements.append(_get_ach_by_id("eye_of_falcon"))

    # 10-12. Качество
    if errors_count == 0 and "perfect_run" not in earned_ids:
        if current_case.get("advanced"):
            new_achievements.append(_get_ach_by_id("perfect_run"))

    if errors_count >= 5 and "survivor" not in earned_ids:
        new_achievements.append(_get_ach_by_id("survivor"))

    if errors_count == 0:
        no_error_streak = 0
        for k, v in all_cases.items():
            if isinstance(v, dict) and v.get("no_errors"):
                no_error_streak += 1
            else:
                no_error_streak = 0
        if no_error_streak >= 2 and "fast_learner" not in earned_ids:
            new_achievements.append(_get_ach_by_id("fast_learner"))

    # 13. Перфекционист (тест на 100%)
    # Эта проверка будет вызываться отдельно из quiz.py, но на всякий случай оставим
    if quiz_results:
        for res in quiz_results:
            if res["correct"] == res["total"] and "perfect_test" not in earned_ids:
                new_achievements.append(_get_ach_by_id("perfect_test"))

    return new_achievements


async def check_quiz_achievements(quiz_results: list, progress: dict) -> list:
    """Проверяет ачивки, связанные с тестами."""
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]
    new_achievements = []

    # 13. Перфекционист
    for res in quiz_results:
        if res["correct"] == res["total"] and "perfect_test" not in earned_ids:
            new_achievements.append(_get_ach_by_id("perfect_test"))
            break

    # 14. Теоретик (пройдены все три уровня)
    levels_passed = set()
    for res in quiz_results:
        # Считаем тест пройденным, если правильных >= 15
        if res["correct"] >= 15:
            levels_passed.add(res["level"])
    
    if len(levels_passed) == 3 and "theory_master" not in earned_ids:
        new_achievements.append(_get_ach_by_id("theory_master"))

    return new_achievements


async def check_library_achievement(progress: dict, articles_read: int) -> list:
    """Проверяет ачивку за чтение статей."""
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]
    new_achievements = []

    if articles_read >= 10 and "bookworm" not in earned_ids:
        new_achievements.append(_get_ach_by_id("bookworm"))

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
