"""Selection Sort implementation with event generation."""
from typing import List, Set
from engine.events import SortEvent, EventType
from algorithms.sorting.base import BaseSortAlgorithm, AlgorithmMetadata

class SelectionSort(BaseSortAlgorithm):
    """Selection Sort algorithm."""
    
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="selection_sort",
            name="Selection Sort",
            best_time="O(n²)",
            avg_time="O(n²)",
            worst_time="O(n²)",
            space_complexity="O(1)",
            is_stable=False,
            description=(
                "Divides the input list into a sorted sublist at the left and an "
                "unsorted sublist at the right. Repeatedly finds the minimum element "
                "from the unsorted sublist and moves it to the end of the sorted sublist."
            ),
            pseudocode=[
                "procedure selectionSort(A : list of sortable items)",
                "    n := length(A)",
                "    for i := 0 to n-2 do",
                "        min_idx := i",
                "        for j := i+1 to n-1 do",
                "            if A[j] < A[min_idx] then",
                "                min_idx := j",
                "            end if",
                "        end for",
                "        if min_idx != i then",
                "            swap(A[i], A[min_idx])",
                "        end if",
                "    end for",
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

        for i in range(n - 1):
            min_idx = i
            for j in range(i + 1, n):
                # Compare current minimum with candidate
                events.append(SortEvent(
                    event_type=EventType.COMPARE,
                    indices=(min_idx, j),
                    values=(arr[min_idx], arr[j]),
                    description=f"Compare current min A[{min_idx}]={arr[min_idx]} with A[{j}]={arr[j]}",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))

                if arr[j] < arr[min_idx]:
                    min_idx = j

            # Swap if minimum is not at i
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                events.append(SortEvent(
                    event_type=EventType.SWAP,
                    indices=(i, min_idx),
                    values=(arr[i], arr[min_idx]),
                    description=f"Swap minimum A[{min_idx}] with A[{i}]",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))

            sorted_indices.add(i)
            events.append(SortEvent(
                event_type=EventType.MARK_SORTED,
                indices=(i,),
                values=(arr[i],),
                description=f"Element at index {i} is in sorted position",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

        # Last element is also sorted
        sorted_indices.add(n - 1)
        events.append(SortEvent(
            event_type=EventType.MARK_SORTED,
            indices=(n - 1,),
            values=(arr[n - 1],),
            description=f"Element at index {n - 1} is in sorted position",
            array_snapshot=list(arr),
            sorted_indices=set(sorted_indices)
        ))

        events.append(SortEvent(
            event_type=EventType.FINISH,
            description="Sorting complete. All elements verified.",
            array_snapshot=list(arr),
            sorted_indices=set(sorted_indices)
        ))
        return events
