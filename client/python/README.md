pixel-yeeter python library
---------------------------

With this software you can draw on DDP and PixelFlood displays such as the ones included in this repository.

See 'examples' for some examples how this works. Note that you may need to adjust the IP-addresses in the examples to match the configuration of your own setup.


installation
------------

pip install -U .


quick how-to
------------

```python
import pixel_yeeter

canvas = pixel_yeeter.frontend.frontend(pixel_yeeter.backend_ddp.backend_ddp('192.168.65.140', 4048, (64, 32)))
```

This creates a canvas to draw on for the DDP-server at IP-address `192.168.65.140` (which is an example). The port is usually 4048 as shown above. `(64, 32)` is the resolution of the DDP display-setup. Indeed for DDP you need to explicitly set this here as it has no way of telling clients what its resolution is.

Retrieve the resolution first: required pixelflood displays:
```python
width, height = canvas.get_resolution()
```

The library has 3 layers: `back`, `screen` and `front`. Usually you draw on `screen` and use `front` for e.g. scroll texts.

Here you draw a gradient on the `back`. When invoking `clear_screen()`, this won't then clear this gradient - use clear_back() for that.

```python
for y in range(height):
    canvas.draw_line_rgb(0, y, width, y, 0, 0, int(y * 255 / height), layer=pixel_yeeter.backend.layer_types.back)
```

When not specifying the layer, things will be drawn on `screen` (the middle layer). Also you can specify colors by RGB value (0...255) or by name.

```python
canvas.draw_line_rgb(0, 0, width, height, 0, 255, 0)
canvas.draw_line_color_by_name(width, 0, 0, height, 'red')
```

Send all (!) layers combined to the DDP or PixelFlood display server.

```python
canvas.send_to_screen()
```
