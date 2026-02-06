# gui/editor.py

class Editor:
    def __init__(self):
        self.active = False
        self.start_point = None  # world coordinates (x, y)

    def toggle(self):
        self.active = not self.active
        self.start_point = None

    def handle_click(self, world_pos, world):
        """
        world_pos: (x, y) in world coordinates
        world: World object
        """
        if self.start_point is None:
            # First click: set start of line
            self.start_point = world_pos
        else:
            # Second click: create obstacle
            world.add_obstacle(self.start_point, world_pos)
            self.start_point = None
