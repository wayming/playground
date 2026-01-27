#include <queue>
#include <tuple>
#include <functional>
#include <string>

using TaskType = std::tuple<int, std::function<void()>>;
auto cmp = [](const TaskType& a, const TaskType& b) {
	return std::get<0>(a) < std::get<0>(b);
};

class TaskQueue {
	std::priority_queue<TaskType, std::vector<TaskType>, decltype(cmp)> tasks{cmp};
public:
	void submit(int p, std::function<void(int)> f, int param) {
		tasks.emplace(p, [param, f, p](){
			std::cout << "Invoke task for priority " << p << std::endl;
			f(param);
		});
		return;
	}
	void run() {
		while(!tasks.empty()) {
			auto&[priority, func] = tasks.top();
			func();
			tasks.pop();
		}
		return;
	}
};