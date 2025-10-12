#pragma once
#include "LogEntry.h"
#include <unordered_map>
#include <string>
#include <vector>

namespace LogAnalyzer {
struct AggregatedStats {
    std::unordered_map<std::string, int> level_count;
    std::unordered_map<std::string, double> avg_latency;
};

AggregatedStats aggregate(const std::vector<LogEntry>& logs);
}
