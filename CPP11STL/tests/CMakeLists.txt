include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
FetchContent_MakeAvailable(googletest)

file(GLOB TEST_SOURCES *.cpp)
add_executable(CPP11STLTESTS ${TEST_SOURCES} "test_d4.cpp" "test_d5.cpp" "test_d6.cpp" "test_d7.cpp" "test_d8.cpp" "test_d9.cpp" "test_d10.cpp" "test_d11.cpp" "test_d12.cpp" "test_d13.cpp" "test_d14.cpp")

# 设置静态运行时库 (/MT 或 /MTd)
if(MSVC)
  set_target_properties(CPP11STLTESTS PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
  )
  # 确保GoogleTest使用静态运行时库
  set_target_properties(gtest gtest_main PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
  )
endif()

target_link_libraries(CPP11STLTESTS PRIVATE gtest_main)

add_dependencies(CPP11STLTESTS CPP11STL)

# Enable testing with GoogleTest
include(GoogleTest)
gtest_discover_tests(CPP11STLTESTS)

# Include the GoogleTest headers directory
target_include_directories(CPP11STLTESTS PRIVATE ${gtest_SOURCE_DIR}/include ${gtest_SOURCE_DIR})