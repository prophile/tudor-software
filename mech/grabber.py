from mech import servo

class Grabber(object):
    def __init__(self, robot):
        self.robot = robot
        self.vertical_servo = None
        self.left_servo = None
        self.right_servo = None

    def _set_vertical_position(self, position):
        servo.set(self.robot, self.vertical_servo, position)

    def _get_vertical_position(self):
        return servo.get(self.robot, self.vertical_servo)

    def _set_grabber_position(self, position):
        servo.set(self.robot, self.left_servo, position)
        servo.set(self.robot, self.right_servo, -position)

    def _get_grabber_position(self):
        return servo.get(self.robot, self.left_servo)

    vertical = property(fget = _get_vertical_position,
                        fset = _set_vertical_position)
    grabber = property(fget = _get_grabber_position,
                       fset = _set_grabber_position)

