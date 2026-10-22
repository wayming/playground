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
#include <optional>

struct Stats
{
    uint32_t count{0};
    uint64_t total{0};
};
struct Record
{
    std::string_view ts;
    std::string_view ip;
    std::string_view url;
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

struct Line
{
    std::string s;
    friend std::istream &operator>>(std::istream &is, Line &line)
    {
        return std::getline(is, line.s);
    }
};

using StatsMap = std::unordered_map<std::string, std::shared_ptr<Stats>, StringHash, std::equal_to<void>>;
std::optional<Record> parse_line(const Line &line)
{
    Record rec;
    std::string_view line_str = std::string_view(line.s);
    auto tokens = std::views::split(line_str, ',');
    if (std::ranges::distance(tokens.begin(), tokens.end()) != 5)
    {
        return std::nullopt;
    }
    auto it = tokens.begin();
    auto end = tokens.end();
    auto get = [&it, &end]() -> std::optional<std::string_view>
    {
        if (it == end)
        {
            return std::nullopt;
        }
        auto sub = *it;
        it++;
        return std::string_view(sub.begin(), sub.end());
    };
    auto get_int = [&get]<typename T>(T) -> std::optional<T>
    {
        T t;
        auto v = get();
        if (v)
        {
            auto field = v.value();

            auto [p, ec] = std::from_chars(field.begin(), field.end(), t);
            if (ec != std::errc{})
            {
                return std::nullopt;
            }
            return t;
        }
        else
        {
            return std::nullopt;
        }
    };
    if (auto v = get(); v)
    {
        rec.ts = v.value();
    }
    if (auto v = get(); v)
    {
        rec.ip = v.value();
    }
    if (auto v = get(); v)
    {
        rec.url = v.value();
    }
    if (auto v = (get_int(uint32_t{})); v)
    {
        rec.status = v.value();
    }
    if (auto v = (get_int(uint64_t{})); v)
    {
        rec.ms = v.value();
    }
    return rec;
}

StatsMap parse2(const std::string &file)
{
    StatsMap results;
    auto fs = std::ifstream(file);
    if (!fs.is_open())
    {
        throw std::runtime_error(std::format("Failed to open file {}", file));
    }
    // auto recs = std::views::istream<Line>(fs) |
    //             std::views::filter([](auto &&r)
    //                                { return !r.s.empty() && r.s.front() != '#'; }) |
    //             std::views::transform(parse_line) |
    //             std::views::filter([](auto &&r)
    //                                { return r && r.value().status >= 500; }) |
    //             std::views::transform([](auto &&r)
    //                                   { return r.value(); });
    // std::ranges::for_each(recs, [&results](const Record &rec)
    //                       {
    //                           auto [p, inserted] =
    //                               results.try_emplace(std::string(rec.url), std::make_shared<Stats>(1, rec.ms));
    //                         if (!inserted) {
    //                             p->second->count++;
    //                             p->second->total += rec.ms;
    //                         } });
    auto recs = std::views::istream<Line>(fs) |
                std::views::transform([&results](auto &&r) -> std::optional<std::pair<std::string, std::shared_ptr<Stats>>>
                                      {
                                  if (r.s.empty() || r.s.front() == '#')
                                  {
                                      return std::nullopt;
                                  }
                                  auto rec = parse_line(r);
                                  if (!rec || rec.value().status < 500)
                                  {
                                      return std::nullopt;
                                  }
                                  return std::pair(std::string(rec.value().url), std::make_shared<Stats>(1, rec.value().ms)); });

    std::ranges::for_each(recs, [&results](auto &&r)
                          {
        if (!r) {
            return;
        }
        auto iter = results.find(r.value().first);
        if (iter == results.end()) {
            results.emplace(std::move(r.value()));
        }else {
            iter->second->count++;
            iter->second->total += r.value().second->total;
        } });
    return results;
}

StatsMap parse(const std::string &file)
{
    StatsMap results;
    std::ifstream cvs_file(file, std::ios::in);
    if (!cvs_file.is_open())
    {
        throw std::runtime_error(std::format("Failed to open file {}", file));
    }
    Record row;
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
    top_n(parse2("d11.csv"), 5);
}