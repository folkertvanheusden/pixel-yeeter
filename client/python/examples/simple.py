#! /usr/bin/env python

import pixel_yeeter.backend_pixelflood
import pixel_yeeter.frontend
import random
import sys
import time


canvas = pixel_yeeter.frontend.frontend(pixel_yeeter.backend_pixelflood.backend_pixelflood('192.168.65.140', 1337, True, None))
width, height = canvas.get_resolution()

while True:
    nr = random.randint(0, 2)

    if nr == 0:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        canvas.set_pixel_rgb(x, y, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    elif nr == 1:
        x1 = random.randint(0, width - 1)
        y1 = random.randint(0, height - 1)
        x2 = random.randint(0, width - 1)
        y2 = random.randint(0, height - 1)
        canvas.draw_line_rgb(x1, y1, x2, y2, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    elif nr == 2:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        canvas.draw_text(x, y, 'FreeSerif.ttf', height * 0.9, 'FvH!', random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    canvas.send_to_screen()
