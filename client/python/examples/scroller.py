#! /usr/bin/env python

import backend_ddp
import frontend
import random
import time


canvas = frontend.frontend(backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32)))
canvas.add_animation('some_message', frontend.scroll_text(canvas, 'white', 'Hello, world!'))

while True:
    time.sleep(3600)
