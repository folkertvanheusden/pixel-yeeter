from matplotlib import colors
from PIL import Image, ImageDraw, ImageFont
from pixel_blaster import backend
import colorsys
import threading
import time


class frontend:
    def __init__(self, b: backend):
        self.b = b

        self._runner_work_items = dict()
        self._runner_lock = threading.Lock()
        threading.Thread(target=self._runner).start()

    def _runner(self) -> None:
        while True:
            self._runner_lock.acquire()
            for name in self._runner_work_items:
                self._runner_work_items[name].tick(self)
            if len(self._runner_work_items):
                self.send_to_screen()
            self._runner_lock.release()

            time.sleep(0.001)

    def add_animation(self, name: str, item) -> None:
        self._runner_lock.acquire()
        self._runner_work_items[name] = item
        self._runner_lock.release()

    def remove_animation(self, name: str) -> None:
        self._runner_lock.acquire()
        del self._runner_work_items[name]
        self._runner_lock.release()

    def get_resolution(self) -> list[int, int]:
        return self.b.get_width(), self.b.get_height()

    def clear_screen(self) -> None:
        self.b.clear_screen()

    def color_name_to_rgb_alpha(self, color: str) -> list[int, int, int, int]:
        try:
            r, g, b, a = colors.to_rgba(color)
            return int(r * 255), int(g * 255), int(b * 255), int(a * 255)
        except ValueError as v:
            return 127, 127, 127, 255

    def color_name_to_rgb(self, color: str) -> list[int, int, int]:
        try:
            r, g, b, a = colors.to_rgba(color)
            return int(r * 255), int(g * 255), int(b * 255)
        except ValueError as v:
            return 127, 127, 127

    def set_pixel_color_by_name(self, x: int, y: int, color: str) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.b.set_pixel(x, y, r, g, b, a)

    # r/g/b: 0...255
    def set_pixel_rgb(self, x: int, y: int, r: int, g: int, b: int) -> None:
        self.b.set_pixel(x, y, r, g, b)

    def draw_line_rgb(self, x_start: int, y_start: int, x_end: int, y_end: int, r: int, g: int, b: int) -> None:
        dx = x_end - x_start
        dy = y_end - y_start
        steep = abs(dy) > abs(dx)
        if steep:
            x_start, y_start = y_start, x_start
            x_end, y_end = y_end, x_end

        if x_start > x_end:
            x_start, x_end = x_end, x_start
            y_start, y_end = y_end, y_start

        dx = x_end - x_start
        dy = y_end - y_start

        error = int(dx / 2.0)
        ystep = 1 if y_start < y_end else -1

        y = y_start
        for x in range(x_start, x_end + 1):
            coord = (y, x) if steep else (x, y)
            self.b.set_pixel(coord[0], coord[1], r, g, b)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

    def draw_line_color_by_name(self, x_start: int, y_start: int, x_end: int, y_end: int, color: str) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.draw_line_rgb(x_start, y_start, x_end, y_end, r, g, b, a)

    def draw_pil_Image(self, pil_canvas: Image, x_offset: int, y_offset: int):
        for y in range(pil_canvas.height):
            y_use = y + y_offset
            if y_use < 0:
                continue
            rgb_values = [pil_canvas.getpixel((x, y)) for x in range(0, pil_canvas.width)]
            self.b.set_pixels_horizontal(x_offset, y_use, rgb_values)

    def draw_text(self, x: int, y: int, font_name: str, font_height: float, text: str, r: int, g: int, b: int) -> None:
        font = ImageFont.truetype(font_name, font_height)
        text_dimensions = font.getbbox(text)
        image = Image.new('RGB', (text_dimensions[2], text_dimensions[3]))
        pil_canvas = ImageDraw.Draw(image)
        pil_canvas.text((0, 0), text, (r, g, b), font = font)
        self.draw_pil_Image(image, x, y)

    def draw_text_color_by_name(self, x: int, y: int, font_name: str, font_height: float, text: str, color: str) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.draw_text(x, y, font_name, font_height, text, r, g, b, a)

    def draw_sparkline_rgb(self, x: int, y: int, height: int, values: list[float], r: int, g: int, b: int) -> None:
        if len(values) >= 2:
            mn, mx = min(values), max(values)
            extent = mx - mn
            scaled = [int((v - mn) / extent * height) for v in values]
            y_prev_offset = scaled[0]
            for y_offset in scaled[1:]:
                self.draw_line_rgb(x, y + y_prev_offset, x + 1, y + y_offset, r, g, b)
                x += 1
                y_prev_offset = y_offset

    def draw_sparkline_color_by_name(self, x: int, y: int, height: int, values: list[float], color: str) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.draw_sparkline_rgb(x, y, height, values, r, g, b, a)

    def fill_region_rgb(self, x: int, y: int, width: int, height: int, r: int, g: int, b: int) -> None:
        for work_y in range(y, y + height):
            for work_x in range(x, x + width):
                self.b.set_pixel(work_x, work_y, r, g, b)

    def fill_region_color_by_name(self, x: int, y: int, width: int, height: int, color: str) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.fill_region_rgb(x, y, width, height, r, g, b, a)

    def send_to_screen(self):
        self.b.update()

class animation:
    def __init__(self):
        pass

    def tick(self, f: frontend) -> None:
        pass

class scroll_text(animation):
    def __init__(self, f: frontend, color_name: str, text: str, font_name: str = 'FreeSerif'):
        self.text = text
        self.f = f
        self.target_width = f.get_resolution()[0]
        self.x = None
        self.clock = 0

        font = ImageFont.truetype(font_name, f.get_resolution()[1])
        text_dimensions = font.getbbox(self.text)
        self.image = Image.new('RGBA', (text_dimensions[2], text_dimensions[3]))
        self.text_width = text_dimensions[2]
        pil_canvas = ImageDraw.Draw(self.image)
        pil_canvas.text((0, 0), text, f.color_name_to_rgb_alpha(color_name), font = font)

    def tick(self, f: frontend) -> None:
        if self.x == None:
            self.x = self.target_width

        self.clock += 1
        if self.clock == 10:
            self.clock = 0
            f.draw_pil_Image(self.image, self.x, 0)
            self.x -= 1
            if self.x < -self.text_width:
                self.x = self.target_width
