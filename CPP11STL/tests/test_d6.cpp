#include <gtest/gtest.h>
#include "../CPP11STL/d6.h"

TEST(TaskThreadPool, Sanity) {
	ThreadsPool pool(10);
	std::vector<std::unique_ptr<std::future<int>>> futures;
	for (int i = 0; i < 100; ++i) {
		futures.emplace_back(pool.enqueue([](int x) { return x * x; }, i));
	}
	for (auto& f : futures) {
		std::cout << f->get() << std::endl;
	}
}