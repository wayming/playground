#include <string>
#include <unordered_map>
#include <fstream>
#include <regex>
#include <algorithm>
#include <optional>
void trim(std::string& src) {
    auto end = src.find_last_not_of(' ');
    if (end == std::string::npos) src.clear();
    src.erase(end+1);

    auto start = src.find_first_not_of(' ');
    src.erase(0, start);
}

std::optional<std::string> extractSection(std::string& src) {
    std::regex e("\\[(.*)\\]");
    std::smatch sm;
    std::regex_match(src.cbegin(), src.cend(), sm, e);
    if (sm.size() == 1) return sm.str(0);
    return std::nullopt;
}

std::optional<std::pair<std::string, std::string>> extractConfig(std::string& src) {
    std::regex e("(\\w)\\s+=\\s+(\\w)");
    std::smatch sm;
    std::regex_match(src.cbegin(), src.cend(), sm, e);
    if (sm.size() == 2) return std::make_pair<std::string, std::string>(sm.str(0), sm.str(1));
    return std::nullopt;
}

using Config = std::unordered_map<std::string, std::unordered_map<std::string, std::string>>;
class ConfigReader {
public:
    Config parse(const std::string& file) {
        std::ifstream s(file);
        if (!s.good()) throw std::runtime_error(std::string("failed to read file ") + file);
        
        Config config;
        std::string thisSection;
        while (s.good()) {
            std::string line;
            std::getline(s, line);

            trim(line);
            if (line.empty()) continue;
            auto section = extractSection(line);
            if (section) { thisSection = section.value(); continue; }
            auto kvPair = extractConfig(line);
            if (kvPair) config[thisSection].emplace(kvPair.value());
        }

        return config;
    }
};