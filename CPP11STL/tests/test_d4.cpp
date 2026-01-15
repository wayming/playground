#include <gtest/gtest.h>
#include "../CPP11STL/d4.h"

TEST(LogBufferTests, Sanity) {
	LogBuffer buff1;
	buff1.add("Log line 1");
	buff1.add("Log line 2");
	buff1.add("Log line 3");
	buff1.add("Log line 4");

	LogBuffer buff2;
	buff2.add("Log line 5");
	buff2.add("Log line 6");
	buff2.add("Log line 7");
	buff2.add("Log line 8");

	// Move Assign
	LogBuffer buff3;
	buff3 = std::move(buff2);

	// Move Construct
	LogBuffer buff4 = std::move(buff3);

	buff1.merge(std::move(buff4));

	buff1.show();
	ASSERT_EQ(buff1.buffer().size(), 8);
}