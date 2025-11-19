#include <queue>
#include <tuple>
#include <functional>
#include <string>

auto cmp = [](const auto& a, const auto& b) {
	return std::get<0>(a) < std::get<0>(b);
};

struct TaskQueue {
	using taskFunc = std::function<void(int)>;
	void submit(int prioriy, taskFunc func) {
		tasks.emplace(prioriy, func);
	}
	void run() {
		while (!tasks.empty()) {
			int p;
			taskFunc f;
			std::tie(p, f) = tasks.top();
			tasks.pop();
			f(p);
		}
	}

	std::priority_queue<
		std::tuple<int, taskFunc>,
		std::vector<std::tuple<int, taskFunc>>,
		decltype(cmp)> tasks{cmp};
};