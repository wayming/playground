#pragma once
#include "LogEntry.h"
#include <vector>
#include <functional>

namespace LogAnalyzer {

enum class FilterType { LEVEL, MODULE, MESSAGE_CONTAINS };

class Filter {
public:
    explicit Filter(FilterType type, std::string pattern);
    std::vector<LogEntry> apply(const std::vector<LogEntry>& logs) const;

private:
    FilterType type_;
    std::string pattern_;
};

}  // namespace LogAnalyzer
