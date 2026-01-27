# (C) 2026 by folkert van heusden <mail@vanheusden.com>, released under Apache License v2.0
cmake_minimum_required(VERSION 3.9.4)

project(server VERSION 1.0)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_definitions("-D_FILE_OFFSET_BITS=64")

set(CMAKE_BUILD_TYPE RelWithDebInfo)

if (CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
        MESSAGE("WITH LTO")
        cmake_policy(SET CMP0069 NEW)
        set(CMAKE_POLICY_DEFAULT_CMP0069 NEW)
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
else()
        MESSAGE("without LTO")
endif()

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

add_executable(server
	ddp_handler.cpp
	error.cpp
	server.cpp
	net.cpp
	pixelflood_handler.cpp
	)
target_compile_options(server PRIVATE -march=native -mtune=native -O3)

set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
set(THREADS_PREFER_PTHREAD_FLAG TRUE)
find_package(Threads)

find_package(SDL3 REQUIRED CONFIG REQUIRED COMPONENTS SDL3-shared)
target_link_libraries(server PRIVATE SDL3::SDL3)

if (ASAN EQUAL 1)
        target_link_libraries(server PRIVATE -fsanitize=address,undefined Threads::Threads)
elseif (TSAN EQUAL 1)
        target_link_libraries(server PRIVATE -fsanitize=thread Threads::Threads)
elseif (MSAN EQUAL 1)
        target_link_libraries(server PRIVATE -fsanitize=memory Threads::Threads)
else()
        target_link_libraries(server PRIVATE Threads::Threads)
endif()
