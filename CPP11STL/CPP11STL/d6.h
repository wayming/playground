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
using TASK_TYPE = std::packaged_task<int()>;
class ThreadsPool {
public:
	ThreadsPool(size_t n) {
		for (int i = 0; i < n; ++i) {
			this->threads.emplace_back(
				std::thread(
					[this]() {
						while (true) {
							std::packaged_task<int()> task;
							{
								std::unique_lock<std::mutex> l(this->taskQueueMutex);
								this->taskAvailable.wait(l, [this]() {return !this->taskQueue.empty() || this->complete; });

								// Complete processing
								if (this->taskQueue.empty() && this->complete) break;

								task = std::move(this->taskQueue.front());
								this->taskQueue.pop();
							}
							task();
						}

					}
				)
			);
		}
	}
	~ThreadsPool() {
		this->complete = true;
		this->taskAvailable.notify_all();
		while (true) {
			{
				std::lock_guard<std::mutex> l(this->taskQueueMutex);
				if (this->taskQueue.empty()) break;
			}
			std::this_thread::sleep_for(std::chrono::milliseconds(10));
		}

		for (auto& t : this->threads) {
			t.join();
		}
	}

	std::unique_ptr<std::future<int>> enqueue(std::function<int(int)> call, int arg) {
		if (this->complete) {
			std::cout << "thread pool exiting, not accepting new tasks" << std::endl;
			return std::unique_ptr<std::future<int>>{};
		}

		std::packaged_task<int()> task(std::bind(call, arg));
		std::unique_ptr<std::future<int>> fut = std::make_unique<std::future<int>>(task.get_future());
		{
			std::lock_guard<std::mutex> l(this->taskQueueMutex);
			this->taskQueue.emplace(std::move(task));
			this->taskAvailable.notify_one();
		}
		return fut;
	}

private:
	std::vector<std::thread> threads;
	std::queue<std::packaged_task<int()>> taskQueue;
	std::mutex taskQueueMutex;
	std::condition_variable taskAvailable;
	std::atomic<bool> complete = false;
};