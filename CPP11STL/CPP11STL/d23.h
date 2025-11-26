#include <future>
#include <list>
#include <utility>
#include <unordered_map>
#include <mutex>
#include <tuple>
#include <chrono>
#include <algorithm>
#include <atomic>
#include <fstream>
#include <queue>
#include <future>
#include <condition_variable>


class RotateLogger {
public:
    RotateLogger(const std::string& fileName, size_t nbytes) : baseName(fileName), nbytes(nbytes) {
        fut = std::async(&RotateLogger::logWriter, this);
    }
    ~RotateLogger() {
        stop = true;
        cv.notify_one();
        try {
            fut.get();
        } catch (std::exception& e) {
            out.flush();
            std::cout << "caught: " << e.what() << std::endl;
        }
    }
    void log(std::initializer_list<std::string> messages) {
        if (stop) { std::cerr << "logger closing" << std::endl; return; }

        std::lock_guard<std::mutex> lock(mtx);
        for (auto& m : messages) {
            msgQueue.push(std::move(m));
            cv.notify_one();
        }
    }

private:
    bool logWriter() {
        file = baseName + "." + std::to_string(fileSeq);
        out.open(file, std::iostream::trunc);
        if (!out.good()) {
            throw std::runtime_error("Failed to open file " + file);
        }
        while(true) {
            std::string msg;
            {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, [this]() { return !msgQueue.empty() or stop; });
                if (stop and msgQueue.empty()) break;
                msg = msgQueue.front();
                msgQueue.pop();
            }
            
            if (out.tellp() > nbytes) rotate();
        }
        return true;
    }

    void rotate() {
        out.flush();
        out.close();
        file = nextName();
        out.open(file, std::iostream::trunc);
        if (!out.good()) {
            throw std::runtime_error("Failed to open file " + file);
        }
    }

    std::string nextName() {
        if (++fileSeq == 5) fileSeq = 0;
        return baseName + "." + std::to_string(fileSeq);
    }

private:
    std::string baseName;
    std::string file;
    size_t nbytes;
    std::atomic<int> fileSeq = 0;
    std::ofstream out;

    std::queue<std::string> msgQueue;
    std::mutex mtx;
    std::condition_variable cv;
    std::atomic<bool> stop = false;
    std::future<bool> fut;

};