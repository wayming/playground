# CMakeList.txt : CMake project for CPP11STL, include source and define
# project specific logic here.
#

# Add source to this project's executable.
add_executable (CPP11STL "CPP11STL.cpp" "CPP11STL.h" "d4.h" "d5.h" "d6.h" "d7.h" "d8.h" "d9.h" "d10.h" "d11.h" "d12.h" "d13.h" "d14.h")

set_property(TARGET CPP11STL PROPERTY CXX_STANDARD 17)

if(MSVC)
  set_target_properties(CPP11STL PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL"
  )
endif()