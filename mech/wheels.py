from collections import namedtuple

from math import sin, cos

import numpy

from interpolator import Interpolator, smooth_ease

class WheelSystem(object):
    def __init__(self, robot):
        self.robot = robot
        self.ramp_time = 0.3
        self._wheels = {}
        self._forward_matrix = None
        self._back_matrix = None
        self._wheel_indices = None
        self._wheel_speeds = {}

    def add_wheel(self, n, x, y, angle, radius, calibration = 1.0):
        overall_adjust = calibration / radius
        factor_advance = cos(angle)
        factor_lateral = sin(angle)
        factor_turn = x*cos(angle) + y*sin(angle)
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
            self._forward_matrix = numpy.matrix(rows)

    def _calculate_back_matrix(self):
        if self._back_matrix is not None:
            return
        self._calculate_forward_matrix()
        self._back_matrix = numpy.linalg.pinv(self._forward_matrix)

    def drive(self, advancing = 0, lateral = 0, angular = 0, ramp = True):
        self._calculate_forward_matrix()
        speeds = self._forward_matrix * numpy.array([[advancing],
                                                     [lateral],
                                                     [angular]])
        for i, speed in enumerate(speeds):
            speed = float(speed)
            n = self._wheel_indices[i]
            if not ramp:
                self._wheel_speeds[n].set(speed)
            else:
                self._wheel_speeds[n].smooth(speed, self.ramp_time)
        self.ramp_update()

    def ramp_update(self):
        if self._forward_matrix is not None:
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
        speeds = [0.0] * len(self._wheels)
        for i, n in self._wheel_indices.iteritems():
            speeds[i] = self._wheel_speeds[n].value
        speed_vector = numpy.array([[x] for x in speeds])
        calculated_components = self._back_matrix * speed_vector
        return (float(calculated_components[0, 0]),
                float(calculated_components[1, 0]),
                float(calculated_components[2, 0]))

    current_motion = property(fget = _current_motion)

