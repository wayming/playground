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
	template<typename F, typename... Args>
	void run(int n, F&& f, Args&&... args) {
		for(int i = 0; i < n; ++i) {
			using ReturnType = std::invoke_result_t<F, Args...>;
			std::packaged_task<ReturnType()> task([f, args...]()mutable {
				return f(args...);
			});
			futures.push_back(task.get_future());
			threads.emplace_back([t = std::move(task)]() mutable {
				t();
			});
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

};

auto runSqureTasks(int n) {
	RandomeTaskScheduler sche;
	std::mt19937 gen{std::random_device{}()};
	std::uniform_int_distribution<int> dist{0, 99};
	sche.run(n, [](int x) {
		auto now = std::chrono::steady_clock::now();
		std::this_thread::sleep_for(std::chrono::milliseconds(rand()%1000));
		auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - now);
		std::cout << "Calculate " << x << " took " << duration.count() << "ms" << std::endl;
		return x * x;
	}, dist(gen));

	return sche.results();
}