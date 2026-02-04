# gui/renderer.py

import pygame
import math
from core.constants import *


class Renderer:
    def __init__(self, screen):
        self.screen = screen

        # Transparent surface for rays
        self.ray_surface = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.SRCALPHA
        )

    def world_to_screen(self, x, y):
        sx = int(x * SCALE)
        sy = int((WORLD_HEIGHT - y) * SCALE)
        return sx, sy

    def draw_world(self, world, editor=None, mouse_world=None, show_rays=True):
        self.screen.fill(WHITE)

        pygame.draw.rect(
            self.screen, BLACK,
            (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 2
        )

        self.draw_rect(world.start_region, GREEN)
        self.draw_rect(world.target_region, RED)

        for obs in world.obstacles:
            self.draw_line(obs.p1, obs.p2, BLACK)

        for robot in world.robots:
            self.draw_robot(robot)

        # ---- RAYS (DRAW SEPARATELY WITH ALPHA) ----
        if show_rays:
            self.ray_surface.fill((0, 0, 0, 0))  # clear transparent surface
            for robot in world.robots:
                self.draw_rays(robot, world)
            self.screen.blit(self.ray_surface, (0, 0))

        # Preview obstacle line
        if editor and editor.active and editor.start_point and mouse_world:
            self.draw_line(editor.start_point, mouse_world, GRAY)

    def draw_rect(self, rect, color):
        x1, y1 = self.world_to_screen(rect.x, rect.y + rect.h)
        w = int(rect.w * SCALE)
        h = int(rect.h * SCALE)
        pygame.draw.rect(self.screen, color, (x1, y1, w, h), 2)

    def draw_line(self, p1, p2, color):
        s1 = self.world_to_screen(*p1)
        s2 = self.world_to_screen(*p2)
        pygame.draw.line(self.screen, color, s1, s2, 2)

    def draw_robot(self, robot):
        sx, sy = self.world_to_screen(robot.x, robot.y)
        r = int(robot.radius * SCALE)
        pygame.draw.circle(self.screen, BLUE, (sx, sy), r)
        pygame.draw.circle(self.screen, BLACK, (sx, sy), r, 1)

    def draw_rays(self, robot, world):
        angles = [-math.pi / 4, 0, math.pi / 4]
        max_range = 20.0

        for a in angles:
            dist = robot.sense(a, world, max_range)
            end_x = robot.x + math.cos(a) * dist
            end_y = robot.y + math.sin(a) * dist

            s1 = self.world_to_screen(*robot.position)
            s2 = self.world_to_screen(end_x, end_y)

            # RGBA: last value is alpha (lower = more transparent)
            pygame.draw.line(
                self.ray_surface,
                (120, 120, 120, 60),  # soft gray, low opacity
                s1,
                s2,
                2
            )
