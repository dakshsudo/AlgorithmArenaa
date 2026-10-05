"""Breadth-First Search (BFS) pathfinding algorithm."""
from collections import deque
from typing import List, Tuple, Set, Dict, Optional
from algorithms.pathfinding.base import BasePathfinder, PathfindingMetadata
from algorithms.pathfinding.models import GridMap, PathEvent, PathEventType

class BFSPathfinder(BasePathfinder):
    """Breadth-First Search: explores graph level-by-level using a FIFO queue."""

    def get_metadata(self) -> PathfindingMetadata:
        return PathfindingMetadata(
            slug="bfs",
            name="Breadth-First Search (BFS)",
            guarantees_shortest_path=True,
            supports_weights=False,
            time_complexity="O(V + E)",
            space_complexity="O(V)",
            description=(
                "Traverses the grid level by level using a FIFO queue. "
                "Guarantees finding the shortest path (minimum number of steps) "
                "in unweighted grids."
            ),
            pseudocode=[
                "procedure BFS(start, target):",
                "    queue := FIFOQueue()",
                "    queue.push(start)",
                "    parent[start] := null",
                "    visited := {start}",
                "    while queue is not empty do:",
                "        current := queue.pop()",
                "        if current = target then return reconstructPath(parent, target)",
                "        for neighbor in getNeighbors(current) do:",
                "            if neighbor not in visited and not isWall(neighbor) then:",
                "                visited.add(neighbor)",
                "                parent[neighbor] := current",
                "                queue.push(neighbor)",
                "    return failure (no path)"
            ]
        )

    def search(self, grid: GridMap) -> Tuple[List[PathEvent], List[Tuple[int, int]], int]:
        events: List[PathEvent] = []
        start = grid.start
        target = grid.target

        if start == target:
            events.append(PathEvent(
                event_type=PathEventType.FOUND_PATH,
                current_node=start,
                path=[start],
                cost_so_far=0,
                description="Start is already at the destination."
            ))
            return events, [start], 0

        queue = deque([start])
        visited: Set[Tuple[int, int]] = {start}
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        found = False

        while queue:
            current = queue.popleft()

            events.append(PathEvent(
                event_type=PathEventType.EXPLORE,
                current_node=current,
                frontier_nodes=list(queue),
                visited_nodes=set(visited),
                description=f"Exploring node {current}"
            ))

            if current == target:
                found = True
                break

            for neighbor in grid.getNeighbors(*current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

                    events.append(PathEvent(
                        event_type=PathEventType.VISIT_FRONTIER,
                        current_node=neighbor,
                        frontier_nodes=list(queue),
                        visited_nodes=set(visited),
                        description=f"Discovered frontier node {neighbor}"
                    ))

        if not found:
            events.append(PathEvent(
                event_type=PathEventType.NO_PATH,
                visited_nodes=set(visited),
                description="No path found. Destination is completely blocked by walls."
            ))
            return events, [], 0

        # Reconstruct path
        path: List[Tuple[int, int]] = []
        curr = target
        while curr in parent:
            path.append(curr)
            curr = parent[curr]
        path.append(start)
        path.reverse()

        cost = len(path) - 1

        events.append(PathEvent(
            event_type=PathEventType.FOUND_PATH,
            current_node=target,
            visited_nodes=set(visited),
            path=list(path),
            cost_so_far=cost,
            description=f"Path found! Length: {len(path)} steps, Cost: {cost}"
        ))

        return events, path, cost
