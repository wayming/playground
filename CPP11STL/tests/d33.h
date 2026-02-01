#include <vector>

template <typename T>
class LockFreeQueue {
    std::vector<T> buffer;
    size_t capacitiy;
    std::atomic<size_t> head = 0;
    std::atomic<size_t> tail = 0;
public:
    LockFreeQueue(size_t num) : capacity(num), buffer.reserve(capacity) {}
    bool enqueue(T t) {
        auto pos = tail.load(std::memory_order_relaxed);
        auto next = (pos + 1) % capacity;
        if (next == head.load(std::memory_order_acquire)) {
            std::cout << "queue is full" << std::endl;
            return false;
        }
        buffer[pos] = std::move(t);
        tail.store(next, std::memory_order_release);
        return true;
    }
    bool dequeue(T& res) {
        auto pos = head.load(std::memory_order_relaxed);
        auto next = (pos + 1) % capacity;
        if (next == tail.load(std::memory_order_acquire)) {
            std::cout << "queue is empty" << std::endl;
            return false;
        }
        res = std::move(buffer[pos]);
        head.store(next, std::memory_order_release);
    }
};