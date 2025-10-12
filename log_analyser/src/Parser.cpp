\
    #include "Parser.h"
    #include <fstream>
    #include <regex>
    #include <iostream>

    using namespace std;
    namespace fs = std::filesystem;

    namespace LogAnalyzer {

    // Example log formats supported (simple):
    // [2025-10-12 10:00:00] ModuleA [INFO] message... latency=123ms
    // or
    // 2025-10-12 10:00:00 INFO ModuleA message... latency=123ms
    std::optional<LogEntry> parse_line(const std::string& line) {
        // Try bracketed format first
        static const std::regex re1(R"(\[(.*?)\]\s+(\\w+)\s+\[(\\w+)\\]\s+(.*))");
        static const std::regex re2(R"((\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2})\\s+(\\w+)\\s+(\\w+)\\s+(.*))");
        std::smatch m;
        LogEntry e;
        if (std::regex_match(line, m, re1)) {
            e.module = m[2];
            e.level = m[3];
            e.message = m[4];
        } else if (std::regex_match(line, m, re2)) {
            e.module = m[3];
            e.level = m[2];
            e.message = m[4];
        } else {
            return std::nullopt;
        }

        // try to parse latency like "... latency=123ms"
        std::smatch mm;
        static const std::regex lat_re(R"(latency=(\\d+(?:\\.\\d+)?)ms)");
        if (std::regex_search(e.message, mm, lat_re)) {
            try {
                e.latency_ms = std::stod(mm[1].str());
            } catch (...) { e.latency_ms = std::nullopt; }
        }

        e.timestamp = std::chrono::system_clock::now();
        return e;
    }

    std::vector<LogEntry> parse_file(const fs::path& path) {
        std::vector<LogEntry> out;
        std::ifstream in(path);
        if (!in.is_open()) {
            std::cerr << "Failed to open " << path << "\\n";
            return out;
        }
        std::string line;
        while (std::getline(in, line)) {
            if (auto e = parse_line(line)) out.push_back(std::move(*e));
        }
        return out;
    }

    } // namespace LogAnalyzer
