#include <iostream>
#include <source_location>
#include <format>
#include <vector>
#include <string_view>
#include <functional>
#include <fstream>
#include <memory>
#include <string>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <sstream>
template <class... Args>
std::string message(std::format_string<Args...> fmt, Args &&...args)
{
    return std::format(fmt, std::forward<Args>(args)...);
}

class Logger;
template <class T>
concept NotLogger = !std::same_as<std::remove_cvref_t<T>, Logger>;

class Logger
{
    std::function<void(std::string_view)> log_;

public:
    // template <class T, class U = std::remove_cvref_t<T>>
    //    requires(!std::is_same<U, Logger>)
    template <NotLogger T>
    explicit Logger(T &&t)
    {
        using U = std::remove_cvref_t<T>;
        auto obj = std::make_shared<U>(std::forward<T>(t));
        log_ = [obj](std::string_view s)
        { obj->log(s); };
    }
    void log(std::string_view s) { log_(s); }
};
class StandardLogger
{
public:
    void log(std::string_view s) { std::cout << s << std::endl; }
};
class FileLogger
{
    std::ofstream ofs;

public:
    explicit FileLogger(const std::string &name) : ofs(name) {}
    void log(std::string_view s)
    {
        ofs << s << std::endl;
    }
};

class LogHub
{
private:
    std::queue<std::string> messages_;
    std::mutex mtx_;
    std::condition_variable cv_;
    bool stop_ = false;
    std::vector<Logger> loggers_;

public:
    LogHub(/* args */)
    {
        loggers_.emplace_back(Logger(StandardLogger()));
        loggers_.emplace_back(Logger(FileLogger("d1.log")));
        loggers_.emplace_back(Logger(FileLogger("d2.log")));
    }
    ~LogHub() = default;
    void submit(std::string &&msg)
    {
        {
            std::scoped_lock lock(mtx_);
            if (stop_)
            {
                std::cout << "logging hub stopped" << std::endl;
                return;
            }
            messages_.emplace(std::move(msg));
        }
        cv_.notify_one();
    }
    void run()
    {
        while (true)
        {
            std::unique_lock<std::mutex> lock(mtx_);
            cv_.wait(lock, [this]()
                     { return !messages_.empty() || stop_; });
            if (messages_.empty() && stop_)
            {
                std::cout << "complete and exit" << std::endl;
                return;
            }
            std::string msg(std::move(messages_.front()));
            messages_.pop();
            lock.unlock();
            for (auto &logger : loggers_)
            {
                logger.log(std::string_view(msg));
            }
        }
    }
    void shutdown()
    {
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            stop_ = true;
        }
        cv_.notify_all();
    }
};

void produce_messages(LogHub &hub, size_t count)
{
    std::source_location loc = std::source_location::current();
    std::stringstream ss;
    ss << std::this_thread::get_id();
    for (size_t i = 0; i < count; i++)
    {
        hub.submit(message("Thread [{}]: Error {} at line {}, file {}, func()",
                           ss.str(), i, loc.line(), loc.file_name(), loc.function_name()));
        std::this_thread::sleep_for(std::chrono::nanoseconds(i * 100));
    }
}
int main()
{
    LogHub hub;
    auto hub_thread = std::thread(&LogHub::run, &hub);

    std::vector<std::thread> threads;
    for (size_t i = 0; i < 10; i++)
    {
        threads.emplace_back(produce_messages, std::ref(hub), 1000);
    }

    for (auto &t : threads)
    {
        t.join();
    }
    hub.shutdown();
    hub_thread.join();
    return 0;
}