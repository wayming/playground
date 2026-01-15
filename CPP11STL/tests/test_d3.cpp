#include <gtest/gtest.h>
#include "../CPP11STL/d3.h"

TEST(ResourceManagementTests, Sanity) {
	ResourcePool pool;
	{
		std::shared_ptr<Resource> r0 = pool.acquireResource(5);
		r0->fill("this is a test string");
	}
	{
		std::shared_ptr<Resource> r0 = pool.acquireResource(5);
		EXPECT_EQ(r0->asString(), std::string("this is a test string"));
	}
	std::weak_ptr<Resource> weakRes = pool.acquireResource(5);
	std::shared_ptr<Resource> sharedRes = pool.acquireResource(5);
	pool.destroy();
	EXPECT_EQ(weakRes.lock()->asString(), std::string("this is a test string"));
	EXPECT_EQ(sharedRes->asString(), std::string("this is a test string"));
	
	sharedRes.reset();
	EXPECT_EQ(weakRes.expired(), true);

	EXPECT_EQ(1, 1);
}