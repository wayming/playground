#include <gtest/gtest.h>
#include "../CPP11STL/d1.h"

TEST(SchedulerTest, Sanity) {
	Scheduler sched;
	std::vector<std::thread> threads;
	for (int i = 0; i < 10; ++i) {
		std::this_thread::sleep_for(std::chrono::milliseconds(100));
		threads.emplace_back(
			[&sched, i]() {
				for (int k = 0; k < 10; ++k) {
					std::this_thread::sleep_for(std::chrono::seconds(1));
					sched.add([i]() {
						auto now = std::chrono::system_clock::now();
						std::time_t t = std::chrono::system_clock::to_time_t(now);

						std::cout << "fired for " << i << " at "
							<< std::ctime(&t)
							<< std::endl;
						}, i);
				}

			}
		);
	}


	std::thread worker([&sched]() { sched.run(); });

	for (auto& t : threads) {
		t.join();
	}

	std::this_thread::sleep_for(std::chrono::milliseconds(100));
	sched.stop();
	worker.join();
}