#include <array>
#include <functional>
#include <atomic>
#include <cstdint>
#include <thread>
#include <iostream>
#include <chrono>
#include <type_traits>

inline constexpr size_t kCacheLine = std::hardware_destructive_interference_size;

template <class T, size_t N = 1024>
// requires std::is_trivially_copyable_v < T>
class LockFreeSPSC
{
private:
    static_assert(N >= 2, "minimum capacity is 2");
    static_assert(std::is_default_constructible_v<T>, "T must be default constructable");
    alignas(kCacheLine) std::array<T, N> buffer;

    // Keep each thread’s private cache of the peer index on its own cache line:
    // cached_consume (producer-only) belongs next to produce, and cached_produce
    // 1(consumer-only) next to consume. Otherwise the producer keeps contending
    // with the consumer’s writes to consume, which cancels the benefit of caching the peer index.
    alignas(kCacheLine) std::atomic<size_t> produce = {0};
    size_t cached_produce = 0;

    alignas(kCacheLine) std::atomic<size_t> consume = {0};
    size_t cached_consume = 0;
    static constexpr size_t next(std::size_t n) noexcept
    {
        return (n + 1 == N) ? 0 : n + 1;
    }

public:
    static constexpr bool hot_path_safe = std::is_trivially_copyable_v<T>;

    template <class U>
    bool try_push(U &&u)
    {

        const auto curr = produce.load(std::memory_order_relaxed);
        const auto nxt = next(curr);
        if (nxt == cached_consume)
        {
            cached_consume = consume.load(std::memory_order_acquire);
            if (nxt == cached_consume)
            {
                // Leave one out
                return false;
            }
        }

        buffer[curr] = std::forward<U>(u);
        produce.store(nxt, std::memory_order_release);
        return true;
    }

    bool try_pop(T &t)
    {
        auto curr = consume.load(std::memory_order_relaxed);
        if (curr == cached_produce)
        {
            cached_produce = produce.load(std::memory_order_acquire);
            if (curr == cached_produce)
            {
                return false;
            }
        }

        t = std::move(buffer[curr]);

        consume.store(next(curr), std::memory_order_release);
        return true;
    }
};

int main()
{
    LockFreeSPSC<std::function<void()>> queue;
    auto producer = std::jthread([&queue](std::stop_token stop)
                                 {
                    uint64_t idx = 0;
                    while (!stop.stop_requested()) {

                    if (!queue.try_push([idx]()
                                        { std::cout << idx << std::endl; }))
                    {
                        continue;
                    }
                    ++idx;
                                     } });

    auto consumer = std::jthread([&queue](std::stop_token stop)
                                 {
                    while (!stop.stop_requested()) {

                    std::function<void()> f;
                    if (!queue.try_pop(f))
                    {
                        continue;
                    }
                    f();} });

    std::this_thread::sleep_for(std::chrono::seconds(10));
    producer.get_stop_source().request_stop();
    producer.join();
    consumer.get_stop_source().request_stop();
    consumer.join();

    struct Num
    {
        int k = {0};
    };
    LockFreeSPSC<Num> queue2;
    static_assert(LockFreeSPSC<Num>::hot_path_safe, "queue must be hot-path safe");
    producer = std::jthread([&queue2](std::stop_token stop)
                            {
        auto idx = 0;
        while (!stop.stop_requested())
        {
            {
                if (queue2.try_push(Num{idx}))
                {
                    ++idx;
                }
            }
        } });
    consumer = std::jthread([&queue2](std::stop_token stop)
                            {
        while (!stop.stop_requested())
        {
            Num n;
            if (queue2.try_pop(n))
            {
                std::cout << n.k << std::endl;
            }
        } });

    std::this_thread::sleep_for(std::chrono::seconds(10));
    producer.get_stop_source().request_stop();
    producer.join();
    consumer.get_stop_source().request_stop();
    consumer.join();
    return 0;
}