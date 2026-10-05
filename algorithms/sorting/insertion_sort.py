"""Insertion Sort implementation with event generation."""
from typing import List, Set
from engine.events import SortEvent, EventType
from algorithms.sorting.base import BaseSortAlgorithm, AlgorithmMetadata

class InsertionSort(BaseSortAlgorithm):
    """Insertion Sort algorithm."""
    
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="insertion_sort",
            name="Insertion Sort",
            best_time="O(n)",
            avg_time="O(n²)",
            worst_time="O(n²)",
            space_complexity="O(1)",
            is_stable=True,
            description=(
                "Iteratively inserts each element into its proper position "
                "within the already sorted portion of the array. Highly efficient "
                "for small or nearly sorted datasets."
            ),
            pseudocode=[
                "procedure insertionSort(A : list of sortable items)",
                "    for i := 1 to length(A)-1 do",
                "        key := A[i]",
                "        j := i - 1",
                "        while j >= 0 and A[j] > key do",
                "            A[j + 1] := A[j]",
                "            j := j - 1",
                "        end while",
                "        A[j + 1] := key",
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

        # Index 0 is trivially a sorted subarray of size 1
        sorted_indices.add(0)

        for i in range(1, n):
            key = arr[i]
            j = i - 1

            while j >= 0:
                # Compare key with A[j]
                events.append(SortEvent(
                    event_type=EventType.COMPARE,
                    indices=(j, j + 1),
                    values=(arr[j], key),
                    description=f"Compare A[{j}]={arr[j]} with key={key}",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))

                if arr[j] > key:
                    arr[j + 1] = arr[j]
                    events.append(SortEvent(
                        event_type=EventType.WRITE,
                        indices=(j + 1,),
                        values=(arr[j + 1],),
                        description=f"Shift A[{j}]={arr[j]} to A[{j+1}]",
                        array_snapshot=list(arr),
                        sorted_indices=set(sorted_indices)
                    ))
                    j -= 1
                else:
                    break

            if arr[j + 1] != key:
                arr[j + 1] = key
                events.append(SortEvent(
                    event_type=EventType.WRITE,
                    indices=(j + 1,),
                    values=(key,),
                    description=f"Insert key={key} at index {j+1}",
                    array_snapshot=list(arr),
                    sorted_indices=set(sorted_indices)
                ))

            for k in range(i + 1):
                sorted_indices.add(k)

        events.append(SortEvent(
            event_type=EventType.FINISH,
            description="Sorting complete. All elements verified.",
            array_snapshot=list(arr),
            sorted_indices=set(sorted_indices)
        ))
        return events
