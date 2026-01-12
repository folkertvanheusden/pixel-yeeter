#! /usr/bin/env python

import backend_ddp
import frontend
import random
import time


canvas = frontend.frontend(backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32)))

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
        canvas.draw_sparkline_color_by_name(0, 0, height, values1, 'green')
        canvas.draw_sparkline_color_by_name(0, 0, height, values2, 'red')
        canvas.send_to_screen()

        time.sleep(0.05 if len(values1) == width else 0.01)

except KeyboardInterrupt as ki:
    print('Terminating')
