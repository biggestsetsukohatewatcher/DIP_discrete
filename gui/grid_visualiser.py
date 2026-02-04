import matplotlib.pyplot as plt
import matplotlib.patches as patches
from core.geometry import Rectangle, LineSegment

def show_grid_popup(controller, world):
    """
    Visualizes the adaptive occupancy grid in a separate matplotlib window.
    """
    # Determine robot radius (use first robot or default)
    radius = 1.0
    if world.robots:
        radius = world.robots[0].radius

    # Build the grid using the controller's logic
    grid_cells = controller.build_occupancy_grid(world, radius)

    # Setup plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("Adaptive Grid Discretization & Paths\n(Green=Free, Red=Occupied)")
    ax.set_xlim(0, world.width)
    ax.set_ylim(0, world.height)
    ax.set_aspect('equal')

    # Draw grid cells
    for (x, y, w, h, is_free) in grid_cells:
        color = 'green' if is_free else 'red'
        # Draw cell with transparency
        rect = patches.Rectangle(
            (x, y), w, h,
            linewidth=0.5,
            edgecolor='blue',
            facecolor=color,
            alpha=0.2
        )
        ax.add_patch(rect)

    # Draw obstacles
    for obs in world.obstacles:
        if isinstance(obs, Rectangle):
            r = patches.Rectangle(
                (obs.x, obs.y), obs.w, obs.h,
                linewidth=1, edgecolor='black', facecolor='gray'
            )
            ax.add_patch(r)
        elif isinstance(obs, LineSegment):
            ax.plot([obs.p1[0], obs.p2[0]], [obs.p1[1], obs.p2[1]], 'k-', linewidth=2)

    # Draw Start/Target regions for context
    s = world.start_region
    ax.add_patch(patches.Rectangle((s.x, s.y), s.w, s.h, fill=False, edgecolor='green', linestyle='--', label='Start'))
    
    t = world.target_region
    ax.add_patch(patches.Rectangle((t.x, t.y), t.w, t.h, fill=False, edgecolor='red', linestyle='--', label='Target'))

    # Draw Robot Paths
    path_label_added = False
    for robot in world.robots:
        # Draw robot current position
        circle = patches.Circle((robot.x, robot.y), robot.radius, color='blue', alpha=0.6, zorder=5)
        ax.add_patch(circle)

        if robot.path and robot.path_index < len(robot.path):
            # Construct path points: Current Pos -> Remaining Waypoints
            xs = [robot.x]
            ys = [robot.y]
            for i in range(robot.path_index, len(robot.path)):
                wx, wy = robot.path[i]
                xs.append(wx)
                ys.append(wy)
            
            label = "Robot Path" if not path_label_added else None
            ax.plot(xs, ys, 'b.-', linewidth=1.5, markersize=4, label=label, zorder=4)
            path_label_added = True

    plt.legend(loc='upper right')
    
    # Show the popup (blocking)
    plt.show()
