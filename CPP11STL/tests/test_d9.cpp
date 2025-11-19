#include <gtest/gtest.h>
#include "../CPP11STL/d9.h"
#include <ctime>
TEST(CronJobTest, Sanity) {
	CronJob c1([]() {
		auto now = std::chrono::system_clock::now();
		std::time_t now_t = std::chrono::system_clock::to_time_t(now);
		std::cout << "alarm1 at " << ctime(&now_t) << std::endl;
		}, 100
	);

	CronJob c2([]() {
		auto now = std::chrono::system_clock::now();
		std::time_t now_t = std::chrono::system_clock::to_time_t(now);
		std::cout << "alarm2 at " << ctime(&now_t) << std::endl;
		}, 150
	);

	std::this_thread::sleep_for(std::chrono::seconds(3));
	c1.stop();
	c2.stop();

}