#include <gtest/gtest.h>
#include "../CPP11STL/d5.h"

TEST(AsyncTests, Sanity) {
	auto results = runSqureTasks(5);
	ASSERT_EQ(results.size(), 5);
	for (auto& x : results) {
		std::cout << x << ",";
	}
	std::cout << std::endl;
}