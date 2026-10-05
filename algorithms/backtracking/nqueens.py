"""N-Queens backtracking solver and event stream generator."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Set

class NQueensEventType(str, Enum):
    TRY_CANDIDATE = "try_candidate"
    PLACE_QUEEN = "place_queen"
    CONFLICT = "conflict"
    BACKTRACK = "backtrack"
    SOLUTION_FOUND = "solution_found"
    SEARCH_COMPLETE = "search_complete"

@dataclass
class NQueensEvent:
    event_type: NQueensEventType
    row: int
    col: int
    # Current placements: queens[r] = c
    queens: List[int] = field(default_factory=list)
    conflicting_queen: Optional[Tuple[int, int]] = None
    solution_index: Optional[int] = None
    description: str = ""

class NQueensSolver:
    """Solves the N-Queens problem with recursive backtracking and detailed event generation."""

    KNOWN_SOLUTION_COUNTS = {
        4: 2,
        5: 10,
        6: 4,
        7: 40,
        8: 92,
        9: 352,
        10: 724,
    }

    @staticmethod
    def is_valid_solution(queens: List[int]) -> bool:
        """Verify that no two queens share a row, column, or diagonal."""
        n = len(queens)
        if len(set(queens)) != n:
            return False
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                c1, c2 = queens[r1], queens[r2]
                if abs(r1 - r2) == abs(c1 - c2):
                    return False
        return True

    def solve(self, n: int, find_one: bool = False) -> Tuple[List[NQueensEvent], List[List[int]]]:
        """Execute backtracking search and return event stream and list of complete solutions."""
        events: List[NQueensEvent] = []
        solutions: List[List[int]] = []

        # queens[r] = column of queen at row r, -1 if not placed
        queens = [-1] * n
        cols: Set[int] = set()
        diag1: Set[int] = set() # r - c
        diag2: Set[int] = set() # r + c

        attempts = 0
        conflicts = 0

        def backtrack(row: int) -> bool:
            nonlocal attempts, conflicts

            if row == n:
                sol = list(queens)
                solutions.append(sol)
                events.append(NQueensEvent(
                    event_type=NQueensEventType.SOLUTION_FOUND,
                    row=row - 1,
                    col=queens[row - 1],
                    queens=list(queens),
                    solution_index=len(solutions),
                    description=f"Solution #{len(solutions)} found!"
                ))
                return find_one

            for col in range(n):
                attempts += 1
                events.append(NQueensEvent(
                    event_type=NQueensEventType.TRY_CANDIDATE,
                    row=row,
                    col=col,
                    queens=list(queens),
                    description=f"Evaluating candidate square ({row}, {col})"
                ))

                # Check conflict
                if col in cols or (row - col) in diag1 or (row + col) in diag2:
                    conflicts += 1
                    # Find which queen causes conflict
                    conflict_pos = None
                    for r_prev in range(row):
                        c_prev = queens[r_prev]
                        if c_prev == col or abs(r_prev - row) == abs(c_prev - col):
                            conflict_pos = (r_prev, c_prev)
                            break

                    events.append(NQueensEvent(
                        event_type=NQueensEventType.CONFLICT,
                        row=row,
                        col=col,
                        queens=list(queens),
                        conflicting_queen=conflict_pos,
                        description=f"Conflict detected at ({row}, {col}) with Queen at {conflict_pos}"
                    ))
                    continue

                # Place queen
                queens[row] = col
                cols.add(col)
                diag1.add(row - col)
                diag2.add(row + col)

                events.append(NQueensEvent(
                    event_type=NQueensEventType.PLACE_QUEEN,
                    row=row,
                    col=col,
                    queens=list(queens),
                    description=f"Placed Queen safely at ({row}, {col})"
                ))

                should_stop = backtrack(row + 1)
                if should_stop:
                    return True

                # Backtrack
                events.append(NQueensEvent(
                    event_type=NQueensEventType.BACKTRACK,
                    row=row,
                    col=col,
                    queens=list(queens),
                    description=f"Backtracking: Removing Queen from ({row}, {col})"
                ))

                queens[row] = -1
                cols.remove(col)
                diag1.remove(row - col)
                diag2.remove(row + col)

            return False

        backtrack(0)

        events.append(NQueensEvent(
            event_type=NQueensEventType.SEARCH_COMPLETE,
            row=n,
            col=n,
            queens=[-1] * n if not solutions else list(solutions[-1]),
            description=f"Search complete. Total solutions: {len(solutions)}, attempts: {attempts}, conflicts: {conflicts}"
        ))

        return events, solutions
