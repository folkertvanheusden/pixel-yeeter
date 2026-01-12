#include <cstdint>
#include <cstring>
#include <functional>
#include <string>
#include <vector>
#include <netinet/in.h>
#include <sys/socket.h>


bool handle_ddp_payload_binary(const uint8_t *const buffer, const size_t n, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> queue_pixels)
{
	if (n < 10)  // invalid packet
		return false;
	if ((buffer[0] >> 6) != 1)  // unexpected version
		return false;

	bool has_timecode = buffer[0] & 16;

	if (((buffer[2] >> 3) & 7) != 1)  // only RGB
		return false;
	if ((buffer[2] & 7) != 3)  // only 8 bits per pixel
		return false;

	if (buffer[3] != 1 && buffer[3] != 255)  // output
		return false;

	uint32_t offset = (buffer[4] << 24) | (buffer[5] << 16) | (buffer[6] << 8) | buffer[7];
	// uint16_t length = (buffer[8] << 8) | buffer[9];

	std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > pixels;

	int packet_start_index = has_timecode ? 14 : 10;
	for(size_t i=packet_start_index; i<n; i += 3) {
		unsigned offset_offseted = offset + i - packet_start_index;
		int x = (offset_offseted / 3) % width;
		int y = offset_offseted / (width * 3);
		pixels.push_back({ x, y, buffer[i + 0], buffer[i + 1], buffer[i + 2] });
	}

	queue_pixels(pixels);

	return buffer[0] & 1;  // VSYNC
}

void handle_ddp_status_request(const int fd, const sockaddr_in6 & addr, const socklen_t len)
{
	std::string msg = "{\"status\" { \"man\": \"www.vanheusden.com\", \"mod\": \"hub75 ddp server\", \"ver\": \"0.1\", \"push\": true, \"ntp\": false } }";
	size_t total_len = 10 + msg.size();
	uint8_t *buffer = new uint8_t[total_len]();

	buffer[0] = 64 | 4 | 1;  // version_1, reply, push
	buffer[3] = 251;  // json status
	buffer[8] = msg.size() >> 8;
	buffer[9] = msg.size();
	memcpy(&buffer[10], msg.c_str(), msg.size());

	sendto(fd, buffer, total_len, 0, reinterpret_cast<const sockaddr *>(&addr), len);

	delete [] buffer;
}

void handle_ddp_client_datagram(const int fd, const int width, int const height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> queue_pixels, std::function<void()> put_pixels)
{
	uint8_t buffer[65536];

	for(;;) {
		sockaddr_in6 addr { };
		socklen_t    addr_len = sizeof addr;
		int rc = recvfrom(fd, buffer, sizeof buffer, 0, reinterpret_cast<sockaddr *>(&addr), &addr_len);
		if (rc == -1)
			break;
		if (rc == 0)
			continue;

		if (buffer[3] == 251 && (buffer[0] & 2))  // json status (251) request (bit 1)
			handle_ddp_status_request(fd, addr, addr_len);
		else {
			if (handle_ddp_payload_binary(buffer, rc, width, height, queue_pixels))
				put_pixels();
		}
	}
}
