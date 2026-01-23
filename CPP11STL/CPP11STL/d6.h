#include <vector>
#include <thread>
#include <queue>
#include <functional>
#include <future>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <memory>
#include <iostream>

class ThreadPool {
	std::vector<std::thread> threads;
	std::queue<std::function<void()>> tasks;
	std::mutex queueMutex;
	std::condition_variable cond;
	std::atomic<bool> stop = false;
public:
	ThreadPool(int n) {
		for(int i = 0; i < n; ++i) {
			threads.emplace_back([this](){
				while(true) {
					std::unique_lock<std::mutex> lock(queueMutex);
					cond.wait(lock, [this]() {return stop || !tasks.empty();});
					if (stop && tasks.empty()) {
						std::cout << "task queue drained, exit" << std::endl;
						break;
					}
					auto task = std::move(tasks.front());
					tasks.pop();
					lock.unlock();
					task();
				}
			});
		}
	}

	~ThreadPool() {
		stop = true;
		cond.notify_all();
		for(auto& t : threads) {
			t.join();
		}
	}
	ThreadPool(const ThreadPool&) = delete;
	ThreadPool operator=(const ThreadPool&) = delete;
	
	template<typename Func, typename... Args>
	auto enqueue(Func&& f, Args&&... args) {
		using returnType = std::invoke_result_t<Func, Args...>;
		auto task = std::make_shared<std::packaged_task<returnType()>>([f, args...]() mutable {
			return f(args...);
		});
		auto retFuture = task->get_future();
		{
			std::lock_guard<std::mutex> lock(queueMutex);
			if (stop) {
				throw std::runtime_error("threads pool stopped.");
			}
			tasks.emplace([task](){(*task)();});
		}
		cond.notify_one();

		return retFuture;
	}
};