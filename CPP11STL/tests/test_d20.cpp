#include <gtest/gtest.h>
#include "../CPP11STL/d20.h"
#include <iostream>
#include <sstream>
#include <chrono>
#include <ctime>
#include <thread>
#include <vector>


TEST(FuturePipeTest, Sanity) {
	auto pipe = make_future<int>(5)
		| [](int x) { return x * x * x; }
		| [](int x) { return std::to_string(x); }
		| [](const std::string& str) { std::cout << "[" << str << "]" << std::endl; return "DONE"; };

	std::cout << pipe.get() << std::endl;
}