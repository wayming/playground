#include <coroutine>
#include <iostream>
#include <thread>
#include <chrono>

using Clock = std::chrono::steady_clock;
Clock::time_point g_start;

double elapsed() {
    return std::chrono::duration<double>(Clock::now() - g_start).count();
}

// ---------- Task<T> 定义（和之前一样） ----------
template<typename T>
struct Task {
    struct promise_type {
        T result;
        Task get_return_object() {
            return Task{ std::coroutine_handle<promise_type>::from_promise(*this) };
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_value(T value) { result = value; }
        void unhandled_exception() { std::terminate(); }
    };
    std::coroutine_handle<promise_type> handle;
    explicit Task(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Task() { if (handle) handle.destroy(); }
    T get_result() { return handle.promise().result; }
    bool done() { return handle.done(); }
};

struct AsyncSleep {
    int seconds;
    bool await_ready() { return false; }
    void await_suspend(std::coroutine_handle<> handle) {
        std::thread([handle, this]() {
            std::this_thread::sleep_for(std::chrono::seconds(seconds));
            handle.resume();
        }).detach();
    }
    void await_resume() {}
};

Task<int> fetch_data(const char* name, int seconds) {
    printf("[%.1fs] %s: 开始请求 (预计耗时%d秒)\n", elapsed(), name, seconds);
    co_await AsyncSleep{seconds};
    printf("[%.1fs] %s: 请求完成!\n", elapsed(), name);
    co_return seconds;
}

int main() {
    g_start = Clock::now();

    // 同时"发起"两个任务：一个3秒，一个1秒
    auto taskA = fetch_data("任务A", 3);
    auto taskB = fetch_data("任务B", 1);

    // 证明main线程没有被阻塞：它继续做自己的事(打印计数)
    for (int i = 1; i <= 4; ++i) {
        printf("[%.1fs] main: 正在做别的事... (%d/4)\n", elapsed(), i);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    while (!taskA.done() || !taskB.done()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    printf("[%.1fs] 全部完成，总耗时约3秒（如果是串行执行，会是4秒）\n", elapsed());
}