#include <thread>
#include <list>
#include <functional>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <future>
#include <iostream>

class ThreadPool
{
private:
    /* data */
    std::list<std::thread> threads_list_;
    std::queue<std::function<void()>> work_queue_;
    std::condition_variable cv_;
    std::mutex mtx_;
    bool terminate = false;
private:
    void work() {
        while (true)
        {
            std::unique_lock<std::mutex> lock(mtx_);
            cv_.wait(lock, [this](){return !work_queue_.empty() || terminate;});
            if (work_queue_.empty() && terminate) {return;}
            auto task = std::move(work_queue_.front());
            work_queue_.pop();
            lock.unlock();
            task();
        }
    }

public:
    ThreadPool(size_t size){
        for (int i = 0; i < size; i++) {
            threads_list_.emplace_back([this](){work();});
        }
    }

    ~ThreadPool() {
        shutdown();
    };

    template<class T>
    auto submit(T&& f)
    {
        using RetType = std::invoke_result_t<T>;
        auto taskPtr = std::make_shared<std::packaged_task<RetType()>>(std::forward<T>(f));
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            work_queue_.emplace([taskPtr](){(*taskPtr)();});
        }

        cv_.notify_one();
        return taskPtr->get_future();
    }

    void shutdown()
    {
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            if (terminate) return;

            terminate = true;
        }
        cv_.notify_all();

        for (auto& t : threads_list_) {
            t.join();
        }
    }
};
std::string to_upper(const std::string& input)
{
    std::string result;
    std::transform(input.begin(), input.end(), std::back_inserter(result), [](unsigned char c){return toupper(c); });
    return result;
}
int main() {
    ThreadPool threads(10);
    std::vector<std::future<std::string>> futures;
    std::string input("conver to upper ");
    for (size_t i = 0; i < 1000000; i++)
    {
        auto proms = std::make_shared<std::promise<std::string>>();
        futures.emplace_back(
            threads.submit([input, i](){return to_upper(input + std::to_string(i));}));

    }

    for (auto& f : futures) {
        std::cout << f.get() << std::endl;
    }
 
    threads.shutdown();
}