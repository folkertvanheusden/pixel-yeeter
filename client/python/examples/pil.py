#! /usr/bin/env python

from PIL import Image, ImageDraw, ImageFont
import backend_pixelflood
import colorsys
import frontend
import time


text = 'Hello'
canvas = frontend.frontend(backend_pixelflood.backend_pixelflood('192.168.65.140', 1337, True, None))
width, height = canvas.get_resolution()

x = 0
y = 0
dx = 1
dy = 1

image = Image.new('RGB', (width, height))
pil_canvas = ImageDraw.Draw(image)
font = ImageFont.truetype('FreeSerif.ttf', height * 0.9)

h = 0

while True:
    rgb_in = colorsys.hls_to_rgb(h / 360, 0.5, 1)
    h += 1
    if h == 360:
        h = 0
    rgb_out = (int(rgb_in[0] * 255), int(rgb_in[1] * 255), int(rgb_in[2] * 255))

    pil_canvas.rectangle((0, 0, width, height), fill = 'black')
    pil_canvas.text((x, y), text, rgb_out, font = font)

    canvas.draw_pil_Image(image, x, y)
    canvas.send_to_screen()

    y += dy
    if y >= height:
        y = height - 1
        dy = -1
    elif y < -height:
        y = -height
        dy = 1

    time.sleep(0.01)
