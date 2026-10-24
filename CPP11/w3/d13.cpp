#include <coroutine>
#include <exception>
#include <utility>
#include <cstdio>
#include <iostream>

struct final_awaiter
{
    bool await_ready() noexcept { return false; }
    template <class P>
    void await_suspend(std::coroutine_handle<P> handle) noexcept
    {
        if (auto c = handle.promise().continuation)
        {
            c.resume();
        }
    }
    void await_resume() const noexcept {}
};

struct task
{
    struct promise_type
    {
        int val = 0;
        std::coroutine_handle<> continuation{};
        task get_return_object()
        {
            return task{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_always initial_suspend() noexcept { return std::suspend_always{}; }
        final_awaiter final_suspend() noexcept { return final_awaiter{}; }
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

    auto operator co_await() && noexcept
    {
        struct awaiter
        {
            std::coroutine_handle<promise_type> handle; // copy from task coroutine handle
            bool await_ready() { return handle.done(); }
            void await_suspend(std::coroutine_handle<> caller)
            {
                handle.promise().continuation = caller;
                handle.resume();
            }
            int await_resume() const noexcept { return handle.promise().val; }
        };
        return awaiter{handle};
    }
};

task inner()
{
    std::puts("inner start");
    co_return 11;
}

task outer()
{
    std::puts("outer start");

    std::puts("outer await");
    auto v = co_await inner();

    std::puts("outer resume");
    co_return v + 200;
}
int main()
{
    task t = outer();

    std::puts("first resume");
    t.resume();

    std::puts("done");
    std::cout << t.done() << t.result() << std::endl;
    return 0;
}