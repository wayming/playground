#include <string>
#include <unordered_map>
#include <fstream>
#include <regex>
#include <algorithm>

std::string trim(const std::string& src) {
    auto begin = src.find_first_not_of(' ');
    if (begin == std::string::npos) return "";
    
    auto end = src.find_last_not_of(' ');
    if (end == std::string::npos) return "";

    return src.substr(begin, end-begin+1);
}

void trim(std::string& str) {
    auto notSpace = [](char c) {return !std::isspace(c); };
    str.erase(str.begin(), std::find_if(str.begin(), str.end(), notSpace)); // trim left
    str.erase(std::find_if(str.rbegin(), str.rend(), notSpace).base(), str.end()); // trim right
}

class ConfigReader {
public:
    using SECTION = std::unordered_map<std::string, std::string>;
    void parse(const std::string& file) {
        std::ifstream fs(file, std::iostream::in);
        if (!fs.good()) {
            throw std::runtime_error("Failed to open file " + file);
        }

        std::string line;
        std::regex keyPattern(R"(\[(.*)\])");
        std::regex valPattern(R"((.*)\s+=\s+(.*))");
        std::smatch matches;
        std::string key;
        while(std::getline(fs, line)) {
            trim(line);
            std::regex_match(line, matches, keyPattern);
            if (matches.size() == 2) {
                key = matches[1];
                continue;
            }

            std::regex_match(line, matches, valPattern);
            if (matches.size() == 3) {
                config[key].emplace(matches[1], matches[2]);
                continue;
            }
        }
    }

    const SECTION& operator[](const std::string& key) {
        return config.at(key);
    }

    void dump() {
        for(auto& [k, v] : config) {
            std::cout << "[" << k << "]" << std::endl;
            for (auto& [vk, vv] : v) {
                std::cout << vk << " => " << vv << std::endl;
            }
        }
    }

private:
    std::unordered_map<std::string, SECTION> config;
};