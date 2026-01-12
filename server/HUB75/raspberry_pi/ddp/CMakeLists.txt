# (C) 2026 by folkert van heusden <mail@vanheusden.com>, released under Apache License v2.0
cmake_minimum_required(VERSION 3.9.4)

project(hub75-ddp-server VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_definitions("-D_FILE_OFFSET_BITS=64")

set(CMAKE_BUILD_TYPE RelWithDebInfo)

add_compile_options(-Wall -pedantic)

include_directories(rpi-rgb-led-matrix/include)
link_directories(rpi-rgb-led-matrix/lib)

add_executable(hub75-ddp-server
	error.cpp
	hub75-ddp-server.cpp
	net.cpp
	ddp_handler.cpp
	)

target_link_libraries(hub75-ddp-server rgbmatrix)

set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
set(THREADS_PREFER_PTHREAD_FLAG TRUE)
find_package(Threads)
target_link_libraries(hub75-ddp-server Threads::Threads)
