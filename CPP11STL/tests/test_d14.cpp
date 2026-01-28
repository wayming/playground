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
	std::vector<std::thread> consumers;
	for (int i = 0; i < 2; i++) {
		consumers.emplace_back([&q]() {
			while (true) {
				try {
					std::cout << "consumer-" << std::this_thread::get_id() << ":" << q.pop() << std::endl;
					std::this_thread::sleep_for(std::chrono::milliseconds(10));
				} catch(QueueEmptyException& e) {
					// ignore queue empty error
					std::cout << e.what() << std::endl;
				} catch(QueueClosedException& e) {
					std::cout << e.what() << std::endl;
					break;
				}
			}
		});

	}
	for (int i = 0; i < 2; i++) {
		consumers.emplace_back([&q]() {
			while (true) {
				try {
					std::string message;
					if (q.try_pop(message)) {
						std::cout << "consumer-" << std::this_thread::get_id() << ":" << message << ":try_pop" << std::endl;
					}
					std::this_thread::sleep_for(std::chrono::milliseconds(10));
				} catch(QueueClosedException& e) {
					std::cout << e.what() << std::endl;
					break;
				}
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

	for (auto& c : consumers) {
		c.join();
	}
}