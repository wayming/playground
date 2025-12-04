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
#include <tuple>
#include <chrono>
#include <thread>

class RotateLogger {
public:
    RotateLogger(const std::string& fileName, size_t nbytes) : baseFile(fileName), nbytes(nbytes) {
        out = LogStream(new std::ofstream(baseFile, std::ios::out | std::ios::trunc), OfStreamDeleter());
        if (!out->good()) throw std::runtime_error("Failed to open file " + baseFile);
        fut = std::async(&RotateLogger::logWriter, this);
    }
    ~RotateLogger() {
        stop = true;
        cv.notify_one();
        try {
            fut.get();
        } catch (std::exception& e) {
            std::cout << "caught: " << e.what() << std::endl;
        }
    }
    auto log(std::initializer_list<std::string> messages) {
        std::vector<LogFuture> futures;

        if (stop) { std::cerr << "logger closing" << std::endl; return futures; }

        std::lock_guard<std::mutex> lock(mtx);
        for (const auto& m : messages) {
            LogPromise p;
            futures.push_back(p.get_future());
            msgQueue.push(std::make_unique<LogMessage>(
                std::make_tuple(m, std::move(p), std::chrono::steady_clock::now())));
            cv.notify_one();
        }

        return futures;
    }

private:
    bool logWriter() {
        while(true) {
            std::unique_ptr<LogMessage> msg;
            {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, [this]() { return !msgQueue.empty() || stop; });
                if (stop && msgQueue.empty()) break;
                msg = std::move(msgQueue.front());
                msgQueue.pop();
            }
            *out << std::get<0>(*msg) << "\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(5)); // simulate delay
            std::get<1>(*msg).set_value(std::chrono::steady_clock::now() - std::get<2>(*msg));
            if (out->tellp() > nbytes) rotate();
        }

        return true;
    }

    void rotate() {
        if (logFiles.size() < 5) logFiles.push_back(baseFile + "." + std::to_string(logFiles.size()));
        for (int idx = logFiles.size() - 2; idx >= 0; --idx) {
            if (idx == 4) continue; // discard the last one
            // std::cout << "rename " << logFiles[idx] << " to " << logFiles[idx+1] << std::endl;
            std::rename(logFiles[idx].c_str(), logFiles[idx+1].c_str());
        }

        std::rename(baseFile.c_str(), logFiles[0].c_str());
        // std::cout << "rename " << baseFile << " to " << logFiles[0] << std::endl;

        if(out && out->is_open()) {
            out->flush();
            out->close();
        }
        out->open(baseFile, std::ios::out | std::ios::trunc);
        if (!out->good()) {
            throw std::runtime_error("Failed to open file " + baseFile);
        }
    }

private:

    struct OfStreamDeleter {
        void operator()(std::ofstream* os) const {
            if (os && os->is_open()) {
                os->flush();
                os->close();
            } 
            delete os;
        }
    };
    using LogStream = std::unique_ptr<std::ofstream, OfStreamDeleter>;
    using LogPromise = std::promise<std::chrono::steady_clock::duration>;
    using LogFuture = std::future<std::chrono::steady_clock::duration>;
    using LogMessage = std::tuple<
        std::string,
        LogPromise,
        std::chrono::steady_clock::time_point>;
    std::string baseFile;
    size_t nbytes;
    std::atomic<int> fileSeq = 0;
    std::vector<std::string> logFiles = {};
    LogStream out;

    std::queue<std::unique_ptr<LogMessage>> msgQueue = {};
    std::mutex mtx;
    std::condition_variable cv;
    std::atomic<bool> stop = false;
    std::future<bool> fut;

};