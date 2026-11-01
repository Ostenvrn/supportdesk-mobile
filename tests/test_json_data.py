# tests/test_json_data.py

import json
import pytest
from importlib import resources


class TestJSONData:
    """Тесты для проверки целостности JSON-файлов."""

    def _load_json(self, filename: str) -> dict:
        """Вспомогательная функция для загрузки JSON из папки assets."""
        data_file = resources.files("assets").joinpath(filename)
        with data_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def test_cases_simulator_valid(self):
        """Проверка, что cases_simulator.json валиден и содержит нужные поля."""
        data = self._load_json("cases_simulator.json")
        assert "cases" in data
        assert len(data["cases"]) > 0
        
        for case in data["cases"]:
            assert "id" in case, "У заявки отсутствует id"
            assert "number" in case, "У заявки отсутствует number"
            assert "complaint" in case, "У заявки отсутствует complaint"
            assert "commands" in case, "У заявки отсутствуют commands"
            assert len(case["commands"]) > 0, f"У заявки {case['id']} нет команд"
            
            # Проверяем, что последняя команда финальная
            has_final = any(cmd.get("is_final") for cmd in case["commands"])
            assert has_final, f"В заявке {case['id']} нет финальной команды (is_final)"

    def test_cases_advanced_valid(self):
        """Проверка, что cases_advanced_batch.json валиден."""
        data = self._load_json("cases_advanced_batch.json")
        assert "cases" in data
        
        for case in data["cases"]:
            assert "id" in case
            assert "number" in case
            assert "complaint" in case
            assert "commands" in case
            
            has_final = any(cmd.get("is_final") for cmd in case["commands"])
            assert has_final, f"В сложной заявке {case['id']} нет финальной команды"

    def test_quiz_questions_valid(self):
        """Проверка, что quiz_questions.json валиден."""
        data = self._load_json("quiz_questions.json")
        assert "questions" in data
        assert len(data["questions"]) > 0
        
        for q in data["questions"]:
            assert "level" in q, "У вопроса отсутствует level"
            assert "question" in q, "У вопроса отсутствует текст"
            assert "options" in q, "У вопроса отсутствуют options"
            assert "correct" in q, "У вопроса отсутствует правильный ответ"
            assert len(q["options"]) >= 2, "Должно быть минимум 2 варианта ответа"
            assert 0 <= q["correct"] < len(q["options"]), "Индекс правильного ответа вне диапазона"

    def test_knowledge_valid(self):
        """Проверка, что knowledge.json валиден."""
        data = self._load_json("knowledge.json")
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        for cat in data["categories"]:
            assert "id" in cat, "У категории отсутствует id"
            assert "name" in cat, "У категории отсутствует название"
            assert "articles" in cat, "У категории отсутствуют статьи"
            
            for art in cat["articles"]:
                assert "title" in art, "У статьи отсутствует заголовок"
                assert "content" in art, "У статьи отсутствует текст"
