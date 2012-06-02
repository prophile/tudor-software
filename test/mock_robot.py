from collections import namedtuple
import multiprocessing, time

BatteryLevel = namedtuple('BatteryLevel', ('voltage', 'current'))

class MockPower(object):
    def __init__(self):
        self.led = [0] * 3
        self.battery = BatteryLevel(voltage = 12.0, current = 3.3)

    def beep(self, *args):
        pass

class MockMotor(object):
    def __init__(self, n, callback):
        self.id = n
        self.callback = callback
        self.duty = 0

    def _get_target(self):
        return self.duty

    def _set_target(self, value):
        self.callback(self.id, value)
        self.duty = value

    target = property(fget = _get_target, fset = _set_target)

class MockServo(object):
    def __init__(self, n, callback):
        self.id = n
        self.callback = callback
        self.servo_values = [50] * 8

    def __getitem__(self, n):
        return self.servo_values[n]

    def __setitem__(self, n, value):
        self.callback(self.id, n, value)
        self.servo_values[n] = value

class MockRobot(object):
    def __init__(self, nmotors = 3, nservos = 1):
        def print_info(pipe):
            data_dictionary = {}
            for n in xrange(nmotors):
                data_dictionary["M{0}".format(n)] = 0.0
            for n in xrange(nservos):
                for m in xrange(8):
                    data_dictionary["S{0}:{1}".format(n, m)] = 0.0
            while True:
                time.sleep(0.2)
                while pipe.poll():
                    key, value = pipe.recv()
                    data_dictionary[key] = value
                data_output = ' | '.join('{0}: {1: 4}'.format(x, int(y)) for (x, y) in sorted(data_dictionary.items()))
                with open('/tmp/status', 'w') as f:
                    f.write('{0}\n'.format(data_output))
        parent_pipe, child_pipe = multiprocessing.Pipe()
        self._info_thread = multiprocessing.Process(target = print_info, args = (child_pipe,))
        def motor_callback(n, value):
            parent_pipe.send(('M{0}'.format(n), value))
        def servo_callback(n, m, value):
            parent_pipe.send(('S{0}:{1}'.format(n, m), value))
        self.motors = [MockMotor(n, motor_callback) for n in xrange(nmotors)]
        self.servos = [MockServo(n, servo_callback) for n in xrange(nservos)]
        self.power = MockPower()
        self.usbkey = '.'
        self._info_thread.start()

