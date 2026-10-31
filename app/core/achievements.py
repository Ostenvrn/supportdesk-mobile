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
    
    # Тесты
    {"id": "perfect_test", "title": "Перфекционист", "description": "Сдал тест на 100% (20 из 20)", "icon": "💯"},
    {"id": "theory_master", "title": "Теоретик", "description": "Прошёл тесты L1, L2 и L3", "icon": "🎓"},
    {"id": "speed_test", "title": "Скоростной тест", "description": "Сдал тест быстрее чем за 3 минуты", "icon": "⏱️"},
    {"id": "first_test", "title": "Новичок в теории", "description": "Прошёл первый тест", "icon": "📝"},
    
    # Справочник и система
    {"id": "bookworm", "title": "Книжный червь", "description": "Прочитал 10 статей в Справочнике", "icon": "📚"},
    {"id": "night_owl", "title": "Ночной инженер", "description": "Пользовался программой в тёмной теме", "icon": "🦉"},
    {"id": "marathon", "title": "Марафонец", "description": "Решил 5 заявок подряд", "icon": "🏃"},
    {"id": "reset_button", "title": "Начать сначала", "description": "Сбросил прогресс, чтобы учиться заново", "icon": "🔄"},
    
    # Терминал
    {"id": "cmd_master", "title": "Мастер команд", "description": "Ввёл 10 команд вручную", "icon": "⌨️"},
    {"id": "no_hints", "title": "Без подсказок", "description": "Решил 5 заявок в продвинутом режиме", "icon": "🙈"},
    {"id": "night_shift", "title": "Ночная смена", "description": "Решил заявку после 00:00", "icon": "🌙"},
    {"id": "early_bird", "title": "Ранняя пташка", "description": "Решил заявку до 06:00", "icon": "🌅"},
    {"id": "b2b_hero", "title": "Герой B2B", "description": "Решил 3 корпоративные заявки", "icon": "💼"},
    {"id": "dns_hunter", "title": "Охотник за DNS", "description": "Решил 3 заявки по теме DNS", "icon": "🔍"},
    {"id": "test_streak", "title": "Стабильность", "description": "Прошёл 3 теста подряд на проходной балл", "icon": "📈"},
    {"id": "all_topics", "title": "Эрудит", "description": "Решил заявки из всех 4 тем", "icon": "🧩"},
    {"id": "fast_reader", "title": "Быстрое чтение", "description": "Прочитал 5 статей за один день", "icon": "📖"},
    {"id": "legend", "title": "Легенда поддержки", "description": "Достиг 50 решённых заявок", "icon": "👑"},
    
    # Новые в 1.3.0 (Терминал)
    {"id": "hacker", "title": "Хакер", "description": "Ввёл команду telnet в терминале", "icon": "💻"},
    {"id": "net_engineer", "title": "Сетевой инженер", "description": "Ввёл 100 команд в терминале", "icon": "🛠️"},
    {"id": "sfc_scan", "title": "Тяжелая артефакт", "description": "Запустил проверку системы (sfc /scannow)", "icon": "🩺"},
    {"id": "cleaner", "title": "Очиститель", "description": "Очистил экран терминала 10 раз", "icon": "🧹"}
]


async def check_achievements(progress: dict, current_case: dict, time_spent: int, errors_count: int = 0) -> list:
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]
    new_achievements = []

    all_cases = {k: v for k, v in progress.items() if not k.startswith("__")}
    solved_count = len(all_cases)

    if solved_count >= 1 and "first_blood" not in earned_ids: new_achievements.append(_get_ach_by_id("first_blood"))
    if time_spent < 60 and "speed_demon" not in earned_ids: new_achievements.append(_get_ach_by_id("speed_demon"))
    if solved_count >= 5 and "veteran_5" not in earned_ids: new_achievements.append(_get_ach_by_id("veteran_5"))
    if solved_count >= 10 and "expert_l2" not in earned_ids: new_achievements.append(_get_ach_by_id("expert_l2"))
    if solved_count >= 25 and "veteran_25" not in earned_ids: new_achievements.append(_get_ach_by_id("veteran_25"))
    if solved_count >= 50 and "legend" not in earned_ids: new_achievements.append(_get_ach_by_id("legend"))

    topic_counts = {}
    for k, v in all_cases.items():
        if isinstance(v, dict):
            topic = v.get("topic", "unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    if topic_counts.get("gov", 0) >= 3 and "gov_master" not in earned_ids: new_achievements.append(_get_ach_by_id("gov_master"))
    if topic_counts.get("internet", 0) >= 5 and "net_guru" not in earned_ids: new_achievements.append(_get_ach_by_id("net_guru"))
    if topic_counts.get("tv", 0) >= 3 and "tv_master" not in earned_ids: new_achievements.append(_get_ach_by_id("tv_master"))
    if topic_counts.get("cameras", 0) >= 3 and "eye_of_falcon" not in earned_ids: new_achievements.append(_get_ach_by_id("eye_of_falcon"))
    if topic_counts.get("dns", 0) >= 3 and "dns_hunter" not in earned_ids: new_achievements.append(_get_ach_by_id("dns_hunter"))
    
    if len([t for t in topic_counts.keys() if t in ["internet", "tv", "cameras", "gov"]]) == 4 and "all_topics" not in earned_ids:
         new_achievements.append(_get_ach_by_id("all_topics"))

    if errors_count == 0 and "perfect_run" not in earned_ids:
        if current_case.get("advanced"): new_achievements.append(_get_ach_by_id("perfect_run"))
    if errors_count >= 5 and "survivor" not in earned_ids: new_achievements.append(_get_ach_by_id("survivor"))
    if errors_count == 0:
        no_error_streak = 0
        for k, v in all_cases.items():
            if isinstance(v, dict) and v.get("no_errors"): no_error_streak += 1
            else: no_error_streak = 0
        if no_error_streak >= 2 and "fast_learner" not in earned_ids: new_achievements.append(_get_ach_by_id("fast_learner"))
        if no_error_streak >= 4 and "marathon" not in earned_ids: new_achievements.append(_get_ach_by_id("marathon"))

    from datetime import datetime
    now = datetime.now()
    if now.hour >= 0 and now.hour < 6 and "night_shift" not in earned_ids: new_achievements.append(_get_ach_by_id("night_shift"))
    if now.hour >= 6 and now.hour < 9 and "early_bird" not in earned_ids: new_achievements.append(_get_ach_by_id("early_bird"))

    return new_achievements


async def check_quiz_achievements(quiz_results: list, progress: dict) -> list:
    earned = progress.get("__achievements__", [])
    earned_ids = [a["id"] for a in earned]
    new_achievements = []

    if quiz_results and "first_test" not in earned_ids:
        new_achievements.append(_get_ach_by_id("first_test"))

    for res in quiz_results:
        if res["correct"] == res["total"] and "perfect_test" not in earned_ids:
            new_achievements.append(_get_ach_by_id("perfect_test"))
        if res["correct"] >= 15 and res.get("time", 999) < 180 and "speed_test" not in earned_ids:
            new_achievements.append(_get_ach_by_id("speed_test"))

    levels_passed = set()
    for res in quiz_results:
        if res["correct"] >= 15: levels_passed.add(res["level"])
    if len(levels_passed) == 3 and "theory_master" not in earned_ids:
        new_achievements.append(_get_ach_by_id("theory_master"))

    return new_achievements


async def check_library_achievement(progress: dict, articles_read: int) -> list:
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
