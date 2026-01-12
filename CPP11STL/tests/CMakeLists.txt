include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
FetchContent_MakeAvailable(googletest)

file(GLOB TEST_SOURCES "test_*.cpp")
foreach(TEST_FILE ${TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    add_executable(${TEST_NAME} ${TEST_FILE})

    # 设置静态运行时库 (/MT 或 /MTd)
    if(MSVC)
      set_target_properties(${TEST_NAME} PROPERTIES
        MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
      )
      # 确保GoogleTest使用静态运行时库
      set_target_properties(gtest gtest_main PROPERTIES
        MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
      )
    endif()

    target_link_libraries(${TEST_NAME} PRIVATE gtest_main)

    add_dependencies(${TEST_NAME} CPP11STL)

    # Enable testing with GoogleTest
    include(GoogleTest)
    gtest_discover_tests(${TEST_NAME}
        TEST_PREFIX "Test_"
        TEST_SUFFIX ""
        PROPERTIES ENVIRONMENT "GTEST_CATCH_EXCEPTIONS=0"
        TEST_EXTRA_ARGS "--gtest_catch_exceptions=0;--gtest_color=yes;--gtest_print_time=1"
    )

    # Include the GoogleTest headers directory
    target_include_directories(${TEST_NAME} PRIVATE ${gtest_SOURCE_DIR}/include ${gtest_SOURCE_DIR})
endforeach()

