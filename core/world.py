# core/world.py

import random
from core.geometry import Rectangle, LineSegment
from core.robot import Robot


class World:
    def __init__(self, num_robots=10, width=100, height=100):
        self.width = width
        self.height = height
        self.num_robots = num_robots
        self.obstacles = []

        self.start_region = Rectangle(10, 10, 20, 20)
        self.target_region = Rectangle(90, 90, 20, 20)

        self.robots = []
        self.spawn_robots()

    def add_obstacle(self, p1, p2):
        self.obstacles.append(LineSegment(p1, p2))

    def spawn_robots(self):
        self.robots = []
        attempts = 0
        max_attempts = 1000

        for i in range(self.num_robots):
            while True:
                attempts += 1
                if attempts > max_attempts:
                    raise RuntimeError("Failed to place robots without overlap.")

                x = random.uniform(
                    self.start_region.x + 1,
                    self.start_region.x + self.start_region.w - 1
                )
                y = random.uniform(
                    self.start_region.y + 1,
                    self.start_region.y + self.start_region.h - 1
                )

                if not self._overlaps_existing((x, y), radius=1.0):
                    self.robots.append(Robot(i, (x, y)))
                    break

    def reset_robots(self):
        """Reset robots back to the start region."""
        self.spawn_robots()

    def _overlaps_existing(self, pos, radius):
        px, py = pos
        for r in self.robots:
            dx = r.x - px
            dy = r.y - py
            if dx * dx + dy * dy < (2 * radius) ** 2:
                return True
        return False
    
    def random_target_in_region(self):
        """
        Returns a random (x, y) coordinate strictly inside target_region
        """
        cx, cy = self.target_region.x, self.target_region.y
        w, h = self.target_region.w, self.target_region.h

        x = random.uniform(cx + 0.1, cx + w - 0.1)
        y = random.uniform(cy + 0.1, cy + h - 0.1)

        return (x, y)
