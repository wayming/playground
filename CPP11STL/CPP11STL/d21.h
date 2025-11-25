#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <numeric>

class StockDataParser {
public:
    std::vector<std::string> split(const std::string& str) {
        std::vector<std::string> tokens;
        size_t begin = 0;
        while(begin != std::string::npos) {
            auto end = str.find(',', begin);
            if (end == std::string::npos) break;
            tokens.emplace_back(str.substr(begin, end - begin));
            begin = end+1;
        }
        tokens.emplace_back(str.substr(begin));
        return tokens;
    }

    void header(const std::string& str) {
        size_t idx = 0;
        for (auto& key : split(str)) {
            cols[key] = idx++;
        }
    }
    void parse(const std::string& filePath, const std::string& colName) {
        std::ifstream s(filePath);
        if (!s.good()) throw std::runtime_error("Failed to open file " + filePath);
        
        std::string row;
        std::getline(s, row);
        header(row);
        if (cols.find(colName) == cols.end()) throw std::runtime_error("Invalid columen name " + colName);

        while(s.good() && !s.eof()) {
            std::getline(s, row);
            if (row.length() == 0) {
                continue; // skip empty line
            }
            
            try {
                targets.push_back(std::stod(split(row)[cols.at(colName)]));
            } catch (std::exception) {
                std::cerr << "bad format for line " << row << std::endl;
                throw;
            }
        }

        std::cout << "sum=" << std::accumulate(targets.begin(), targets.end(), 0)
                  << ", min=" << *std::min_element(targets.begin(), targets.end())
                  << ", max=" << *std::max_element(targets.begin(), targets.end()) << std::endl;
    
    }
private:
    std::vector<double> targets;
    std::unordered_map<std::string, size_t> cols;
};