#include <stdlib.h>
#include <gtest/gtest.h>
#include "../CPP11STL/d13.h"
#include <iostream>
TEST(TaskQeuueTest, Sanity) {
	TaskQueue tasksScheduler;
	tasksScheduler.submit(10, [](int x, int y) { std::cout << x << "," << y << std::endl; }, std::rand()%100, std::rand()%100);
	tasksScheduler.submit(50, [](std::string x, std::string y, int z) { std::cout << x << "," << y << "," << z << std::endl; }, "aa", "bb", 100);
	tasksScheduler.submit(30, [](int x) { std::cout << x << std::endl; }, std::rand()%100);
	tasksScheduler.submit(40, [](int x) { std::cout << x << std::endl; }, std::rand()%100);
	tasksScheduler.run();
}