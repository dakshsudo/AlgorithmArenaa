# Algorithm Arena ⚡

**Algorithm Arena** is an interactive, native desktop educational suite for **Design and Analysis of Algorithms (DAA)**, engineered in Python with PySide6. It is designed for computer science students, educators, and laboratory evaluations to visualize, execute, compare, and analyze foundational algorithms with deterministic, step-by-step playback and verifiable correctness.

---

## 🎯 Master Capabilities

1. **Native Windows Desktop**: Built exclusively with PySide6 (Qt) for high-performance custom `QPainter` canvas rendering without browser or JavaScript overhead.
2. **100% Offline Operation**: Completely self-contained. No cloud accounts, external APIs, telemetry, or network connections required.
3. **Synchronized Event Streams**: Real algorithm executions drive visualizations (comparisons, swaps, node explorations, candidate placements, backtracks).
4. **Deterministic Step Playback**: Support for Play, Pause, Resume, Reset, Step Forward, and **$O(1)$ Step Backward** via snapshot state restoration.
5. **Isolated Algorithmic Benchmarks**: Algorithmic runtime benchmarks in the Comparison Lab are executed in isolation on separate cloned inputs without animation render delay.
6. **DAA Curriculum Aligned**: Covers Sorting, Graph Traversals & Shortest Paths, Backtracking (N-Queens), Asymptotic Complexity (Big-O), Quizzes, and Viva Voce preparation.

---

## 🛠 Technology Stack

- **Language**: Python 3.11 / 3.12 / 3.13
- **GUI Framework**: PySide6 (Qt 6.8+)
- **Testing**: pytest (121 automated tests passing)
- **Styling**: Custom modern dark theme QSS with accessible contrast and custom layout components
- **Persistence**: SQLite (`data/arena_progress.db`) & bundled offline JSON

---

## 🧭 Modules & Features

### 1. ⌂ Dashboard
- Central launchpad with interactive navigation cards for all 6 modules.
- Project overview, key DAA highlights, and viva study recommendations.

### 2. 📶 Sorting Algorithm Lab
- **Algorithms**: Bubble Sort (early-exit optimized), Selection Sort, Insertion Sort, Merge Sort, Quick Sort (Lomuto partition with explicit pivot), and Heap Sort (in-place iterative Max-Heapify).
- **Visualization**: Dynamic vertical bars with normalized zero-baseline (supporting negative and positive values), labels, indices, and state colors (comparing, swapping/writing, pivot, sorted, merge range).
- **Controls**: Start, Pause, Resume, Reset, Step Forward, Step Backward, speed adjustment slider (10ms–800ms), and pure runtime benchmark button.
- **Input Generation**: Random, Nearly Sorted, Reverse Sorted, Duplicate-Heavy, and custom manual text parser with inline error validation.
- **Metrics**: Comparisons, Swaps, Writes, Step progress, Elapsed animation time, and automated correctness/sortedness verification.

### 3. 🗺 Pathfinding & Graph Lab
- **Algorithms**: Breadth-First Search (BFS), Depth-First Search (DFS), Dijkstra's Algorithm, and A* Search.
- **Interactive Grid**: Click and drag to draw walls, place 5x weights, move start (S) and target (T), or erase obstacles.
- **Procedural Mazes**: Random obstacles, Recursive Division maze generation, and Weighted River terrain.
- **Metrics & States**: Visited nodes, frontier tracking, path length, path cost, elapsed time, and optimal route reconstruction.

### 4. ♛ N-Queens Backtracking Lab
- **Configurations**: Configurable $N \times N$ chessboard ($N = 4$ to $10$, with $N=8$ preset).
- **Visualization**: Alternating board tiles, golden queen crowns (♛), candidate evaluation squares, and red attack conflict vector lines.
- **Search Modes**: "Find One Solution" vs "Enumerate All Solutions" (cancellable without freezing).
- **Solution Replay**: Dropdown list to inspect and display any discovered solution directly on the board.
- **Metrics**: Placements tested, conflicts pruned, current recursion depth (row), solutions found, and elapsed time.

### 5. ⚖ Algorithm Comparison Lab
- **Multi-Algorithm Benchmarking**: Select and benchmark multiple sorting or pathfinding algorithms on identical cloned inputs.
- **Results Table**: Measured runtime (ms), operation counts, auxiliary space, and correctness status.
- **Comparative Charts**: Interactive bar charts toggling between Execution Time (ms) and Total Operations.

### 6. 📈 Complexity & Big-O Lab
- **Growth Classes**: $O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$, and $O(2^n)$.
- **Interactive Scaling**: Input size slider ($N = 1$ to $50$) with dynamic vertical marker on mathematical curves.
- **Dynamic Table**: Exact theoretical operation count calculated at current $N$.
- **Foundations Guide**: Formal Big-O definitions ($c$ and $n_0$), dominant operations principle, and auxiliary space analysis.

