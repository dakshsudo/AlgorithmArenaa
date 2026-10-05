# Algorithm Arena ⚡

**Algorithm Arena** is an interactive, native desktop educational suite for **Design and Analysis of Algorithms (DAA)**, engineered in Python with PySide6. It is designed for computer science students, educators, and laboratory evaluations to visualize, execute, compare, and analyze foundational algorithms with deterministic, step-by-step playback and verifiable correctness.

---

## 🎯 Key Capabilities & Design Pillars

1. **Native Desktop Experience**: Built exclusively with PySide6 (Qt) for high performance, smooth custom painting, and responsive rendering on Windows without any browser overhead.
2. **100% Offline Capability**: Runs completely standalone. No cloud accounts, external APIs, telemetry, or network connections required.
3. **Accurate & Synchronized Metrics**: Algorithm animations are powered by actual execution event streams (comparisons, swaps, node explorations, candidate placements, backtracks). Operation counters reflect real operations.
4. **Independent Benchmarking**: Algorithmic runtime benchmarks in the Comparison Lab are executed in isolation on separate cloned inputs without animation render delay.
5. **DAA Curriculum Aligned**: Covers Sorting, Graph Traversals & Shortest Paths, Backtracking (N-Queens), Asymptotic Complexity (Big-O), Quizzes, and Viva Voce preparation.

---

## 🛠 Technology Stack

- **Language**: Python 3.11 / 3.12 / 3.13
- **GUI Framework**: PySide6 (Qt 6.8+)
- **Testing**: pytest
- **Styling**: Custom modern dark theme QSS with accessible contrast and custom layout components
- **Persistence**: SQLite (local user progress, settings) & bundled offline JSON

---

## 📂 Project Architecture

```
Algorithm Arena/
├── main.py                     # Application launcher
├── requirements.txt            # Pinned dependencies (PySide6, pytest)
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation
│
├── app/                        # Application configuration & theme
│   ├── application.py          # QApplication factory & high-DPI setup
│   ├── navigation.py           # Navigation registry & destinations
│   ├── settings.py             # Global constants & file paths
│   └── theme.py                # Color palette & unified dark QSS
│
├── ui/                         # UI pages & view components
│   ├── main_window.py          # Main window with sidebar navigation & stack
│   ├── dashboard_page.py       # Home dashboard with quick-launch cards
│   ├── sorting_page.py         # Sorting visualizer lab (Phase 2)
│   ├── pathfinding_page.py     # Pathfinding visualizer lab (Phase 3)
│   ├── nqueens_page.py         # N-Queens backtracking lab (Phase 4)
│   ├── comparison_page.py      # Algorithm comparison lab (Phase 5)
│   ├── complexity_page.py      # Asymptotic complexity & Big-O lab (Phase 5)
│   ├── learning_page.py        # Learning, quizzes & viva centre (Phase 6)
│   └── components/
│       ├── header.py           # Reusable page header
│       └── card.py             # Action card component
│
├── algorithms/                 # Pure algorithm implementations & event generators
│   ├── sorting/                # Bubble, Selection, Insertion, Merge, Quick, Heap
│   ├── pathfinding/            # BFS, DFS, Dijkstra, A*
│   └── backtracking/           # N-Queens recursive backtracking
│
├── engine/                     # Execution, events & playback controllers
├── visualizers/                # Custom Qt painting canvases
├── services/                   # Benchmarks, validation & local progress storage
├── content/                    # Offline educational content & viva questions
├── data/                       # Local SQLite database storage
└── tests/                      # Automated test suite
    └── test_smoke.py           # Phase 1 smoke tests
```

---

## 🚀 Setup & Run Instructions

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed on Windows.
- VS Code (recommended).

### 2. Virtual Environment Setup
Open PowerShell in the project directory:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 4. Run the Application
```powershell
python main.py
```

### 5. Run Automated Tests
```powershell
python -m pytest -v
```

---

## 🧭 Navigation & Modules

| Module | Description | Phase |
| :--- | :--- | :--- |
| **Dashboard** | Overview, quick-launch cards, project stats, and DAA tips | Complete (Phase 1) |
| **Sorting Lab** | Bar visualizer, comparisons, swaps, write counters, step playback | In Progress (Phase 2) |
| **Pathfinding Lab** | Interactive grid, BFS, DFS, Dijkstra, A*, obstacle generation | Scheduled (Phase 3) |
| **N-Queens Lab** | Chessboard backtracking, conflict line visualization, solutions | Scheduled (Phase 4) |
| **Comparison Lab** | Multi-algorithm side-by-side benchmarking on identical inputs | Scheduled (Phase 5) |
| **Complexity Lab** | Big-O growth curves, input size scaling, dominant operations | Scheduled (Phase 5) |
| **Learning & Viva** | Curated notes, pseudocode, MCQ quizzes, oral viva questions | Scheduled (Phase 6) |

---

## 🧪 Testing Summary

Automated testing is maintained at every phase.
- **Phase 1 Smoke Tests**:
  - `test_main_window_initialization`: Verifies window construction, minimum dimensions, and stack pages.
  - `test_all_destinations_registered`: Validates all 7 navigation destinations and their sidebar buttons.
  - `test_navigation_switching`: Verifies active page transitions and button states.
  - `test_dashboard_card_navigation_signal`: Confirms dashboard action cards smoothly switch views.
- **Run command**:
  ```powershell
  .\.venv\Scripts\python.exe -m pytest
  ```
- **Current status**: 4 passed in 1.09s.
