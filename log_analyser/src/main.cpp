\
    #include "Parser.h"
    #include "Aggregator.h"
    #include "Reporter.h"
    #include "Filter.h"
    #include "ThreadSafeQueue.h"
    #include <iostream>
    #include <filesystem>
    #include <thread>
    #include <vector>

    using namespace LogAnalyzer;
    namespace fs = std::filesystem;

    int main() {
        ThreadSafeQueue<std::vector<LogEntry>> queue;
        std::vector<std::thread> producers;

        // spawn producer threads: parse each file concurrently
        for (auto& p : fs::directory_iterator("./logs")) {
            if (p.path().extension() == ".log") {
                producers.emplace_back([&queue, path = p.path()]() {
                    auto parsed = LogAnalyzer::parse_file(path);
                    queue.push(std::move(parsed));
                });
            }
        }

        // consumer thread: collect parsed batches
        std::vector<LogEntry> all;
        std::thread consumer([&]() {
            while (true) {
                auto opt = queue.pop();
                if (!opt) break;
                auto batch = std::move(*opt);
                std::move(batch.begin(), batch.end(), std::back_inserter(all));
            }
        });

        // wait producers, signal stop, then wait consumer
        for (auto& t : producers) t.join();
        queue.stop();
        consumer.join();

        // apply a filter: only ERROR logs
        Filter errFilter(FilterType::LEVEL, "ERROR");
        auto errorLogs = errFilter.apply(all);

        auto stats = aggregate(errorLogs);
        report_to_console(stats);
        report_to_file(stats, "report.json");

        return 0;
    }
