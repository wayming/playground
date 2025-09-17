#include "stack.hpp"
#include <atomic>
#include <thread>
#include <iostream>
#include <vector>
#include <chrono>

using namespace std;

atomic<int> count = 0;
atomic<int> push_thread_done = 0;
int main() {
    LockFreeStack stack;
    vector<thread> ts;
    for (int i = 0; i < 20; i++) {
        ts.emplace_back(thread([&stack, i]() {
            if (i % 2 == 0) {
                int j = 0;
                for (; j < 10000; j++) {
                    stack.push(i*j);
                }
                push_thread_done.fetch_add(1, std::memory_order_relaxed);
            } else {
                int v;
                bool result;
                while((result = stack.pop(v)) || push_thread_done.load(std::memory_order_relaxed) < 5) {
                    if (result) {
                        count.fetch_add(1, std::memory_order_relaxed);
                        // cout << "Pop " << v << endl;
                    } else {
                        this_thread::yield();
                    }
                }
            }
        }));
    }
    for (auto &t : ts) {
        t.join();
    }
    cout << "Count: " << count << endl;
}