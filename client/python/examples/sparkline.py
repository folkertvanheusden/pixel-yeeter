#! /usr/bin/env python

import backend_pixelflood
import frontend
import random
import time


canvas = frontend.frontend(backend_pixelflood.backend_pixelflood('192.168.65.140', 1337, True))

try:
    width, height = canvas.get_resolution()

    y = 0
    values = []
    while True:
        y += random.random() * 2 - 1
        values.append(y)
        if len(values) > width:
            del values[0]

        canvas.clear_screen()
        canvas.draw_sparkline_rgb(0, 0, height, values, 0, 255, 0)
        canvas.send_to_screen()

        if len(values) == width:
            time.sleep(0.5)

except KeyboardInterrupt as ki:
    print('Terminating')
