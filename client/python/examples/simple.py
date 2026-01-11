#! /usr/bin/env python

import backend_pixelflood
import frontend
import random
import sys
import time


canvas = frontend.frontend(backend_pixelflood.backend_pixelflood('192.168.65.140', 1337, True))
width, height = canvas.get_resolution()

while True:
    if random.randint(0, 1):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        canvas.set_pixel_rgb(x, y, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    else:
        x1 = random.randint(0, width - 1)
        y1 = random.randint(0, height - 1)
        x2 = random.randint(0, width - 1)
        y2 = random.randint(0, height - 1)
        canvas.draw_line_rgb(x1, y1, x2, y2, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    canvas.send_to_screen()
