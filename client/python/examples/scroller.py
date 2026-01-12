#! /usr/bin/env python

import pixel_blaster.backend_ddp
import pixel_blaster.frontend
import random
import time


canvas = pixel_blaster.frontend.frontend(pixel_blaster.backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32)))
canvas.add_animation('some_message', pixel_blaster.frontend.scroll_text(canvas, 'white', 'Hello, world!'))

while True:
    time.sleep(3600)
