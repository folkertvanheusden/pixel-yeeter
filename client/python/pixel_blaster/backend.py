class backend:
    def __init__(self, width: int, height: int):
        self._init(width, height)

    def _init(self, width: int, height: int):
        self.width = width
        self.height = height
        self.clear_screen()
        self.clear_overlay()

    def clear_screen(self) -> None:
        self.fb = [ 0 ] * self.width * self.height * 4

    def clear_overlay(self) -> None:
        self.fbo = [ 0 ] * self.width * self.height * 4

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int, overlay: bool = False) -> None:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            reference = self.fbo if overlay else self.fb
            reference[o + 0] = r & 255
            reference[o + 1] = g & 255
            reference[o + 2] = b & 255
            reference[o + 3] = 255

    def set_pixel_alpha(self, x: int, y: int, r: int, g: int, b: int, a: int, overlay: bool = False) -> None:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            reference = self.fbo if overlay else self.fb
            reference[o + 0] = r & 255
            reference[o + 1] = g & 255
            reference[o + 2] = b & 255
            reference[o + 3] = a & 255

    def set_pixels_horizontal(self, x: int, y: int, values: list[list[int]], overlay: bool = False) -> None:
        if len(values) == 0 or y >= self.height or y < 0:
            return
        offset_y = self.width * y * 4
        reference = self.fbo if overlay else self.fb
        if len(values[0]) == 4:
            for x_work in range(max(0, x), min(self.width, x + len(values))):
                offset_work = offset_y + x_work * 4
                pixel = values[x_work - x]
                reference[offset_work + 0] = pixel[0]
                reference[offset_work + 1] = pixel[1]
                reference[offset_work + 2] = pixel[2]
                reference[offset_work + 3] = pixel[3]
        else:
            for x_work in range(max(0, x), min(self.width, x + len(values))):
                offset_work = offset_y + x_work * 4
                pixel = values[x_work - x]
                reference[offset_work + 0] = pixel[0]
                reference[offset_work + 1] = pixel[1]
                reference[offset_work + 2] = pixel[2]
                reference[offset_work + 3] = 255

    def get_pixel(self, x: int, y: int, overlay: bool = False) -> list[int, int, int]:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            reference = self.fbo if overlay else self.fb
            o = y * self.width * 4 + x * 4
            return reference[o + 0], reference[o + 1], reference[o + 2] 
        return None

    def get_pixel_alpha(self, x: int, y: int, overlay: bool = False) -> list[int, int, int, int]:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            reference = self.fbo if overlay else self.fb
            o = y * self.width * 4 + x * 4
            return reference[o + 0], reference[o + 1], reference[o + 2], reference[o + 3]
        return None

    def update(self):
        pass
