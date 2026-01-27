#include <cstdint>
#include <functional>
#include <vector>


void handle_ddp_client_datagram(const int udp_bin_fd, const int width, int const height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> queue_pixels, std::function<void()> put_pixels);

void transmit_ddp_broadcast(const int port);
