def lerp(a, b, delta):
    return delta*b + (1-delta)*a

def smooth_linear(x):
    return x

def smooth_ease_in(x):
    return x**3

def smooth_ease_out(x):
    return x**0.2

def smooth_ease(x):
    return lerp(smooth_ease_in(x),
                smooth_ease_out(x),
                x)

class Interpolator(object):
    def __init__(self):
        self.smooth_function = smooth_linear
        from time import time
        self.time_function = time
        self.set(0)

    @property
    def _alpha(self):
        t = self.time_function()
        if t < self._start_time:
            return 0
        elif t >= self._end_time:
            return 1
        else:
            return self.smooth_function((t - self._start_time) /
                                        (self._end_time - self._start_time))

    def set(self, value):
        self._start_value = value
        self._end_value = value
        self._start_time = 0
        self._end_time = 1

    @property
    def value(self):
        return lerp(self._start_value, self._end_value, self._alpha)

    def smooth(self, target, time):
        self._start_value = self.value
        self._end_value = target
        current_time = self.time_function()
        self._start_time = current_time
        self._end_time = current_time + time


