#include <gtest/gtest.h>
#include "../CPP11STL/d10.h"
#include <thread>

TEST(PricingStats, Sanity) {
	PricingStats stats(1);
	stats.add(10);
	stats.add(20);
	stats.add(30);
	stats.add(40);
	stats.add(50);
	EXPECT_EQ(stats.count(), 5);
	EXPECT_EQ(stats.min(), 10);
	EXPECT_EQ(stats.max(), 50);
	std::this_thread::sleep_for(std::chrono::seconds(1));
	EXPECT_EQ(stats.count(), 0);
	EXPECT_EQ(stats.min(), -1);
	EXPECT_EQ(stats.max(), -1);
}