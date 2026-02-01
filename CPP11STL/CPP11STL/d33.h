#include <vector>

// tail point to the next solt for enqueue
template <typename T>
class LockFreeQueue {
    std::vector<T> buffer;
    size_t capacity;
    std::atomic<size_t> head = 0;
    std::atomic<size_t> tail = 0;
public:
    LockFreeQueue(size_t num) : capacity(num) { buffer.resize(capacity); }
    bool enqueue(T t) {
        //std::cout << "enqueue " << t << std::endl;
        auto pos = tail.load(std::memory_order_relaxed);
        auto next = (pos + 1) % capacity;
        // Use next to check, must ensure there is one empty slot between next and head
        // Effectively the capacity is less one.
        // This is to distinguish the empty queue scenario where tail == head
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
        if (pos == tail.load(std::memory_order_acquire)) {
            std::cout << "queue is empty" << std::endl;
            return false;
        }
        //std::cout << "dequeue " << buffer[pos] << std::endl;
        res = std::move(buffer[pos]);
        auto next = (pos + 1) % capacity;
        head.store(next, std::memory_order_release);
        return true;
    }

    // Multiple producer implementation with ABA issue unresolved.
    bool enqueueMP(T t) {
        //std::cout << "enqueue " << t << std::endl;
        auto pos = tail.load(std::memory_order_relaxed);
        size_t next;
        do {
            next = (pos + 1) % capacity;
            // Use next to check, must ensure there is one empty slot between next and head
            // Effectively the capacity is less one.
            // This is to distinguish the empty queue scenario where tail == head
            if (next == head.load(std::memory_order_acquire)) {
                std::cout << "queue is full" << std::endl;
                return false;
            }
        } while(!tail.compare_exchange_weak(pos, next, std::memory_order_release));

        buffer[pos] = std::move(t); // data racing

        return true;
    }

    // Multiple consumer implementation with ABA issue unresolved.
    bool dequeueMC(T& res) {
        auto pos = head.load(std::memory_order_relaxed);
        size_t next;
        do {
            next = (pos + 1) % capacity;
            if (pos == tail.load(std::memory_order_acquire)) {
                std::cout << "queue is empty" << std::endl;
                return false;
            }
        } while(!head.compare_exchange_weak(pos, next, std::memory_order_release));

        //std::cout << "dequeue " << buffer[pos] << std::endl;
        res = std::move(buffer[pos]); // data racing

        return true;
    }
};