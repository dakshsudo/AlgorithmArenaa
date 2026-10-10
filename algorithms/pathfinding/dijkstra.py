"""Dijkstra's shortest path algorithm supporting non-negative weights."""
import heapq
from typing import List, Tuple, Set, Dict, Optional
from algorithms.pathfinding.base import BasePathfinder, PathfindingMetadata
from algorithms.pathfinding.models import GridMap, PathEvent, PathEventType

class DijkstraPathfinder(BasePathfinder):
    """Dijkstra's Algorithm: finds the lowest-cost path using a priority queue."""

    def get_metadata(self) -> PathfindingMetadata:
        return PathfindingMetadata(
            slug="dijkstra",
            name="Dijkstra's Algorithm",
            guarantees_shortest_path=True,
            supports_weights=True,
            time_complexity="O((V + E) log V)",
            space_complexity="O(V)",
            description=(
                "Finds the shortest or lowest-cost path from start to target. "
                "Maintains a min-heap priority queue ordered by cumulative path cost. "
                "Supports non-negative cell movement weights."
            ),
            pseudocode=[
                "procedure Dijkstra(start, target):",
                "    pq := MinPriorityQueue()",
                "    dist[start] := 0",
                "    pq.push(0, start)",
                "    while pq is not empty do:",
                "        (d, current) := pq.pop()",
                "        if d > dist[current] then continue",
                "        if current = target then return reconstructPath(parent, target)",
                "        for neighbor in getNeighbors(current) do:",
                "            weight := getEdgeWeight(neighbor)",
                "            if dist[current] + weight < dist[neighbor] then:",
                "                dist[neighbor] := dist[current] + weight",
                "                parent[neighbor] := current",
                "                pq.push(dist[neighbor], neighbor)",
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

        # Priority queue entries: (cost, counter, (r, c))
        # counter ensures tie-breaking without comparing tuples directly
        counter = 0
        pq: List[Tuple[int, int, Tuple[int, int]]] = [(0, counter, start)]
        dist: Dict[Tuple[int, int], int] = {start: 0}
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
        visited: Set[Tuple[int, int]] = set()

        found = False

        while pq:
            d, _, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            frontier_list = [node for _, _, node in pq if node not in visited]
            events.append(PathEvent(
                event_type=PathEventType.EXPLORE,
                current_node=current,
                frontier_nodes=frontier_list,
                visited_nodes=set(visited),
                cost_so_far=d,
                description=f"Exploring node {current} (Cost so far: {d})"
            ))

            if current == target:
                found = True
                break

            for neighbor in grid.getNeighbors(*current):
                step_cost = grid.get_cost(*neighbor)
                new_dist = d + step_cost

                if neighbor not in dist or new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    parent[neighbor] = current
                    counter += 1
                    heapq.heappush(pq, (new_dist, counter, neighbor))

                    events.append(PathEvent(
                        event_type=PathEventType.VISIT_FRONTIER,
                        current_node=neighbor,
                        frontier_nodes=[node for _, _, node in pq if node not in visited],
                        visited_nodes=set(visited),
                        cost_so_far=new_dist,
                        description=f"Updated neighbor {neighbor} with tentative cost {new_dist}"
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
        total_cost = dist[target]

        events.append(PathEvent(
            event_type=PathEventType.FOUND_PATH,
            current_node=target,
            visited_nodes=set(visited),
            path=list(path),
            cost_so_far=total_cost,
            description=f"Optimal path found by Dijkstra! Length: {steps} steps ({len(path)} nodes), Total Cost: {total_cost}"
        ))

        return events, path, total_cost
