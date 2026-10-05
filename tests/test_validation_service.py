"""Tests for ValidationService array parsing, generation, and correctness."""
import pytest
from services.validation_service import ValidationService

def test_parse_valid_manual_inputs():
    valid_inputs = [
        ("1, 2, 3, 4", [1, 2, 3, 4]),
        ("  10   20   30  ", [10, 20, 30]),
        ("-15, 0, 42, -99", [-15, 0, 42, -99]),
        ("100,200,300", [100, 200, 300]),
    ]
    for raw, expected in valid_inputs:
        is_valid, parsed, err = ValidationService.parse_manual_array(raw)
        assert is_valid is True, f"Failed on valid input '{raw}': {err}"
        assert parsed == expected

def test_parse_invalid_manual_inputs():
    invalid_inputs = [
        ("", "empty"),
        ("     ", "empty"),
        ("one, two, three", "Invalid integer token"),
        ("1, 2, abc, 4", "Invalid integer token"),
        ("42", "at least 2"),
        ("10000, 2", "out of bounds"),
        ("-1500, 2", "out of bounds"),
    ]
    for raw, reason in invalid_inputs:
        is_valid, parsed, err = ValidationService.parse_manual_array(raw)
        assert is_valid is False, f"Expected invalid for '{raw}'"
        assert len(err) > 0

def test_array_generators():
    size = 25
    r = ValidationService.generate_random(size)
    assert len(r) == size

    ns = ValidationService.generate_nearly_sorted(size)
    assert len(ns) == size

    rev = ValidationService.generate_reverse_sorted(size)
    assert len(rev) == size
    # Check that reverse is actually descending
    for i in range(len(rev) - 1):
        assert rev[i] >= rev[i + 1]

    dup = ValidationService.generate_duplicate_heavy(size)
    assert len(dup) == size
    # Pool has 5 distinct numbers, so in 25 elements there should be duplicates
    assert len(set(dup)) <= 5

def test_verify_sorted_correctness():
    orig = [5, 2, 9, 1]
    sorted_copy = [1, 2, 5, 9]
    is_valid, msg = ValidationService.verify_sorted_correctness(orig, sorted_copy)
    assert is_valid is True

    # Corrupted values (different multiset)
    corrupted = [1, 2, 5, 8]
    is_valid, msg = ValidationService.verify_sorted_correctness(orig, corrupted)
    assert is_valid is False

    # Unsorted
    unsorted = [1, 5, 2, 9]
    is_valid, msg = ValidationService.verify_sorted_correctness(orig, unsorted)
    assert is_valid is False
