from matplotlib import colors
from PIL import Image, ImageDraw, ImageFont
import backend
import colorsys


class frontend:
    def __init__(self, b: backend):
        self.b = b

    def get_resolution(self) -> list[int, int]:
        return self.b.get_width(), self.b.get_height()

    def _color_name_to_rgb(self, color: str) -> list[int, int, int]:
        try:
            r, g, b = colors.to_rgba(color)
            return int(r * 255), int(g * 255), int(b * 255)
        except ValueError as v:
            return 127, 127, 127

    def set_pixel_color_by_name(self, x: int, y: int, color: str) -> None:
        r, g, b = self._color_name_to_rgb(color)
        self.b.set_pixel(x, y, r, g, b)

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
        r, g, b = self._color_name_to_rgb(color)
        self.draw_line_rgb(x_start, y_start, x_end, y_end, r, g, b)

    def draw_pil_Image(self, pil_canvas: Image, x_offset: int, y_offset: int):
        for y in range(pil_canvas.height):
            y_use = y + y_offset
            for x in range(pil_canvas.width):
                rgb = pil_canvas.getpixel((x, y))
                self.b.set_pixel(x + x_offset, y_use, rgb[0], rgb[1], rgb[2])

    def draw_text(self, x: int, y: int, font_name: str, font_height: float, text: str, r: int, g: int, b: int) -> None:
        font = ImageFont.truetype(font_name, font_height)
        text_dimensions = font.getbbox(text)
        image = Image.new('RGB', (text_dimensions[2], text_dimensions[3]))
        pil_canvas = ImageDraw.Draw(image)
        pil_canvas.text((0, 0), text, (r, g, b), font = font)
        self.draw_pil_Image(image, x, y)

    def draw_text_color_by_name(self, x: int, y: int, font_name: str, font_height: float, text: str, color: str) -> None:
        r, g, b = self._color_name_to_rgb(color)
        self.draw_text(x, y, font_name, font_height, text, r, g, b)

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
        r, g, b = self._color_name_to_rgb(color)
        self.draw_sparkline_rgb(x, y, height, values, r, g, b)

    def fill_region_rgb(self, x: int, y: int, width: int, height: int, r: int, g: int, b: int) -> None:
        for work_y in range(y, y + height):
            for work_x in range(x, x + width):
                self.b.set_pixel(work_x, work_y, r, g, b)

    def fill_region_color_by_name(self, x: int, y: int, width: int, height: int, color: str) -> None:
        r, g, b = self._color_name_to_rgb(color)
        self.fill_region_rgb(x, y, width, height, r, g, b)

    def send_to_screen(self):
        self.b.update()
