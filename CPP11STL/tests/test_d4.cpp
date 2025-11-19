#include <gtest/gtest.h>
#include "../CPP11STL/d4.h"

TEST(LogBufferTests, Sanity) {
	LogBuffer buff1;
	buff1.addLog("Log line 1");
	buff1.addLog("Log line 2");
	buff1.addLog("Log line 3");
	buff1.addLog("Log line 4");

	LogBuffer buff2;
	buff2.addLog("Log line 5");
	buff2.addLog("Log line 6");
	buff2.addLog("Log line 7");
	buff2.addLog("Log line 8");

	LogBuffer buff3;
	buff3 = std::move(buff2);

	buff1.merge(std::move(buff3));

	buff1.show();
}