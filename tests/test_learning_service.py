"""Automated tests for offline learning content, SQLite progress, and quizzes."""
import tempfile
from pathlib import Path
import pytest
from PySide6.QtWidgets import QApplication
from app.application import create_application
from services.progress_service import ProgressService
from app.settings import CONTENT_DIR
import json
from ui.learning_page import LearningPage

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = create_application()
    return app

def test_json_content_integrity():
    # 1. Algorithms
    algo_path = CONTENT_DIR / "algorithms.json"
    assert algo_path.exists()
    with open(algo_path, "r", encoding="utf-8") as f:
        algos = json.load(f)
    assert len(algos) >= 10
    for slug, item in algos.items():
        assert "name" in item
        assert "purpose" in item
        assert "time_complexity" in item
        assert "space_complexity" in item

    # 2. Viva questions
    viva_path = CONTENT_DIR / "viva_questions.json"
    assert viva_path.exists()
    with open(viva_path, "r", encoding="utf-8") as f:
        viva = json.load(f)
    assert len(viva) >= 10
    for q in viva:
        assert "question" in q
        assert "answer" in q

    # 3. Quizzes
    quiz_path = CONTENT_DIR / "quizzes.json"
    assert quiz_path.exists()
    with open(quiz_path, "r", encoding="utf-8") as f:
        quizzes = json.load(f)
    assert len(quizzes) >= 8
    for q in quizzes:
        assert "question" in q
        assert "options" in q
        assert len(q["options"]) >= 3
        assert "correct_index" in q
        assert "explanation" in q

def test_sqlite_progress_service():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_arena.db"
        service = ProgressService(db_path=db_file)

        assert service.is_lesson_completed("bubble_sort") is False
        service.mark_lesson_completed("bubble_sort")
        assert service.is_lesson_completed("bubble_sort") is True
        assert "bubble_sort" in service.get_completed_lessons()

        # Quiz history
        assert len(service.get_quiz_history()) == 0
        service.record_quiz_score("Sorting", 5, 5)
        history = service.get_quiz_history()
        assert len(history) == 1
        assert history[0]["score"] == 5
        assert history[0]["total"] == 5

def test_learning_page_ui(qapp):
    page = LearningPage()
    assert page.tabs.count() == 4
    assert len(page.algorithms_data) >= 10
    assert len(page.viva_data) >= 10
    assert len(page.quiz_data) >= 8

    # Mark current lesson as complete
    page._on_mark_complete()
    assert page.complete_btn.text() == "✓ Completed"

    page.close()
