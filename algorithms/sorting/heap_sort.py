"""Heap Sort implementation with in-place iterative heapify and event generation."""
from typing import List, Set
from engine.events import SortEvent, EventType
from algorithms.sorting.base import BaseSortAlgorithm, AlgorithmMetadata

class HeapSort(BaseSortAlgorithm):
    """Heap Sort algorithm with in-place Max-Heapify."""
    
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            slug="heap_sort",
            name="Heap Sort",
            best_time="O(n log n)",
            avg_time="O(n log n)",
            worst_time="O(n log n)",
            space_complexity="O(1)",
            is_stable=False,
            description=(
                "A comparison-based sort using a Binary Heap data structure. "
                "Builds a Max-Heap in O(n) time, then repeatedly extracts the maximum "
                "element to the end of the array and restores the heap property in O(log n)."
            ),
            pseudocode=[
                "procedure heapSort(A)",
                "    buildMaxHeap(A)",
                "    for i := length(A) - 1 down to 1 do",
                "        swap(A[0], A[i])",
                "        maxHeapify(A, 0, i)",
                "    end for",
                "end procedure",
                "",
                "procedure maxHeapify(A, root, heapSize)",
                "    largest := root",
                "    left := 2 * root + 1",
                "    right := 2 * root + 2",
                "    if left < heapSize and A[left] > A[largest] then largest := left",
                "    if right < heapSize and A[right] > A[largest] then largest := right",
                "    if largest != root then",
                "        swap(A[root], A[largest])",
                "        maxHeapify(A, largest, heapSize)",
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

        def sift_down(root: int, heap_size: int):
            curr = root
            while True:
                largest = curr
                left = 2 * curr + 1
                right = 2 * curr + 2

                if left < heap_size:
                    events.append(SortEvent(
                        event_type=EventType.COMPARE,
                        indices=(left, largest),
                        values=(arr[left], arr[largest]),
                        description=f"Heapify: Compare left child A[{left}]={arr[left]} with current largest A[{largest}]={arr[largest]}",
                        array_snapshot=list(arr),
                        sorted_indices=set(sorted_indices)
                    ))
                    if arr[left] > arr[largest]:
                        largest = left

                if right < heap_size:
                    events.append(SortEvent(
                        event_type=EventType.COMPARE,
                        indices=(right, largest),
                        values=(arr[right], arr[largest]),
                        description=f"Heapify: Compare right child A[{right}]={arr[right]} with current largest A[{largest}]={arr[largest]}",
                        array_snapshot=list(arr),
                        sorted_indices=set(sorted_indices)
                    ))
                    if arr[right] > arr[largest]:
                        largest = right

                if largest != curr:
                    arr[curr], arr[largest] = arr[largest], arr[curr]
                    events.append(SortEvent(
                        event_type=EventType.SWAP,
                        indices=(curr, largest),
                        values=(arr[curr], arr[largest]),
                        description=f"Heapify: Swap parent A[{curr}] with child A[{largest}]",
                        array_snapshot=list(arr),
                        sorted_indices=set(sorted_indices)
                    ))
                    curr = largest
                else:
                    break

        # 1. Build max heap
        for i in range(n // 2 - 1, -1, -1):
            sift_down(i, n)

        # 2. Extract elements one by one
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            events.append(SortEvent(
                event_type=EventType.SWAP,
                indices=(0, i),
                values=(arr[0], arr[i]),
                description=f"Extract maximum element from root to sorted position A[{i}]",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

            sorted_indices.add(i)
            events.append(SortEvent(
                event_type=EventType.MARK_SORTED,
                indices=(i,),
                values=(arr[i],),
                description=f"Element A[{i}] placed in final sorted position",
                array_snapshot=list(arr),
                sorted_indices=set(sorted_indices)
            ))

            sift_down(0, i)

        # Root element 0 is finally sorted
        sorted_indices.add(0)
        events.append(SortEvent(
            event_type=EventType.MARK_SORTED,
            indices=(0,),
            values=(arr[0],),
            description="Element A[0] is in final sorted position",
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
