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

void print_steady_clock_time(const std::chrono::steady_clock::time_point time)
{
    std::cout << "now: " << std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now().time_since_epoch()).count() << std::endl;
    std::cout << "time: " << std::chrono::duration_cast<std::chrono::seconds>(time.time_since_epoch()).count() << std::endl;
}
class Scheduler
{
private:
    std::priority_queue<Task, std::vector<Task>, decltype([](const auto &t1, const auto &t2)
                                                          { return t1.start_time > t2.start_time; })>
        task_queue;
    TASK_ID next = 0;
    std::condition_variable_any cv;
    std::mutex mtx;

public:
    template <class T>
    TASK_ID after(uint32_t after, T &&t)
    {
        TASK_ID this_id;
        {
            std::scoped_lock<std::mutex> lock(mtx);
            this_id = ++next;
            task_queue.emplace(
                Task{this_id, std::chrono::steady_clock::now() + std::chrono::seconds(after), std::forward<T>(t), std::chrono::seconds::zero()});
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
            task_queue.emplace(
                Task{this_id, std::chrono::steady_clock::now() + std::chrono::seconds(every), std::forward<T>(t), std::chrono::seconds(every)});
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
            Task task;
            {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, stop, [this, &stop]()
                        { return !task_queue.empty() || stop.stop_requested(); });

                if (stop.stop_requested())
                {
                    break;
                }
                if (!task_queue.empty())
                {
                    task = task_queue.top();
                }
                if (task.start_time > std::chrono::steady_clock::now())
                {
                    cv.wait_until(lock, stop, task.start_time, [this]()
                                  { return task_queue.empty() || task_queue.top().start_time < std::chrono::steady_clock::now(); });
                }
                if (!task_queue.empty())
                {
                    task = task_queue.top();
                    task_queue.pop();
                }
            }

            // print_steady_clock_time(task.start_time);
            try
            {
                task.run();
            }
            catch (const std::exception &e)
            {
                std::cerr << e.what() << '\n';
            }

            if (task.every > std::chrono::seconds::zero())
            {
                task.start_time = task.start_time + task.every;
                // print_steady_clock_time(task.start_time);
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