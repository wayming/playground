#include <gtest/gtest.h>
#include "../CPP11STL/d8.h"
#include <ctime>
#include <memory>
TEST(CronJobTest, Sanity) {
	{
		auto c1 = std::make_unique<CronJob>();
		c1->Run([]() {
			auto now = std::chrono::system_clock::now();
			std::time_t now_t = std::chrono::system_clock::to_time_t(now);
			std::cout << "alarm1 at " << ctime(&now_t) << std::endl;
			}, std::chrono::milliseconds(100)
		);

		c1->Run([]() {
			auto now = std::chrono::system_clock::now();
			std::time_t now_t = std::chrono::system_clock::to_time_t(now);
			std::cout << "alarm2 at " << ctime(&now_t) << std::endl;
			}, std::chrono::milliseconds(250)
		);

		std::this_thread::sleep_for(std::chrono::seconds(3));
	}
}