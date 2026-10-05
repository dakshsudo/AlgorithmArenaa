"""Validation service for array inputs, generators, and correctness checks."""
import random
import re
from typing import List, Tuple

class ValidationService:
    """Provides array parsing, validation, generation, and correctness verification."""
    
    MIN_ARRAY_SIZE = 2
    MAX_ARRAY_SIZE = 100
    MIN_VAL = -999
    MAX_VAL = 999

    @classmethod
    def parse_manual_array(cls, text: str) -> Tuple[bool, List[int], str]:
        """Parse and validate user-entered array string.
        
        Accepts comma- or whitespace-separated integers.
        Returns:
            (is_valid, parsed_list, error_message)
        """
        text = text.strip()
        if not text:
            return False, [], "Input is empty. Please enter comma- or space-separated numbers."

        # Split on commas or whitespace
        tokens = re.split(r"[\s,]+", text)
        parsed: List[int] = []

        for token in tokens:
            if not token:
                continue
            try:
                val = int(token)
                if val < cls.MIN_VAL or val > cls.MAX_VAL:
                    return False, [], f"Value {val} out of bounds. Allowed range: [{cls.MIN_VAL}, {cls.MAX_VAL}]."
                parsed.append(val)
            except ValueError:
                return False, [], f"Invalid integer token: '{token}'. Please enter numbers only."

        if len(parsed) < cls.MIN_ARRAY_SIZE:
            return False, [], f"Array must contain at least {cls.MIN_ARRAY_SIZE} numbers."

        if len(parsed) > cls.MAX_ARRAY_SIZE:
            return False, [], f"Array length {len(parsed)} exceeds maximum allowed size of {cls.MAX_ARRAY_SIZE}."

        return True, parsed, ""

    @classmethod
    def generate_random(cls, size: int, min_val: int = 5, max_val: int = 100) -> List[int]:
        """Generate an array of random uniformly distributed integers."""
        size = max(cls.MIN_ARRAY_SIZE, min(cls.MAX_ARRAY_SIZE, size))
        return [random.randint(min_val, max_val) for _ in range(size)]

    @classmethod
    def generate_nearly_sorted(cls, size: int) -> List[int]:
        """Generate an array that is mostly sorted with a few swapped pairs."""
        size = max(cls.MIN_ARRAY_SIZE, min(cls.MAX_ARRAY_SIZE, size))
        step = max(1, 100 // size)
        arr = [5 + i * step for i in range(size)]
        
        # Swap 10% to 15% of adjacent or near elements
        num_swaps = max(1, size // 8)
        for _ in range(num_swaps):
            i = random.randint(0, size - 2)
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
            
        return arr

    @classmethod
    def generate_reverse_sorted(cls, size: int) -> List[int]:
        """Generate a strictly descending array."""
        size = max(cls.MIN_ARRAY_SIZE, min(cls.MAX_ARRAY_SIZE, size))
        step = max(1, 100 // size)
        return [100 - i * step for i in range(size)]

    @classmethod
    def generate_duplicate_heavy(cls, size: int) -> List[int]:
        """Generate an array containing repeated values from a small unique set."""
        size = max(cls.MIN_ARRAY_SIZE, min(cls.MAX_ARRAY_SIZE, size))
        pool = [12, 28, 45, 60, 85]
        return [random.choice(pool) for _ in range(size)]

    @classmethod
    def verify_sorted_correctness(cls, original: List[int], result: List[int]) -> Tuple[bool, str]:
        """Verify that result is monotonically non-decreasing and is a permutation of original."""
        if len(original) != len(result):
            return False, f"Length mismatch: original has {len(original)}, result has {len(result)}."

        # Check multiset equality
        if sorted(original) != sorted(result):
            return False, "Data corruption: elements in result do not match elements in original input."

        # Check sortedness
        for i in range(len(result) - 1):
            if result[i] > result[i + 1]:
                return False, f"Array is not sorted: index {i} ({result[i]}) > index {i+1} ({result[i+1]})."

        return True, "Verified: Array is correctly sorted and matches input multiset."
