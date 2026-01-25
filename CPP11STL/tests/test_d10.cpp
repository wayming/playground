#include <gtest/gtest.h>
#include "../CPP11STL/d10.h"
#include <thread>

TEST(TuplePrint, Sanity) {
	auto t = std::make_tuple<int, std::string, double>(100, "test string", 4.001);
	tuple_print_left_ref(t);
	tuple_print_right_ref(std::move(t));

	tuple_print(std::make_tuple<int, std::string, double>(100, "perfect forwarding", 4.001));
}