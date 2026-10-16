#include <thread>
#include <queue>
#include <functional>
#include <chrono>
#include <vector>
#include <condition_variable>
#include <mutex>
#include <iostream>

using TASK_ID = uint64_t;
struct Task
{
    TASK_ID id;
    std::chrono::steady_clock::time_point start_time;
    std::function<void()> run;
    std::chrono::seconds every;
};

// std::string time_point_to_str(const std::chrono::time_point& time) {

// }
class Scheduler
{
private:
    std::priority_queue<Task, std::vector<Task>, decltype([](const auto &t1, const auto &t2)
                                                          { return t1.id < t2.id; })>
        task_queue;
    TASK_ID next = 0;
    std::condition_variable_any cv;
    std::mutex mtx;

public:
    template <class T>
    TASK_ID after(uint32_t after, T &&t)
    {
        std::scoped_lock<std::mutex> lock(mtx);
        auto this_id = ++next;
        task_queue.emplace(
            Task{this_id, std::chrono::steady_clock::now() + std::chrono::seconds(after), std::forward<T>(t), std::chrono::seconds::zero()});

        return this_id;
    }

    template <class T>
    TASK_ID every(uint32_t every, T &&t)
    {
        std::scoped_lock<std::mutex> lock(mtx);
        auto this_id = ++next;
        task_queue.emplace(
            Task{this_id, std::chrono::steady_clock::now() + std::chrono::seconds(every), std::forward<T>(t), every});

        return this_id;
    }

    void run(std::stop_token stop)
    {
        while (!stop.stop_requested() || !task_queue.empty())
        {
            Task task;
            {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, stop, [this, &stop]()
                        { return !task_queue.empty() || stop.stop_requested(); });

                if (!task_queue.empty())
                {
                    task = std::move(task_queue.top());
                    task_queue.pop();
                }
            }

            auto seconds_to_run = std::chrono::duration_cast<std::chrono::seconds>(task.start_time - std::chrono::steady_clock::now());
            if (seconds_to_run > std::chrono::seconds::zero())
            {
                std::cout << "sleep " << seconds_to_run << std::endl;
                std::this_thread::sleep_for(seconds_to_run);
            }
            task.run();
            if (task.every > std::chrono::seconds::zero())
            {
                task.start_time = std::chrono::steady_clock::now() + task.every;
                {
                    std::scoped_lock<std::mutex> lock(mtx);
                    task_queue.emplace(std::move(task));
                }
            }
        }
    }
};

int main()
{
    Scheduler sch;
    auto worker = std::jthread([&sch](std::stop_token stop)
                               { sch.run(stop); });

    std::vector<std::thread> producers;
    for (size_t i = 0; i < 10; i++)
    {
        producers.emplace_back([i, &sch]()
                               { 
                                auto tid = std::this_thread::get_id(); 
                                sch.after(i, [tid]()
                                           { std::cout << tid << " at " << std::chrono::system_clock::now() << std::endl; }); });
    }

    worker.get_stop_source().request_stop();

    for (auto &t : producers)
    {
        t.join();
    }
    worker.join();
    return 0;
}