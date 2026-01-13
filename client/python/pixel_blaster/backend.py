class backend:
    def __init__(self, width: int, height: int):
        self._init(width, height)

    def _init(self, width: int, height: int):
        self.width = width
        self.height = height
        self.clear_screen()

    def clear_screen(self) -> None:
        self.fb = [ 0 ] * self.width * self.height * 4

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            self.fb[o + 0] = r & 255
            self.fb[o + 1] = g & 255
            self.fb[o + 2] = b & 255
            self.fb[o + 3] = 255

    def set_pixel_alpha(self, x: int, y: int, r: int, g: int, b: int, a: int) -> None:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            self.fb[o + 0] = r & 255
            self.fb[o + 1] = g & 255
            self.fb[o + 2] = b & 255
            self.fb[o + 3] = a & 255

    def set_pixels_horizontal(self, x: int, y: int, values: list[list[int]]) -> None:
        if len(values) == 0 or y >= self.height or y < 0:
            return
        offset_y = self.width * y * 4
        if len(values[0]) == 4:
            for x_work in range(max(0, x), min(self.width, x + len(values))):
                offset_work = offset_y + x_work * 4
                pixel = values[x_work - x]
                self.fb[offset_work + 0] = pixel[0]
                self.fb[offset_work + 1] = pixel[1]
                self.fb[offset_work + 2] = pixel[2]
                self.fb[offset_work + 3] = pixel[3]
        else:
            for x_work in range(max(0, x), min(self.width, x + len(values))):
                offset_work = offset_y + x_work * 4
                pixel = values[x_work - x]
                self.fb[offset_work + 0] = pixel[0]
                self.fb[offset_work + 1] = pixel[1]
                self.fb[offset_work + 2] = pixel[2]
                self.fb[offset_work + 3] = 255

    def get_pixel(self, x: int, y: int) -> list[int, int, int]:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            return self.fb[o + 0], self.fb[o + 1], self.fb[o + 2] 
        return None

    def get_pixel_alpha(self, x: int, y: int) -> list[int, int, int, int]:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            return self.fb[o + 0], self.fb[o + 1], self.fb[o + 2], self.fb[o + 3]
        return None

    def update(self):
        pass
