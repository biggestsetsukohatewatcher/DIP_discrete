# core/controller.py
import math
import heapq
from core.geometry import LineSegment, Rectangle
from core.constants import WORLD_WIDTH, WORLD_HEIGHT


class Controller:
    def __init__(self, base_grid=8.0, min_grid=1.0):
        """
        base_grid: maximum size for a cell (coarse resolution)
        min_grid: minimum size for a cell (fine resolution near obstacles)
        """
        self.base_grid = base_grid
        self.min_grid = min_grid

    # --- Distance from point to segment ---
    @staticmethod
    def point_to_segment_distance(px, py, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        return math.hypot(px - nearest_x, py - nearest_y)

    # --- Adaptive occupancy grid ---
    def build_occupancy_grid(self, world, robot_radius):
        """
        Returns a list of tuples:
        (x0, y0, w, h, is_free)
        """
        grid_cells = []

        def subdivide(x0, y0, w, h):
            mid_x, mid_y = x0 + w / 2, y0 + h / 2
            near_obs = False

            # 1. Broad phase: Check if any obstacle is within the cell's bounding box (expanded by radius)
            cell_aabb = (
                x0 - robot_radius, 
                y0 - robot_radius, 
                w + 2 * robot_radius, 
                h + 2 * robot_radius
            )

            for obs in world.obstacles:
                if isinstance(obs, Rectangle):
                    if (obs.x < cell_aabb[0] + cell_aabb[2] and obs.x + obs.w > cell_aabb[0] and
                        obs.y < cell_aabb[1] + cell_aabb[3] and obs.y + obs.h > cell_aabb[1]):
                        near_obs = True
                        break
                elif isinstance(obs, LineSegment):
                    # Distance from center to segment
                    dist = self.point_to_segment_distance(mid_x, mid_y, obs.p1, obs.p2)
                    # Conservative check: if distance < radius + half_diagonal, it might intersect
                    half_diag = math.hypot(w, h) / 2
                    if dist < robot_radius + half_diag:
                        near_obs = True
                        break

            # 2. Decision to subdivide or stop
            should_subdivide = False
            
            if near_obs:
                # If near obstacle, subdivide unless we reached min resolution
                if w > self.min_grid:
                    should_subdivide = True
            else:
                # If free, subdivide unless we are small enough (base_grid)
                if w > self.base_grid:
                    should_subdivide = True

            if not should_subdivide:
                # Leaf node
                # If near_obs is True here, it means we hit min_grid, so it's occupied.
                is_free = not near_obs
                grid_cells.append((x0, y0, w, h, is_free))
                return

            # Subdivide into 4
            hw, hh = w / 2, h / 2
            subdivide(x0, y0, hw, hh)
            subdivide(x0 + hw, y0, hw, hh)
            subdivide(x0, y0 + hh, hw, hh)
            subdivide(x0 + hw, y0 + hh, hw, hh)

        # Start with the full world dimensions
        subdivide(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        return grid_cells

    # --- Helper to find cell index ---
    def get_cell_index(self, x, y, grid_cells):
        best_idx = -1
        min_dist = float('inf')
        
        for i, (cx, cy, w, h, is_free) in enumerate(grid_cells):
            if not is_free:
                continue
            # Check if point is strictly inside
            if cx <= x <= cx + w and cy <= y <= cy + h:
                return i
            
            # Fallback: find nearest center
            center_x, center_y = cx + w / 2, cy + h / 2
            d = math.hypot(center_x - x, center_y - y)
            if d < min_dist:
                min_dist = d
                best_idx = i
                
        return best_idx

    # --- A* path planning over adaptive grid ---
    def plan_path(self, robot, world, target):
        grid_cells = self.build_occupancy_grid(world, robot.radius)
        
        start_idx = self.get_cell_index(robot.x, robot.y, grid_cells)
        end_idx = self.get_cell_index(target[0], target[1], grid_cells)

        if start_idx == -1 or end_idx == -1:
            return None

        # A* Initialization
        # Node state is the index in grid_cells
        start_cell = grid_cells[start_idx]
        start_center = (start_cell[0] + start_cell[2]/2, start_cell[1] + start_cell[3]/2)
        
        end_cell = grid_cells[end_idx]
        end_center = (end_cell[0] + end_cell[2]/2, end_cell[1] + end_cell[3]/2)

        # Priority Queue: (f_score, cell_index, path_points)
        open_set = []
        heapq.heappush(open_set, (0, start_idx, [start_center]))
        
        g_score = {start_idx: 0}
        visited = set()

        while open_set:
            _, current_idx, path = heapq.heappop(open_set)
            
            if current_idx in visited:
                continue
            visited.add(current_idx)

            if current_idx == end_idx:
                # Path found
                return path + [target]

            current_cell = grid_cells[current_idx]
            cx, cy = current_cell[0] + current_cell[2]/2, current_cell[1] + current_cell[3]/2
            cw, ch = current_cell[2], current_cell[3]

            # Find neighbors
            for i, cell in enumerate(grid_cells):
                if i == current_idx or not cell[4]: # Skip self or occupied
                    continue
                if i in visited:
                    continue

                nx, ny = cell[0] + cell[2]/2, cell[1] + cell[3]/2
                nw, nh = cell[2], cell[3]

                # Optimization: Bounding box check for adjacency
                # If centers are too far, they can't be neighbors
                if abs(nx - cx) > (cw + nw) / 2 + 0.1: continue
                if abs(ny - cy) > (ch + nh) / 2 + 0.1: continue

                # Geometric Adjacency Check (Touching edges)
                dx = abs(nx - cx)
                dy = abs(ny - cy)
                sum_w = (cw + nw) / 2
                sum_h = (ch + nh) / 2
                EPS = 0.1

                # Touching in X (vertical edge shared)
                touch_x = (abs(dx - sum_w) < EPS) and (dy < sum_h - EPS)
                # Touching in Y (horizontal edge shared)
                touch_y = (abs(dy - sum_h) < EPS) and (dx < sum_w - EPS)
                # Touching Corner (Diagonal)
                touch_diag = (abs(dx - sum_w) < EPS) and (abs(dy - sum_h) < EPS)

                if touch_x or touch_y or touch_diag:
                    dist = math.hypot(nx - cx, ny - cy)
                    new_g = g_score[current_idx] + dist
                    
                    if i not in g_score or new_g < g_score[i]:
                        g_score[i] = new_g
                        h = math.hypot(end_center[0] - nx, end_center[1] - ny)
                        heapq.heappush(open_set, (new_g + h, i, path + [(nx, ny)]))

        # Fallback
        return None

    # --- Move robot along path safely ---
    def update(self, robot, dt, world):
        if not robot.path or robot.path_index >= len(robot.path):
            return

        target = robot.path[robot.path_index]
        dx = target[0] - robot.x
        dy = target[1] - robot.y
        dist = math.hypot(dx, dy)

        if dist < 0.2: # Slightly larger tolerance for waypoints
            robot.path_index += 1
            if robot.path_index >= len(robot.path):
                return
            
            # Update target to next waypoint immediately for continuous movement
            target = robot.path[robot.path_index]
            dx = target[0] - robot.x
            dy = target[1] - robot.y
            dist = math.hypot(dx, dy)

        # Step-limited movement
        step = min(robot.speed * dt, 2.0)
        vx = dx / dist * step
        vy = dy / dist * step
        new_x = robot.x + vx
        new_y = robot.y + vy

        # Clamp to world
        new_x = max(robot.radius, min(WORLD_WIDTH - robot.radius, new_x))
        new_y = max(robot.radius, min(WORLD_HEIGHT - robot.radius, new_y))

        # Check collisions
        collision = False
        
        # Robot-robot collision
        for other in world.robots:
            if other is robot:
                continue
            if math.hypot(new_x - other.x, new_y - other.y) < robot.radius + other.radius:
                # Priority: Lower ID moves, Higher ID waits
                if robot.id > other.id:
                    return
                collision = True
                break
        
        # Static collision (Safety net)
        if not collision:
            for obs in world.obstacles:
                if isinstance(obs, Rectangle):
                    if (obs.x - robot.radius <= new_x <= obs.x + obs.w + robot.radius and
                        obs.y - robot.radius <= new_y <= obs.y + obs.h + robot.radius):
                        collision = True
                        break
                elif isinstance(obs, LineSegment):
                    if self.point_to_segment_distance(new_x, new_y, obs.p1, obs.p2) < robot.radius:
                        collision = True
                        break

        if not collision:
            robot.x = new_x
            robot.y = new_y
        else:
            # Simple local avoidance: stop or nudge
            pass
