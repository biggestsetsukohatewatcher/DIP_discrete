# simulation/sensors.py

import math


def raycast(origin, direction, obstacles, robots, max_range, self_robot):
    """
    Cast a ray and return distance to nearest hit.

    origin: (x, y)
    direction: (dx, dy) - MUST be normalized
    obstacles: list of LineSegment
    robots: list of Robot
    max_range: float
    self_robot: Robot (to ignore self)
    """
    ox, oy = origin
    dx, dy = direction

    closest_dist = max_range

    # --- Check obstacle intersections ---
    for obs in obstacles:
        hit = ray_line_intersection(
            origin, direction, obs.p1, obs.p2
        )
        if hit is not None:
            dist = hit
            if dist < closest_dist:
                closest_dist = dist

    # --- Check robot intersections ---
    for robot in robots:
        if robot is self_robot:
            continue

        hit = ray_circle_intersection(
            origin,
            direction,
            (robot.x, robot.y),
            robot.radius
        )
        if hit is not None and hit < closest_dist:
            closest_dist = hit

    return closest_dist


def ray_line_intersection(origin, direction, p1, p2):
    """
    Ray vs line segment intersection.
    Returns distance t along ray, or None.
    """
    ox, oy = origin
    dx, dy = direction
    x1, y1 = p1
    x2, y2 = p2

    rx, ry = dx, dy
    sx, sy = x2 - x1, y2 - y1

    denom = rx * sy - ry * sx
    if abs(denom) < 1e-8:
        return None  # Parallel

    qpx = x1 - ox
    qpy = y1 - oy

    t = (qpx * sy - qpy * sx) / denom
    u = (qpx * ry - qpy * rx) / denom

    if t >= 0 and 0 <= u <= 1:
        return t

    return None


def ray_circle_intersection(origin, direction, center, radius):
    """
    Ray vs circle intersection.
    Returns distance t along ray, or None.
    """
    ox, oy = origin
    dx, dy = direction
    cx, cy = center

    fx = ox - cx
    fy = oy - cy

    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - radius * radius

    disc = b * b - 4 * a * c
    if disc < 0:
        return None

    disc = math.sqrt(disc)
    t1 = (-b - disc) / (2 * a)
    t2 = (-b + disc) / (2 * a)

    if t1 >= 0:
        return t1
    if t2 >= 0:
        return t2

    return None
