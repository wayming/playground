#include <functional>
#include <chrono>
#include <thread>
#include <atomic>
#include <iostream>

using MilliSecondsDuration = std::chrono::duration<int, std::milli>;
class CronJob {
	std::vector<std::thread> threads;
	std::atomic<bool> run = true;
public:
	void Run(std::function<void()> f, MilliSecondsDuration d) {
		threads.emplace_back(
			std::thread([f = std::move(f), d, this]() mutable {
				auto lastRun = std::chrono::steady_clock::time_point::min();
				while(run) {
					auto now = std::chrono::steady_clock::now();
					if (now > lastRun + d) {
						f();
						lastRun = now;
					} else {
						auto waitDuration = lastRun + d - now;
						if (waitDuration > std::chrono::steady_clock::duration::zero()) {
							std::this_thread::sleep_for(waitDuration);
						}
					}
				}
			})
		);
	}
	~CronJob() {
		run = false;
		for(auto& t : threads) {
			t.join();
		}
	}
};