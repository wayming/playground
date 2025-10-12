#pragma once
#include <string>
#include <optional>
#include <chrono>

struct LogEntry {
    std::chrono::system_clock::time_point timestamp;
    std::string module;
    std::string level;   // e.g. INFO, WARN, ERROR
    std::string message;
    std::optional<double> latency_ms; // optional latency value if present in log

    LogEntry() = default;
};
