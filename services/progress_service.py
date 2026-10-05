"""SQLite database service for persisting student learning progress and quiz scores."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Generator
from app.settings import DB_PATH

class ProgressService:
    """Manages local SQLite database for learning tracking and quiz history."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS completed_lessons (
                        slug TEXT PRIMARY KEY,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quiz_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        quiz_category TEXT,
                        score INTEGER,
                        total_questions INTEGER,
                        attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except sqlite3.Error:
            pass

    def mark_lesson_completed(self, slug: str):
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO completed_lessons (slug) VALUES (?)", (slug,))
                conn.commit()
        except sqlite3.Error:
            pass

    def is_lesson_completed(self, slug: str) -> bool:
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM completed_lessons WHERE slug = ?", (slug,))
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False

    def get_completed_lessons(self) -> List[str]:
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT slug FROM completed_lessons")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def record_quiz_score(self, category: str, score: int, total: int):
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO quiz_attempts (quiz_category, score, total_questions) VALUES (?, ?, ?)",
                    (category, score, total)
                )
                conn.commit()
        except sqlite3.Error:
            pass

    def get_quiz_history(self) -> List[Dict]:
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, quiz_category, score, total_questions, attempted_at FROM quiz_attempts ORDER BY attempted_at DESC LIMIT 20")
                rows = cursor.fetchall()
                return [
                    {
                        "id": r[0],
                        "category": r[1],
                        "score": r[2],
                        "total": r[3],
                        "timestamp": r[4]
                    }
                    for r in rows
                ]
        except sqlite3.Error:
            return []
