#include <cerrno>
#include <cstring>
#include <netdb.h>
#include <string>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/types.h>

#include "error.h"


int start_tcp_listen(const std::string & bind_to, const int listen_port)
{
	int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
	if (listen_fd == -1)
		error_exit(true, "start_tcp_listen: cannot create socket");

        int reuse_addr = 1;
        if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, (char *)&reuse_addr, sizeof(reuse_addr)) == -1)
                error_exit(true, "start_tcp_listen: setsockopt(SO_REUSEADDR) failed");

	int q_size = SOMAXCONN;
	if (setsockopt(listen_fd, SOL_TCP, TCP_FASTOPEN, &q_size, sizeof q_size))
		error_exit(true, "start_tcp_listen: failed to enable TCP FastOpen");

        struct sockaddr_in server_addr { };
        server_addr.sin_family = AF_INET;
        server_addr.sin_port   = htons(listen_port);
	int rc = inet_pton(AF_INET, bind_to.c_str(), &server_addr.sin_addr);
	if (rc == 0)
		error_exit(false, "start_tcp_listen: \"%s\" is not a valid IP-address", bind_to.c_str());
	if (rc == -1)
		error_exit(true, "start_tcp_listen: problem interpreting \"%s\"", bind_to.c_str());

        if (bind(listen_fd, (struct sockaddr *)&server_addr, sizeof server_addr) == -1)
                error_exit(true, "start_tcp_listen: failed to bind to port %d", listen_port);

        if (listen(listen_fd, q_size) == -1)
                error_exit(true, "start_tcp_listen: listen failed");

	return listen_fd;
}

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

std::string get_endpoint_name(int fd)
{
	char host[256] { "? " };
	char serv[256] { "? " };
	struct sockaddr_in6 addr { 0 };
	socklen_t addr_len = sizeof addr;

	if (getpeername(fd, (struct sockaddr *)&addr, &addr_len) == -1)
		snprintf(host, sizeof host, "[FAILED TO FIND NAME OF %d: %s (1)]", fd, strerror(errno));
	else
		getnameinfo((struct sockaddr *)&addr, addr_len, host, sizeof(host), serv, sizeof(serv), NI_NUMERICHOST | NI_NUMERICSERV);

	return std::string(host) + "." + std::string(serv);
}


std::pair<int, std::string> get_broadcast_fd(const int port)
{
        sockaddr_in addr {};
        addr.sin_family      = AF_INET;
        addr.sin_port        = htons(port);
        addr.sin_addr.s_addr = inet_addr("255.255.255.255");

	int fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd == -1)
		error_exit(true, "get_broadcast_fd: cannot create socket");

	int yes = 1;
	if (setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &yes, sizeof(yes)) == -1)
		error_exit(true, "get_broadcast_fd: cannot set socket to broadcast");

        if (connect(fd, reinterpret_cast<sockaddr *>(&addr), sizeof addr) == -1)
		error_exit(true, "get_broadcast_fd: cannot connect socket to broadcast address");

	sockaddr_in local { };
	socklen_t   local_len = sizeof local;
	if (getsockname(fd, reinterpret_cast<sockaddr *>(&local), &local_len) == -1)
		error_exit(true, "get_broadcast_fd: getsockname");

	char host[256] { "?" };
	char serv[256] { "?" };
	getnameinfo((struct sockaddr *)&local, local_len, host, sizeof host, serv, sizeof serv, NI_NUMERICHOST | NI_NUMERICSERV);

	return { fd, std::string(host) + ":" + std::string(serv) };
}
