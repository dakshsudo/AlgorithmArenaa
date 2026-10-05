"""Bubble Sort implementation with early-exit optimization and event generation."""
from typing import List, Set
from engine.events import SortEvent, EventType
from algorithms.sorting.base import BaseSortAlgorithm, AlgorithmMetadata

class BubbleSort(BaseSortAlgorithm):
    """Bubble sort algorithm with early-exit flag."""
    
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="bubble_sort",
            name="Bubble Sort",
            best_time="O(n)",
            avg_time="O(n²)",
            worst_time="O(n²)",
            space_complexity="O(1)",
            is_stable=True,
            description=(
                "Repeatedly steps through the list, compares adjacent elements, "
                "and swaps them if they are in the wrong order. Includes early-exit "
                "optimization if no swaps occur during a pass."
            ),
            pseudocode=[
                "procedure bubbleSort(A : list of sortable items)",
                "    n := length(A)",
                "    repeat",
                "        swapped := false",
                "        for i := 1 to n-1 inclusive do",
                "            if A[i-1] > A[i] then",
                "                swap(A[i-1], A[i])",
                "                swapped := true",
                "            end if",
                "        end for",
                "        n := n - 1",
                "    until not swapped",
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

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                # Compare adjacent elements
                events.append(SortEvent(
                    event_type=EventType.COMPARE,
                    indices=(j, j + 1),
                    values=(arr[j], arr[j + 1]),
                    description=f"Compare A[{j}]={arr[j]} and A[{j+1}]={arr[j+1]}",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))

                if arr[j] > arr[j + 1]:
                    # Swap
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
                    events.append(SortEvent(
                        event_type=EventType.SWAP,
                        indices=(j, j + 1),
                        values=(arr[j], arr[j + 1]),
                        description=f"Swap A[{j}] and A[{j+1}]",
                        array_snapshot=list(arr),
                        sorted_indices=set(sorted_indices)
                    ))

            # The element at n - i - 1 is now in its final sorted position
            sorted_indices.add(n - i - 1)
            events.append(SortEvent(
                event_type=EventType.MARK_SORTED,
                indices=(n - i - 1,),
                values=(arr[n - i - 1],),
                description=f"Element at index {n - i - 1} is in sorted position",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

            # Early exit check
            if not swapped:
                # All remaining elements [0 .. n - i - 2] are also sorted
                for k in range(n - i - 1):
                    sorted_indices.add(k)
                break

        # Mark any remaining elements as sorted and finish
        for k in range(n):
            sorted_indices.add(k)

        events.append(SortEvent(
            event_type=EventType.FINISH,
            description="Sorting complete. All elements verified.",
            array_snapshot=list(arr),
            sorted_indices=set(sorted_indices)
        ))
        return events
