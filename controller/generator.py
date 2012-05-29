from multiprocessing import Process, Pipe

from .controller import Controller

from math import radians

def schedule_by_parts(scheduler, frame):
    def trigger():
        try:
            delay = frame.next()
            scheduler.enter(delay, 3, trigger, ())
        except StopIteration:
            pass
    trigger()

class GeneratorController(Controller):
    def start(self):
        parent_conn, child_conn = Pipe()
        self.data_pipe = parent_conn
        def generator_process(data, generator, settings):
            for command, args in generator(settings):
                if command != '':
                    data.send((command, args))
                if data.poll():
                    return
        self.process = Process(target = generator_process,
                               args = (child_conn, self.generator,
                                       self.control_settings))
        self.process.start()
        self.in_grab = False

    def stop(self):
        self.data_pipe.send("STOP")
        self.data_pipe.close()
        self.process.join()
        self.data_pipe = None
        self.process = None

    def tick(self):
        if self.data_pipe.poll():
            command, args = self.data_pipe.recv()
            self.post(command.lower(), args)

    def post(self, command, args):
        handler_name = "handle_{0}".format(command)
        handler = lambda *x: None
        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            print "unknown command {0}".format(command)
        handler(*args)

    def handle_go(self, advancing = 0, lateral = 0, angular = 0):
        self.wheels.target = (float(advancing),
                              float(lateral),
                              float(angular))

    def handle_acquire(self):
        if self.in_grab:
            return
        def acquire():
            self.in_grab = True
            self.grabber.vertical = 0.7
            yield 0.6
            self.grabber.grabber = 0.6
            yield 0.5
            self.grabber.vertical = -0.7
            yield 1.2
            self.grabber.grabber = -0.6
            yield 0.1
            self.grabber.vertical = 0.0
            yield 0.5
            self.in_grab = False
        schedule_by_parts(self.scheduler, acquire())

    def handle_deposit(self):
        if self.in_grab:
            return
        def acquire():
            self.in_grab = True
            self.grabber.vertical = -0.7
            yield 0.6
            self.grabber.grabber = 0.6
            yield 0.5
            self.grabber.vertical = 0.7
            yield 1.2
            self.grabber.grabber = -0.6
            yield 0.1
            self.grabber.vertical = 0.0
            yield 0.5
            self.in_grab = False
        schedule_by_parts(self.scheduler, acquire())

    def handle_adjust(self, state):
        state = (state.lower() == 'on')
        if state:
            self.wheels.start_turn_adjust()
        else:
            self.wheels.stop_turn_adjust()

    def handle_pan(self, yaw, pitch):
        yaw, pitch = float(yaw), float(pitch)
        self.camera_mount.yaw = radians(yaw)
        self.camera_mount.pitch = radians(pitch)

    def handle_headlights(self, state):
        state = (state.lower() == 'on')
        self.camera_mount.headlights = 0

    def handle_reset(self):
        self.camera_mount.yaw = 0
        self.camera_mount.pitch = 0
        self.camera_mount.headlights = False
        self.wheels.target = (0, 0, 0)

