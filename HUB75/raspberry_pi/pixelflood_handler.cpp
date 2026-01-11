#include <cctype>
#include <cstdint>
#include <cstring>
#include <functional>
#include <unistd.h>
#include <vector>

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

void handle_pixelflood_client(const int fd, const bool is_datagram, const int width, const int height, std::function<void(const std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > &)> draw_pixels)
{
	if (is_datagram) {
		// TODO
		return;
	}

	char   buffer[65536];
	size_t n = 0;
	size_t o = 0;

	std::vector<std::tuple<int, int, uint8_t, uint8_t, uint8_t> > pixels;

	for(;;) {
		int rc = read(fd, &buffer[n], sizeof(buffer) - n);
		if (rc == -1 || rc == 0)
			break;

		n += rc;

		while(o < n) {
			char *lf = reinterpret_cast<char *>(memchr(&buffer[o], '\n', n - o));
			if (lf == nullptr)
				break;

			*lf = 0x00;
			if (o + 5 <= n && memcmp(&buffer[o], "SIZE", 4) == 0) {
				std::string reply = "SIZE " + std::to_string(width) + " " + std::to_string(height) + "\n";
				if (WRITE(fd, reply.c_str(), reply.size()) == false)
					break;
			}
			// PX x y rrggbb\n => 14
			else if (o + 14 <= n && buffer[o + 0] == 'P' && buffer[o + 1] == 'X' && buffer[o + 2] == ' ') {
				char *p_space1 = nullptr;
				int   x        = int(strtol(&buffer[o + 2], &p_space1, 10));
				if (*p_space1 != ' ')
					return;
				char *p_space2 = nullptr;
				int   y        = int(strtol(p_space1 + 1, &p_space2, 10));
				if (*p_space2 != ' ')
					return;
				p_space2++;
				int   r        = (hextonibble(p_space2[0]) << 4) + hextonibble(p_space2[1]);
				int   g        = (hextonibble(p_space2[2]) << 4) + hextonibble(p_space2[3]);
				int   b        = (hextonibble(p_space2[4]) << 4) + hextonibble(p_space2[5]);

				if (x < 0 || x >= width || y < 0 || y > height || r > 255 || g > 255 || b > 255)
					return;

				pixels.push_back({ x, y, r, g, b });
			}
			else {
				return;
			}

			o = lf + 1 - buffer;
		}

		if (o < n) {
			memmove(&buffer[0], &buffer[o], n - o);
			n = o;
			o = 0;
		}

		draw_pixels(pixels);
		pixels.clear();
	}
}
