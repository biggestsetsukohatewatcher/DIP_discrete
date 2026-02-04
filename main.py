# main.py

import pygame
import sys
import random
from core.world import World
from core.controller import Controller
from core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from gui.renderer import Renderer
from gui.ui import UI
from gui.editor import Editor
from gui.grid_visualiser import show_grid_popup


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("ESO-MAPF Demo")

    clock = pygame.time.Clock()

    # ---- Initialize World ----
    world = World(num_robots=5, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    # ---- Initialize Renderer ----
    renderer = Renderer(screen)

    # ---- Initialize UI & Editor ----
    ui = UI()
    editor = Editor()

    # ---- Initialize Controller ----
    controller = Controller(base_grid=5.0, min_grid=1.0)

    # ---- Simulation engine placeholder ----
    class Engine:
        def __init__(self):
            
            self.sim_time = 0.0
            self.speed_multiplier = 1
            self.running = False
            self.completed = False
            self.completion_time = 0.0

    engine = Engine()

    running = True
    show_rays = True

    # ---- Helper: assign paths individually ----
    def assign_paths():
        for robot in world.robots:
            # Assign random target inside target region
            if robot.target is None:
                cx, cy = world.target_region.x, world.target_region.y
                w, h = world.target_region.w, world.target_region.h
                robot.target = (
                    cx + 0.1 + (w - 0.2) * random.random(),
                    cy + 0.1 + (h - 0.2) * random.random()
                )
            # Plan ESO-MAPF path
            path = controller.plan_path(robot, world, robot.target)
            if path is None:
                print(f"No findable path for Robot {robot.id}")
                robot.set_path([])
            else:
                robot.set_path(path)

    while running:
        dt = clock.tick(FPS) / 1000.0  # delta time in seconds
        dt *= engine.speed_multiplier
        if engine.running:
            engine.sim_time += dt

        # ---- Mouse position ----
        mouse_sx, mouse_sy = pygame.mouse.get_pos()
        mouse_world = ui.screen_to_world(mouse_sx, mouse_sy)

        # ---- Event Handling ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    world.reset_robots()
                elif event.key == pygame.K_SPACE:
                    show_rays = not show_rays
                elif event.key == pygame.K_e:
                    editor.toggle()
                elif event.key == pygame.K_g:
                    print("Showing grid discretization popup...")
                    show_grid_popup(controller, world)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    if ui.start_clicked(event.pos):
                        print("START button clicked!")
                        assign_paths()
                        engine.running = True
                        engine.sim_time = 0.0
                        engine.completed = False
                    elif ui.reset_clicked(event.pos):
                        print("RESET button clicked!")
                        world.reset_robots()
                        world.obstacles.clear()
                    else:
                        if editor.active:
                            editor.handle_click(mouse_world, world)
                    # speed buttons
                    speed = ui.speed_clicked(event.pos)
                    if speed:
                        engine.speed_multiplier = speed

        # ---- Update Robots ----
        if engine.running:
            all_reached = True
            for robot in world.robots:
                controller.update(robot, dt, world)
                if not world.target_region.contains((robot.x, robot.y)):
                    all_reached = False
            
            if all_reached and world.robots:
                engine.running = False
                engine.completed = True
                engine.completion_time = engine.sim_time
                print(f"Completed in {engine.completion_time:.2f}s")

        # ---- Draw World & UI ----
        renderer.draw_world(world, editor=editor, mouse_world=mouse_world, show_rays=show_rays)
        ui.draw(screen, mouse_world, edit_mode=editor.active, engine=engine)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
