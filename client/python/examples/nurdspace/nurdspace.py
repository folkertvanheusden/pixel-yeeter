#! /usr/bin/env python3

import pixel_yeeter.backend
import pixel_yeeter.backend_ddp
import pixel_yeeter.frontend
import paho.mqtt.client as mqtt
import queue
import random
import socket
import threading
import time

MQTT_POWER_HOST = 'mqtt.vm.nurd.space'
MQTT_POWER_PORT = 1883
MQTT_POWER_TOPIC = 'ha-bridge/sensor.power'
POWER_FONT = 'Courier_New.ttf'

MQTT_BTC_HOST = 'vps001.vanheusden.com'
MQTT_BTC_PORT = 1883
MQTT_BTC_TOPIC = 'vanheusden/bitcoin/bitstamp_usd'

#DDP_HOST = '192.168.65.140'
DDP_HOST = '10.208.1.48'
DDP_PORT = 4048
DDP_DIM = (128, 32)

MPD_HOST = 'spacesound.vm.nurd.space'
MPD_PORT = '6600'
MPD_FONT = 'Courier_New.ttf'
MPD_FONT_HEIGHT = 13

SCROLLER_PORT = 50010
SCROLLER_FONT = './UnifontExMono.ttf'
SCROLLER_SPEED = 1  # bigger value is slower, minimum is 1

HTTP_INTERFACE = '0.0.0.0'
HTTP_PORT = 8000

canvas = pixel_yeeter.frontend.frontend(pixel_yeeter.backend_ddp.backend_ddp(DDP_HOST, DDP_PORT, DDP_DIM))
width, height = canvas.get_resolution()

def mpd():
    from mpd import (MPDClient, CommandError)

    while True:
        try:
            client = MPDClient()
            client.connect(MPD_HOST, MPD_PORT)
            print('Connected to MPD server')

            while True:
                cs = client.currentsong()
                song = ''
                if 'artist' in cs:
                    song += cs['artist']
                if 'title' in cs:
                    song += ' - ' + cs['title']
                if 'name' in cs:
                    song += ' - ' + cs['name']

                text_y_offset = height - MPD_FONT_HEIGHT
                canvas.fill_region_color_by_name(0, text_y_offset, width, MPD_FONT_HEIGHT, 'black')
                canvas.draw_text_color_by_name(0, text_y_offset, MPD_FONT, MPD_FONT_HEIGHT - 2, song, 'grey', pixel_yeeter.backend.layer_types.middle)
                canvas.send_to_screen()

                time.sleep(5)

        except Exception as e:
            print(f'MPD failed: {e} ({e.__traceback__.tb_lineno})')
            time.sleep(1)

t_mpd = threading.Thread(target=mpd)
t_mpd.start()


def power_usage(queue: queue.Queue):
    def on_message(client, userdata, message):
        if message.topic == MQTT_POWER_TOPIC:
            try:
                power_value = float(message.payload.decode('utf-8'))
                queue.put(power_value)
                text = f'{int(power_value)} W'
                font_name = POWER_FONT
                font_height = 13
                text_x_offset = width - canvas.get_text_width(font_name, font_height, text)
                canvas.fill_region_color_by_name(text_x_offset, 0, width, font_height, 'black')
                if power_value > 1000:
                    color = 'red'
                elif power_value > 500:
                    color = 'yellow'
                else:
                    color = 'green'
                canvas.draw_text_color_by_name(text_x_offset, 0, font_name, font_height - 1, text, color, pixel_yeeter.backend.layer_types.middle)
                canvas.send_to_screen()
            except Exception as e:
                print(f'power usage on_message failed: {e} ({e.__traceback__.tb_lineno})')

    def on_connect(client, userdata, flags, rc, bla):
        if rc == 0:
            client.subscribe(MQTT_POWER_TOPIC)

    while True:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.connect(MQTT_POWER_HOST, port=MQTT_POWER_PORT, keepalive=60)
            client.on_message = on_message
            client.on_connect = on_connect
            client.loop_forever()

        except Exception as e:
            print(f'power usage failed: {e} ({e.__traceback__.tb_lineno})')
            time.sleep(1)

