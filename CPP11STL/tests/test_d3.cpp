#include <gtest/gtest.h>
#include "../CPP11STL/d3.h"

TEST(ResourceManagementTests, Sanity) {
	ResourcePool pool(10);
	{
		std::shared_ptr<Resource> r0 = pool.AcquireResource(5);
		r0->Set(std::string("this is a test string"));
	}
	{
		std::shared_ptr<Resource> r0 = pool.AcquireResource(5);
		EXPECT_EQ(r0->Get(), std::string("this is a test string"));
	}
	std::weak_ptr<Resource> wptrRes = pool.AcquireResource(5);
	std::shared_ptr<Resource> sptrRes = pool.AcquireResource(5);
	pool.Destroy();
	EXPECT_EQ(wptrRes.lock()->Get(), std::string("this is a test string"));
	EXPECT_EQ(sptrRes->Get(), std::string("this is a test string"));
	
	sptrRes.reset();
	EXPECT_EQ(wptrRes.expired(), true);

	EXPECT_EQ(1, 1);
}