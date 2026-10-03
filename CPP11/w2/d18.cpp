#include <queue>
#include <thread>
#include <mutex>
#include <functional>
#include <future>
#include <chrono>
#include <ranges>
#include <iostream>
#include <exception>
class ServerStopping : public std::exception
{
public:
    const char *what() const noexcept override { return "server stopping"; };
};

class Server
{
private:
    std::queue<std::function<void()>> queue_;
    std::condition_variable cv_;
    std::mutex mtx_;
    bool stopping = false;
    std::vector<std::thread> threads;

public:
    Server(size_t nthreads);
    ~Server();
    template <class T>
    auto submit(T &&t)
    {
        // using R = std::invoke_result_t<T &>;
        using R = decltype(t());
        auto task = std::make_shared<std::packaged_task<R()>>(std::forward<T>(t));
        auto future = task->get_future();
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            if (stopping)
            {
                throw ServerStopping();
            }
            queue_.emplace([task]()
                           { (*task)(); });
        }
        cv_.notify_one();
        return future;
    }

    void run()
    {
        while (true)
        {
            std::unique_lock<std::mutex> lock(mtx_);
            cv_.wait(lock, [this]()
                     { return !queue_.empty() || stopping; });
            if (queue_.empty() && stopping)
            {
                return;
            }
            auto task = std::move(queue_.front());
            queue_.pop();
            lock.unlock();
            task();
        }
    }

    void shutdown()
    {
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            stopping = true;
            cv_.notify_all();
        }
    }
};

Server::Server(size_t nthreads)
{
    for (size_t i = 0; i < nthreads; i++)
    {
        threads.emplace_back(&Server::run, this);
    }
}

Server::~Server()
{
    shutdown();
    for (auto &th : threads)
    {
        th.join();
    }
}

int main()
{
    Server s(10);
    std::vector<std::future<int64_t>> fus;
    for (auto i : std::views::iota(1, 1000))
    {
        try
        {
            fus.emplace_back(s.submit([i]()
                                      { std::this_thread::sleep_for(std::chrono::milliseconds(i)); return (int64_t)(i * i); }));
        }
        catch (const ServerStopping &e)
        {
            std::cout << e.what() << '\n';
            break;
        }
        catch (const std::exception &e)
        {
            std::cerr << e.what() << '\n';
        }
    }
    s.shutdown();
    for (auto &f : fus)
    {
        std::cout << f.get() << std::endl;
    }
}