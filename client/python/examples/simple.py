#! /usr/bin/env python

import backend_pixelflood
import random
import sys


b = backend_pixelflood.backend_pixelflood('192.168.65.140', 1337, True)

while True:
    for y in range(b.get_height()):
        for x in range(b.get_width()):
            b.set_pixel(x, y, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    b.update()