pu_queue = queue.Queue()
t_pu = threading.Thread(target=power_usage, args=(pu_queue,))
t_pu.start()

def btc(queue: queue.Queue):
    def on_message(client, userdata, message):
        if message.topic == MQTT_BTC_TOPIC:
            try:
                btc_value = float(message.payload.decode('utf-8'))
                queue.put(btc_value)
            except Exception as e:
                print(f'btc on_message failed: {e} ({e.__traceback__.tb_lineno})')

    def on_connect(client, userdata, flags, rc, bla):
        if rc == 0:
            client.subscribe(MQTT_BTC_TOPIC)

    while True:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.connect(MQTT_BTC_HOST, port=MQTT_BTC_PORT, keepalive=60)
            client.on_message = on_message
            client.on_connect = on_connect
            client.loop_forever()

        except Exception as e:
            print(f'btc failed: {e} ({e.__traceback__.tb_lineno})')
            time.sleep(1)

btc_queue = queue.Queue()
t_btc = threading.Thread(target=btc, args=(btc_queue,))
t_btc.start()

def scroller(queue):
    def stripper(what_in):
        what = ''
        skip = False
        for w in what_in:
            if skip:
                if w == '$':
                    skip = False
            elif w == '$':
                skip = True
            else:
                what += w
        return what

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('0.0.0.0', SCROLLER_PORT))
    while True:
        try:
            data = s.recv(1024)
            stripped = stripper(data.decode('utf-8'))
            queue.put(stripped)

        except Exception as e:
            print(f'scroller failed: {e} ({e.__traceback__.tb_lineno})')
            time.sleep(0.1)

scroller_queue = queue.Queue()
t_scroller = threading.Thread(target=scroller, args=(scroller_queue,))
t_scroller.start()
scroller_name = 'scroller_msg'

def http_rest(queue):
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class http_server(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/':
                try:
                    length = int(self.headers.get('content-length'))
                    msg = self.rfile.read(length)
                    queue.put(msg.decode('ascii'))
                    self.send_response(200)
                except Exception as e:
                    print(f'http_rest (POST) failed: {e} ({e.__traceback__.tb_lineno})')
                    self.send_response(500)
            else:
                self.send_response(404)
            self.end_headers()

    httpd = HTTPServer((HTTP_INTERFACE, HTTP_PORT), http_server)
    httpd.serve_forever()

t_http = threading.Thread(target=http_rest, args=(scroller_queue,))
t_http.start()

pu_values = []
btc_values = []
scroller_since = None

while True:
    try:
        # power usage
        try:
            value = pu_queue.get(timeout = 0.1)
            pu_values.append(value)
            while len(pu_values) > width:
                del pu_values[0]
        except queue.Empty:
            pass

        # bitcoin
        try:
            value = btc_queue.get(timeout = 0.1)
            btc_values.append(value)
            while len(btc_values) > width:
                del btc_values[0]
        except queue.Empty:
            pass

        canvas.clear_back()
        canvas.draw_sparkline_color_by_name(0, 0, height - MPD_FONT_HEIGHT, pu_values, 'red', pixel_yeeter.backend.layer_types.back)
        canvas.draw_sparkline_color_by_name(0, 0, height - MPD_FONT_HEIGHT, btc_values, 'blue', pixel_yeeter.backend.layer_types.back)
        canvas.send_to_screen()

        # scroller
        try:
            text = scroller_queue.get(timeout = 0.1)
            if not scroller_since is None:
                canvas.remove_animation(scroller_name)
            canvas.add_animation(scroller_name, pixel_yeeter.frontend.scroll_text(canvas, 'white', text, font_name_or_names=SCROLLER_FONT, speed=SCROLLER_SPEED))
            scroller_since = time.time()
        except queue.Empty:
            pass

        if not scroller_since is None:
            now = time.time()
            if now - scroller_since >= 10.0 and canvas.get_animation(scroller_name).get_run_count() >= 2:
                canvas.remove_animation(scroller_name)
                scroller_since = None
                canvas.clear_front()
                canvas.send_to_screen()

    except Exception as e:
        print(f'main failed: {e} ({e.__traceback__.tb_lineno})')
        time.sleep(1)
