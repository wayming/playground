#include <memory>
#include <thread>
#include <iostream>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <vector>
#include <chrono>

class QueueFullException : public std::exception
{
public:
    const char* what() const noexcept { return "queue full"; }
};
template <class T>
class WorkQueueSafe
{
public:
    WorkQueueSafe(size_t cap) : _cap(cap),_running(true) {}
    ~WorkQueueSafe() { shutdown(); }

    void push(T t)
    {
        {
            std::lock_guard<std::mutex> lock(_mtx);
            if (!_running) throw std::runtime_error("queue closed");
            if (_q.size() >= _cap) throw QueueFullException();
            _q.push(std::move(t));
        }
        _cond.notify_one();
    }

    T pop() {
        std::unique_lock<std::mutex> lock(_mtx);
        _cond.wait(lock, [this](){return !this->_q.empty() || !this->_running;});
        if (_q.empty() && !_running) {throw std::runtime_error("queue closed");}
        auto val = std::move(_q.front());
        _q.pop();
        return val;
    }

    void shutdown() {
        _running = false;
        _cond.notify_all();
    }

private:
    size_t _cap;
    std::queue<T> _q;
    std::mutex _mtx;
    std::condition_variable _cond;
    std::atomic<bool> _running;

};
WorkQueueSafe<int> queueSafe(100);
void producer(size_t num) {
    try
    {
        for (int i = 0; i < num; i++) {
            try
            {
                queueSafe.push(i);
            }
            catch(const QueueFullException& e)
            {
                std::cout << e.what() << std::endl;
            }
            
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }

}

void consumer() {
    try
    {
        while (true) {
            std::cout << queueSafe.pop() << std::endl;
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }
}

int main()
{
    std::vector<std::thread> producers;
    std::vector<std::thread> consumers;
    for (int i = 0; i < 10; i++) {
        producers.emplace_back(producer, 100);
    }
    
    for (int i = 0; i < 10; i++) {
        consumers.emplace_back(consumer);
    }

    std::this_thread::sleep_for(std::chrono::seconds(5));
    queueSafe.shutdown();
    for (auto& t : producers) {
        t.join();
    }
    for (auto& t : consumers) {
        t.join();
    }

    return 0;
}
