#include <cstdint>
#include <cstdio>
#include <mutex>
#include <optional>
#include <thread>
#include <unistd.h>
#include <sys/socket.h>
#include <SDL3/SDL.h>

#include "error.h"
#include "ddp_handler.h"
#include "net.h"
#include "pixelflood_handler.h"


std::mutex       sdl_lock;
int              win_width    = 0;
int              win_height   = 0;
uint8_t         *frame_buffer = nullptr;
std::atomic_bool has_pixels { false };

void draw_pixels(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > & pixels)
{
	for(auto & pixel: pixels) {
		const auto [x, y, r, g, b] = pixel;
		int offset = y * win_width * 4 + x * 4;
		frame_buffer[offset + 0] = r;
		frame_buffer[offset + 1] = g;
		frame_buffer[offset + 2] = b;
	}
}

void put_pixels()
{
	has_pixels = true;
}

void usage()
{
	printf("-W x  width\n");
	printf("-H x  height\n");
	printf("-h    this help\n");
}

int main(int argc, char *argv[])
{
	std::optional<int> set_width;
	std::optional<int> set_height;
	int c = 0;
	while((c = getopt(argc, argv, "W:H:h")) != -1) {
		if (c == 'W')
			set_width = atoi(optarg);
		else if (c == 'H')
			set_height = atoi(optarg);
		else {
			usage();
			exit(0);
		}
	}

	if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) == false)
		error_exit(false, "Cannot initialize SDL");

	if (set_width.has_value() != set_height.has_value())
		error_exit(false, "Need to set either both dimensions or none");

	SDL_SetHint(SDL_HINT_RENDER_VSYNC, "1");
	SDL_Window *win = nullptr;
	if (set_width.has_value()) {
		win = SDL_CreateWindow("server", set_width.value(), set_height.value(), 0);
		SDL_MaximizeWindow(win);
		SDL_SyncWindow(win);
	}
	else {
		win = SDL_CreateWindow("server", 320, 240, SDL_WINDOW_RESIZABLE);
		SDL_MaximizeWindow(win);
		SDL_SyncWindow(win);
	}
	SDL_GetWindowSize(win, &win_width, &win_height);
	printf("Window size: %dx%d, driver: %s\n", win_width, win_height, SDL_GetCurrentVideoDriver());
	SDL_Renderer *screen = SDL_CreateRenderer(win, nullptr);

	size_t n_bytes = win_width * win_height * 4;
	frame_buffer = new uint8_t[n_bytes]();
	memset(frame_buffer, 255, n_bytes);

	// pixelflood
	int pixelflood_udp_txt_fd = start_udp_listen("0.0.0.0", 1337);
	std::thread t_txt([&] {
			handle_pixelflood_client_datagram_text(pixelflood_udp_txt_fd, win_width, win_height, draw_pixels, put_pixels);
	});
	t_txt.detach();

	int pixelflood_udp_bin_fd = start_udp_listen("0.0.0.0", 1338);
	std::thread t_bin([&] {
			handle_pixelflood_client_datagram_binary(pixelflood_udp_bin_fd, win_width, win_height, draw_pixels, put_pixels);
	});
	t_bin.detach();

	int pixelflood_tcp_txt_fd = start_tcp_listen("0.0.0.0", 1337);
	std::thread t_txt_tcp([&] {
		for(;;) {
			int cfd = accept(pixelflood_tcp_txt_fd, nullptr, nullptr);
			if (cfd == -1)
				error_exit(true, "accept failed");

			std::thread t([&] {
					handle_pixelflood_client_stream_text(cfd, win_width, win_height, draw_pixels, put_pixels);
					close(cfd);
			});
			t.detach();
		}
	});
	t_txt_tcp.detach();

	// DDP
	std::thread t_ddp_tcp([&] {
		int ddp_udp_bin_fd = start_udp_listen("0.0.0.0", 4048);
		handle_ddp_client_datagram(ddp_udp_bin_fd, win_width, win_height, draw_pixels, put_pixels);
		close(ddp_udp_bin_fd);
	});
	t_ddp_tcp.detach();

	std::thread t_ddp_broadcast([&] {
		for(;;) {
			transmit_ddp_broadcast(4048);
			sleep(5);
		}
	});
	t_ddp_broadcast.detach();

	std::thread t_pixelflood_broadcast([&] {
		for(;;) {
			transmit_pixelflood_broadcast(1337, win_width, win_height);
			sleep(5);
		}
	});
	t_pixelflood_broadcast.detach();

	SDL_Texture *texture = SDL_CreateTexture(screen, SDL_PIXELFORMAT_RGBA32, SDL_TEXTUREACCESS_STREAMING, win_width, win_height);
	SDL_SetTextureBlendMode(texture, SDL_BLENDMODE_NONE);

	for(;;) {
		SDL_Event event { };

		if (has_pixels.exchange(false)) {
			void *pixels = nullptr;
			int   pitch  = 0;
			if (SDL_LockTexture(texture, NULL, &pixels, &pitch) == false)
				printf("SDL_LockTexture failed\n");
			memcpy(pixels, frame_buffer, win_height * pitch);
			SDL_UnlockTexture(texture);
			SDL_RenderTexture(screen, texture, nullptr, nullptr);
			if (SDL_RenderPresent(screen) == false)
				printf("SDL_RenderPresent failed\n");

			while(SDL_PollEvent(&event)) {
				printf("%d\n", event.type);
				if (event.type == SDL_EVENT_QUIT)
					exit(1);
			}
		}
		else {
			while(SDL_WaitEventTimeout(&event, 1)) {
				if (event.type == SDL_EVENT_QUIT)
					exit(1);
			}
		}
	}

	SDL_DestroyTexture(texture);

	close(pixelflood_tcp_txt_fd);
	close(pixelflood_udp_bin_fd);
	close(pixelflood_udp_txt_fd);

	delete [] frame_buffer;

	return 0;
}
