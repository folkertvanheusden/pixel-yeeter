#! /usr/bin/env python

import pixel_yeeter
import random
import time


canvas = pixel_yeeter.frontend.frontend(pixel_yeeter.backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32)))
width, height = canvas.get_resolution()
canvas.clear_screen()
for y in range(height):
    canvas.draw_line_rgb(0, y, width, y, 0, 0, 255)
canvas.draw_line_rgb(0, 0, width, height, 0, 255, 0)
canvas.draw_line_rgb(width, 0, 0, height, 255, 0, 0)
canvas.send_to_screen()

while True:
    time.sleep(3600)
