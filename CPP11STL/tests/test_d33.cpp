#include <gtest/gtest.h>
#include "../CPP11STL/d33.h"
#include <thread>
#include <chrono>
TEST(LockFreeQueue, MPMC) {
	LockFreeQueue<int> queue(10);
	std::vector<std::thread> threads;
	for (int n = 0; n < 10; ++n) {
		threads.emplace_back([&queue](int x){
			for (int y = 0; y < 10; ++y) {
				while(!queue.enqueueMP(10 * x + y)) {
					std::this_thread::sleep_for(std::chrono::milliseconds(1));
				}
			}
		}, n);
	}

	for (int n = 10; n < 20; ++n) {
		threads.emplace_back([&queue](int x){
			for (int y = 0; y < 10; ++y) {
				int i = 0;
				while(!queue.dequeueMC(i)) {
					std::this_thread::sleep_for(std::chrono::milliseconds(1));
				}
				std::cout<< i << std::endl;
			}
		}, n);
	}

	for(auto& t : threads) {
		t.join();
	}

}