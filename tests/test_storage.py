# tests/test_storage.py

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.storage import (
    load_profile, save_profile, 
    load_progress, save_progress,
    load_theme, save_theme,
    load_quiz_results, save_quiz_result
)

# Создаем фейковый класс, который имитирует SharedPreferences
class MockSharedPreferences:
    def __init__(self):
        self.storage = {}

    async def get(self, key):
        return self.storage.get(key)

    async def set(self, key, value):
        self.storage[key] = value

# Фикстура для подмены SharedPreferences
@pytest.fixture
def mock_prefs():
    mock_instance = MockSharedPreferences()
    with patch("flet.SharedPreferences", return_value=mock_instance):
        yield mock_instance


class TestStorage:
    """Тесты для модуля хранения данных."""

    @pytest.mark.asyncio
    async def test_save_and_load_profile(self, mock_prefs):
        """Сохранение и загрузка имени профиля."""
        await save_profile("Александр")
        name = await load_profile()
        assert name == "Александр"

    @pytest.mark.asyncio
    async def test_load_empty_profile(self, mock_prefs):
        """Загрузка профиля, если ничего не сохранено."""
        name = await load_profile()
        assert name == ""

    @pytest.mark.asyncio
    async def test_save_and_load_progress(self, mock_prefs):
        """Сохранение и загрузка прогресса (словаря)."""
        progress = {"case_1": {"status": "passed", "time": 120}}
        await save_progress(progress)
        loaded = await load_progress()
        assert loaded == progress
        assert loaded["case_1"]["status"] == "passed"

    @pytest.mark.asyncio
    async def test_load_empty_progress(self, mock_prefs):
        """Загрузка пустого прогресса."""
        progress = await load_progress()
        assert progress == {}

    @pytest.mark.asyncio
    async def test_save_and_load_theme(self, mock_prefs):
        """Сохранение и загрузка темы."""
        await save_theme(True) # Темная
        is_dark = await load_theme()
        assert is_dark is True

        await save_theme(False) # Светлая
        is_dark = await load_theme()
        assert is_dark is False

    @pytest.mark.asyncio
    async def test_save_quiz_result(self, mock_prefs):
        """Сохранение результата теста и проверка истории."""
        # Сохраняем один результат
        await save_quiz_result(level=1, correct=15, total=20, time_spent=120)
        
        history = await load_quiz_results()
        assert len(history) == 1
        assert history[0]["level"] == 1
        assert history[0]["correct"] == 15
        assert history[0]["total"] == 20
        
        # Сохраняем второй результат
        await save_quiz_result(level=2, correct=10, total=20, time_spent=300)
        history = await load_quiz_results()
        assert len(history) == 2
        assert history[1]["level"] == 2
