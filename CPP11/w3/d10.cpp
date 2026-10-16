#include <thread>
#include <queue>
#include <functional>
#include <chrono>
#include <vector>
#include <condition_variable>
#include <mutex>

using TASK_ID = uint64_t;
struct Task
{
    TASK_ID id;
    std::chrono::steady_clock::time_point start_time;
    std::function<void()> run;
    std::chrono::seconds every;
};

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
        auto this_id = ++next;
        task_queue.emplace(
            Task{this_id, std::chrono::steady_clock::now() + std::chrono::seconds(after), std::forward<T>, 0});

        return this_id;
    }

    template <class T>
    TASK_ID every(uint32_t every, T &&t)
    {
        auto this_id = ++next;
        task_queue.emplace(
            Task{this_id, std::chrono::steady_clock::now() + std::chrono::seconds(every), std::forward<T>, every});

        return this_id;
    }

    void run(std::stop_token stop)
    {
        while (!stop.stop_requested() || !task_queue.empty())
        {
            std::unique_lock<std::mutex> lock(mtx);
            cv.wait(lock, stop, [this, &stop]()
                    { return !task_queue.empty() || stop.stop_requested(); });

            Task task;
            if (!task_queue.empty())
            {
                task = std::move(task_queue.top());
                task_queue.pop();
            }

            auto seconds_to_run = std::chrono::duration_cast<std::chrono::seconds>(task.start_time - std::chrono::steady_clock::now());
            if (seconds_to_run > std::chrono::seconds::zero())
            {
                std::this_thread::sleep_for(seconds_to_run);
            }
            task.run();
            if (task.every > std::chrono::seconds::zero())
            {
                task.start_time = std::chrono::steady_clock::now() + task.every;
                task_queue.emplace(std::move(task));
            }
        }
    }
};

int main()
{
    return 0;
}