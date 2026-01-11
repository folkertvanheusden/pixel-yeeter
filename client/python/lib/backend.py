class backend:
    def __init__(self, width: int, height: int):
        self._init(width, height)

    def _init(self, width: int, height: int):
        self.width = width
        self.height = height
        self.clear_screen()

    def clear_screen(self) -> None:
        self.fb = [ 0 ] * self.width * self.height * 3

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            if r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255:
                o = y * self.width * 3 + x * 3
                self.fb[o + 0] = r
                self.fb[o + 1] = g
                self.fb[o + 2] = b

    def set_pixels_horizontal(self, x: int, y: int, values: list[list[int]]) -> None:
        offset_y = self.width * y * 3
        for x_work in range(max(0, x), min(self.width, x + len(values))):
            offset_work = offset_y + x_work * 3
            pixel = values[x_work - x]
            self.fb[offset_work + 0] = pixel[0]
            self.fb[offset_work + 1] = pixel[1]
            self.fb[offset_work + 2] = pixel[2]

    def get_pixel(self, x: int, y: int) -> list[int, int, int]:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 3 + x * 3
            return self.fb[o + 0], self.fb[o + 1], self.fb[o + 2]
        return None

    def update(self):
        pass
