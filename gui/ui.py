# gui/ui.py

import pygame
from core.constants import *


class UI:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 24)

        # Buttons
        self.start_button = pygame.Rect(10, 40, 120, 30)
        self.reset_button = pygame.Rect(140, 40, 120, 30)

        self.speed_buttons = {
            1: pygame.Rect(10, 80, 50, 30),
            2: pygame.Rect(70, 80, 50, 30),
            4: pygame.Rect(130, 80, 50, 30),
            16: pygame.Rect(190, 80, 60, 30),
        }

    def screen_to_world(self, sx, sy):
        wx = sx / SCALE
        wy = WORLD_HEIGHT - (sy / SCALE)
        return wx, wy

    def draw(self, screen, world_pos, edit_mode, engine):
        wx, wy = world_pos

        if engine.completed:
            time_text = f"COMPLETED in {engine.completion_time:.2f} s"
        else:
            time_text = f"Time: {engine.sim_time:.2f} s"

        mode_text = "EDIT MODE" if edit_mode else "RUN MODE"
        speed_text = f"Speed: {int(engine.speed_multiplier)}×"

        header = self.font.render(
            f"{mode_text} | {time_text} | {speed_text} | Mouse: ({wx:.2f}, {wy:.2f})",
            True,
            BLACK
        )
        screen.blit(header, (10, 10))

        # START
        pygame.draw.rect(screen, BLUE, self.start_button)
        screen.blit(self.font.render("START", True, WHITE), (35, 47))

        # RESET
        pygame.draw.rect(screen, RED, self.reset_button)
        screen.blit(self.font.render("RESET", True, WHITE), (165, 47))

        # Speed buttons
        for speed, rect in self.speed_buttons.items():
            color = GREEN if engine.speed_multiplier == speed else GRAY
            pygame.draw.rect(screen, color, rect)
            label = self.font.render(f"{speed}×", True, BLACK)
            screen.blit(label, (rect.x + 10, rect.y + 6))

    def start_clicked(self, pos):
        return self.start_button.collidepoint(pos)

    def reset_clicked(self, pos):
        return self.reset_button.collidepoint(pos)

    def speed_clicked(self, pos):
        for speed, rect in self.speed_buttons.items():
            if rect.collidepoint(pos):
                return speed
        return None
