        for robot in world.robots:
            path = controller.plan_path(robot, world, target=robot.target)
            robot.set_path(path)