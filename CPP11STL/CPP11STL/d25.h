#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include <sstream>

std::vector<std::string> split(const std::string src) {
    std::stringstream ss(src);
    std::vector<std::string> tokens;
    std::string token;
    while (!ss.eof()) {
        std::getline(ss, token, ',');
        tokens.emplace_back(std::move(token));
    }
    return tokens;
}
