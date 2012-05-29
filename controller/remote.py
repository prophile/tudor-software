import socket

def _setup_network(settings):
    pass

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

