# tests/test_achievements.py

import pytest
from unittest.mock import patch
from app.core.achievements import check_achievements, save_achievements, get_all_achievements


class TestAchievements:
    """Тесты для системы достижений."""

    @pytest.mark.asyncio
    async def test_first_blood(self):
        """Проверка ачивки 'Первая кровь'."""
        progress = {"case_1": {"status": "passed"}} # Имитируем, что заявка уже записана
        current_case = {"id": "case_1", "topic": "internet", "advanced": False}
        
        new_achievements = await check_achievements(progress, current_case, time_spent=120, errors_count=0)
        
        ach_ids = [a["id"] for a in new_achievements]
        assert "first_blood" in ach_ids

    @pytest.mark.asyncio
    async def test_speed_demon(self):
        """Проверка ачивки 'Скорострел' (меньше 60 секунд)."""
        progress = {"case_1": {"status": "passed"}}
        current_case = {"id": "case_1", "topic": "internet", "advanced": False}
        
        new_achievements = await check_achievements(progress, current_case, time_spent=45, errors_count=0)
        
        ach_ids = [a["id"] for a in new_achievements]
        assert "speed_demon" in ach_ids

    @pytest.mark.asyncio
    async def test_veteran_5(self):
        """Проверка ачивки 'Пятерня' (5 заявок)."""
        progress = {
            "case_1": {"status": "passed"},
            "case_2": {"status": "passed"},
            "case_3": {"status": "passed"},
            "case_4": {"status": "passed"},
            "case_5": {"status": "passed"},
        }
        current_case = {"id": "case_5", "topic": "internet", "advanced": False}
        
        new_achievements = await check_achievements(progress, current_case, time_spent=120, errors_count=0)
        
        ach_ids = [a["id"] for a in new_achievements]
        assert "veteran_5" in ach_ids

    @pytest.mark.asyncio
    async def test_perfect_run_advanced(self):
        """Проверка ачивки 'Безупречно' (0 ошибок в продвинутом режиме)."""
        progress = {"adv_1": {"status": "passed"}}
        current_case = {"id": "adv_1", "topic": "gov", "advanced": True}
        
        new_achievements = await check_achievements(progress, current_case, time_spent=120, errors_count=0)
        
        ach_ids = [a["id"] for a in new_achievements]
        assert "perfect_run" in ach_ids

    @pytest.mark.asyncio
    async def test_survivor(self):
        """Проверка ачивки 'Выживший' (5 ошибок, но заявка решена)."""
        progress = {"case_1": {"status": "passed"}}
        current_case = {"id": "case_1", "topic": "internet", "advanced": False}
        
        new_achievements = await check_achievements(progress, current_case, time_spent=120, errors_count=5)
        
        ach_ids = [a["id"] for a in new_achievements]
        assert "survivor" in ach_ids

    @pytest.mark.asyncio
    @patch("app.core.achievements.datetime")
    async def test_night_shift(self, mock_datetime):
        """Проверка ачивки 'Ночная смена' (время 02:00)."""
        # Настраиваем мок, чтобы datetime.now() возвращал 2 часа ночи
        mock_datetime.now.return_value.hour = 2
        
        progress = {"case_1": {"status": "passed"}}
        current_case = {"id": "case_1", "topic": "internet", "advanced": False}
        
        new_achievements = await check_achievements(progress, current_case, time_spent=120, errors_count=0)
        
        ach_ids = [a["id"] for a in new_achievements]
        assert "night_shift" in ach_ids

    @pytest.mark.asyncio
    async def test_no_duplicates(self):
        """Проверка, что ачивки не дублируются при сохранении."""
        progress = {}
        ach1 = {"id": "first_blood", "title": "Первая кровь", "icon": "🩸"}
        
        progress = await save_achievements(progress, [ach1])
        assert len(progress["__achievements__"]) == 1
        
        progress = await save_achievements(progress, [ach1])
        assert len(progress["__achievements__"]) == 1
