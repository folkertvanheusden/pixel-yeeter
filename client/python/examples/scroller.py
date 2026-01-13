#! /usr/bin/env python

import pixel_yeeter.backend_ddp
import pixel_yeeter.frontend
import random
import time


canvas = pixel_yeeter.frontend.frontend(pixel_yeeter.backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32)))
canvas.add_animation('some_message', pixel_yeeter.frontend.scroll_text(canvas, 'white', 'Hello, world!'))

while True:
    time.sleep(3600)
