#include <gtest/gtest.h>
#include "../CPP11STL/d13.h"
#include <iostream>
TEST(TaskQeuueTest, Sanity) {
	TaskQueue tasksScheduler;
	tasksScheduler.submit(10, [](int x) { std::cout << x << std::endl; });
	tasksScheduler.submit(50, [](int x) { std::cout << x << std::endl; });
	tasksScheduler.submit(30, [](int x) { std::cout << x << std::endl; });
	tasksScheduler.submit(40, [](int x) { std::cout << x << std::endl; });
	tasksScheduler.run();
}