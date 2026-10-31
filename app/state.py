# app/state.py
#
# Глобальное состояние приложения.

# Версия приложения (менять при каждом релизе)
APP_VERSION = "1.2.0"

# Имя профиля (пусто, если профиль ещё не создан).
profile_name = ""

# Флаг создания профиля.
profile_created = False

# Прогресс: словарь вида {case_id: "passed" / "failed"}.
progress = {}


def reset_state():
    """
    Сбрасывает состояние (используется для отладки/тестов).
    """
    global profile_name, profile_created, progress
    profile_name = ""
    profile_created = False
    progress = {}
