DEBUG_MODE = False

if DEBUG_MODE:
    from test import mock_robot
    R = mock_robot.MockRobot()
else:
    from sr import *
    R = Robot()

from controller import remote, generator, test

controller = generator.GeneratorController(R)
#controller.generator = remote.remote_control
controller.generator = test.test_control
controller.run()

