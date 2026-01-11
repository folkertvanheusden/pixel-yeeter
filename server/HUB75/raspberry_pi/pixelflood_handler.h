#include <cstdint>
#include <functional>
#include <led-matrix.h>
#include <vector>

void handle_pixelflood_client_stream_text(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels);
void handle_pixelflood_client_datagram_text(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels);
void handle_pixelflood_client_datagram_binary(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels);
