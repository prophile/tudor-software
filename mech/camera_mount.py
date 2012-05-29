from math import pi
from mech import servo

class CameraMount(object):
    def __init__(self, robot):
        self.robot = robot
        self.pitch_servo = None
        self.yaw_servo = None
        self.headlight_servo = None
        self.pitch_calibration = (1.0, 0.0)
        self.yaw_calibration = (1.0, 0.0)

    def _set_pitch(self, pitch):
        servo.set(self.robot, self.pitch_servo,
                  pitch / (pi/4), calibration = self.pitch_calibration)

    def _get_pitch(self):
        return (pi/4) * servo.get(self.robot, self.pitch_servo,
                                  calibration = self.pitch_calibration)

    def _set_yaw(self, yaw):
        servo.set(self.robot, self.yaw_servo,
                  yaw / (pi/3), calibration = self.yaw_calibration)

    def _get_yaw(self):
        return (pi/3) * servo.get(self.robot, self.yaw_servo,
                                  calibration = self.yaw_calibration)

    def _set_headlights(self, enabled):
        servo.set(self.robot, self.headlight_servo, 1 if enabled else -1)

    def _get_headlights(self, enabled):
        return servo.get(self.robot, self.headlight_servo) > 0

    pitch = property(fget = _get_pitch, fset = _set_pitch)
    yaw = property(fget = _get_yaw, fset = _set_yaw)
    headlights = property(fget = _get_headlights, fset = _set_headlights)

