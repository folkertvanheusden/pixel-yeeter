from PIL import Image, ImageColor, ImageDraw, ImageFont
from pixel_yeeter import backend
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

    def get_animation(self, name: str):
        self._runner_lock.acquire()
        rc = self._runner_work_items[name]
        self._runner_lock.release()
        return rc

    def get_resolution(self) -> list[int, int]:
        return self.b.get_width(), self.b.get_height()

    def clear_back(self) -> None:
        self.b.clear_back()

    def clear_screen(self) -> None:
        self.b.clear_screen()

    def clear_front(self) -> None:
        self.b.clear_front()

    def color_name_to_rgb(self, color: str) -> list[int, int, int]:
        try:
            return ImageColor.getrgb(color)
        except ValueError as v:
            return 127, 127, 127

    def color_name_to_rgb_alpha(self, color: str) -> list[int, int, int, int]:
        rgb = self.color_name_to_rgb(color)
        return rgb[0], rgb[1], rgb[2], 255

    def set_pixel_color_by_name(self, x: int, y: int, color: str) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.b.set_pixel_alpha(x, y, r, g, b, a)

    # r/g/b: 0...255
    def set_pixel_rgb(self, x: int, y: int, r: int, g: int, b: int, a: int = 255, layer: backend.layer_types = backend.layer_types.middle) -> None:
        self.b.set_pixel_alpha(x, y, r, g, b, a, layer)

    def draw_line_rgb(self, x_start: int, y_start: int, x_end: int, y_end: int, r: int, g: int, b: int, a: int = 255, layer: backend.layer_types = backend.layer_types.middle) -> None:
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
            self.b.set_pixel_alpha(coord[0], coord[1], r, g, b, a, layer)
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx

    def draw_line_color_by_name(self, x_start: int, y_start: int, x_end: int, y_end: int, color: str, layer: backend.layer_types = backend.layer_types.middle) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.draw_line_rgb(x_start, y_start, x_end, y_end, r, g, b, a, layer)

    def draw_pil_Image(self, pil_canvas: Image, x_offset: int, y_offset: int, layer: backend.layer_types = backend.layer_types.middle):
        for y in range(pil_canvas.height):
            y_use = y + y_offset
            if y_use < 0:
                continue
            region = pil_canvas.crop((0, y, pil_canvas.width, y + 1))
            rgb_values = list(region.tobytes())
            self.b.set_pixels_horizontal(x_offset, y_use, rgb_values, layer)

    def get_text_width(self, font_name: str, font_height: float, text: str) -> int:
        font = ImageFont.truetype(font_name, font_height, layout_engine=ImageFont.Layout.RAQM)
        text_dimensions = font.getbbox(text)
        return text_dimensions[2]

    def prepare_text(self, font_name_or_names: str | list, font_height: float, text: str, r: int, g: int, b: int, a: int) -> list[Image, int, int]:
        def font_has_glyph(font, ch):
            try:
                mask = font.getmask(ch)
                return mask.size[0] > 0 and mask.size[1] > 0
            except:
                return False

        def pick_best_font_for_str(fonts, str_):
            best_count = -1
            best_font = fonts[-1]
            for font in fonts:
                count = 0
                for c in str_:
                    if font_has_glyph(font, c):
                        count += 1
                if count == len(str_):
                    return font
                if count > best_count:
                    best_count = count
                    best_font = font
            return fonts[-1]   # fallback

        if type(font_name_or_names) == str:
            font = ImageFont.truetype(font_name_or_names, font_height)
        else:
            fonts = []
            for font_name in font_name_or_names:
                try:
                    fonts.append(ImageFont.truetype(font_name, font_height))
                except Exception as e:
                    print(f'Font {font_name} is not usable for height {font_height}: {e}')
            font = pick_best_font_for_str(fonts, text)
        text_dimensions = font.getbbox(text)
        image = Image.new('RGBA', (text_dimensions[2], text_dimensions[3]))
        pil_canvas = ImageDraw.Draw(image)
        pil_canvas.text((0, 0), text, (r, g, b, a), font = font, embedded_color=True)
        return image, text_dimensions[2], text_dimensions[3]

    def draw_prepared_text(self, prepared_text: list[Image, int, int], x: int, y: int, layer: backend.layer_types = backend.layer_types.middle):
        self.draw_pil_Image(prepared_text[0], x, y, layer)

    def draw_text(self, x: int, y: int, font_name: str, font_height: float, text: str, r: int, g: int, b: int, layer: backend.layer_types = backend.layer_types.middle) -> None:
        prepared_text = self.prepare_text(font_name, font_height, text, r, g, b, 255)
        self.draw_prepared_text(prepared_text, x, y, layer)

    def draw_text_color_by_name(self, x: int, y: int, font_name: str, font_height: float, text: str, color: str, layer: backend.layer_types = backend.layer_types.middle) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.draw_text(x, y, font_name, font_height, text, r, g, b, layer)

    def draw_sparkline_rgb(self, x: int, y: int, height: int, values: list[float], r: int, g: int, b: int, a: int = 255, layer: backend.layer_types = backend.layer_types.middle) -> None:
        if len(values) >= 1:
            mn, mx = min(values), max(values)
            extent = mx - mn
            if extent != 0:
                scaled = [int((v - mn) / extent * height) for v in values]
                y_prev_offset = scaled[0]
                for y_offset in scaled[1:]:
                    self.draw_line_rgb(x, y + y_prev_offset, x + 1, y + y_offset, r, g, b, a, layer)
                    x += 1
                    y_prev_offset = y_offset

    def draw_sparkline_color_by_name(self, x: int, y: int, height: int, values: list[float], color: str, layer: backend.layer_types = backend.layer_types.middle) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.draw_sparkline_rgb(x, y, height, values, r, g, b, a, layer)

    def fill_region_rgb(self, x: int, y: int, width: int, height: int, r: int, g: int, b: int, a: int = 255, layer: backend.layer_types = backend.layer_types.middle) -> None:
        rgb_values = [r, g, b, a] * width
        for work_y in range(y, y + height):
            self.b.set_pixels_horizontal(x, work_y, rgb_values, layer)

    def fill_region_color_by_name(self, x: int, y: int, width: int, height: int, color: str, layer: backend.layer_types = backend.layer_types.middle) -> None:
        r, g, b, a = self.color_name_to_rgb_alpha(color)
        self.fill_region_rgb(x, y, width, height, r, g, b, a, layer)

    def send_to_screen(self):
        self.b.update()

