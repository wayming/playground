#include <functional>
#include <chrono>
#include <thread>
#include <atomic>
#include <iostream>
class CronJob {
public:
	CronJob(std::function<void()> f, int milliInterval) {
		func = std::move(f);
		t = std::thread(
			[milliInterval, this]() {
				while (run) {
					try { func(); }
					catch (std::exception& e) { std::cerr << "Failed to run function. Error: " << e.what() << std::endl; }
					std::this_thread::sleep_for(std::chrono::milliseconds(milliInterval));
				}
			}
		);
	}
	void stop() {
		run = false;
		t.join();
	}
private:
	std::function<void()> func;
	std::thread t;
	std::atomic<bool> run = true;
};