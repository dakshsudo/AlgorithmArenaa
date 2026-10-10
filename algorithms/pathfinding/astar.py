"""A* Search pathfinding algorithm using Manhattan distance heuristic."""
import heapq
from typing import List, Tuple, Set, Dict, Optional
from algorithms.pathfinding.base import BasePathfinder, PathfindingMetadata
from algorithms.pathfinding.models import GridMap, PathEvent, PathEventType

class AStarPathfinder(BasePathfinder):
    """A* Search: informed heuristic search with f(n) = g(n) + h(n)."""

    def get_metadata(self) -> PathfindingMetadata:
        return PathfindingMetadata(
            slug="astar",
            name="A* Search",
            guarantees_shortest_path=True,
            supports_weights=True,
            time_complexity="O(E log V) best/average, O(b^d) worst",
            space_complexity="O(V)",
            description=(
                "Informed heuristic search that evaluates nodes using f(n) = g(n) + h(n), "
                "where g(n) is the exact cost from start to n, and h(n) is the estimated "
                "Manhattan distance to target. Highly directed and optimal with admissible heuristic."
            ),
            pseudocode=[
                "procedure AStar(start, target):",
                "    pq := PriorityQueue()",
                "    gScore[start] := 0",
                "    fScore[start] := h(start, target)",
                "    pq.push(fScore[start], start)",
                "    while pq is not empty do:",
                "        current := pq.popMin()",
                "        if current = target then return reconstructPath(parent, target)",
                "        for neighbor in getNeighbors(current) do:",
                "            tentative_g := gScore[current] + getEdgeWeight(neighbor)",
                "            if tentative_g < gScore[neighbor] then:",
                "                parent[neighbor] := current",
                "                gScore[neighbor] := tentative_g",
                "                fScore[neighbor] := tentative_g + h(neighbor, target)",
                "                pq.push(fScore[neighbor], neighbor)",
                "    return failure (no path)"
            ]
        )

    @staticmethod
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Admissible Manhattan distance heuristic for 4-directional grids."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

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

        counter = 0
        h_start = self.heuristic(start, target)
        pq: List[Tuple[int, int, int, Tuple[int, int]]] = [(h_start, 0, counter, start)]
        g_score: Dict[Tuple[int, int], int] = {start: 0}
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
        visited: Set[Tuple[int, int]] = set()

        found = False

        while pq:
            f, g, _, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            frontier_list = [node for _, _, _, node in pq if node not in visited]
            events.append(PathEvent(
                event_type=PathEventType.EXPLORE,
                current_node=current,
                frontier_nodes=frontier_list,
                visited_nodes=set(visited),
                cost_so_far=g,
                description=f"Exploring node {current} (g={g}, h={self.heuristic(current, target)}, f={f})"
            ))

            if current == target:
                found = True
                break

            for neighbor in grid.getNeighbors(*current):
                step_cost = grid.get_cost(*neighbor)
                tentative_g = g + step_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    parent[neighbor] = current
                    h = self.heuristic(neighbor, target)
                    f_val = tentative_g + h
                    counter += 1
                    heapq.heappush(pq, (f_val, tentative_g, counter, neighbor))

                    events.append(PathEvent(
                        event_type=PathEventType.VISIT_FRONTIER,
                        current_node=neighbor,
                        frontier_nodes=[node for _, _, _, node in pq if node not in visited],
                        visited_nodes=set(visited),
                        cost_so_far=tentative_g,
                        description=f"Discovered neighbor {neighbor} (g={tentative_g}, h={h}, f={f_val})"
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

        steps = len(path) - 1 if len(path) > 1 else 0
        total_cost = g_score[target]

        events.append(PathEvent(
            event_type=PathEventType.FOUND_PATH,
            current_node=target,
            visited_nodes=set(visited),
            path=list(path),
            cost_so_far=total_cost,
            description=f"Optimal path found by A*! Length: {steps} steps ({len(path)} nodes), Total Cost: {total_cost}"
        ))

        return events, path, total_cost
