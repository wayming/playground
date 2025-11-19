#include <random>
#include <algorithm>
#include <future>
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <atomic>
#include <thread>
void run(int n) {
	std::default_random_engine gen;
	std::uniform_int_distribution<int> dist(100, 500);
	std::vector<int> randomDelay(n);
	std::generate(randomDelay.begin(), randomDelay.end(), [&gen, &dist]() {return dist(gen); });
	std::vector<std::future<int>> futures;
	futures.reserve(randomDelay.size());
	std::mutex mtx;
	std::condition_variable start;
	std::atomic<int> readyThreads = 0;
	for (auto delay : randomDelay) {
		futures.emplace_back(std::async([&start, &mtx, &readyThreads](int n) {
			{
				std::unique_lock<std::mutex> lock(mtx);
				readyThreads++;
				std::cout << readyThreads << std::endl;
				start.wait(lock);
			}
			std::chrono::system_clock::time_point begin = std::chrono::system_clock::now();
			std::this_thread::sleep_for(std::chrono::milliseconds(n));
			std::chrono::system_clock::duration defer = std::chrono::system_clock::now() - begin;
			std::cout << "delay " << defer.count() << "ms" << std::endl;
			return n * n;
			}, delay));
	}

	while (true)
	{
		std::cout << readyThreads << std::endl;
		if (readyThreads == n) break;
		std::this_thread::sleep_for(std::chrono::milliseconds(5));
	}
	start.notify_all();
	std::chrono::system_clock::time_point begin = std::chrono::system_clock::now();
	for (auto& f : futures) std::cout << f.get() << std::endl;
	std::chrono::system_clock::duration defer = std::chrono::system_clock::now() - begin;
	std::cout << "total delay " << defer.count() << "ms" << std::endl;
}