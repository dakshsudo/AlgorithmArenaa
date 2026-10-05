"""Maze generation algorithms and predefined grid presets."""
import random
from typing import Set, Tuple, Dict
from algorithms.pathfinding.models import GridMap

class MazeGenerator:
    """Generates procedural mazes and terrain maps on a GridMap."""

    @staticmethod
    def random_walls(grid: GridMap, density: float = 0.28):
        """Randomly distribute wall obstacles while ensuring start/target remain clear."""
        grid.walls.clear()
        grid.weights.clear()

        for r in range(grid.rows):
            for c in range(grid.cols):
                if (r, c) == grid.start or (r, c) == grid.target:
                    continue
                if random.random() < density:
                    grid.walls.add((r, c))

    @staticmethod
    def recursive_division(grid: GridMap):
        """Generate a maze using recursive subdivision."""
        grid.walls.clear()
        grid.weights.clear()

        # Add outer boundary walls
        for r in range(grid.rows):
            grid.walls.add((r, 0))
            grid.walls.add((r, grid.cols - 1))
        for c in range(grid.cols):
            grid.walls.add((0, c))
            grid.walls.add((grid.rows - 1, c))

        def divide(r1, r2, c1, c2):
            if r2 - r1 < 2 or c2 - c1 < 2:
                return

            # Choose orientation
            horizontal = (r2 - r1) > (c2 - c1)

            if horizontal:
                wall_r = random.randrange(r1 + 1, r2, 2) if (r2 - r1) > 2 else (r1 + r2) // 2
                passage_c = random.randrange(c1, c2 + 1)
                for c in range(c1, c2 + 1):
                    if c != passage_c and (wall_r, c) != grid.start and (wall_r, c) != grid.target:
                        grid.walls.add((wall_r, c))
                divide(r1, wall_r - 1, c1, c2)
                divide(wall_r + 1, r2, c1, c2)
            else:
                wall_c = random.randrange(c1 + 1, c2, 2) if (c2 - c1) > 2 else (c1 + c2) // 2
                passage_r = random.randrange(r1, r2 + 1)
                for r in range(r1, r2 + 1):
                    if r != passage_r and (r, wall_c) != grid.start and (r, wall_c) != grid.target:
                        grid.walls.add((r, wall_c))
                divide(r1, r2, c1, wall_c - 1)
                divide(r1, r2, wall_c + 1, c2)

        divide(1, grid.rows - 2, 1, grid.cols - 2)
        grid.walls.discard(grid.start)
        grid.walls.discard(grid.target)

    @staticmethod
    def weighted_river(grid: GridMap):
        """Create a central weighted river/swamp terrain with a bridge."""
        grid.walls.clear()
        grid.weights.clear()

        mid_c = grid.cols // 2
        for r in range(grid.rows):
            for dc in (-2, -1, 0, 1, 2):
                c = mid_c + dc
                if 0 <= c < grid.cols and (r, c) != grid.start and (r, c) != grid.target:
                    # Bridge in the middle has normal cost 1
                    if abs(r - grid.rows // 2) > 2:
                        grid.weights[(r, c)] = grid.weight_cost
