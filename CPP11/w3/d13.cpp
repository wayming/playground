#include <coroutine>
#include <exception>
#include <utility>
#include <cstdio>
#include <iostream>
struct task
{
    struct promise_type
    {
        int val = 0;
        task get_return_object()
        {
            return task{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_always initial_suspend() noexcept { return std::suspend_always{}; }
        std::suspend_always final_suspend() noexcept { return std::suspend_always{}; }
        void return_value(int v) { val = v; }
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;
    explicit task(std::coroutine_handle<promise_type> h) : handle(h) {}
    task(task &&t) : handle{std::exchange(t.handle, {})} {}
    ~task()
    {
        if (handle)
            handle.destroy();
    }

    void resume() { return handle.resume(); }
    bool done() const { return handle.done(); }
    int result() const { return handle.promise().val; }
};

task compute()
{
    std::puts("compute starts");
    co_await std::suspend_always{};
    std::puts("compute resume");
    co_return 40;
}

int main()
{
    task t = compute();

    std::puts("first resume");
    t.resume();

    std::puts("second resume");
    t.resume();

    std::puts("done");
    std::cout << t.done() << t.result() << std::endl;
    return 0;
}