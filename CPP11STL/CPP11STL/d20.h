#include <future>
#include <functional>
#include <iostream>

// thread_pool.hpp
#ifndef THREAD_POOL_HPP
#define THREAD_POOL_HPP

#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <future>
#include <memory>

class ThreadPool {
public:
    explicit ThreadPool(std::size_t threads = std::thread::hardware_concurrency())
        : stop(false) {
        for (std::size_t i = 0; i < threads; ++i)
            workers_.emplace_back([this] {
                for (;;) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(queue_mutex_);
                        condition_.wait(lock, [this] { return stop || !tasks_.empty(); });
                        if (stop && tasks_.empty()) return;
                        task = std::move(tasks_.front());
                        tasks_.pop();
                    }
                    task();
                }
            });
    }

    // 提交任务到池子，返回 std::future<ReturnType>
    template<class F, class... Args>
    auto enqueue(F&& f, Args&&... args) -> std::future<typename std::result_of<F(Args...)>::type> {
        using ReturnType = typename std::result_of<F(Args...)>::type;
        auto task = std::make_shared< std::packaged_task<ReturnType()> >(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        std::future<ReturnType> res = task->get_future();
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            if (stop) throw std::runtime_error("enqueue on stopped ThreadPool");
            tasks_.emplace([task]() { (*task)(); });
        }
        condition_.notify_one();
        return res;
    }

    ~ThreadPool() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            stop = true;
        }
        condition_.notify_all();
        for (std::thread& worker : workers_) worker.join();
    }

private:
    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex queue_mutex_;
    std::condition_variable condition_;
    bool stop;
};

#endif // THREAD_POOL_HPP

template<typename T>
class FuturePipe {
public:
    explicit FuturePipe(const std::future<T>& t) : currentFuture{t} {}
    explicit FuturePipe(std::future<T>&& t) : currentFuture{std::move(t)} {}

    template<typename F>
    auto operator|(F&& f) {
        using RET = decltype(f(std::declval<T>()));

        return FuturePipe<RET>(std::async(std::launch::async,
            [f, fut = std::move(currentFuture)]() mutable -> RET {
                return f(fut.get());
            }
        ));
    }

    T get() { return currentFuture.get(); }
private:
    std::future<T> currentFuture;
};

template<typename T>
FuturePipe<T> make_future(const T& t) {
    return FuturePipe<T>(std::async(std::launch::async,
        [t]() {
            return t;
        }
    ));
}