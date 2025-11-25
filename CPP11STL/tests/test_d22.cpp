#include <gtest/gtest.h>
#include "../CPP11STL/d22.h"
#include <thread>

TEST(LRUSafeTest, Sanity) {
	LRUSafe cache(5, 100);
	cache.put("a", "100");
	cache.put("b", "200");
	cache.put("c", "300");
	cache.put("d", "400");
	cache.put("e", "500");
	cache.put("f", "600");
	ASSERT_EQ(cache.get("b"), "200");
	cache.dump();
	ASSERT_THROW(cache.get("a"), std::runtime_error);
	std::this_thread::sleep_for(std::chrono::milliseconds(300));
	cache.dump();
	ASSERT_THROW(cache.get("b"), std::runtime_error);
}