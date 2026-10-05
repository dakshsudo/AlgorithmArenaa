"""Learning & Viva Centre page: comprehensive notes, viva voce, quizzes, and progress tracking."""
import json
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QScrollArea, QTabWidget, QRadioButton,
    QButtonGroup, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
)
from PySide6.QtCore import Qt

from app.theme import Colors
from app.settings import CONTENT_DIR
from ui.components.header import PageHeader
from services.progress_service import ProgressService

class LearningPage(QWidget):
    """Learning & Viva Centre page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LearningPage")

        self.progress_service = ProgressService()
        self.algorithms_data: Dict = {}
        self.viva_data: List = []
        self.quiz_data: List = []

        self._current_quiz_idx: int = 0
        self._quiz_score: int = 0

        self._load_offline_content()
        self._init_ui()
        self._update_progress_tab()

    def _load_offline_content(self):
        # 1. Algorithms notes
        algo_file = CONTENT_DIR / "algorithms.json"
        if algo_file.exists():
            with open(algo_file, "r", encoding="utf-8") as f:
                self.algorithms_data = json.load(f)

        # 2. Viva questions
        viva_file = CONTENT_DIR / "viva_questions.json"
        if viva_file.exists():
            with open(viva_file, "r", encoding="utf-8") as f:
                self.viva_data = json.load(f)

        # 3. Quizzes
        quiz_file = CONTENT_DIR / "quizzes.json"
        if quiz_file.exists():
            with open(quiz_file, "r", encoding="utf-8") as f:
                self.quiz_data = json.load(f)

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(24, 20, 24, 20)
        root_layout.setSpacing(14)

        header = PageHeader(
            title="Learning & Viva Centre",
            subtitle="Curated revision notes, pseudocode, multiple-choice quizzes with feedback, and viva voce practice."
        )
        root_layout.addWidget(header)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER_DEFAULT};
                background: {Colors.BG_BASE};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: {Colors.BG_SURFACE};
                color: {Colors.TEXT_SECONDARY};
                padding: 10px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: {Colors.BG_SURFACE_ELEVATED};
                color: {Colors.PRIMARY};
                border-bottom: 2px solid {Colors.PRIMARY};
            }}
            QTabBar::tab:hover {{
                color: {Colors.TEXT_PRIMARY};
            }}
        """)

        # Tab 1: Study Notes
        self.tabs.addTab(self._create_notes_tab(), "📖 Study Notes & Theory")

        # Tab 2: Viva Voce Prep
        self.tabs.addTab(self._create_viva_tab(), "🎓 Viva Voce Prep")

        # Tab 3: Interactive Quizzes
        self.tabs.addTab(self._create_quiz_tab(), "📝 Interactive Quizzes")

        # Tab 4: Progress Tracking
        self.tabs.addTab(self._create_progress_tab(), "📊 My Progress")

        root_layout.addWidget(self.tabs, 1)

    # --- TAB 1: Study Notes ---
    def _create_notes_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Selector Row
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel("Select Topic:"))

        self.note_algo_combo = QComboBox()
        self.note_algo_combo.setFixedWidth(220)
        for slug, data in self.algorithms_data.items():
            self.note_algo_combo.addItem(f"{data.get('category')}: {data.get('name')}", slug)
        self.note_algo_combo.currentIndexChanged.connect(self._on_note_algo_changed)
        sel_row.addWidget(self.note_algo_combo)

        sel_row.addStretch()

        self.complete_btn = QPushButton("✓ Mark Lesson Complete")
        self.complete_btn.setProperty("class", "secondary-btn")
        self.complete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.complete_btn.clicked.connect(self._on_mark_complete)
        sel_row.addWidget(self.complete_btn)

        layout.addLayout(sel_row)

        # Note Card
        self.note_card = QFrame()
        self.note_card.setObjectName("LearnNoteCard")
        self.note_card.setStyleSheet(f"""
            QFrame#LearnNoteCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        self.note_layout = QVBoxLayout(self.note_card)
        self.note_layout.setContentsMargins(16, 16, 16, 16)
        self.note_layout.setSpacing(12)

        self.lbl_note_title = QLabel("")
        self.lbl_note_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        self.note_layout.addWidget(self.lbl_note_title)

        self.lbl_note_body = QLabel("")
        self.lbl_note_body.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_note_body.setWordWrap(True)
        self.lbl_note_body.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; line-height: 1.6;")
        self.note_layout.addWidget(self.lbl_note_body)

        layout.addWidget(self.note_card)
        layout.addStretch()

        scroll.setWidget(container)
        self._on_note_algo_changed()
        return scroll

    def _on_note_algo_changed(self):
        slug = self.note_algo_combo.currentData()
        if not slug or slug not in self.algorithms_data:
            return

        data = self.algorithms_data[slug]
        self.lbl_note_title.setText(data.get("name", ""))

        html = f"""
        <p><b>Purpose:</b> {data.get('purpose', '')}</p>
        <p><b>Problem Statement:</b> {data.get('problem_statement', '')}</p>
        <p><b>Intuition:</b> {data.get('intuition', '')}</p>
        
        <div style="background-color: #0b0f19; border-left: 3px solid #38bdf8; padding: 10px; margin: 8px 0; border-radius: 4px;">
            <b>Worked Example:</b><br>{data.get('worked_example', '')}
        </div>

        <p><b>Complexity Analysis:</b><br>
        &bull; <b>Time:</b> {data.get('time_complexity', '')}<br>
        &bull; <b>Space:</b> {data.get('space_complexity', '')}<br>
        &bull; <b>Stability:</b> {data.get('stability', 'N/A')}</p>

        <p><b>Advantages:</b><br>{'<br>'.join('&bull; ' + adv for adv in data.get('advantages', []))}</p>
        <p><b>Limitations:</b><br>{'<br>'.join('&bull; ' + lim for lim in data.get('limitations', []))}</p>
        <p><b>Exam-Relevant Observations:</b><br>{data.get('exam_observations', '')}</p>
        """
        self.lbl_note_body.setText(html)

        # Update complete button state
        is_done = self.progress_service.is_lesson_completed(slug)
        if is_done:
            self.complete_btn.setText("✓ Completed")
            self.complete_btn.setEnabled(False)
        else:
            self.complete_btn.setText("Mark Lesson Complete")
            self.complete_btn.setEnabled(True)

    def _on_mark_complete(self):
        slug = self.note_algo_combo.currentData()
        if slug:
            self.progress_service.mark_lesson_completed(slug)
            self._on_note_algo_changed()
            self._update_progress_tab()

    # --- TAB 2: Viva Voce Prep ---
    def _create_viva_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        info_lbl = QLabel("Frequently Asked DAA Laboratory Viva Questions & Examiner Answers")
        info_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(info_lbl)

        for idx, item in enumerate(self.viva_data, 1):
            q_frame = QFrame()
            frame_id = f"vivaCard_{idx}"
            q_frame.setObjectName(frame_id)
            q_frame.setStyleSheet(f"""
                QFrame#{frame_id} {{
                    background-color: {Colors.BG_SURFACE};
                    border: 1px solid {Colors.BORDER_DEFAULT};
                    border-radius: 8px;
                }}
            """)
            q_layout = QVBoxLayout(q_frame)
            q_layout.setContentsMargins(12, 12, 12, 12)
            q_layout.setSpacing(6)

            q_text = QLabel(f"<b>Q{idx}. [{item.get('category')}] {item.get('question')}</b>")
            q_text.setWordWrap(True)
            q_text.setStyleSheet(f"color: {Colors.PRIMARY_LIGHT}; font-size: 13px;")
            q_layout.addWidget(q_text)

            ans_box = QLabel(f"<b>Model Answer:</b> {item.get('answer')}")
            ans_box.setWordWrap(True)
            ans_box.setStyleSheet(f"""
                background-color: {Colors.BG_BASE};
                color: {Colors.TEXT_SECONDARY};
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid {Colors.BORDER_SUBTLE};
                font-size: 12px;
                line-height: 1.5;
            """)
            q_layout.addWidget(ans_box)

            layout.addWidget(q_frame)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    # --- TAB 3: Interactive Quizzes ---
    def _create_quiz_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Question header
        self.quiz_num_lbl = QLabel("Question 1 of 8")
        self.quiz_num_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {Colors.PRIMARY}; text-transform: uppercase;")
        layout.addWidget(self.quiz_num_lbl)

        self.quiz_question_lbl = QLabel("")
        self.quiz_question_lbl.setWordWrap(True)
        self.quiz_question_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(self.quiz_question_lbl)

        # Options Container
        self.options_frame = QFrame()
        self.options_frame.setObjectName("QuizOptionsCard")
        self.options_frame.setStyleSheet(f"""
            QFrame#QuizOptionsCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        self.options_layout = QVBoxLayout(self.options_frame)
        self.options_layout.setContentsMargins(16, 16, 16, 16)
        self.options_layout.setSpacing(10)

        self.radio_group = QButtonGroup(self)
        self.radio_buttons: List[QRadioButton] = []

        layout.addWidget(self.options_frame)

        # Action Buttons Row
        btn_row = QHBoxLayout()
        self.submit_quiz_btn = QPushButton("Submit Answer")
        self.submit_quiz_btn.setProperty("class", "primary-btn")
        self.submit_quiz_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_quiz_btn.clicked.connect(self._on_submit_quiz_answer)
        btn_row.addWidget(self.submit_quiz_btn)

        self.next_quiz_btn = QPushButton("Next Question →")
        self.next_quiz_btn.setProperty("class", "secondary-btn")
        self.next_quiz_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_quiz_btn.setEnabled(False)
        self.next_quiz_btn.clicked.connect(self._on_next_quiz_question)
        btn_row.addWidget(self.next_quiz_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Feedback box
        self.quiz_feedback_box = QFrame()
        self.quiz_feedback_box.setObjectName("QuizFeedbackCard")
        self.quiz_feedback_box.setStyleSheet(f"""
            QFrame#QuizFeedbackCard {{
                background-color: {Colors.BG_SURFACE_ELEVATED};
                border-radius: 8px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        self.quiz_feedback_box.hide()
        f_layout = QVBoxLayout(self.quiz_feedback_box)
        f_layout.setContentsMargins(12, 12, 12, 12)
        self.feedback_title = QLabel("")
        self.feedback_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        self.feedback_desc = QLabel("")
        self.feedback_desc.setWordWrap(True)
        self.feedback_desc.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; line-height: 1.4;")
        f_layout.addWidget(self.feedback_title)
        f_layout.addWidget(self.feedback_desc)
        layout.addWidget(self.quiz_feedback_box)

        layout.addStretch()
        scroll.setWidget(container)

        self._load_current_quiz_question()
        return scroll

    def _load_current_quiz_question(self):
        if not self.quiz_data:
            return

        q = self.quiz_data[self._current_quiz_idx]
        self.quiz_num_lbl.setText(f"Question {self._current_quiz_idx + 1} of {len(self.quiz_data)} ({q.get('category')})")
        self.quiz_question_lbl.setText(q.get("question", ""))

        # Clear old radio buttons
        for rb in self.radio_buttons:
            self.radio_group.removeButton(rb)
            rb.deleteLater()
        self.radio_buttons.clear()

        # Add new options
        for idx, opt in enumerate(q.get("options", [])):
            rb = QRadioButton(opt)
            rb.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_PRIMARY}; padding: 6px;")
            self.radio_group.addButton(rb, idx)
            self.options_layout.addWidget(rb)
            self.radio_buttons.append(rb)

        self.submit_quiz_btn.setEnabled(True)
        self.next_quiz_btn.setEnabled(False)
        self.quiz_feedback_box.hide()

    def _on_submit_quiz_answer(self):
        selected_id = self.radio_group.checkedId()
        if selected_id == -1:
            return

        q = self.quiz_data[self._current_quiz_idx]
        correct_idx = q.get("correct_index", 0)

        is_correct = (selected_id == correct_idx)
        if is_correct:
            self._quiz_score += 1
            self.feedback_title.setText("✓ Correct!")
            self.feedback_title.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: 700;")
            self.quiz_feedback_box.setStyleSheet(f"background-color: rgba(16, 185, 129, 0.1); border: 1px solid {Colors.SUCCESS}; border-radius: 8px; padding: 12px;")
        else:
            self.feedback_title.setText(f"✗ Incorrect. The correct answer was: {q['options'][correct_idx]}")
            self.feedback_title.setStyleSheet(f"color: {Colors.DANGER}; font-weight: 700;")
            self.quiz_feedback_box.setStyleSheet(f"background-color: rgba(244, 63, 94, 0.1); border: 1px solid {Colors.DANGER}; border-radius: 8px; padding: 12px;")

        self.feedback_desc.setText(q.get("explanation", ""))
        self.quiz_feedback_box.show()

        self.submit_quiz_btn.setEnabled(False)
        self.next_quiz_btn.setEnabled(True)

    def _on_next_quiz_question(self):
        if self._current_quiz_idx < len(self.quiz_data) - 1:
            self._current_quiz_idx += 1
            self._load_current_quiz_question()
        else:
            # End of quiz - record score
            total = len(self.quiz_data)
            self.progress_service.record_quiz_score("Comprehensive DAA", self._quiz_score, total)
            self.quiz_num_lbl.setText("Quiz Completed")
            self.quiz_question_lbl.setText(f"You finished the quiz! Final Score: {self._quiz_score} / {total} ({int((self._quiz_score / total) * 100)}%)")
            self.options_frame.hide()
            self.submit_quiz_btn.hide()
            self.next_quiz_btn.setText("↺ Retake Quiz")
            self.next_quiz_btn.clicked.disconnect()
            self.next_quiz_btn.clicked.connect(self._restart_quiz)
            self._update_progress_tab()

    def _restart_quiz(self):
        self._current_quiz_idx = 0
        self._quiz_score = 0
        self.options_frame.show()
        self.submit_quiz_btn.show()
        self.next_quiz_btn.setText("Next Question →")
        self.next_quiz_btn.clicked.disconnect()
        self.next_quiz_btn.clicked.connect(self._on_next_quiz_question)
        self._load_current_quiz_question()

    # --- TAB 4: Progress Tracking ---
    def _create_progress_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Overview Stats Card
        stat_card = QFrame()
        stat_card.setObjectName("LearnOverviewCard")
        stat_card.setStyleSheet(f"""
            QFrame#LearnOverviewCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        s_layout = QVBoxLayout(stat_card)
        s_layout.setContentsMargins(16, 16, 16, 16)
        s_layout.setSpacing(10)

        s_header = QLabel("Learning Curriculum Progress")
        s_header.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        s_layout.addWidget(s_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Colors.BG_BASE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                height: 18px;
                text-align: center;
                color: {Colors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY};
                border-radius: 5px;
            }}
        """)
        s_layout.addWidget(self.progress_bar)

        self.lbl_completed_count = QLabel("")
        self.lbl_completed_count.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        s_layout.addWidget(self.lbl_completed_count)

        layout.addWidget(stat_card)

        # Quiz History Table Card
        table_card = QFrame()
        table_card.setObjectName("LearnHistoryCard")
        table_card.setStyleSheet(f"""
            QFrame#LearnHistoryCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
            }}
        """)
        t_layout = QVBoxLayout(table_card)
        t_layout.setContentsMargins(14, 14, 14, 14)
        t_layout.setSpacing(8)

        t_lbl = QLabel("Recent Quiz Score History (SQLite Persisted)")
        t_lbl.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        t_layout.addWidget(t_lbl)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Quiz Category", "Score", "Percentage", "Date & Time"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setMinimumHeight(180)
        t_layout.addWidget(self.history_table)

        layout.addWidget(table_card)
        layout.addStretch()

        scroll.setWidget(container)
        return scroll

    def _update_progress_tab(self):
        completed = self.progress_service.get_completed_lessons()
        total_lessons = len(self.algorithms_data) if self.algorithms_data else 11
        count = len(completed)

        pct = int((count / total_lessons) * 100) if total_lessons > 0 else 0
        if hasattr(self, "progress_bar"):
            self.progress_bar.setValue(pct)
            self.lbl_completed_count.setText(f"{count} of {total_lessons} lessons completed ({pct}%)")

        # Update quiz history
        history = self.progress_service.get_quiz_history()
        if hasattr(self, "history_table"):
            self.history_table.setRowCount(len(history))
            for row, item in enumerate(history):
                score = item["score"]
                tot = item["total"]
                pct_str = f"{int((score/tot)*100)}%" if tot > 0 else "0%"
                self.history_table.setItem(row, 0, QTableWidgetItem(item["category"]))
                self.history_table.setItem(row, 1, QTableWidgetItem(f"{score} / {tot}"))
                self.history_table.setItem(row, 2, QTableWidgetItem(pct_str))
                self.history_table.setItem(row, 3, QTableWidgetItem(str(item["timestamp"])))
