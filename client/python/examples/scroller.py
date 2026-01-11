#! /usr/bin/env python

import backend_pixelflood
import frontend
import random
import time


canvas = frontend.frontend(backend_pixelflood.backend_pixelflood('192.168.65.140', 1338, False, (64, 32)))
canvas.add_animation('some_message', frontend.scroll_text(canvas, 'white', 'Hello, world!'))

while True:
    time.sleep(3600)
