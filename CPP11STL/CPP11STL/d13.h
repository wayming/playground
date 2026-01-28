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
	template<typename F, typename... Args>
	void submit(int p, F&& f, Args&&... args) {

		// C++17
		// auto taskData = std::make_tuple(std::forward<F>(f), std::forward<Args>(args)...);
		// tasks.emplace(p, [p, data = std::move(taskData)]() mutable{
		// 	std::cout << "Invoke task prioriy " << p << std::endl;
		// 	std::apply([](auto&& f, auto&&... args) {
		// 		std::invoke(
		// 			std::forward<decltype(f)>(f),
		// 			std::forward<decltype(args)>(args)...
		// 		);
		// 	}, std::move(data));
		// });

		// C++20
		tasks.emplace(p, [p, f = std::forward<F>(f), ...args = std::forward<Args>(args)]() mutable {
			std::cout << "Invoke task prioriy " << p << std::endl;
			// f(args...);
			std::invoke(std::move(f), std::move(args)...);
		});
	}
	void run() {
		while(!tasks.empty()) {
			auto&[priority, func] = std::move(tasks.top());
			func();
			tasks.pop();
		}
		return;
	}
};