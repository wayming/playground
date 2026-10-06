#include <filesystem>
#include <iostream>
#include <queue>
#include <thread>
#include <future>
#include <semaphore>
#include <ifstream>
class CalcFailureException : public std::exception
{
    std::string file_;

public:
    CalcFailureException(const std::string &file) : file_(file) {}
    const char *what()
    {
        return "Failed to calc size for file " + file_;
    }
};
class MTFileProcessor
{
private:
    /* data */
    std::queue<std::packaged_task<size_t()>> tasks_;
    std::vector<std::thread> threads_;
    std::counting_semaphore throating_;

public:
    MTFileProcessor::MTFileProcessor(size_t threads_count, size_t parallel) : throating_(parallel)
    {
        for (size_t i = 0; i < threads_count; i++)
        {
            threads_.emplace_back(&MTFileProcessor::process, this);
        }
    }

    MTFileProcessor::~MTFileProcessor()
    {
    }

    void process()
    {
        while (true)
        {
            tasks_.front()();
            tasks_.pop();
        }
    }

    future<size_t> submit(const std::string &dir)
    {
        auto task = std::packaged_task<size_t()>([std::move(f.path().string())]()
                                                 { return calc_size(f); });
        auto f = task.get_future();
        tasks_.emplace(std::move(task));
        return f;
    }
};
size_t calc_size(const std::string &path)
{
    std::ifstream s(path);
    if (!s.good())
    {
        throw CalcFailureException(path);
    }
    s.seekg(std::iostream::end);
    return s.tellg();
}
std::vector<future<size_t>> consumer(MTFileProcessor processor, const std::string &dir)
{
    std::vector<future<size_t>> futures;
    for (auto &f : std::filesystem::recursive_directory_iterator("../.."))
    {
        futures.emplace_back(processor.submit(f.path().string()));
    }
    return futures;
}
int main()
{
}