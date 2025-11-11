#include <thread>
#include <vector>
#include <chrono>
#include <random>
#include <iostream>

void task_runner(int n) {
    std::vector<std::thread> threads;
    threads.reserve(n);
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < n; ++i) {
        threads.emplace_back(std::thread([i](){
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_int_distribution dis(100, 500);
            auto start = std::chrono::high_resolution_clock::now();
            std::this_thread::sleep_for(std::chrono::milliseconds(dis(gen)));
            auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start);
            std::cout << "Task " << i << " is done in " << duration.count() << "ms." << std::endl;         
        }));
    }

    for (auto& t : threads) t.join();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now() - start);
    std::cout << "All tasks are done in " << duration.count() << "ms." << std::endl;         

}

int main() {
    task_runner(10);
}