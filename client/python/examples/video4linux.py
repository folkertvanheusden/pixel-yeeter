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

mode_since = time.time()
blob = True

bx = 0
by = 0
dx = -1
dy = 1

xt = 0
yt = 0

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

    factor_x = cam_width / (width * 2)
    factor_y = cam_height / (height * 2)
    factor = max(factor_x, factor_y)

    new_width = int(cam_width / factor)
    new_height = int(cam_height / factor)

    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    pil_img = Image.fromarray(img)

    # blob
    new_img = Image.new(mode='RGBA', size=(new_width, new_height))

    for y in range(new_height):
        for x in range(new_width):
            gx = x + math.sin((x + xt) / new_width * 2 * 3.1415) * new_width / 8
            if gx < 0:
                gx = 0
            elif gx >= new_width:
                gx = new_width -1
            gy = y + math.sin((y + yt) / new_height * 2 * 3.1415) * new_height / 8
            if gy < 0:
                gy = 0
            elif gy >= new_height:
                gy = new_height -1
            rgba = pil_img.getpixel((int(gx), int(gy)))
            new_img.putpixel((x, y), rgba)

    xt += 1
    if xt >= new_width:
        xt = 0
    yt += 1
    if yt >= new_height:
        yt = 0

    canvas.clear_front()
    canvas.draw_pil_Image(new_img, bx, by, pixel_yeeter.backend.layer_types.front)
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
