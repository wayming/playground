# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required(VERSION 3.15)
project(CPP11STL)

enable_testing()

# 不设置全局运行时库，交给子项目单独配置
add_subdirectory(CPP11STL)
add_subdirectory(tests)