#include <cstdint>
#include <functional>
#include <vector>

void handle_pixelflood_client_stream_text(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels);
void handle_pixelflood_client_datagram_text(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels);
void handle_pixelflood_client_datagram_binary(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels);

void transmit_pixelflood_broadcast(const int port, const int width, const int height);
