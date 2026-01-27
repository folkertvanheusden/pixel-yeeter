#! /usr/bin/env python

# apt install python3-opencv
# or pip install opencv-python

from PIL import Image
import cv2
import math
import numpy
import pixel_yeeter
import time


def decode_fourcc(cc):
    return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])


canvas = pixel_yeeter.frontend.frontend(pixel_yeeter.backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32)))
width, height = canvas.get_resolution()

cap = cv2.VideoCapture(0)
cam_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
cam_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

mode = 0
mode_since = time.time()

bx = 0
by = 0
dx = -1
dy = 1

while True:
    _status, img = cap.read()
    if not _status:
        continue

    fourcc = decode_fourcc(cap.get(cv2.CAP_PROP_FOURCC))

    if not bool(cap.get(cv2.CAP_PROP_CONVERT_RGB)):
        if fourcc == "MJPG":
            img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
        elif fourcc == "YUYV":
            img = cv2.cvtColor(img, cv2.COLOR_YUV2GRAY_YUYV)
        else:
            print(f'{fourcc}: unsupported video format')
            break

    if mode == 0:
        factor_x = cam_width / (width * 2)
        factor_y = cam_height / (height * 2)
        factor = max(factor_x, factor_y)

        new_width = int(cam_width / factor)
        new_height = int(cam_height / factor)

        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        pil_img = Image.fromarray(img)
        canvas.clear_front()
        canvas.draw_pil_Image(pil_img, bx, by, pixel_yeeter.backend.layer_types.front)
        canvas.send_to_screen()

        bx += dx
        if bx <= -new_width / 4:
            dx = 1
        elif bx >= 0:
            dx = -1
        by += dy
        if by <= -new_height / 2:
            dy = 1
        elif by >= 0:
            dy = -1

    else:
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        pil_img = Image.fromarray(img)
        new_img = Image.new(mode='RGBA', size=(width, height))

        for y in range(height):
            for x in range(width):
                gx = x + math.sin(x / width * 2 * 3.1415) * width / 8
                if gx < 0:
                    gx = 0
                elif gx >= width:
                    gx = width -1
                gy = y + math.sin(y / height * 2 * 3.1415) * height / 8
                if gy < 0:
                    gy = 0
                elif gy >= height:
                    gy = height -1
                rgba = pil_img.getpixel((int(gx), int(gy)))
                new_img.putpixel((x, y), rgba)

        canvas.clear_front()
        canvas.draw_pil_Image(new_img, 0, 0, pixel_yeeter.backend.layer_types.front)
        canvas.send_to_screen()

    now = time.time()
    if now - mode_since >= 7.5:
        mode_since = now
        mode = (mode + 1) % 2
