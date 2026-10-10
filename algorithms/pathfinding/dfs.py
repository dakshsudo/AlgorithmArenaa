"""Depth-First Search (DFS) pathfinding algorithm."""
from typing import List, Tuple, Set, Dict, Optional
from algorithms.pathfinding.base import BasePathfinder, PathfindingMetadata
from algorithms.pathfinding.models import GridMap, PathEvent, PathEventType

class DFSPathfinder(BasePathfinder):
    """Depth-First Search: explores graph deeply along branches using a LIFO stack."""

    def get_metadata(self) -> PathfindingMetadata:
        return PathfindingMetadata(
            slug="dfs",
            name="Depth-First Search (DFS)",
            guarantees_shortest_path=False,
            supports_weights=False,
            time_complexity="O(V + E)",
            space_complexity="O(V)",
            description=(
                "Explores as far as possible along each branch before backtracking. "
                "Uses a LIFO stack. Does NOT guarantee finding the shortest path, "
                "and often produces lengthy winding paths in open grids."
            ),
            pseudocode=[
                "procedure DFS(start, target):",
                "    stack := LIFOStack()",
                "    stack.push(start)",
                "    parent[start] := null",
                "    visited := set()",
                "    while stack is not empty do:",
                "        current := stack.pop()",
                "        if current not in visited then:",
                "            visited.add(current)",
                "            if current = target then return reconstructPath(parent, target)",
                "            for neighbor in getNeighbors(current) do:",
                "                if neighbor not in visited and not isWall(neighbor) then:",
                "                    parent[neighbor] := current",
                "                    stack.push(neighbor)",
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

        stack = [start]
        visited: Set[Tuple[int, int]] = set()
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        found = False

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)

            events.append(PathEvent(
                event_type=PathEventType.EXPLORE,
                current_node=current,
                frontier_nodes=list(stack),
                visited_nodes=set(visited),
                description=f"Exploring node {current}"
            ))

            if current == target:
                found = True
                break

            for neighbor in grid.getNeighbors(*current):
                if neighbor not in visited:
                    parent[neighbor] = current
                    stack.append(neighbor)
                    events.append(PathEvent(
                        event_type=PathEventType.VISIT_FRONTIER,
                        current_node=neighbor,
                        frontier_nodes=list(stack),
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

        cost = sum(grid.get_cost(*node) for node in path[1:]) if len(path) > 1 else 0
        steps = len(path) - 1 if len(path) > 1 else 0

        events.append(PathEvent(
            event_type=PathEventType.FOUND_PATH,
            current_node=target,
            visited_nodes=set(visited),
            path=list(path),
            cost_so_far=cost,
            description=f"Path found! (DFS path is not guaranteed optimal). Length: {steps} steps ({len(path)} nodes), Cost: {cost}"
        ))

        return events, path, cost
