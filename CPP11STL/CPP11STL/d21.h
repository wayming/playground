#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

class StockDataParser {
public:
    void parse(const std::string& filePath) {
        std::ifstream s(filePath);
        if (!s.good()) {
            throw std::runtime_error("Failed to open file " + filePath);
        }
        std::string row;
        std::getline(s, row); // skip header
        while(s.good() && !s.eof()) {
            std::getline(s, row);
            if (row.length() == 0) {
                continue; // skip empty line
            }
            int found = 0;
            size_t begin = 0;
            while (found < 2) {
                begin = row.find(',', begin+1);
                if (begin == std::string::npos) {
                    throw std::runtime_error("bad format for line " + row);
                }
                found++;
            }
            begin = begin+1;
            auto end = row.find(',', begin);
            if (end == std::string::npos) {
                throw std::runtime_error("bad format for line " + row);
            }

            auto price = row.substr(begin, end-begin);
            try {
                prices.push_back(std::stod(price));
            } catch (std::exception) {
                std::cerr << "bad format for line " << row << std::endl;
                throw;
            }
        }

        double sum;
        std::for_each(prices.begin(), prices.end(), [&sum](auto p) { sum += p; });
        std::cout << "sum=" << sum << ", min=" << *std::min_element(prices.begin(), prices.end())
                  << ", max=" << *std::max_element(prices.begin(), prices.end()) << std::endl;
    
    }
private:
    std::vector<double> prices;
};