#! /usr/bin/env python

import pixel_blaster.backend_ddp
import random
import sys
import time


b = pixel_blaster.backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32))

start_ts = time.time()
prev_ts = start_ts
n_frames = 0

while True:
    for y in range(b.get_height()):
        for x in range(b.get_width()):
            b.set_pixel(x, y, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    b.update()

    n_frames += 1
    now_ts = time.time()
    if now_ts - prev_ts >= 1.0:
        prev_ts = now_ts
        print(f'{n_frames / (now_ts - start_ts):.2f} FPS')
