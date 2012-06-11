import abc, time, math, sched

from mech import grabber, wheels, camera_mount

DEFAULT_NAME = 'Robbie'

class _ConfigurationLoader(object):
    def __init__(self, controller, configuration):
        self.configuration = configuration
        self.controller = controller

    def load_all(self):
        self.controller.name = self.configuration.get('name', DEFAULT_NAME)
        self.load_wheels()
        self.load_grabber()
        self.load_camera_mount()
        self.load_control()

    def load_wheels(self):
        config = self.configuration['wheels']
        for n, wheel in config.iteritems():
            self.controller.wheels.add_wheel(n,
                                             wheel['distance'],
                                             math.radians(wheel['angle']),
                                             wheel.get('radius', 0.05),
                                             wheel.get('calibration', 0.01))
    def load_grabber(self):
        config = self.configuration['grabber']
        self.controller.grabber.vertical_servo = config['servos']['vertical']
        self.controller.grabber.left_servo = config['servos']['left']
        self.controller.grabber.right_servo = config['servos']['right']

    def load_camera_mount(self):
        config = self.configuration['camera_mount']
        if 'yaw' in config:
            self.controller.camera_mount.yaw_servo = tuple(config['yaw']['servo'])
            self.controller.camera_mount.yaw_calibration = tuple(config['yaw']['calibration'])
        if 'pitch' in config:
            self.controller.camera_mount.pitch_servo = tuple(config['pitch']['servo'])
            self.controller.camera_mount.pitch_calibration = tuple(config['pitch']['calibration'])
        if 'headlights' in config:
            self.controller.camera_mount.headlights_servo = tuple(config['headlights']['servo'])

    def load_control(self):
        self.controller.control_settings = self.configuration.get('control', {})

class Controller(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, robot, calibration_file = None):
        self.robot = robot
        self.wheels = wheels.WheelSystem(robot)
        self.grabber = grabber.Grabber(robot)
        self.camera_mount = camera_mount.CameraMount(robot)
        self._load_calibration(calibration_file)
        self.exit = False
        self.update_frequency = 30.0
        self.name = DEFAULT_NAME
        self.scheduler = None
        self.control_settings = None

    def tick(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def run_once(self):
        self.tick()
        self.wheels.ramp_update()

    def run(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.exit = False
        self.start()
        def cycle():
            self.run_once()
            if not self.exit:
                self.scheduler.enter(1.0 / self.update_frequency, -1, cycle, ())
        cycle()
        self.scheduler.run()
        self.stop()

    def _load_calibration(self, calibration_file):
        if calibration_file is None:
            calibration_file = self.robot.usbkey + '/configuration.yaml'
        if hasattr(calibration_file, 'read'):
            self._load_calibration_from_stream(calibration_file)
        else:
            with open(calibration_file, 'r') as stream:
                self._load_calibration_from_stream(stream)

    def _load_calibration_from_stream(self, stream):
        import yaml
        configuration = yaml.load(stream)
        loader = _ConfigurationLoader(configuration = configuration,
                                      controller = self)
        loader.load_all()

