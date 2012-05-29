import socket, time

def _network_command(command, *args, **kwargs):
    print command.format(*args, **kwargs)

def _setup_network(settings):
    settings = settings or {}
    network_settings = settings.get('network', {})
    interface = network_settings.get('interface', 'wlan0')
    key = network_settings.get('key', None)
    ssid = network_settings.get('ssid', 'SR-COMPETITOR')
    mode = network_settings.get('mode', 'managed')
    # Kill NM
    _network_command('killall NetworkManager')

    # Connection to the wireless network
    _network_command('iwconfig {interface} down', interface=interface)
    _network_command('iwconfig {interface} mode {mode}', interface=interface,
                                                         mode=mode)
    if key is not None:
        _network_command('iwconfig {interface} key "{key}"', interface=interface,
                                                           key=key)
    _network_command('iwconfig {interface} essid {ssid}', interface=interface,
                                                          ssid=ssid)
    _network_command('iwconfig {interface} up', interface=interface)
    _network_command('yes n | dhclient {interface}', interface=interface)

    # Wait 5 seconds for configuration to finish
    time.sleep(5)

    # Dump the config to the screen
    _network_command('ifconfig')

def _start_gstreamer(settings, address):
    pass

def _stop_gstreamer(settings):
    pass

def remote_control(settings):
    _setup_network(settings)
    listener = socket.socket(socket.AF_INET6,
                             socket.SOCK_STREAM,
                             socket.SOL_TCP)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('::', 13525))
    listener.listen(5)
    while True:
        (client, address) = listener.accept()
        _start_gstreamer(settings, address[0])
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
        _stop_gstreamer(settings)

