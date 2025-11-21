#include <iostream>
#include <mutex>
#include <unordered_map>
enum class LOG_LEVEL {ERROR, WARN, INFO, DEBUG};
std::unordered_map<LOG_LEVEL, std::string> LOG_LEVEL_STR =
{
    {LOG_LEVEL::ERROR, "ERROR"},
    {LOG_LEVEL::WARN,  "WARN"},
    {LOG_LEVEL::INFO,  "INFO"},
    {LOG_LEVEL::DEBUG, "DEBUG"}
};

class ThreadSafeLogger {
public:
    ThreadSafeLogger(std::ostream& s, LOG_LEVEL l) : out(s), lvl(l) {}
    
    template <typename... ARGS>
    void logInfo(ARGS&&... args) {
        log(LOG_LEVEL::INFO, std::forward<ARGS>(args)...);
    }

    template <typename... ARGS>
    void logDebug(ARGS&&... args) {
        log(LOG_LEVEL::DEBUG, std::forward<ARGS>(args)...);
    }

    template <typename... ARGS>
    void log(LOG_LEVEL l, ARGS&&... args) {
        if (l > lvl) {
            return;
        }

        std::lock_guard<std::mutex> lock(mtx);
        out << LOG_LEVEL_STR[l] << " ";
        (out << ... << args);
        out << std::endl;
    }


private:
    std::ostream& out;
    LOG_LEVEL lvl;
    std::mutex mtx;
};