class animation:
    def __init__(self):
        self.run_count = 0

    def get_run_count(self) -> int:
        return self.run_count

    def tick(self, f: frontend) -> None:
        pass

class scroll_text(animation):
    def __init__(self, f: frontend, color_name: str, text: str, font_name_or_names: str | list = 'FreeSerif', speed: int = 10, font_height: int = None):
        super().__init__()
        self.text = text
        self.f = f
        self.target_width = f.get_resolution()[0]
        self.x = None
        self.clock = 0
        self.speed = speed

        r, g, b, a = f.color_name_to_rgb_alpha(color_name)
        prepared_text = f.prepare_text(font_name_or_names, f.get_resolution()[1] if font_height is None else font_height, text, r, g, b, a)
        self.image = prepared_text[0]

        new_height = f.get_resolution()[1]
        if new_height != prepared_text[2]:
            new_width  = int(new_height * prepared_text[1] / prepared_text[2])
            self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
            self.text_width = new_width
        else:
            self.text_width = prepared_text[1]

    def tick(self, f: frontend) -> None:
        if self.x == None:
            self.x = 0

        self.clock += 1
        if self.clock == self.speed:
            self.clock = 0
            f.clear_front()
            temp_x = self.x
            while temp_x < self.target_width:
                f.draw_pil_Image(self.image, temp_x, 0, backend.layer_types.front)
                temp_x += self.text_width
            self.x -= 1
            if self.x <= -self.text_width:
                self.x = 0
                self.run_count += 1
