from pixel_yeeter import backend
import socket
import time


class backend_ddp(backend.backend):
    def __init__(self, host: str, port: int, dimensions: list[int, int]):
        super().__init__(dimensions[0], dimensions[1])
        self.host = host
        self.port = port
        self.fd = None

        self.update()

    def update(self):
        while True:
            try:
                if self.fd is None:
                    self.fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                def gen_header():
                    buffer = bytearray()
                    buffer.append(64)  # version 1
                    buffer.append(0)  # no alpha
                    buffer.append((1 << 3) | 3)  # RGB, 8 bit
                    buffer.append(1)  # default output device
                    buffer.append(0)  # offset
                    buffer.append(0)
                    buffer.append(0)
                    buffer.append(0)
                    buffer.append(0)  # length
                    buffer.append(0)
                    assert len(buffer) == 10
                    return buffer

                packets = []
                buffer = gen_header()
                p_offset = offset = 0
                for y in range(self.height):
                    for x in range(self.width):
                        r, g, b = self.get_mixed_pixel(x, y)
                        buffer.append(r)
                        buffer.append(g)
                        buffer.append(b)
                        offset += 3

                        if len(buffer) > 1440 - 3:
                            payload_len = len(buffer) - 10
                            buffer[4] = p_offset >> 24
                            buffer[5] = (p_offset >> 16) & 255
                            buffer[6] = (p_offset >> 8) & 255
                            buffer[7] = p_offset & 255
                            buffer[8] = payload_len >> 8
                            buffer[9] = payload_len & 255
                            packets.append(buffer)
                            p_offset = offset
                            buffer = gen_header()

                if len(buffer) > 10:
                    payload_len = len(buffer) - 10
                    buffer[4] = p_offset >> 24
                    buffer[5] = (p_offset >> 16) & 255
                    buffer[6] = (p_offset >> 8) & 255
                    buffer[7] = p_offset & 255
                    buffer[8] = payload_len >> 8
                    buffer[9] = payload_len & 255
                    packets.append(buffer)

                packets[-1][0] |= 1  # PUSH flag

                for packet in packets:
                    self.fd.sendto(packet, (self.host, self.port))

                break  # all good

            except Exception as e:
                print(f'backend_ddp::update: {e} ({e.__traceback__.tb_lineno})')
                self.fd.close()
                self.fd = None
                time.sleep(0.5)
