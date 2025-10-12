#pragma once
#include <queue>
#include <mutex>
#include <condition_variable>
#include <optional>

namespace LogAnalyzer {

// Header-only thread-safe queue for passing parsed batches between threads.
template <typename T>
class ThreadSafeQueue {
public:
    ThreadSafeQueue() = default;
    ThreadSafeQueue(const ThreadSafeQueue&) = delete;
    ThreadSafeQueue& operator=(const ThreadSafeQueue&) = delete;

    void push(T value) {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            q_.push(std::move(value));
        }
        cv_.notify_one();
    }

    // pop will return std::nullopt if stop() has been called and queue empty.
    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mtx_);
        cv_.wait(lock, [&]{ return !q_.empty() || stopped_; });
        if (q_.empty() && stopped_) return std::nullopt;
        T val = std::move(q_.front());
        q_.pop();
        return val;
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            stopped_ = true;
        }
        cv_.notify_all();
    }

    bool empty() const {
        std::lock_guard<std::mutex> lock(mtx_);
        return q_.empty();
    }

private:
    mutable std::mutex mtx_;
    std::queue<T> q_;
    std::condition_variable cv_;
    bool stopped_ = false;
};

} // namespace LogAnalyzer
