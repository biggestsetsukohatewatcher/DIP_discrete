# core/geometry.py

class LineSegment:
    def __init__(self, p1, p2):
        self.p1 = p1  # (x, y)
        self.p2 = p2  # (x, y)


class Rectangle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, point):
        px, py = point
        return (
            self.x <= px <= self.x + self.w and
            self.y <= py <= self.y + self.h
        )
