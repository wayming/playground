#include <random>
#include <algorithm>
#include <future>
#include <chrono>
#include <condition_variable>
#include <iostream>
#include <atomic>
#include <thread>
#include <functional>

class RandomeTaskScheduler {
public:
	template<typename f>
	void run(int n, std::function<int(int)> f) {
		for(int i = 0; i < n; ++i) {
			std::packaged_task<int(int)> t(f);
			futures.push_back(t.get_future());
			threads.emplace_back(std::move(t), dist(gen));
		}
	}
	auto results() {
		std::vector<int> res;

		for(auto& t : threads) {
			t.join();
		}
		threads.clear();

		for(auto& f : futures) {
			res.push_back(f.get());
		}
		futures.clear();
		return res;
	}
private:
	std::vector<std::future<int>> futures;
	std::vector<std::thread> threads;
	std::mt19937 gen{std::random_device{}()};
	std::uniform_int_distribution<int> dist{0, 99};
};

auto runSqureTasks(int n) {
	RandomeTaskScheduler sche;
	sche.run(n, [](int x) {
		auto now = std::chrono::steady_clock::now();
		std::this_thread::sleep_for(std::chrono::milliseconds(rand()%1000));
		auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - now);
		std::cout << "Calculate " << x << " took " << duration.count() << "ms" << std::endl;
		return x * x;
	});

	return sche.results();
}