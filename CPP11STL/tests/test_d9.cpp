#include <gtest/gtest.h>
#include "../CPP11STL/d9.h"
#include <thread>

TEST(SlidingWindowPricingStats, Sanity) {
	SlidingWindowPricingStats stats(2);
	stats.add(10);
	stats.add(20);
	stats.add(30);
	std::this_thread::sleep_for(std::chrono::seconds(1));
	stats.add(40);
	stats.add(50);
	EXPECT_EQ(stats.count(), 5);
	EXPECT_EQ(stats.min().value(), 10);
	EXPECT_EQ(stats.max().value(), 50);
	EXPECT_DOUBLE_EQ(stats.avg().value(), 30.0);
	std::this_thread::sleep_for(std::chrono::seconds(1));
	EXPECT_EQ(stats.count(), 2);
	EXPECT_EQ(stats.min().value(), 40);
	EXPECT_EQ(stats.max().value(), 50);
	EXPECT_DOUBLE_EQ(stats.avg().value(), 45);
	std::this_thread::sleep_for(std::chrono::seconds(2));
	EXPECT_EQ(stats.count(), 0);
	EXPECT_EQ(stats.min(), std::nullopt);
	EXPECT_EQ(stats.max(), std::nullopt);
	EXPECT_EQ(stats.avg(), std::nullopt);
}