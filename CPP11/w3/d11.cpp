#include <fstream>
#include <string_view>
#include <format>
#include <iostream>
#include <ranges>
#include <cstdint>
#include <unordered_map>
#include <algorithm>
#include <vector>
#include <math.h>
#include <memory>
#include <charconv>

struct Stats
{
    uint32_t count{0};
    uint64_t total{0};
};
struct Log
{
    std::string ts;
    std::string ip;
    std::string url;
    uint32_t status;
    uint64_t ms;
};

struct StringHash
{
    using is_transparent = void;
    std::size_t operator()(std::string_view sv) const
    {
        return std::hash<std::string_view>{}(sv);
    }
};

using StatsMap = std::unordered_map<std::string, std::shared_ptr<Stats>, StringHash, std::equal_to<void>>;
StatsMap parse(const std::string &file)
{
    StatsMap results;
    std::ifstream cvs_file(file, std::ios::in);
    if (!cvs_file.is_open())
    {
        throw std::runtime_error(std::format("Failed to open file {}", file));
    }
    Log row;
    for (std::string line; std::getline(cvs_file, line);)
    {
        if (line.empty() || line.front() == '#')
        {
            continue;
        }
        if (line.back() == '\r')
        {
            line.pop_back();
        }
        auto tokens = std::views::split(line, ',');
        if (std::ranges::distance(tokens.begin(), tokens.end()) != 5)
        {
            throw std::runtime_error(std::format("Invalid row - {}", line));
        }

        auto iter = tokens.begin();

        // url
        iter = tokens.begin();
        std::ranges::advance(iter, 2);
        std::string_view url;
        if (iter != tokens.end())
        {
            auto subrange = *iter;
            url = std::string_view(subrange.begin(), subrange.end());
        }

        // status
        std::ranges::advance(iter, 1);
        {
            auto subrange = *iter;
            uint32_t status;
            std::string_view sv(subrange.begin(), subrange.end());
            auto [p, ec] = std::from_chars(sv.begin(), sv.end(), status);
            if (ec != std::errc{})
            {
                continue;
            }
            if (status < 500)
            {
                continue;
            }
        }

        // latency
        std::ranges::advance(iter, 1);
        uint64_t latency = 0;
        if (iter != tokens.end())
        {
            auto subrange = *iter;
            std::string_view sv(subrange.begin(), subrange.end());
            auto [p, ec] = std::from_chars(sv.begin(), sv.end(), latency);
            if (ec != std::errc{})
            {
                continue;
            }
        }

        auto [stats_ptr, inserted] = results.try_emplace(std::string(url));
        if (inserted)
        {
            stats_ptr->second = std::make_shared<Stats>(1, latency);
        }
        else
        {
            stats_ptr->second->total += latency;
            stats_ptr->second->count++;
        }
    }

    return results;
}

void top_n(const StatsMap &stats, size_t n)
{

    n = std::min(n, stats.size());
    if (n == 0)
    {
        return;
    }
    std::vector<std::pair<std::string_view, std::shared_ptr<Stats>>> keys;
    for (const auto &[key, val] : stats)
    {
        keys.emplace_back(key, val);
    }
    auto nth = keys.begin() + n;
    std::ranges::partial_sort(keys.begin(), nth, keys.end(), std::ranges::greater{}, [](const auto &item)
                              { return item.second->count; });
    for (auto it = keys.begin(); it < nth; ++it)
    {

        std::cout << it->first << " count=" << it->second->count
                  << " avg=" << (it->second->total / it->second->count) << std::endl;
    }
}
int main()
{
    top_n(parse("d11.csv"), 5);
}