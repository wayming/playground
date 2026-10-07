#include <filesystem>
#include <iostream>
#include <queue>
#include <thread>
#include <future>
#include <semaphore>
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <optional>
#include <random>

struct CalcResult
{
    std::string name;
    uint64_t size;
};
class CalcFailureException : public std::exception
{
    std::string message_;

public:
    explicit CalcFailureException(const std::string &file, const std::string &reason) : message_((std::string("Failed to calc size for file ") + file + std::string(", reason: ") + reason)) {}
    const char *what() const noexcept override
    {
        return message_.c_str();
    }
};

CalcResult calc_size(const std::string &path)
{
    thread_local std::random_device rd;
    thread_local std::mt19937 gen(rd());
    thread_local std::uniform_int_distribution<int> dist(1, 100);
    try
    {
        auto len = std::filesystem::file_size(path);
        std::this_thread::sleep_for(std::chrono::milliseconds(dist(gen)));
        return CalcResult{path, len};
    }
    catch (const std::exception &e)
    {
        throw CalcFailureException(path, std::string(e.what()));
    }
}

class MTFileProcessor
{
private:
    static constexpr size_t MAX_CONCURR = 10;
    std::queue<std::packaged_task<CalcResult()>> tasks_;
    std::vector<std::thread> threads_;
    std::counting_semaphore<MAX_CONCURR> throating_;
    std::mutex mtx_;
    std::mutex mtxstart_;
    std::condition_variable cv_;
    std::condition_variable cvstart_;
    bool completed_{false};
    bool started_{false};

public:
    MTFileProcessor(size_t threads_count)
        : throating_(MAX_CONCURR)
    {
        for (size_t i = 0; i < threads_count; i++)
        {
            threads_.emplace_back(&MTFileProcessor::process, this);
        }
    }

    ~MTFileProcessor()
    {
        stop();
        for (auto &t : threads_)
        {
            t.join();
        }
    }

    void process()
    {
        {
            std::unique_lock<std::mutex> lock(mtxstart_);
            cvstart_.wait(lock, [this]()
                          { return started_; });
            lock.unlock();
        }

        while (true)
        {
            std::unique_lock<std::mutex> lock(mtx_);
            cv_.wait(lock, [this]()
                     { return !tasks_.empty() || completed_; });
            if (tasks_.empty() && completed_)
            {
                lock.unlock();
                break;
            }
            auto task = std::move(tasks_.front());
            tasks_.pop();
            lock.unlock();
            throating_.acquire();
            task();
            throating_.release();
        }
    }
    void stop()
    {
        start();
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            completed_ = true;
        }
        cv_.notify_all();
    }
    void start()
    {
        {
            std::scoped_lock<std::mutex> lock(mtxstart_);
            started_ = true;
        }
        cvstart_.notify_all();
    }
    std::optional<std::future<CalcResult>> submit(const std::string &dir)
    {
        auto task = std::packaged_task<CalcResult()>(
            [dir]()
            { return calc_size(dir); });
        auto f = task.get_future();
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            if (completed_)
            {
                return std::nullopt;
            }

            tasks_.emplace(std::move(task));
        }
        cv_.notify_one();

        return f;
    }
};
std::vector<std::future<CalcResult>> consumer(MTFileProcessor &processor, const std::string &dir)
{
    std::vector<std::future<CalcResult>> futures;
    std::error_code ec;
    std::filesystem::recursive_directory_iterator it(dir, std::filesystem::directory_options::skip_permission_denied, ec), end;
    for (; it != end && !ec; it.increment(ec))
    {
        std::error_code fec;
        if (!it->is_regular_file(fec) || fec)
        {
            if (fec)
            {
                std::cout << "skip file " << it->path() << ", error=" << fec.message() << std::endl;
            }
            continue;
        }
        if (auto fu = processor.submit(it->path().string()); fu)
        {
            futures.emplace_back(std::move(fu.value()));
        }
        else
        {
            std::cout << "processor stopped, task draining" << std::endl;
            break;
        }
    }
    if (ec)
    {
        std::cout << "directory iteration error: " << ec.message();
    }
    return futures;
}
int main()
{
    MTFileProcessor processor(20);
    processor.start();
    auto fus = consumer(processor, "..");
    processor.stop();
    for (auto &f : fus)
    {
        try
        {
            auto r = f.get();
            std::cout << r.name << "-" << r.size << std::endl;
        }
        catch (const std::exception &e)
        {
            std::cerr << "future error: " << e.what() << '\n';
        }
    }
}