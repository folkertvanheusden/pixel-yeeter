#include <cerrno>
#include <cstring>
#include <netdb.h>
#include <string>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>

#include "error.h"


int start_udp_listen(const std::string & bind_to, const int listen_port)
{
	int listen_fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (listen_fd == -1)
		error_exit(true, "start_udp_listen: cannot create socket");

        int reuse_addr = 1;
        if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, (char *)&reuse_addr, sizeof(reuse_addr)) == -1)
                error_exit(true, "start_udp_listen: setsockopt(SO_REUSEADDR) failed");

        struct sockaddr_in server_addr { };
        server_addr.sin_family = AF_INET;
        server_addr.sin_port   = htons(listen_port);
	int rc = inet_pton(AF_INET, bind_to.c_str(), &server_addr.sin_addr);
	if (rc == 0)
		error_exit(false, "start_udp_listen: \"%s\" is not a valid IP-address", bind_to.c_str());
	if (rc == -1)
		error_exit(true, "start_udp_listen: problem interpreting \"%s\"", bind_to.c_str());

        if (bind(listen_fd, (struct sockaddr *)&server_addr, sizeof server_addr) == -1)
                error_exit(true, "start_udp_listen: failed to bind to port %d", listen_port);

	return listen_fd;
}
