#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <iostream>
#include <vector>
#include <memory>

struct QueueFullException : public std::exception {
    const char* what() const noexcept { return "queue full"; }
};
struct QueueClosed : public std::exception {
    const char* what() const noexcept { return "queue closed"; }
};
template <class T>
class QueueSafe
{
private:
    size_t cap_;
    std::queue<T> queue_;
    std::mutex mtx_;
    std::condition_variable cv_;
    bool done = false;
public:
    void Push(T t) {
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            if (done) {throw QueueClosed(); }
            if (queue_.size() >= cap_) {throw QueueFullException();}
            queue_.push(std::move(t));
        }
        cv_.notify_one();
    }

    T Pop() {
        {
            std::unique_lock<std::mutex> lock(mtx_);
            cv_.wait(lock, [this](){return !queue_.empty() || done;});
            if (queue_.empty() && done) {throw QueueClosed();}
            auto v = std::move(queue_.front());
            queue_.pop();
            return v;
        }
    }

    void Done() {
        {
            std::scoped_lock<std::mutex> lock(mtx_);
            done = true;
        }
        cv_.notify_all();
    }

    QueueSafe(size_t cap) : cap_(cap), done(false)
    {
    }

    ~QueueSafe()
    {
        Done();
    }
};

class Worker
{
private:
    /* data */
public:
    virtual void Run() = 0;
};

class Producer : public Worker {
private:
    std::shared_ptr<QueueSafe<int>> q_;
    size_t count_;
public:
    Producer(std::shared_ptr<QueueSafe<int>> in_queue, size_t count) : q_(in_queue), count_(count) {}
    void Run() override {
        auto next = 1;
        while (next <= count_)
        {
            try
            {
                q_->Push(next);
            }
            catch(const QueueFullException& e)
            {
                std::cout << e.what() << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
                continue;
            }
            catch(const QueueClosed& e) {
                std::cout << e.what() << std::endl;
                break;
            }
            std::cout << "enqueue " << next << std::endl;
            next++;
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }
};


class Processer : public Worker {
private:
    std::shared_ptr<QueueSafe<int>> in_q_;
    std::shared_ptr<QueueSafe<int>> out_q_;
public:
    Processer(std::shared_ptr<QueueSafe<int>> in_queue, std::shared_ptr<QueueSafe<int>> out_queue)
    : in_q_(in_queue), out_q_(out_queue) {}
    void Run() override {
        int next;
        bool full = false;
        while (true)
        {
            try
            {
                if (!full) {
                    next = in_q_->Pop();
                }
                out_q_->Push(next*next);
                full = false;
            }
            catch(const QueueClosed& e) {
                std::cout << e.what() << std::endl;
                break;
            }
            catch(const QueueFullException& e)
            {
                std::cout << e.what() << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
                full = true;
                continue;
            }
            
        }
        
    }
};

class Consumer : public Worker {
private:
    std::shared_ptr<QueueSafe<int>> in_q_;
public:
    Consumer(std::shared_ptr<QueueSafe<int>> in_queue)
        : in_q_(in_queue) {}

    void Run() override {
        double sum = 0.0;
        while (true)
        {
            try
            {
                sum += in_q_->Pop();
                std::cout << "sum = " << sum << std::endl;
            }
            catch(const QueueClosed& e) {
                std::cout << e.what() << std::endl;
                break;
            }
        }
        
    }
};


int main() {
    auto number_queue = std::make_shared<QueueSafe<int>>(1000000);
    auto power_queue = std::make_shared<QueueSafe<int>>(1000000);
    std::vector<std::thread> threads;
    for (int i = 0; i < 3; i++) {
        threads.emplace_back([number_queue](){
            Producer p(number_queue, 10000);
            p.Run();
        });
    }
    for (int i = 0; i < 2; i++) {
        threads.emplace_back([number_queue, power_queue](){
            Processer p(number_queue, power_queue);
            p.Run();
        });
    }
    threads.emplace_back([power_queue](){
        Consumer p(power_queue);
        p.Run();
    });

    // Producer done
    auto iter = threads.begin();
    for (iter; iter != std::next(threads.begin(), 3); iter++) {
        iter->join();
    }
    number_queue->Done();

    // Processor done
    iter = std::next(threads.begin(), 3);
    for (iter; iter != std::next(threads.begin(), 5); iter++) {
        iter->join();
    }
    power_queue->Done();

    // Consumer done
    std::prev(threads.end())->join();
}