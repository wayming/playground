#include <atomic>
#include <memory>

using namespace std;

struct Node {
    int data;
    Node* next;
};

class LockFreeStack {
public:
    LockFreeStack() {}
    ~LockFreeStack() {
        int v;
        while(pop(v)) {
            1;
        }
    }
    LockFreeStack(const LockFreeStack&) = delete;
    LockFreeStack(const LockFreeStack&&) = delete;
    LockFreeStack& operator=(const LockFreeStack&) = delete;
    LockFreeStack& operator=(const LockFreeStack&&) = delete;

    void push(int v) {
        Node* newHead = new Node{v, nullptr};
        Node* oldHead = head.load();
        do {
            newHead->next = oldHead;
        } while (!head.compare_exchange_weak(oldHead, newHead, std::memory_order_release, std::memory_order_relaxed));
    }

    bool pop(int& v) {
        Node* oldHead = head.load();
        Node* newHead = nullptr;
        do {
            if (oldHead != nullptr) {
                newHead = oldHead->next;
            }
        } while (!head.compare_exchange_weak(oldHead, newHead, std::memory_order_acquire, std::memory_order_relaxed));

        if (oldHead == nullptr) {
            return false;
        }

        v = oldHead->data;
        // delete(oldHead);
        oldHead = nullptr;
        return true;
    }
private:
    atomic<Node*> head;
};