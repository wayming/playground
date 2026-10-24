#include <coroutine>
#include <exception>
#include <utility>
#include <cstdio>
#include <iostream>
#include <chrono>
#include <queue>
#include <vector>
#include <functional>
#include <thread>

struct final_awaiter
{
    bool await_ready() noexcept { return false; }
    template <class P>
    std::coroutine_handle<> await_suspend(std::coroutine_handle<P> handle) noexcept
    {
        auto c = handle.promise().continuation;
        return c ? c : std::noop_coroutine();
    }
    void await_resume() const noexcept {}
};

struct task
{
    struct promise_type
    {
        int val = 0;
        std::coroutine_handle<> continuation{};
        std::exception_ptr exp{};

        task get_return_object()
        {
            return task{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_always initial_suspend() noexcept { return std::suspend_always{}; }
        final_awaiter final_suspend() noexcept { return final_awaiter{}; }
        void return_value(int v) { val = v; }
        void unhandled_exception() { exp = std::current_exception(); }
        int result()
        {
            if (exp)
            {
                std::rethrow_exception(exp);
            }
            return val;
        }
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
            std::coroutine_handle<promise_type> await_suspend(std::coroutine_handle<> caller)
            {
                handle.promise().continuation = caller;
                return handle;
            }
            int await_resume() const { return handle.promise().result(); }
        };
        return awaiter{handle};
    }
};

struct Scheduler
{
    struct timer
    {
        std::chrono::steady_clock::time_point when;
        size_t seq;
        std::coroutine_handle<> handle;
        bool operator>(const timer &other) const
        {
            if (when != other.when)
                return when > other.when;
            return seq > other.seq;
        }
    };
    size_t seq = 0;
    std::priority_queue<timer, std::vector<timer>, std::greater<>> tasks;
    void add(std::chrono::steady_clock::time_point when, std::coroutine_handle<> h)
    {
        tasks.emplace(when, ++seq, h);
    }

    void run()
    {
        while (!tasks.empty())
        {
            timer t = tasks.top();
            tasks.pop();
            std::this_thread::sleep_until(t.when);
            t.handle.resume();
        }
    }
};
inline Scheduler SCHD;

inline auto sleep_for(std::chrono::steady_clock::duration d)
{
    struct awaiter
    {
        std::chrono::steady_clock::duration d;
        bool await_ready() const noexcept { return d <= std::chrono::steady_clock::duration::zero(); }
        void await_suspend(std::coroutine_handle<> h) const
        {
            SCHD.add(std::chrono::steady_clock::now() + d, h);
        }
        void await_resume() const noexcept {}
    };
    return awaiter{d};
}

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

task fetch(std::chrono::milliseconds d)
{
    std::cout << "start " << d.count() << " at " << std::chrono::system_clock::now() << std::endl;
    co_await sleep_for(d);
    std::cout << "resume " << d.count() << " at " << std::chrono::system_clock::now() << std::endl;
    co_return d.count();
}

int main()
{
    task t = outer();

    std::puts("first resume");
    t.resume();

    std::puts("done");
    std::cout << t.done() << t.result() << std::endl;

    task a = fetch(std::chrono::milliseconds(10)), b = fetch(std::chrono::milliseconds(100)), c = fetch(std::chrono::milliseconds(50));
    a.resume();
    b.resume();
    c.resume();
    SCHD.run();
    std::cout << a.result() << " " << b.result() << " " << c.result();
    return 0;
}