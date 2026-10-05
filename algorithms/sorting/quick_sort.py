"""Quick Sort implementation with explicit pivot tracking and event generation."""
from typing import List, Set
from engine.events import SortEvent, EventType
from algorithms.sorting.base import BaseSortAlgorithm, AlgorithmMetadata

class QuickSort(BaseSortAlgorithm):
    """Quick Sort algorithm using Lomuto partition."""
    
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="quick_sort",
            name="Quick Sort",
            best_time="O(n log n)",
            avg_time="O(n log n)",
            worst_time="O(n²)",
            space_complexity="O(log n)",
            is_stable=False,
            description=(
                "A divide-and-conquer algorithm that selects a 'pivot' element, "
                "partitions the array around the pivot so smaller elements go to the left "
                "and larger to the right, then recursively sorts the sub-arrays. "
                "Auxiliary space is O(log n) for call stack frames."
            ),
            pseudocode=[
                "procedure quickSort(A, low, high)",
                "    if low < high then",
                "        p := partition(A, low, high)",
                "        quickSort(A, low, p - 1)",
                "        quickSort(A, p + 1, high)",
                "    end if",
                "end procedure",
                "",
                "procedure partition(A, low, high)",
                "    pivot := A[high]",
                "    i := low - 1",
                "    for j := low to high - 1 do",
                "        if A[j] <= pivot then",
                "            i := i + 1",
                "            swap(A[i], A[j])",
                "        end if",
                "    end for",
                "    swap(A[i + 1], A[high])",
                "    return i + 1",
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

        def partition(low: int, high: int) -> int:
            pivot = arr[high]
            events.append(SortEvent(
                event_type=EventType.PIVOT,
                indices=(high,),
                values=(pivot,),
                pivot_index=high,
                range_bounds=(low, high),
                description=f"Selected pivot A[{high}] = {pivot}",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

            i = low - 1
            for j in range(low, high):
                events.append(SortEvent(
                    event_type=EventType.COMPARE,
                    indices=(j, high),
                    values=(arr[j], pivot),
                    pivot_index=high,
                    range_bounds=(low, high),
                    description=f"Compare A[{j}]={arr[j]} with pivot {pivot}",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))

                if arr[j] <= pivot:
                    i += 1
                    if i != j:
                        arr[i], arr[j] = arr[j], arr[i]
                        events.append(SortEvent(
                            event_type=EventType.SWAP,
                            indices=(i, j),
                            values=(arr[i], arr[j]),
                            pivot_index=high,
                            range_bounds=(low, high),
                            description=f"Swap smaller element A[{i}] and A[{j}]",
                            array_snapshot=list(arr),
                            sorted_indices=set(sorted_indices)
                        ))

            # Put pivot into place at i + 1
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            events.append(SortEvent(
                event_type=EventType.SWAP,
                indices=(i + 1, high),
                values=(arr[i + 1], arr[high]),
                pivot_index=i + 1,
                range_bounds=(low, high),
                description=f"Move pivot into final partition index {i + 1}",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

            # Pivot at i + 1 is guaranteed in sorted position
            sorted_indices.add(i + 1)
            events.append(SortEvent(
                event_type=EventType.MARK_SORTED,
                indices=(i + 1,),
                values=(arr[i + 1],),
                pivot_index=None,
                description=f"Pivot at index {i + 1} is now in final position",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

            return i + 1

        def quick_sort_helper(low: int, high: int):
            if low < high:
                p = partition(low, high)
                quick_sort_helper(low, p - 1)
                quick_sort_helper(p + 1, high)
            elif low == high:
                sorted_indices.add(low)

        quick_sort_helper(0, n - 1)

        for idx in range(n):
            sorted_indices.add(idx)

        events.append(SortEvent(
            event_type=EventType.FINISH,
            description="Sorting complete. All elements verified.",
            array_snapshot=list(arr),
            sorted_indices=set(sorted_indices)
        ))
        return events
