from pixel_blaster import backend
import socket
import time


class backend_pixelflood(backend.backend):
    def __init__(self, host: str, port: int, is_tcp: bool, override_dimensions: list[int, int] | None):
        if override_dimensions:
            super().__init__(override_dimensions[0], override_dimensions[1])
        else:
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
                    if self.is_tcp:
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

                    else:
                        self.fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                if self.is_tcp:
                    self.fd.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)

                    for y in range(self.height):
                        buffer = ''
                        for x in range(self.width):
                            r, g, b = self.get_pixel(x, y)
                            buffer += f'PX {x} {y} {r:02x}{g:02x}{b:02x}\n'

                        self.fd.send(buffer.encode('ascii'))

                    self.fd.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                else:
                    buffer = bytearray()
                    buffer.append(0)  # version
                    buffer.append(0)  # no alpha

                    for y in range(self.height):
                        for x in range(self.width):
                            buffer.append(x & 255)
                            buffer.append(x >> 8)
                            buffer.append(y & 255)
                            buffer.append(y >> 8)
                            r, g, b = self.get_mixed_pixel(x, y)
                            buffer.append(r)
                            buffer.append(g)
                            buffer.append(b)

                            if len(buffer) > 1122 - 7:
                                self.fd.sendto(buffer, (self.host, self.port))
                                buffer = bytearray()
                                buffer.append(0)  # version
                                buffer.append(0)  # no alpha

                    if len(buffer) > 2:
                        self.fd.sendto(buffer, (self.host, self.port))

                break  # succes!

            except Exception as e:
                print(f'backend_pixelflood::update: {e} ({e.__traceback__.tb_lineno})')
                self.fd.close()
                self.fd = None
                time.sleep(0.5)
