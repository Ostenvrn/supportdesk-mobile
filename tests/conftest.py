# tests/conftest.py
import sys
import os

# Добавляем корневую папку проекта в sys.path, чтобы импорты app.* работали
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
