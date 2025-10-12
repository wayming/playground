#pragma once
#include "Aggregator.h"
#include <string>

namespace LogAnalyzer {
void report_to_console(const AggregatedStats& stats);
void report_to_file(const AggregatedStats& stats, const std::string& filename);
}
