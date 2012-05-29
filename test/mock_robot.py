from collections import namedtuple

BatteryLevel = namedtuple('BatteryLevel', ('voltage', 'current'))

class MockPower(object):
    def __init__(self):
        self.led = [0] * 3
        self.battery = BatteryLevel(voltage = 12.0, current = 3.3)

    def beep(self, *args):
        pass

class MockMotor(object):
    def __init__(self, n):
        self.id = n
        self.duty = 0

    def _get_target(self):
        return self.duty

    def _set_target(self, value):
        self.duty = value
        print 'Motor {0} duty set to {1}'.format(self.id, self.duty)

    target = property(fget = _get_target, fset = _set_target)

class MockServo(object):
    def __init__(self, n):
        self.id = n
        self.servo_values = [50] * 8

    def __getitem__(self, n):
        return self.servo_values[n]

    def __setitem__(self, n, value):
        print 'Servo {0}:{1} set to {2}'.format(self.id, n, value)
        self.servo_values[n] = value

class MockRobot(object):
    def __init__(self, nmotors = 3, nservos = 1):
        self.motors = [MockMotor(n) for n in xrange(nmotors)]
        self.servos = [MockServo(n) for n in xrange(nservos)]
        self.power = MockPower()
        self.usbkey = '.'

