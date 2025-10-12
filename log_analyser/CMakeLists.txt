cmake_minimum_required(VERSION 3.15)
project(LogAnalyzer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(include)

add_executable(LogAnalyzer
    src/main.cpp
    src/Parser.cpp
    src/Aggregator.cpp
    src/Reporter.cpp
    src/Filter.cpp
    # ThreadSafeQueue is header-only template, no cpp needed
)
