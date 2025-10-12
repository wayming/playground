\
    #include "Aggregator.h"
    #include <numeric>
    #include <algorithm>

    namespace LogAnalyzer {

    AggregatedStats aggregate(const std::vector<LogEntry>& logs) {
        AggregatedStats stats;
        // count levels
        for (const auto& e : logs) {
            stats.level_count[e.level]++;
            if (e.latency_ms) stats.avg_latency[e.module] += *e.latency_ms;
        }
        // compute averages
        for (auto& kv : stats.avg_latency) {
            const std::string& mod = kv.first;
            int count = std::count_if(logs.begin(), logs.end(),
                [&](const LogEntry& le){ return le.module == mod && le.latency_ms; });
            if (count > 0) kv.second /= count;
        }
        return stats;
    }

    } // namespace LogAnalyzer
