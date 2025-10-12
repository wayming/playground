#pragma once
#include "LogEntry.h"
#include <string>
#include <vector>
#include <optional>
#include <filesystem>

namespace LogAnalyzer {
std::optional<LogEntry> parse_line(const std::string& line);
std::vector<LogEntry> parse_file(const std::filesystem::path& path);
}
