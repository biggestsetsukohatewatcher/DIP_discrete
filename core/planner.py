# core/planner.py
class DiscretePlan:
    def __init__(self):
        self.paths = {}  # robot_id -> [(cell, time)]

class Planner:
    def plan(self, world, grid):
        plan = DiscretePlan()
        # TODO: CBS or prioritized planning
        return plan
