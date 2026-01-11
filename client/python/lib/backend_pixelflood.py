import backend
import socket
import time


class backend_pixelflood(backend.backend):
    def __init__(self, host: str, port: int, is_tcp: bool):
        super().__init__(1, 1)
        self.host = host
        self.port = port
        self.is_tcp = is_tcp
        self.fd = None

        self.update()

    def update(self):
        while True:
            try:
                if self.fd == None:
                    self.fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.fd.connect((self.host, self.port))
                    self.fd.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    self.fd.send('SIZE\n'.encode('ascii'))

                    reply = ''
                    while True:
                        cur_reply = self.fd.recv(4096).decode('ascii')
                        reply += cur_reply
                        if '\n' in cur_reply:
                            break

                    parts = cur_reply.replace('\n', ' ').split()
                    new_width = int(parts[1])
                    new_height = int(parts[2])
                    if new_width != self.width or new_height != self.height:
                        self._init(new_width, new_height)

                self.fd.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)

                for y in range(self.height):
                    for x in range(self.width):
                        r, g, b = self.get_pixel(x, y)
                        self.fd.send(f'PX {x} {y} {r:02x}{g:02x}{b:02x}\n'.encode('ascii'))

                self.fd.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                break  # succes!

            except Exception as e:
                print(f'backend_pixelflood::update: {e} ({e.__traceback__.tb_lineno})')
                self.fd.close()
                self.fd = None
                time.sleep(0.5)