### 7. 🎓 Learning & Viva Centre
- **Study Notes**: Comprehensive notes for all 11 algorithms covering problem statement, intuition, worked examples, pseudocode, complexities, and exam observations.
- **Viva Voce Prep**: Curated oral examination questions and detailed examiner model answers.
- **Interactive Quizzes**: Multiple-choice questions with instant scoring, feedback explanation, and retake support.
- **SQLite Progress**: Automatically persists completed lessons, quiz scores, and timestamps to `data/arena_progress.db`.

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
│   ├── sorting_page.py         # Sorting visualizer lab
│   ├── pathfinding_page.py     # Pathfinding visualizer lab
│   ├── nqueens_page.py         # N-Queens backtracking lab
│   ├── comparison_page.py      # Algorithm comparison lab
│   ├── complexity_page.py      # Asymptotic complexity & Big-O lab
│   ├── learning_page.py        # Learning, quizzes & viva centre
│   └── components/             # Reusable cards, headers, and stat frames
│
├── algorithms/                 # Pure algorithm implementations & event generators
│   ├── sorting/                # Bubble, Selection, Insertion, Merge, Quick, Heap
│   ├── pathfinding/            # BFS, DFS, Dijkstra, A*, Mazes
│   └── backtracking/           # N-Queens recursive backtracking solver
│
├── engine/                     # Execution, events & playback controllers
│   ├── events.py               # SortEvent & EventType models
│   ├── run_state.py            # RunState enum (IDLE, RUNNING, PAUSED, FINISHED)
│   ├── playback_controller.py  # Forward/backward sorting playback
│   ├── pathfinding_controller.py # Forward/backward pathfinding playback
│   ├── nqueens_controller.py   # Forward/backward backtracking playback
│   └── benchmark_runner.py     # Pure algorithmic timing in isolation
│
├── visualizers/                # Custom Qt painting canvases
│   ├── sorting_canvas.py       # Bar chart with zero-baseline and state colors
│   ├── grid_canvas.py          # Interactive grid with obstacle/weight painting
│   ├── chessboard_canvas.py    # Chessboard with queens, candidates, attack lines
│   └── chart_view.py           # Bar charts & Big-O growth curves
│
├── services/                   # Services layer
│   ├── validation_service.py   # Input parser, generators, correctness
│   ├── comparison_service.py   # Multi-algorithm benchmark executor
│   ├── complexity_service.py   # Mathematical growth formulas
│   └── progress_service.py     # SQLite persistence for student progress
│
├── content/                    # Offline educational content & viva questions
│   ├── algorithms.json         # Structured notes for all 11 algorithms
│   ├── viva_questions.json     # Curated viva questions and examiner answers
│   └── quizzes.json            # Multiple-choice quiz questions & feedback
│
├── scripts/
│   └── build_windows.ps1       # PyInstaller native Windows packaging script
│
├── data/                       # Local SQLite database storage
└── tests/                      # Automated test suite (121 tests)
```

---

## 🚀 Setup & Run Instructions

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed on Windows.
- VS Code (recommended).

### 2. Virtual Environment Setup
Open PowerShell in the project root:

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

## 📦 Packaging as a Windows Executable

To package Algorithm Arena into a standalone Windows application:

```powershell
# Directory bundle (fast launch, includes bundled content/):
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1

# Or single-file executable:
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -OneFile
```
The output executable is generated inside `dist/AlgorithmArena/AlgorithmArena.exe` (or `dist/AlgorithmArena.exe`).

---

## 📊 Summary of Theoretical Complexities

| Algorithm | Category | Best Time | Average Time | Worst Time | Auxiliary Space | Stable? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bubble Sort** | Sorting | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Yes |
| **Selection Sort** | Sorting | $O(n^2)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | No |
| **Insertion Sort** | Sorting | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Yes |
| **Merge Sort** | Sorting | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | Yes |
| **Quick Sort** | Sorting | $O(n \log n)$ | $O(n \log n)$ | $O(n^2)$ | $O(\log n)$ stack | No |
| **Heap Sort** | Sorting | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(1)$ | No |
| **BFS** | Pathfinding | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ | Optimal (Unweighted) |
| **DFS** | Pathfinding | $O(V + E)$ | $O(V + E)$ | $O(V + E)$ | $O(V)$ | No Shortest Guarantee |
| **Dijkstra** | Pathfinding | $O((V+E)\log V)$| $O((V+E)\log V)$| $O((V+E)\log V)$| $O(V)$ | Optimal (Weighted) |
| **A\* Search** | Pathfinding | $O(E \log V)$ | $O(E \log V)$ | $O(b^d)$ | $O(V)$ | Optimal (Admissible) |
| **N-Queens** | Backtracking | $O(N)$ | $O(b^N)$ | $O(N!)$ | $O(N)$ stack | Complete Search |
