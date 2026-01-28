#include <queue>
#include <string>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
/*
逻辑点	状态	为什么它是正确的？
锁持有时间	🚀 极短	push 采用传值 + move，大对象的拷贝发生在锁外。
丢失唤醒风险	✅ 已解决	graceShutdown 在锁内修改 closed 并 notify_all。
异常安全性	✅ 已解决	try_pop 使用 adopt_lock，即便 move 报错也会自动解锁。
虚假唤醒	✅ 已解决	pop 中的 cv.wait 使用了 Lambda 谓词，完美处理虚假唤醒。
右值支持	✅ 已解决	push(std::string message) 同时高效支持左值和右值。
*/
class QueueEmptyException : public std::exception {
public:
	const char*what() const noexcept override  {
		return "empty queue";
	}
};
class QueueClosedException : public std::exception {
public:
	const char*what() const noexcept override {
		return "queue closed";
	}
};
class QueueSafe {
	std::queue<std::string> messages;
	std::mutex mtx;
	std::atomic<bool> closed = false;
	std::condition_variable cv;
public:
	void push(std::string message) {
		if (closed) throw QueueClosedException();
		std::lock_guard<std::mutex> lock(mtx);
		messages.emplace(std::move(message));
		cv.notify_one();
	}

	// Block until either:
	// a message is return or
	// queue is closed
	std::string pop() {
		std::unique_lock<std::mutex> lock(mtx);
		cv.wait(lock, [this](){
			return closed || !messages.empty();
		});
		if (!messages.empty()) {
			std::string message = std::move(messages.front());
			messages.pop();
			lock.unlock();
			return message;
		} else {
			throw QueueClosedException();
		}
	}

	bool try_pop(std::string& message) {

		if (mtx.try_lock()) {
			std::lock_guard<std::mutex> lock(mtx, std::adopt_lock);
			if (messages.empty()) {
				if (closed) throw QueueClosedException();
				return false;
			}
			message = std::move(messages.front());
			messages.pop();
			return true;
		} else {
			return false;
		}
	}

	bool empty() {
		std::lock_guard<std::mutex> lock(mtx);
		return messages.empty();
	}

	void graceShutdown() {
		// Need the lock as the memory might be reordered to exectue notify_all first
		// Lock queue to avoid lost wake-up.
		std::lock_guard<std::mutex> lock(mtx);
		closed = true;
		cv.notify_all();
	}
};