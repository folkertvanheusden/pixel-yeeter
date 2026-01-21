# (C) 2026 by folkert van heusden <mail@vanheusden.com>, released under Apache License v2.0
cmake_minimum_required(VERSION 3.9.4)

project(hub75-combined-server VERSION 1.0)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_definitions("-D_FILE_OFFSET_BITS=64")

set(CMAKE_BUILD_TYPE RelWithDebInfo)

if (ASAN EQUAL 1)
        SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address,undefined")
        MESSAGE("WITH ASAN (and USAN)")
else()
	MESSAGE("without ASAN/USAN")
endif()

if (MSAN EQUAL 1)
        SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=memory")
        MESSAGE("WITH MSAN")
else()
        MESSAGE("without MSAN")
endif()

if (TSAN EQUAL 1)
        SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread")
        MESSAGE("WITH TSAN")
else()
        MESSAGE("without TSAN")
endif()

add_compile_options(-Wall -pedantic)

include_directories(rpi-rgb-led-matrix/include)
link_directories(rpi-rgb-led-matrix/lib)

add_executable(hub75-combined-server
	ddp_handler.cpp
	error.cpp
	hub75-combined-server.cpp
	net.cpp
	pixelflood_handler.cpp
	)

set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
set(THREADS_PREFER_PTHREAD_FLAG TRUE)
find_package(Threads)

if (ASAN EQUAL 1)
        target_link_libraries(hub75-combined-server PRIVATE -fsanitize=address,undefined Threads::Threads rgbmatrix)
elseif (TSAN EQUAL 1)
        target_link_libraries(hub75-combined-server PRIVATE -fsanitize=thread Threads::Threads rgbmatrix)
elseif (MSAN EQUAL 1)
        target_link_libraries(hub75-combined-server PRIVATE -fsanitize=memory Threads::Threads rgbmatrix)
else()
        target_link_libraries(hub75-combined-server PRIVATE Threads::Threads rgbmatrix)
endif()
