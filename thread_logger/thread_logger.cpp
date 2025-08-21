#include <iostream>
#include <string>
#include <map>
#include <set>
#include <queue>
#include <mutex>
#include <thread>
#include <chrono>
#include <functional>
#include <algorithm>
#include <sstream>
#include <random>
#include <ctime>
#include <cstdlib>
#include <thread>
#include <atomic>
#include <future>
#include <condition_variable>
#include <chrono>
#include <iomanip>

using namespace std;
enum log_level {
    DEBUG,
    INFO,
    WARNING,
    ERROR
};

map<log_level, string> log_level_to_string = {
    {DEBUG, "DEBUG"},
    {INFO, "INFO"},
    {WARNING, "WARNING"},
    {ERROR, "ERROR"}
};

// log message
class LogMessage {
    public:
        LogMessage(string message, log_level level, chrono::time_point<chrono::system_clock> timestamp, thread::id thread_id) {
            this->message = message;
            this->level = level;
            this->timestamp = timestamp;
            this->thread_id = thread_id;
        }
        string timeFormat() const {
            auto log_time = chrono::system_clock::to_time_t(timestamp);
            auto ms = chrono::duration_cast<chrono::milliseconds>(timestamp.time_since_epoch()) % 1000;
            stringstream ss;
            ss << put_time(localtime(&log_time), "%Y-%m-%d %H:%M:%S") << "." << ms.count();
            return ss.str();
        }
        string print() const {
            // format: [2025-08-21 22:14:33.123] [INFO] Starting deployment
            stringstream ss;
            ss << "[" << timeFormat() << "] [" << log_level_to_string[level] << "] [" << thread_id << "] " << message;
            return ss.str();
        }
        bool operator<(const LogMessage &other) const {
            return timestamp < other.timestamp;
        }
    private:
        string message;
        log_level level;
        chrono::time_point<chrono::system_clock> timestamp;
        thread::id thread_id;
};

// thread-safe logger
class ThreadLogger {
public:
    ThreadLogger() {}
    ~ThreadLogger() {}
    void log(LogMessage&& message) {
        lock_guard<mutex> lock(log_mutex);
        log_set.emplace(forward<LogMessage>(message));
    }

    vector<string> getOrderedLogs() {
        lock_guard<mutex> lock(log_mutex);
        vector<string> messages;
        for (const auto &log : log_set) {
            messages.push_back(log.print());
        }
        return messages;
    }
    bool messageLess(const LogMessage &a, const LogMessage &b) {
        return a < b;
    }
private:
    multiset<LogMessage> log_set;
    queue<LogMessage> log_queue;
    mutex log_mutex;
    bool stop = false;
};

// print usage
void usage() {
    cout << "Usage: ./thread_logger <level> <message> <threads> <repeat>" << endl;
    cout << "Level: ";
    for (const auto &p : log_level_to_string) {
        cout << p.second << " ";
    }
    cout << endl;
}
log_level option_to_log_level(string option) {
    for (const auto &p : log_level_to_string) {
        if (p.second == option) {
            return p.first;
        }
    }
    return DEBUG; // default to debug
}
int main(int argc, char *argv[]) {
    if (argc < 4) {
        usage();
        return 1;
    }
    string level = argv[1];
    string message = argv[2];
    int num_threads = atoi(argv[3]);
    int repeat = atoi(argv[4]);
    ThreadLogger logger;
    vector<thread> threads;
    for (int i = 0; i < num_threads; i++) {
        thread t([=, &logger]() -> void {
            srand(time(NULL));
            for (int j = 0; j < repeat; j++) {
                this_thread::sleep_for(chrono::milliseconds(rand() % 5));
                logger.log(LogMessage(message + to_string(rand()), option_to_log_level(level), chrono::system_clock::now(), this_thread::get_id()));
            }
        });
        threads.push_back(move(t));
    }
    for (auto &t : threads) {
        t.join();
    }
    this_thread::sleep_for(chrono::seconds(1));
    vector<string> logs = logger.getOrderedLogs();
    for (const auto &log : logs) {
        cout << log << endl;
    }
    return 0;   
}