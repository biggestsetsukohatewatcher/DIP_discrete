# core/constants.py

WORLD_WIDTH = 128.0
WORLD_HEIGHT = 128.0

# SCALE = 8  # pixels per world unit

# WINDOW_WIDTH = int(WORLD_WIDTH * SCALE)   # 1024
# WINDOW_HEIGHT = int(WORLD_HEIGHT * SCALE) # 1024

FPS = 60

import pygame
pygame.init()
info = pygame.display.Info()
SCREEN_USAGE = 1

SCALE_X = (info.current_w * SCREEN_USAGE) / WORLD_WIDTH
SCALE_Y = (info.current_h * SCREEN_USAGE) / WORLD_HEIGHT
SCALE = int(min(SCALE_X, SCALE_Y))

WINDOW_WIDTH = int(WORLD_WIDTH * SCALE)
WINDOW_HEIGHT = int(WORLD_HEIGHT * SCALE)

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (180, 180, 180)
BLUE  = (80, 120, 255)
GREEN = (80, 200, 120)
RED   = (220, 80, 80)

# Safety parameters
LOOKAHEAD_TIME = 0.5   # seconds
ROBOT_RADIUS = 1.0
EPSILON = 1e-3
