"""Merge Sort implementation with sub-range highlighting and write events."""
from typing import List, Set
from engine.events import SortEvent, EventType
from algorithms.sorting.base import BaseSortAlgorithm, AlgorithmMetadata

class MergeSort(BaseSortAlgorithm):
    """Merge Sort algorithm."""
    
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="merge_sort",
            name="Merge Sort",
            best_time="O(n log n)",
            avg_time="O(n log n)",
            worst_time="O(n log n)",
            space_complexity="O(n)",
            is_stable=True,
            description=(
                "A divide-and-conquer algorithm that recursively halves the array, "
                "sorts each half, and merges the sorted subarrays into a single ordered list."
            ),
            pseudocode=[
                "procedure mergeSort(A, left, right)",
                "    if left < right then",
                "        mid := floor((left + right) / 2)",
                "        mergeSort(A, left, mid)",
                "        mergeSort(A, mid + 1, right)",
                "        merge(A, left, mid, right)",
                "    end if",
                "end procedure"
            ]
        )

    def generate_events(self, initial_array: List[int]) -> List[SortEvent]:
        arr = list(initial_array)
        n = len(arr)
        events: List[SortEvent] = []
        sorted_indices: Set[int] = set()

        if n <= 1:
            if n == 1:
                sorted_indices.add(0)
            events.append(SortEvent(
                event_type=EventType.FINISH,
                description="Array sorted.",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))
            return events

        def merge(left: int, mid: int, right: int):
            events.append(SortEvent(
                event_type=EventType.MERGE_RANGE,
                indices=(left, right),
                range_bounds=(left, right),
                description=f"Merging subarrays [{left}..{mid}] and [{mid+1}..{right}]",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

            left_part = arr[left:mid + 1]
            right_part = arr[mid + 1:right + 1]
            i = 0
            j = 0
            k = left

            while i < len(left_part) and j < len(right_part):
                # We compare left_part[i] and right_part[j]
                events.append(SortEvent(
                    event_type=EventType.COMPARE,
                    indices=(left + i, mid + 1 + j),
                    values=(left_part[i], right_part[j]),
                    range_bounds=(left, right),
                    description=f"Compare left[{i}]={left_part[i]} with right[{j}]={right_part[j]}",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))

                if left_part[i] <= right_part[j]:
                    arr[k] = left_part[i]
                    i += 1
                else:
                    arr[k] = right_part[j]
                    j += 1

                events.append(SortEvent(
                    event_type=EventType.WRITE,
                    indices=(k,),
                    values=(arr[k],),
                    range_bounds=(left, right),
                    description=f"Write {arr[k]} into merged position A[{k}]",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))
                k += 1

            while i < len(left_part):
                arr[k] = left_part[i]
                events.append(SortEvent(
                    event_type=EventType.WRITE,
                    indices=(k,),
                    values=(arr[k],),
                    range_bounds=(left, right),
                    description=f"Write remaining left element {arr[k]} to A[{k}]",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))
                i += 1
                k += 1

            while j < len(right_part):
                arr[k] = right_part[j]
                events.append(SortEvent(
                    event_type=EventType.WRITE,
                    indices=(k,),
                    values=(arr[k],),
                    range_bounds=(left, right),
                    description=f"Write remaining right element {arr[k]} to A[{k}]",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))
                j += 1
                k += 1

            # If this merge covers the entire array, mark all as sorted
            if left == 0 and right == n - 1:
                for idx in range(n):
                    sorted_indices.add(idx)

        def merge_sort_helper(left: int, right: int):
            if left < right:
                mid = (left + right) // 2
                merge_sort_helper(left, mid)
                merge_sort_helper(mid + 1, right)
                merge(left, mid, right)

        merge_sort_helper(0, n - 1)

        for idx in range(n):
            sorted_indices.add(idx)

        events.append(SortEvent(
            event_type=EventType.FINISH,
            description="Sorting complete. All elements verified.",
            array_snapshot=list(arr),
            sorted_indices=set(sorted_indices)
        ))
        return events
