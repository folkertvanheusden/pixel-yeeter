#include <cctype>
#include <cstdint>
#include <cstring>
#include <errno.h>
#include <functional>
#include <optional>
#include <unistd.h>
#include <vector>
#include <netinet/in.h>
#include <sys/socket.h>

#include <led-matrix.h>


bool WRITE(const int fd, const char *p, size_t n)
{
	while(n > 0) {
		int rc = write(fd, p, n);
		if (rc <= 0)
			return false;
		p += rc;
		n -= rc;
	}
	return true;
}

int hextonibble(const char c)
{
	char cu = toupper(c);
	if (cu >= 'A')
		return cu - 'A' + 10;
	return cu - '0';
}

std::optional<std::string> handle_pixelflood_payload_text(char *const buffer, size_t *const n, size_t *const offset, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels)
{
	std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > pixels;

	while(*offset < *n) {
		char *lf = reinterpret_cast<char *>(memchr(&buffer[*offset], '\n', *n - *offset));
		if (lf == nullptr)
			break;

		*lf = 0x00;
		if (*offset + 5 <= *n && memcmp(&buffer[*offset], "SIZE", 4) == 0) {
			*offset = lf + 1 - buffer;
			return "SIZE " + std::to_string(width) + " " + std::to_string(height) + "\n";
		}
		// PX x y rrggbb\n => 14
		else if (*offset + 14 <= *n && buffer[*offset + 0] == 'P' && buffer[*offset + 1] == 'X' && buffer[*offset + 2] == ' ') {
			char *p_space1 = nullptr;
			int   x        = int(strtol(&buffer[*offset + 2], &p_space1, 10));
			if (*p_space1 != ' ')
				return { };
			char *p_space2 = nullptr;
			int   y        = int(strtol(p_space1 + 1, &p_space2, 10));
			if (*p_space2 != ' ')
				return { };
			p_space2++;
			int   r        = (hextonibble(p_space2[0]) << 4) + hextonibble(p_space2[1]);
			int   g        = (hextonibble(p_space2[2]) << 4) + hextonibble(p_space2[3]);
			int   b        = (hextonibble(p_space2[4]) << 4) + hextonibble(p_space2[5]);

			if (x < 0 || x >= width || y < 0 || y > height || r > 255 || g > 255 || b > 255) {
				fprintf(stderr, "Pixel invalid (%d,%d %d,%d,%d | %d,%d)?\n", x, y, r, g, b, width, height);
				return { };
			}

			pixels.push_back({ x, y, r, g, b });
		}
		else {
			fprintf(stderr, "Garbage? (%s)\n", std::string(&buffer[*offset], *n - *offset).c_str());
			return { };
		}

		*offset = lf + 1 - buffer;
	}

	if (*offset < *n) {
		memmove(&buffer[0], &buffer[*offset], *n - *offset);
		*n -= *offset;
		*offset = 0;
	}
	else {
		*n = 0;
		*offset = 0;
	}

	draw_pixels(pixels);
	put_pixels();

	return { };
}

void handle_pixelflood_client_stream_text(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels)
{
	char   buffer[65536];
	size_t n      = 0;
	size_t offset = 0;

	for(;;) {
		int rc = read(fd, &buffer[n], sizeof(buffer) - n);
		if (rc == -1 || rc == 0) {
			fprintf(stderr, "Read error: %s\n", strerror(errno));
			break;
		}

		n += rc;

		auto reply = handle_pixelflood_payload_text(buffer, &n, &offset, width, height, draw_pixels, put_pixels);
		if (reply.has_value())
			WRITE(fd, reply.value().c_str(), reply.value().size());
	}
}

void handle_pixelflood_client_datagram_text(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels)
{
	char buffer[65536];

	for(;;) {
		sockaddr_in6 addr { };
		socklen_t    addr_len = sizeof addr;
		int rc = recvfrom(fd, buffer, sizeof buffer, 0, reinterpret_cast<sockaddr *>(&addr), &addr_len);
		if (rc == -1)
			break;
		if (rc == 0)
			continue;

		size_t n      = rc;
		size_t offset = 0;

		auto reply = handle_pixelflood_payload_text(buffer, &n, &offset, width, height, draw_pixels, put_pixels);
		if (reply.has_value())
			sendto(fd, reply.value().c_str(), reply.value().size(), 0, reinterpret_cast<sockaddr *>(&addr), addr_len);
	}
}

// https://github.com/JanKlopper/pixelvloed/blob/master/protocol.md
void handle_pixelflood_payload_binary(uint8_t *const buffer, const size_t n, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels)
{
	if (buffer[0]) {
		fprintf(stderr, "Protocol version %d not supported yet\n", buffer[0]);
		return;
	}

	bool alpha = buffer[1] & 1;
	int  inc   = alpha ? 8 : 7;

	std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > pixels;

	for(size_t i=2; i<n; i += inc) {
		int     x = (buffer[i + 1] << 8) | buffer[i + 0];
		int     y = (buffer[i + 3] << 8) | buffer[i + 2];
		uint8_t r = buffer[i + 4];
		uint8_t g = buffer[i + 5];
		uint8_t b = buffer[i + 6];
		if (x < 0 || x >= width || y < 0 || y >= height)
			return;
		pixels.push_back({ x, y, r, g, b });
	}

	draw_pixels(pixels);
	put_pixels();
}

void handle_pixelflood_client_datagram_binary(const int fd, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels, std::function<void()> put_pixels)
{
	uint8_t buffer[1122 + 9];  // as per protocol, +9 so not to require bound checks

	for(;;) {
		sockaddr_in6 addr { };
		socklen_t    addr_len = sizeof addr;
		int rc = recvfrom(fd, buffer, sizeof buffer, 0, reinterpret_cast<sockaddr *>(&addr), &addr_len);
		if (rc == -1)
			break;
		if (rc == 0)
			continue;

		handle_pixelflood_payload_binary(buffer, rc, width, height, draw_pixels, put_pixels);
	}
}
