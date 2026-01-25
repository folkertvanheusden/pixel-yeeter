#! /usr/bin/env python

# apt install python3-opencv
# or pip install opencv-python

from PIL import Image
import cv2
import numpy
import pixel_yeeter
import time


def decode_fourcc(cc):
    return "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])


b = pixel_yeeter.backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32))
width, height = b.get_width(), b.get_height()

cap = cv2.VideoCapture(0)
cam_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
cam_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

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
            print("unsupported video format")
            break

    factor_x = cam_width / width
    factor_y = cam_height / height
    factor = max(factor_x, factor_y)

    new_width = int(cam_width / factor)
    new_height = int(cam_height / factor)

    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    for y in range(new_height):
        for x in range(new_width):
            p = img[y][x]
            b.set_pixel(x, y, int(p[2]), int(p[1]), int(p[0]))
    b.update()
