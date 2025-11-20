#include <queue>
#include <string>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
class QueueEmptyException : public std::exception {
public:
	const char* what() const noexcept override {
		return "queue empty";
	}
};
class QueueSafe {
public:
	void push(const std::string& message) {
		std::lock_guard<std::mutex> lock(mtx);
		q.emplace(message);
		cv.notify_one();
	}

	std::string pop() {
		std::unique_lock<std::mutex> lock(mtx);
		cv.wait(lock, [this]() { return !q.empty() || shutdown;  });
		if (q.empty()) {
			throw QueueEmptyException();
		}
		std::string message = q.front();
		q.pop();
		return message;
	}

	bool try_pop(std::string& message) {
		if (mtx.try_lock()) {
			if (q.empty()) {
				mtx.unlock();
				return false;
			}
			std::string message = q.front();
			q.pop();
			mtx.unlock();
			return true;
		}
		return false;
	}

	bool empty() {
		std::lock_guard<std::mutex> lock(mtx);
		return q.empty();
	}

	void graceShutdown() {
		while (!q.empty()) {
			std::this_thread::sleep_for(std::chrono::milliseconds(100));
		}
		shutdown = true;
		cv.notify_all();
	}
private:
	std::queue<std::string> q;
	std::mutex mtx;
	std::condition_variable cv;
	std::atomic<bool> shutdown = false;
};