#include <queue>
#include <chrono>
#include <functional>

#include <mutex>
#include <thread>
#include <atomic>
#include <condition_variable>

class Task {
public:
	Task(std::function<void()> w, int prioriy, std::chrono::steady_clock::time_point s) :
			work(w), pr(prioriy), start(s) {}
	bool operator < (const Task& other) const {
		if (this->pr != other.pr) {
			return this->pr < other.pr;
		}
		else {
			return this->start > other.start;
		}
	}
	std::chrono::steady_clock::time_point when() { return start; }
	void fire() { work(); }
private:
	int pr;
	std::function<void()> work;
	std::chrono::steady_clock::time_point start;
};

class Scheduler {
public:
	void run() {
		while (!done) {
			std::cout << "run" << std::endl;

			std::unique_lock<std::mutex> lock(qMutex);
			if (tasks.empty()) {
				std::cout << "wait done = " << done << std::endl;
				qCV.wait(lock, [this]() {
					return done || !tasks.empty();
				});
			}
			if (tasks.empty()) {
				continue;
			}

			auto topTask = tasks.top();
			if (topTask.when() > std::chrono::steady_clock::now()) {
				qCV.wait_until(lock, topTask.when());
				continue;
			}
			std::cout << "fire" << std::endl;
			topTask.fire();
			tasks.pop();
			lock.unlock();
		}
	}

	void add(std::function<void()> t,
			 int prioriy,
			 std::chrono::steady_clock::time_point start = std::chrono::steady_clock::now()) {
		std::lock_guard<std::mutex> lock(qMutex);
		tasks.emplace(t, prioriy, start);
		qCV.notify_one();
	}

	void stop() { done = true; qCV.notify_all(); }
private:
	std::mutex qMutex;
	std::condition_variable qCV;
	std::priority_queue<Task> tasks;
	std::atomic<bool> done = false;
};