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
        }
    }
    LockFreeStack(const LockFreeStack&) = delete;
    LockFreeStack(LockFreeStack&&) = delete;
    LockFreeStack& operator=(const LockFreeStack&) = delete;
    LockFreeStack& operator=(LockFreeStack&&) = delete;

    void push(int v) {
        Node* node = new Node{v, nullptr};
        Head oldHead = head.load();
        Head newHead;
        do {
            node->next = oldHead.node;
            newHead.node = node;
            newHead.tag = oldHead.tag + 1;
        } while (!head.compare_exchange_weak(oldHead, newHead, std::memory_order_release, std::memory_order_relaxed));
    }

    bool pop(int& v) {
        Head oldHead = head.load();
        Head newHead;
        do {
            if (oldHead.node == nullptr) {
                return false;
            }
            newHead.node = oldHead.node->next;
            newHead.tag = oldHead.tag + 1;
        } while (!head.compare_exchange_weak(oldHead, newHead, std::memory_order_acquire, std::memory_order_relaxed));

        v = oldHead.node->data;
        delete(oldHead.node);
        oldHead.node = nullptr;
        return true;
    }
private:
    struct Head {
        Node* node;
        uint64_t tag;
        bool operator==(const Head& other) const {
            return node == other.node && tag == other.tag;
        }
    };
    atomic<Head> head{Head{nullptr, 0}};
};