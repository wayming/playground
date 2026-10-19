#include <fstream>
#include <string_view>
#include <format>
#include <iostream>
#include <ranges>
#include <cstdint>
#include <unordered_map>
struct stats
{
    uint32_t cout{0};
    uint64_t avg{0};
};
struct Log
{
    std::string ts;
    std::string ip;
    std::string url;
    uint32_t status;
    uint64_t ms;
};
std::unordered_map<std::string, stats> parse(const std::string &file)
{
    std::unordered_map<std::string, stats> results;
    std::ifstream cvs_file(file, std::ios::in);
    if (!cvs_file.is_open())
    {
        throw std::runtime_error(std::format("Failed to open file {}", file));
    }
    Log row;
    for (std::string line; std::getline(cvs_file, line);)
    {
        auto tokens = std::views::split(line, ',');
        if (std::ranges::distance(tokens.begin(), tokens.end()) != 5)
        {
            throw std::runtime_error(std::format("Invalid row - {}", line));
        }
        auto iter = tokens.begin();
        std::ranges::advance(iter, 2);
        std::string url;
        if (iter != tokens.end())
        {
            auto subrange = *iter;
            url = std::string(subrange.begin(), subrange.end());
        }

        if (++iter != tokens.end())
        {
            auto subrange = *iter;
            auto status = std::stoi(std::string(subrange.begin(), subrange.end()));
            if (status < 500)
            {
                continue;
            }
        }
        if (++iter != tokens.end())
        {
            auto subrange = *iter;
            auto latency = std::stoi(std::string(subrange.begin(), subrange.end()));
            results[url].avg = (results[url].avg * results[url].cout + latency) / (results[url].cout + 1);
            results[url].cout++;
            std::cout << url << " " << results[url].cout << " " << results[url].avg << std::endl;
        }
    }

    return results;
}

int main()
{
    for (const auto &record : parse("d11.csv"))
    {
        std::cout << record.first << " " << record.second.cout << " " << record.second.avg << std::endl;
    }
}