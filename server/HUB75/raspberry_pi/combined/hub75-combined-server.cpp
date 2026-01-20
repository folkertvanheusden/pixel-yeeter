#include <cstdint>
#include <cstdio>
#include <led-matrix.h>
#include <mutex>
#include <thread>
#include <unistd.h>
#include <sys/socket.h>

#include "error.h"
#include "ddp_handler.h"
#include "net.h"
#include "pixelflood_handler.h"

std::mutex               canvas_lock;
rgb_matrix::RGBMatrix   *canvas       = nullptr;
rgb_matrix::FrameCanvas *draw_canvas  = nullptr;
uint8_t                 *frame_buffer = nullptr;

void draw_pixels(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > & pixels)
{
	for(auto & pixel: pixels) {
		const auto [x, y, r, g, b] = pixel;
		int offset = y * draw_canvas->width() * 3 + x * 3;
		frame_buffer[offset + 0] = r;
		frame_buffer[offset + 1] = g;
		frame_buffer[offset + 2] = b;
	}
}

void put_pixels()
{
	size_t byte_count = draw_canvas->width() * draw_canvas->height() * 3;
	std::unique_lock<std::mutex> lck(canvas_lock);
	SetImage(draw_canvas, 0, 0,
              frame_buffer, byte_count,
              draw_canvas->width(), draw_canvas->height(),
              false);
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

	frame_buffer = new uint8_t[draw_canvas->width() * draw_canvas->height() * 3]();

	// pixelflood
	int pixelflood_udp_txt_fd = start_udp_listen("0.0.0.0", 1337);
	std::thread t_txt([&] {
			handle_pixelflood_client_datagram_text(pixelflood_udp_txt_fd, draw_canvas->width(), draw_canvas->height(), draw_pixels);
	});
	t_txt.detach();

	int pixelflood_udp_bin_fd = start_udp_listen("0.0.0.0", 1338);
	std::thread t_bin([&] {
			handle_pixelflood_client_datagram_binary(pixelflood_udp_bin_fd, draw_canvas->width(), draw_canvas->height(), draw_pixels);
	});
	t_bin.detach();

	int pixelflood_tcp_txt_fd = start_tcp_listen("0.0.0.0", 1337);
	std::thread t_txt_tcp([&] {
		for(;;) {
			int cfd = accept(pixelflood_tcp_txt_fd, nullptr, nullptr);
			if (cfd == -1)
				error_exit(true, "accept failed");

			std::thread t([&] {
					handle_pixelflood_client_stream_text(cfd, draw_canvas->width(), draw_canvas->height(), draw_pixels);
					close(cfd);
			});
			t.detach();
		}
	});
	t_txt_tcp.detach();
	close(pixelflood_tcp_txt_fd);

	close(pixelflood_udp_bin_fd);
	close(pixelflood_udp_txt_fd);

	// DDP
	std::thread t_ddp_tcp([&] {
		int ddp_udp_bin_fd = start_udp_listen("0.0.0.0", 4048);
		handle_ddp_client_datagram(ddp_udp_bin_fd, draw_canvas->width(), draw_canvas->height(), draw_pixels, put_pixels);
		close(ddp_udp_bin_fd);
	});
	t_ddp_tcp.detach();

	std::thread t_ddp_broadcast([&] {
		for(;;) {
			transmit_ddp_broadcast(4048);
			sleep(5);
		}
	});

	for(;;)
		sleep(3600);

	delete [] frame_buffer;

	return 0;
}
