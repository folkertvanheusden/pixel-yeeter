from enum import IntEnum


class layer_types(IntEnum):
    back = 0,
    middle = 1,
    front = 2 

class backend:
    def __init__(self, width: int, height: int):
        self._init(width, height)

    def _init(self, width: int, height: int):
        self.width = width
        self.height = height
        self.layers: layer_types | None = [ None ] * 3
        self.clear_back()
        self.clear_screen()
        self.clear_front()

    def clear_back(self) -> None:
        self.layers[layer_types.back] = [ 0 ] * self.width * self.height * 4

    def clear_screen(self) -> None:
        self.layers[layer_types.middle] = [ 0 ] * self.width * self.height * 4

    def clear_front(self) -> None:
        self.layers[layer_types.front] = [ 0 ] * self.width * self.height * 4

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def get_mixed_pixel(self, x: int, y: int) -> list[int, int, int]:
        rb, gb, bb, ab = self.get_pixel_alpha(x, y, layer = layer_types.back)
        rm, gm, bm, am = self.get_pixel_alpha(x, y, layer = layer_types.middle)
        rf, gf, bf, af = self.get_pixel_alpha(x, y, layer = layer_types.front)
        rt = (rb * (255 - am) + rm * am) / 255
        gt = (gb * (255 - am) + gm * am) / 255
        bt = (bb * (255 - am) + bm * am) / 255
        r = int((rt * (255 - af) + rf * af) / 255)
        g = int((gt * (255 - af) + gf * af) / 255)
        b = int((bt * (255 - af) + bf * af) / 255)
        return r, g, b

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int, layer: layer_types = layer_types.middle) -> None:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            reference = self.layers[layer]
            reference[o + 0] = r & 255
            reference[o + 1] = g & 255
            reference[o + 2] = b & 255
            reference[o + 3] = 255

    def set_pixel_alpha(self, x: int, y: int, r: int, g: int, b: int, a: int, layer: layer_types = layer_types.middle) -> None:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            o = y * self.width * 4 + x * 4
            reference = self.layers[layer]
            reference[o + 0] = r & 255
            reference[o + 1] = g & 255
            reference[o + 2] = b & 255
            reference[o + 3] = a & 255

    def set_pixels_horizontal(self, x: int, y: int, values: list[int], layer: layer_types = layer_types.middle) -> None:
        if len(values) == 0 or y >= self.height or y < 0:
            return
        target_offset = self.width * y * 4
        if x < 0:
            use = values[-x * 4:min(len(values), self.width * 4 - x * 4)]
        else:
            use = values[x * 4:min(len(values), self.width * 4 + x * 4)]
        self.layers[layer][target_offset + 0:target_offset + len(use)] = use[:]

    def get_pixel(self, x: int, y: int, layer: layer_types = layer_types.middle) -> list[int, int, int]:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            reference = self.layers[layer]
            o = y * self.width * 4 + x * 4
            return reference[o + 0], reference[o + 1], reference[o + 2] 
        return None

    def get_pixel_alpha(self, x: int, y: int, layer: layer_types = layer_types.middle) -> list[int, int, int, int]:
        if x < self.width and y < self.height and x >= 0 and y >= 0:
            reference = self.layers[layer]
            o = y * self.width * 4 + x * 4
            return reference[o + 0], reference[o + 1], reference[o + 2], reference[o + 3]
        return None

    def update(self):
        pass
