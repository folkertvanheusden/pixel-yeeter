#! /usr/bin/env python3

import numpy as np
import os
import pixel_yeeter.backend
import pixel_yeeter.backend_ddp
import pixel_yeeter.frontend
import paho.mqtt.client as mqtt
import queue
import random
import socket
import sounddevice as sd
import threading
import time

MQTT_POWER_HOST = 'mqtt.vm.nurd.space'
MQTT_POWER_PORT = 1883
MQTT_POWER_TOPIC = 'ha-bridge/sensor.power'
POWER_FONT = 'Courier_New.ttf'
POWER_TEXT_HEIGHT = 13

MQTT_BTC_HOST = 'vps001.vanheusden.com'
MQTT_BTC_PORT = 1883
MQTT_BTC_TOPIC = 'vanheusden/bitcoin/bitstamp_usd'

MQTT_STATE_HOST = 'mqtt.vm.nurd.space'
MQTT_STATE_PORT = 1883
MQTT_STATE_TOPIC = 'space/statedigit'

#DDP_HOST = '192.168.65.140'
DDP_HOST = '10.208.1.48'
DDP_PORT = 4048
DDP_DIM = (128, 32)

MPD_HOST = 'spacesound.vm.nurd.space'
MPD_PORT = '6600'
MPD_FONT = '/home/nurds/pixel-yeeter/client/python/examples/nurdspace/Catrinity.otf'
MPD_FONT_HEIGHT = 16

SCROLLER_PORT = 50010
SCROLLER_FONT = '/home/nurds/pixel-yeeter/client/python/examples/nurdspace/Catrinity.otf'
SCROLLER_SPEED = 3  # bigger value is slower, minimum is 1

HTTP_INTERFACE = '0.0.0.0'
HTTP_PORT = 8000

space_state_value = 1

canvas = pixel_yeeter.frontend.frontend(pixel_yeeter.backend_ddp.backend_ddp(DDP_HOST, DDP_PORT, DDP_DIM))
width, height = canvas.get_resolution()

# TODO replace by condition-variable
def check_space_state():
    while space_state_value == 0:
        time.sleep(1)


def mpd():
    from mpd import (MPDClient, CommandError)

    while True:
        check_space_state()

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
                canvas.draw_text_color_by_name(0, text_y_offset, MPD_FONT, MPD_FONT_HEIGHT, song, 'grey', pixel_yeeter.backend.layer_types.middle)
                canvas.send_to_screen()

                time.sleep(1)
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
                font_height = POWER_TEXT_HEIGHT
                text_x_offset = width - canvas.get_text_width(font_name, font_height, '9999 W')
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
            print(f'Subscribe to {MQTT_POWER_TOPIC}')
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
            print(f'Subscribe to {MQTT_BTC_TOPIC}')
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


prev_space_state_value = None
def space_state():
    def on_message(client, userdata, message):
        global space_state_value
        global prev_space_state_value

        if message.topic == MQTT_STATE_TOPIC:
            try:
                space_state_value = float(message.payload.decode('utf-8'))
                if space_state_value != prev_space_state_value:
                    prev_space_state_value = space_state_value
                    print(f'Space state is now {"open" if space_state_value else "closed"}')
            except Exception as e:
                print(f'space_state on_message failed: {e} ({e.__traceback__.tb_lineno})')

    def on_connect(client, userdata, flags, rc, bla):
        if rc == 0:
            print(f'Subscribe to {MQTT_STATE_TOPIC}')
            client.subscribe(MQTT_STATE_TOPIC)

    while True:
        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            client.connect(MQTT_STATE_HOST, port=MQTT_STATE_PORT, keepalive=60)
            client.on_message = on_message
            client.on_connect = on_connect
            client.loop_forever()

        except Exception as e:
            print(f'space_state failed: {e} ({e.__traceback__.tb_lineno})')
            time.sleep(1)

space_state_queue = queue.Queue()
t_space_state = threading.Thread(target=space_state)
t_space_state.start()


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


def snapcast():
    # from systemd
    #def run_snapcast():
    #    os.system('/usr/bin/snapclient -s 1')
    #t = threading.Thread(target=run_snapcast)
    #t.start()

    try:
        samplerate = 8000
        channels = 1
        new_idx = np.linspace(0, 1, 64)  # 64 is width of line
        new_fft_idx = np.linspace(0, 1, 64)

        def callback(indata, frames, time, status):
            if space_state_value == 0:
                return
            if status:
                print(status)
            audio = indata.copy()
            # audio is a NumPy array (frames x channels)
            if audio.shape[0] == 1:
                return
            arr = np.asarray([x[0] for x in audio])
            # interpolate
            n = len(arr)
            old_idx = np.linspace(0, 1, n)
            new_data = np.interp(new_idx, old_idx, arr)
            # fft
            np_fft = np.fft.fft(arr)
            amplitudes = 2 / len(arr) * np.abs(np_fft)
            old_fft_idx = np.linspace(0, 1, len(amplitudes) // 2)
            new_fft_data = np.interp(new_fft_idx, old_fft_idx, [-a for a in amplitudes[0:len(amplitudes) // 2]])
            # print(len(new_fft_data), new_fft_data)

            canvas.fill_region_color_by_name(0, 16, 128, 16, 'black', layer=pixel_yeeter.backend.layer_types.back)
            canvas.draw_sparkline_color_by_name(64, 16, 16, new_fft_data, 'green', pixel_yeeter.backend.layer_types.back)
            canvas.draw_sparkline_color_by_name(0, 16, 16, new_data, 'brown', pixel_yeeter.backend.layer_types.back)
            canvas.send_to_screen()

        with sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            device=0,
            callback=callback
        ):
            while True:
                time.sleep(1000)

    except Exception as e:
        print(f'snapcast failed: {e} ({e.__traceback__.tb_lineno})')
        print(sd.query_devices())

t_snapcast = threading.Thread(target=snapcast)
t_snapcast.start()


pu_values = []
btc_values = []
scroller_since = None
ping_state = False

while True:
    try:
        if space_state_value == 0:
            canvas.clear_back()
            canvas.clear_middle()
            canvas.clear_front()
            c = 255 if ping_state else 0
            ping_state = not ping_state
            canvas.set_pixel_rgb(width // 2, height // 2, c, c, c)
            canvas.send_to_screen()
            time.sleep(1/3)
            continue

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
        canvas.draw_sparkline_color_by_name(0, 0, 16, pu_values, 'red', pixel_yeeter.backend.layer_types.back)
        canvas.draw_sparkline_color_by_name(0, 0, 16, btc_values, 'blue', pixel_yeeter.backend.layer_types.back)
        canvas.send_to_screen()

        # scroller
        try:
            text = scroller_queue.get(timeout = 0.1)
            if len(text) > 1 and text[-1] != ' ':
                text += ' '
            if not scroller_since is None:
                canvas.remove_animation(scroller_name)
            canvas.add_animation(scroller_name, pixel_yeeter.frontend.scroll_text(canvas, 'white', text, font_name_or_names=SCROLLER_FONT, speed=SCROLLER_SPEED))
            scroller_since = time.time()
        except queue.Empty:
            pass

        if not scroller_since is None:
            now = time.time()
            if now - scroller_since >= 15.0 and canvas.get_animation(scroller_name).get_run_count() >= 5:
                canvas.remove_animation(scroller_name)
                scroller_since = None
                canvas.clear_front()
                canvas.send_to_screen()

    except Exception as e:
        print(f'main failed: {e} ({e.__traceback__.tb_lineno})')
        time.sleep(1)
