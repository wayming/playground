#include <iostream>
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
    ThreadPool(size_t n = std::thread::hardware_concurrency()) {
        for (size_t i = 0; i < n; ++i) {
            threads.emplace_back([this](){
                while (true) {
                    std::unique_lock<std::mutex> lock(mtx);
                    cv.wait(lock, [this](){ return stop || !taskQueue.empty();});
                    if (stop && taskQueue.empty()) return;
                    auto task = std::move(taskQueue.front());
                    taskQueue.pop();
                    task();
                }
            });
        }
    }

    template <typename F, typename... Args>
    std::future<typename std::result_of<F(Args...)>::type> enqueue(F&& f, Args&&... args) {
        using RET = decltype(std::forward<F>(f)(std::forward<Args>(args)...));
        auto task = std::make_shared<std::packaged_task<RET()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        auto fu = task->get_future();
        {
            std::scoped_lock<std::mutex> lock(mtx);
            if (stop) throw std::runtime_error("enqueue stopped.");
            taskQueue.emplace([task]() mutable { (*task)(); });
        }
        cv.notify_one();
        return fu;
    }

    ~ThreadPool() {
        stop = true;
        cv.notify_all();
        for (auto& t : threads) t.join();
    }
private:
    std::vector<std::thread> threads;
    std::queue<std::function<void()>> taskQueue;
    std::mutex mtx;
    std::condition_variable cv;
    std::atomic<bool> stop = false;
};


// class ThreadPool {
// public:
//     explicit ThreadPool(std::size_t threads = std::thread::hardware_concurrency())
//         : stop(false) {
//         for (std::size_t i = 0; i < threads; ++i)
//             workers_.emplace_back([this] {
//                 for (;;) {
//                     std::function<void()> task;
//                     {
//                         std::unique_lock<std::mutex> lock(queue_mutex_);
//                         condition_.wait(lock, [this] { return stop || !tasks_.empty(); });
//                         if (stop && tasks_.empty()) return;
//                         task = std::move(tasks_.front());
//                         tasks_.pop();
//                     }
//                     task();
//                 }
//             });
//     }

//     // 提交任务到池子，返回 std::future<ReturnType>
//     template<class F, class... Args>
//     auto enqueue(F&& f, Args&&... args) -> std::future<typename std::result_of<F(Args...)>::type> {
//         using ReturnType = typename std::result_of<F(Args...)>::type;
//         auto task = std::make_shared< std::packaged_task<ReturnType()> >(
//             std::bind(std::forward<F>(f), std::forward<Args>(args)...)
//         );
//         std::future<ReturnType> res = task->get_future();
//         {
//             std::unique_lock<std::mutex> lock(queue_mutex_);
//             if (stop) throw std::runtime_error("enqueue on stopped ThreadPool");
//             tasks_.emplace([task]() { (*task)(); });
//         }
//         condition_.notify_one();
//         return res;
//     }

//     ~ThreadPool() {
//         {
//             std::unique_lock<std::mutex> lock(queue_mutex_);
//             stop = true;
//         }
//         condition_.notify_all();
//         for (std::thread& worker : workers_) worker.join();
//     }

// private:
//     std::vector<std::thread> workers_;
//     std::queue<std::function<void()>> tasks_;
//     std::mutex queue_mutex_;
//     std::condition_variable condition_;
//     bool stop;
// };

static ThreadPool pool;

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
    return FuturePipe<T>(pool.enqueue(
        [](const T& val) {
            return val;
        }, t));
}