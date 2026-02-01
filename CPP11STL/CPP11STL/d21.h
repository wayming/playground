#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <numeric>

class StockDataParser {
    std::unordered_map<std::string, std::vector<std::string>> data;
public:
    std::vector<std::string> split(const std::string& str) {
        std::vector<std::string> tokens;
        size_t begin = 0;
        auto end = str.find(',');
        while(end != std::string::npos) {
            tokens.emplace_back(str.substr(begin, end - begin));
            begin = end + 1;
            end = str.find(',', begin);
        }
        if (begin != std::string::npos) {
            tokens.emplace_back(str.substr(begin, str.size() - begin));
        } else {
            tokens.emplace_back("");
        }

        return tokens;
    }

    void parse(const std::string& filePath) {
        std::ifstream in(filePath);
        bool first = true;
        std::vector<std::string> keys;
        while (in.good()) {
            std::string line;
            std::getline(in, line);
            if (line.length() > 0) {
                auto tokens = split(line);
                if (first) {
                    first = false;
                    keys = std::move(tokens);
                } else {
                    if (tokens.size() != keys.size()) {
                        throw std::runtime_error("invalid number of columns");
                    }
                    for(int i = 0; i < keys.size(); ++i) {
                        data[keys.at(i)].emplace_back(std::move(tokens.at(i)));
                    }
                }
            }
        }
    }

    std::vector<std::string> get(const std::string& key) {
        auto iter = data.find(key);
        if (iter == data.end()) {
            throw std::runtime_error("invalid key");
        }
        
        return iter->second;
    }
};