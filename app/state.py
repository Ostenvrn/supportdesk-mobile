# app/state.py
#
# Глобальное состояние приложения.
# Простые переменные, которые передаются между экранами.
#
# Что храним:
# - profile_name: имя пользователя (из профиля).
# - profile_created: флаг, что профиль создан.
# - progress: прогресс по кейсам (заполнится позже).


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
