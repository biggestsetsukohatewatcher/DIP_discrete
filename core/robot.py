# core/robot.py

import math
from simulation.sensors import raycast


class Robot:
    def __init__(self, robot_id, position, radius=1.0, speed=10.0):
        self.id = robot_id
        self.x, self.y = position
        self.radius = radius
        self.speed = speed
        self.target = None
        # velocity
        self.vx = 0.0
        self.vy = 0.0

        # ---- ESO-MAPF attributes ----
        self.path = []        # list of waypoints [(x, y), ...]
        self.path_index = 0   # which waypoint we're moving toward

    @property
    def position(self):
        return (self.x, self.y)

    # ---- existing methods ----
    def set_velocity_towards(self, target, speed=1.0):
        tx, ty = target
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist > 1e-6:
            self.vx = speed * dx / dist
            self.vy = speed * dy / dist
        else:
            self.vx = 0.0
            self.vy = 0.0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def sense(self, direction, world, max_range=20.0):
        """
        direction: angle in radians
        Returns distance to nearest object.
        """
        dx = math.cos(direction)
        dy = math.sin(direction)

        return raycast(
            origin=(self.x, self.y),
            direction=(dx, dy),
            obstacles=world.obstacles,
            robots=world.robots,
            max_range=max_range,
            self_robot=self
        )

    # ---- NEW ESO-MAPF methods ----
    def set_path(self, path):
        """Assign a path (list of waypoints) to this robot."""
        self.path = path
        self.path_index = 0

    def update_along_path(self, dt, speed=10.0):
        """
        Move the robot along its assigned path using velocity logic.
        Call this instead of update() in the main loop.
        """
        if not self.path or self.path_index >= len(self.path):
            self.vx = 0.0
            self.vy = 0.0
            return

        target = self.path[self.path_index]
        self.set_velocity_towards(target, speed)
        self.update(dt)

        # check if reached the waypoint
        tx, ty = target
        if math.hypot(self.x - tx, self.y - ty) < 0.1:
            self.path_index += 1
