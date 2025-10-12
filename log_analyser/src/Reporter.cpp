\
    #include "Reporter.h"
    #include <iostream>
    #include <fstream>
    #include <sstream>
    #include <iomanip>

    namespace LogAnalyzer {

    void report_to_console(const AggregatedStats& stats) {
        std::cout << "=== Log Level Count ===\n";
        for (const auto& kv : stats.level_count) {
            std::cout << kv.first << ": " << kv.second << "\n";
        }
        std::cout << "\n=== Avg Latency (ms) ===\n";
        for (const auto& kv : stats.avg_latency) {
            std::ostringstream oss;
            oss << std::fixed << std::setprecision(2) << kv.second;
            std::cout << kv.first << ": " << oss.str() << "\n";
        }
    }

    void report_to_file(const AggregatedStats& stats, const std::string& filename) {
        std::ofstream out(filename);
        if (!out.is_open()) {
            std::cerr << "Failed to open " << filename << "\n";
            return;
        }
        out << "{\n  \"levels\": {\n";
        for (auto it = stats.level_count.begin(); it != stats.level_count.end(); ++it) {
            out << "    \"" << it->first << "\": " << it->second;
            if (std::next(it) != stats.level_count.end()) out << ",";
            out << "\n";
        }
        out << "  },\n  \"avg_latency\": {\n";
        for (auto it = stats.avg_latency.begin(); it != stats.avg_latency.end(); ++it) {
            out << "    \"" << it->first << "\": " << std::fixed << std::setprecision(2) << it->second;
            if (std::next(it) != stats.avg_latency.end()) out << ",";
            out << "\n";
        }
        out << "  }\n}\n";
    }

    } // namespace LogAnalyzer
