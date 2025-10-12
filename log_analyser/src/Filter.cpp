\
    #include "Filter.h"
    #include <algorithm>

    namespace LogAnalyzer {

    Filter::Filter(FilterType type, std::string pattern)
        : type_(type), pattern_(std::move(pattern)) {}

    std::vector<LogEntry> Filter::apply(const std::vector<LogEntry>& logs) const {
        std::vector<LogEntry> result;
        result.reserve(logs.size());
        std::copy_if(logs.begin(), logs.end(), std::back_inserter(result),
            [&](const LogEntry& e) {
                switch (type_) {
                    case FilterType::LEVEL:
                        return e.level == pattern_;
                    case FilterType::MODULE:
                        return e.module == pattern_;
                    case FilterType::MESSAGE_CONTAINS:
                        return e.message.find(pattern_) != std::string::npos;
                }
                return false;
            });
        return result;
    }

    } // namespace LogAnalyzer
