#include <thread>
#include <queue>
#include <functional>
#include <chrono>
#include <vector>
#include <condition_variable>
#include <mutex>
#include <iostream>
#include <memory>
#include <map>
#include <unordered_map>

void print_steady_clock_time(const std::chrono::steady_clock::time_point time)
{
    std::cout << "now: " << std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now().time_since_epoch()).count() << std::endl;
    std::cout << "time: " << std::chrono::duration_cast<std::chrono::seconds>(time.time_since_epoch()).count() << std::endl;
}
class Scheduler
{
private:
    using TASK_ID = uint64_t;
    struct Task;

    TASK_ID next = 0;
    std::condition_variable_any cv;
    std::mutex mtx;
    std::unordered_map<TASK_ID, std::shared_ptr<Task>> id_to_task;
    std::multimap<std::chrono::steady_clock::time_point, std::shared_ptr<Task>, std::greater<>> start_time_to_task;
    struct Task
    {
        TASK_ID id;
        std::chrono::steady_clock::time_point start_time;
        std::function<void()> run;
        std::chrono::seconds every;
        std::multimap<std::chrono::steady_clock::time_point, std::shared_ptr<Task>, std::greater<>>::iterator iter{};
    };

public:
    template <class T>
    TASK_ID
    after(uint32_t after, T &&t)
    {
        TASK_ID this_id;
        {
            std::scoped_lock<std::mutex> lock(mtx);
            this_id = ++next;
            auto start = std::chrono::steady_clock::now() + std::chrono::seconds(after);
            auto task = std::make_shared<Task>(this_id, start, std::forward<T>(t), std::chrono::seconds::zero());
            task->iter = start_time_to_task.emplace(start, task);
            id_to_task[task->id] = task;
        }
        cv.notify_one();
        return this_id;
    }

    template <class T>
    TASK_ID every(uint32_t every, T &&t)
    {
        TASK_ID this_id;
        {

            std::scoped_lock<std::mutex> lock(mtx);
            this_id = ++next;
            auto start = std::chrono::steady_clock::now() + std::chrono::seconds(every);
            auto task = std::make_shared<Task>(this_id, start, std::forward<T>(t), std::chrono::seconds(every));
            task->iter = start_time_to_task.emplace(start, task);
            id_to_task[task->id] = task;
        }
        cv.notify_all();
        return this_id;
    }

    void cancel(TASK_ID id)
    {
    }

    void run(std::stop_token stop)
    {
        while (!stop.stop_requested())
        {
            std::shared_ptr<Task> task;
            {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, stop, [this, &stop]()
                        { return !start_time_to_task.empty() || stop.stop_requested(); });

                if (stop.stop_requested())
                {
                    break;
                }

                if (!start_time_to_task.empty())
                {
                    auto start_time = start_time_to_task.begin()->first;
                    cv.wait_until(lock, stop, start_time, [this]()
                                  { return start_time_to_task.empty() || start_time_to_task.begin()->first < std::chrono::steady_clock::now(); });
                }
                if (!start_time_to_task.empty())
                {
                    auto nh = start_time_to_task.extract(start_time_to_task.begin());
                    task = std::move(nh.mapped());
                    id_to_task.erase(task->id);
                }
            }

            // print_steady_clock_time(task->start_time);
            try
            {
                if (task)
                {
                    task->run();
                    if (task->every > std::chrono::seconds::zero())
                    {
                        task->start_time = task->start_time + task->every;
                        // print_steady_clock_time(task->start_time);
                        {
                            std::scoped_lock<std::mutex> lock(mtx);
                            start_time_to_task.emplace(task->start_time, std::move(task));
                        }
                    }
                }
            }
            catch (const std::exception &e)
            {
                std::cerr << e.what() << '\n';
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
    producers.emplace_back([&sch]()
                           {
                                auto tid = std::this_thread::get_id();
                                sch.every(1, [tid]()
                                           { std::cout << tid << " at " << std::chrono::system_clock::now() << std::endl; }); });

    std::this_thread::sleep_for(std::chrono::seconds(15));
    worker.get_stop_source().request_stop();

    for (auto &t : producers)
    {
        t.join();
    }
    worker.join();
    return 0;
}