#include <cstdint>
#include <cstdio>
#include <led-matrix.h>
#include <mutex>
#include <unistd.h>
#include <sys/socket.h>

#include "error.h"
#include "net.h"
#include "pixelflood_handler.h"

std::mutex               canvas_lock;
rgb_matrix::RGBMatrix   *canvas      = nullptr;
rgb_matrix::FrameCanvas *draw_canvas = nullptr;

void draw_pixels(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > & pixels)
{
	std::unique_lock<std::mutex> lck(canvas_lock);

	for(auto & pixel: pixels) {
		const auto [x, y, r, g, b] = pixel;
                draw_canvas->SetPixel(x, y, r, g, b);
	}
	draw_canvas = canvas->SwapOnVSync(draw_canvas);
}

void usage()
{
	fprintf(stderr, "Options:\n");
	rgb_matrix::PrintMatrixFlags(stderr);
}

int main(int argc, char *argv[])
{
	rgb_matrix::RGBMatrix::Options matrix_options;
	rgb_matrix::RuntimeOptions     runtime_opt;
	if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv, &matrix_options, &runtime_opt)) {
		usage();
		return 1;
	}

	canvas = rgb_matrix::CreateMatrixFromOptions(matrix_options, runtime_opt);
        if (canvas == nullptr)
                error_exit(false, "Failed to initialize RGB matrix");
        canvas->SetBrightness(30);
	draw_canvas = canvas->CreateFrameCanvas();

	int fd = start_tcp_listen("0.0.0.0", 1337);

	for(;;) {
		int cfd = accept(fd, nullptr, nullptr);
		if (cfd == -1)
			error_exit(true, "accept failed");

		// TODO threads or so
		handle_pixelflood_client(cfd, false, draw_canvas->width(), draw_canvas->height(), draw_pixels);
		close(cfd);
	}

	close(fd);

	return 0;
}
