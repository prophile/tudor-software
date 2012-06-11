import socket, time, subprocess, os

PORT = 13525

def _network_command(command, *args, **kwargs):
    cmd = command.format(*args, **kwargs)
    print cmd
    os.system(cmd)

def _setup_network(settings):
    settings = settings or {}
    network_settings = settings.get('network', {})
    interface = network_settings.get('interface', 'wlan0')
    key = network_settings.get('key', None)
    ssid = network_settings['ssid']
    mode = network_settings.get('mode', 'managed')
    # Kill NM
    _network_command('killall NetworkManager')

    # Connection to the wireless network
    _network_command('ifconfig {interface} down', interface=interface)
    _network_command('iwconfig {interface} mode {mode}', interface=interface,
                                                         mode=mode)
    if key is not None:
        _network_command('iwconfig {interface} key "{key}"', interface=interface,
                                                           key=key)
    _network_command('iwconfig {interface} essid {ssid}', interface=interface,
                                                          ssid=ssid)
    _network_command('ifconfig {interface} up', interface=interface)
    _network_command('yes n | dhclient {interface}', interface=interface)

    # Wait 5 seconds for configuration to finish
    time.sleep(5)

    # Dump the config to the screen
    _network_command('ifconfig')

class _Streamer(object):
    COMMAND = ("gst-launch autovideosrc ! "
               "video/x-raw-rgb,width=320,height=240,framerate=5/1 ! "
               "ffmpegcolorspace ! "
               "theoraenc speed-level=2 quality=63 ! "
               "udpsink host={host} port=5000")

    def __init__(self, settings):
        self.instance = None

    def start(self, address):
        self.instance = subprocess.Popen(self.COMMAND.format(host=address),
                                         shell=True)

    def stop(self):
        self.instance.terminate()
        self.instance = None

def remote_control(settings):
    _setup_network(settings)
    try:
        listener = socket.socket(socket.AF_INET6,
                                 socket.SOCK_STREAM,
                                 socket.SOL_TCP)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('::', PORT))
        listener.listen(5)
    # TODO: make this exception more constrained
    except Exception:
        print "WARNING: morons detected, IPv6 may have been disabled"
        listener = socket.socket(socket.AF_INET,
                                 socket.SOCK_STREAM,
                                 socket.SOL_TCP)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(('0.0.0.0', PORT))
        listener.listen(5)
    print "Listening on {0}...".format(PORT)
    streamer = _Streamer(settings)
    while True:
        (client, address) = listener.accept()
        print "Got connection from {0}".format(address[0])
        streamer.start(address[0])
        client.settimeout(8)
        client_fp = client.makefile()
        try:
            while True:
                line = client_fp.readline()
                parts = line.strip().split(' ')
                command = parts[0]
                args = parts[1:]
                yield command, args
        except IOError:
            client_fp.close()
            client.close()
        streamer.stop()
        print "Lost connection."

