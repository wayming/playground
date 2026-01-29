#include <iostream>
#include <mutex>
#include <unordered_map>
enum class LOG_LEVEL { ERROR, WARNING, INFO, DEBUG };
std::unordered_map<LOG_LEVEL, std::string> LOG_LEVEL_TEXT {
    {LOG_LEVEL::ERROR, "ERROR"},
    {LOG_LEVEL::WARNING, "WARNING"},
    {LOG_LEVEL::INFO, "INFO"},
    {LOG_LEVEL::DEBUG, "DEBUG"}
};

class ThreadSafeLogger {
    std::ostream& os;
    LOG_LEVEL lvl;
    std::mutex mtx;
public:
    ThreadSafeLogger(std::ostream& o, LOG_LEVEL l) : os(o), lvl(l) {}
    
    template<typename... Args>
    void info(Args&&... args) {
        log(LOG_LEVEL::INFO, std::forward<Args>(args)...);
    }
    template<typename... Args>
    void error(Args&&... args) {
        log(LOG_LEVEL::ERROR, std::forward<Args>(args)...);
    }
    template<typename... Args>
    void warn(Args&&... args) {
        log(LOG_LEVEL::WARNING, std::forward<Args>(args)...);
    }
    template<typename... Args>
    void debug(Args&&... args) {
        log(LOG_LEVEL::DEBUG, std::forward<Args>(args)...);
    }
    template<typename... Args>
    void log(LOG_LEVEL l, Args&&... args) {
        if (l <= lvl) {
            std::lock_guard<std::mutex> lock(mtx);
            (os << "[" << LOG_LEVEL_TEXT.at(l) << "] " << ... << args);
        }
    }
};