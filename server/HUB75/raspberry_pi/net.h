#include <string>


int start_tcp_listen(const std::string & bind_to, const int listen_port);
int start_udp_listen(const std::string & bind_to, const int listen_port);

std::string                 get_endpoint_name(      int fd  );
std::pair<int, std::string> get_broadcast_fd (const int port);
