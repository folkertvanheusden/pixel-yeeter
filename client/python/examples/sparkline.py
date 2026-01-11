#! /usr/bin/env python

import backend_pixelflood
import frontend
import random
import time


canvas = frontend.frontend(backend_pixelflood.backend_pixelflood('192.168.65.140', 1337, True))

try:
    width, height = canvas.get_resolution()

    y1 = 0
    y2 = 0
    values1 = []
    values2 = []
    while True:
        y1 += random.random() * 2 - 1
        values1.append(y1)
        if len(values1) > width:
            del values1[0]
        y2 += random.random() * 2 - 1
        values2.append(y2)
        if len(values2) > width:
            del values2[0]

        canvas.clear_screen()
        canvas.draw_sparkline_rgb(0, 0, height, values1, 0, 255, 0)
        canvas.draw_sparkline_rgb(0, 0, height, values2, 255, 40, 40)
        canvas.send_to_screen()

        if len(values1) == width:
            time.sleep(0.5)

except KeyboardInterrupt as ki:
    print('Terminating')
