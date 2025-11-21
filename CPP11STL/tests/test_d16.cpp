#include <gtest/gtest.h>
#include "../CPP11STL/d16.h"
#include <iostream>
#include <sstream>
#include <chrono>
#include <ctime>
#include <thread>
#include <vector>
#include "stdlib.h"
std::string now() {
	std::time_t now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
	return std::string(ctime(&now));
}

TEST(ThreadSafeLogger, SingleThread) {
	std::stringstream ss;
	ThreadSafeLogger log(ss, LOG_LEVEL::DEBUG);

	auto worker = [&log]() {
		log.logInfo("server start at ", now());
		std::this_thread::sleep_for(std::chrono::milliseconds(rand()%100));
		log.logInfo("request start at ", now());
		std::this_thread::sleep_for(std::chrono::milliseconds(rand()%100));
		log.logInfo("request done at ", now());
		std::this_thread::sleep_for(std::chrono::milliseconds(rand()%100));
		log.logInfo("server stop at ", now());
	};

	std::vector<std::thread> threads;
	for(int i = 0; i < 10; ++i) {
		threads.emplace_back(std::thread(worker));
	}

	for(auto& t : threads) {
		t.join();
	}

	std::cout << ss.str() << std::endl;

}
