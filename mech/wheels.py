from collections import namedtuple

from math import sin, cos, pi

import time

from interpolator import Interpolator, smooth_ease
from matrix import Matrix

_NoInverse = object()

class WheelSystem(object):
    def __init__(self, robot):
        self.robot = robot
        self.ramp_time = 0.3
        self._wheels = {}
        self._forward_matrix = None
        self._back_matrix = None
        self._wheel_indices = None
        self._wheel_speeds = {}
        self._turn_factor_correction = None
        self._last_ramp_update = time.time()
        self.target = (0.0, 0.0, 0.0)
        self.ramp = True

    def add_wheel(self, n, distance, angle, radius, calibration = 1.0):
        overall_adjust = calibration / radius
        factor_advance = -sin(angle)
        factor_lateral = cos(angle)
        factor_turn = distance
        row = (factor_advance * overall_adjust,
               factor_lateral * overall_adjust,
               factor_turn * overall_adjust)
        self._wheels[n] = row
        self._forward_matrix = None
        self._back_matrix = None
        interpolator = Interpolator()
        interpolator.smooth_function = smooth_ease
        self._wheel_speeds[n] = interpolator

    def _calculate_forward_matrix(self):
        if self._forward_matrix is not None:
            return
        self._wheel_indices = {}
        rows = []
        for i, (n, row) in enumerate(self._wheels.iteritems()):
            rows.append(row)
            self._wheel_indices[i] = n
        self._forward_matrix = Matrix(rows)

    def _calculate_back_matrix(self):
        if self._back_matrix is not None:
            return
        self._calculate_forward_matrix()
        try:
            self._back_matrix = self._forward_matrix.pseudo_inverse()
        except NotImplemented:
            self._back_matrix = _NoInverse

    def _drive(self):
        self._calculate_forward_matrix()
        advancing, lateral, angular = self.target
        speeds = self._forward_matrix * (advancing, lateral, angular)
        for i, speed in enumerate(speeds):
            n = self._wheel_indices[i]
            speed_difference = abs(speed - self._wheel_speeds[n].value)
            if not self.ramp or speed_difference < 0.02:
                self._wheel_speeds[n].set(speed)
            else:
                ramp_time = self.ramp_time * speed_difference
                self._wheel_speeds[n].smooth(speed, self.ramp_time)

    def _adjust_turn(self, dt):
        if self._turn_factor_correction is not None:
            advancing, lateral, angular = self.target
            advancing_true, lateral_true, angular_true = self.current_motion
            self._turn_factor_correction += angular_true * dt
            sine, cosine = sin(self._turn_factor_correction), cos(self._turn_factor_correction)
            self.target = (advancing * cosine,
                           lateral * sine,
                           angular)

    def ramp_update(self):
        current_time = time.time()
        dt = current_time - self._last_ramp_update
        self._last_ramp_update = current_time
        self._adjust_turn(dt)
        self._drive()
        for n in self._wheels:
            speed = self._wheel_speeds[n].value
            output = speed * 100
            if output > 100:
                output = 100
            elif output < -100:
                output = -100
            self.robot.motors[n].target = output

    def _current_motion(self):
        self._calculate_back_matrix()
        if self._back_matrix is _NoInverse:
            return self.target # approximate it with the current target
        speeds = [0.0] * len(self._wheels)
        for i, n in self._wheel_indices.iteritems():
            speeds[i] = self._wheel_speeds[n].value
        calculated_components = self._back_matrix * speeds
        return (float(calculated_components[0]),
                float(calculated_components[1]),
                float(calculated_components[2]))

    current_motion = property(fget = _current_motion)

    def start_turn_adjust(self):
        self._turn_factor_correction = 0.0

    def stop_turn_adjust(self):
        self._turn_factor_correction = None

