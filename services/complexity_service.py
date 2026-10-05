"""Complexity calculations, growth formulas, and asymptotic education."""
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class ComplexityClass:
    notation: str
    name: str
    color_hex: str
    description: str
    worked_example: str
    typical_algorithms: str

COMPLEXITY_CLASSES = [
    ComplexityClass(
        notation="O(1)",
        name="Constant",
        color_hex="#10b981", # Emerald
        description="Execution time remains fixed regardless of the input dataset size.",
        worked_example="Array indexing `A[i]`, push/pop on a stack, hash table lookup (average).",
        typical_algorithms="Hash table lookup, push/pop, array indexing"
    ),
    ComplexityClass(
        notation="O(log n)",
        name="Logarithmic",
        color_hex="#06b6d4", # Cyan
        description="Each step divides the remaining problem size by a constant factor (usually 2).",
        worked_example="Binary search on 1,000,000 items takes at most ~20 comparisons.",
        typical_algorithms="Binary Search, Balanced BST search, GCD (Euclidean)"
    ),
    ComplexityClass(
        notation="O(n)",
        name="Linear",
        color_hex="#3b82f6", # Blue
        description="Running time grows in direct, 1-to-1 proportion to the input size.",
        worked_example="Iterating over a list once to find the maximum value among N items.",
        typical_algorithms="Linear Search, Array traversal, Counting Sort"
    ),
    ComplexityClass(
        notation="O(n log n)",
        name="Linearithmic",
        color_hex="#8b5cf6", # Purple
        description="Combination of linear passes with logarithmic division. Optimal for comparison sorts.",
        worked_example="Merge Sort repeatedly splits array into halves (log n levels) and merges (n work per level).",
        typical_algorithms="Merge Sort, Quick Sort (avg), Heap Sort"
    ),
    ComplexityClass(
        notation="O(n²)",
        name="Quadratic",
        color_hex="#f59e0b", # Amber
        description="Often caused by nested loops comparing every element with every other element.",
        worked_example="Nested loop over N items: outer loop runs N times, inner loop runs N times = N² operations.",
        typical_algorithms="Bubble Sort, Selection Sort, Insertion Sort (worst)"
    ),
    ComplexityClass(
        notation="O(2ⁿ)",
        name="Exponential",
        color_hex="#ef4444", # Red
        description="Doubles with each additional element. Quickly becomes intractable for moderate N.",
        worked_example="Naïve recursive Fibonacci: F(n) = F(n-1) + F(n-2) creates 2ⁿ call branches.",
        typical_algorithms="Subset generation, Recursive Fibonacci, Traveling Salesperson (brute force)"
    ),
]

class ComplexityService:
    """Computes growth curve coordinates and values for complexity classes."""

    @staticmethod
    def compute_value(notation: str, n: int) -> float:
        if n <= 0:
            return 0.0
        if notation == "O(1)":
            return 1.0
        elif notation == "O(log n)":
            return math.log2(n)
        elif notation == "O(n)":
            return float(n)
        elif notation == "O(n log n)":
            return n * math.log2(n)
        elif notation == "O(n²)":
            return float(n ** 2)
        elif notation == "O(2ⁿ)":
            # Cap to avoid overflow in rendering
            return float(min(1_000_000, 2 ** min(n, 20)))
        return 0.0

    @classmethod
    def get_growth_points(cls, max_n: int = 50) -> Dict[str, List[Tuple[int, float]]]:
        """Generate (n, f(n)) points for each complexity class."""
        points: Dict[str, List[Tuple[int, float]]] = {}
        for c in COMPLEXITY_CLASSES:
            series = []
            for n in range(1, max_n + 1):
                series.append((n, cls.compute_value(c.notation, n)))
            points[c.notation] = series
        return points
