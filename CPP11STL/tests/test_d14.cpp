#include <gtest/gtest.h>
#include "../CPP11STL/d14.h"
#include <iostream>
#include <vector>
#include <thread>
#include <sstream>
#include <atomic>
#include <chrono>
TEST(QueueSafeTest, Sanity) {
	QueueSafe q;
	std::atomic<bool> stop = false;
	std::vector<std::thread> consumers;
	for (int i = 0; i < 2; i++) {
		consumers.emplace_back([&q, &stop]() {
			while (!stop) {
				try {
					std::cout << "consumer-" << std::this_thread::get_id() << ":" << q.pop() << std::endl;
					std::this_thread::sleep_for(std::chrono::milliseconds(100));
				} catch(QueueEmptyException& e) {
					// ignore queue empty error
					std::cout << e.what() << std::endl;
				}
			}
		});

	}
	for (int i = 0; i < 2; i++) {
		consumers.emplace_back([&q, &stop]() {
			while (!stop) {
				std::string message;
				if (q.try_pop(message)) {
					std::cout << "consumer-" << std::this_thread::get_id() << ":" << message << std::endl;
				}
				std::this_thread::sleep_for(std::chrono::milliseconds(100));
			}
		});
	}
	std::vector<std::thread> producers;
	for (int i = 0; i < 5; i++) {
		producers.emplace_back([&q](int numOfMessages) {
			for (int i = 0; i < numOfMessages; ++i) {
				std::stringstream ss;
				ss << "producer-" << std::this_thread::get_id() << ": message" << i;
				q.push(ss.str());
			}
		}, 10);
	}

	for (auto& p : producers) {
		p.join();
	}

	q.graceShutdown();
	stop = true;

	for (auto& c : consumers) {
		c.join();
	}
}