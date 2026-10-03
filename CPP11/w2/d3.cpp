#include <string_view>
#include <vector>
#include <string>
#include <iostream>

std::vector<std::string_view> split(std::string_view str, const std::string_view delim) {
    size_t begin = 0;
    std::vector<std::string_view> results;
    while (true) {
        auto pos = str.find(delim, begin);
        if (pos == std::string::npos) {
            results.emplace_back(str.substr(begin));
            break;
        }
        results.emplace_back(str.substr(begin, pos-begin));
        begin = pos + delim.size();
    }
    return results;
}
int main() 
{
    for(auto s : split("a;b;c",";")) {
        std::cout << "test1 " << s << std::endl;
    }

    for(auto s : split("abc",";")) {
        std::cout << "test2 " << s << std::endl;
    }

    for(auto s : split(";;;",";")) {
        std::cout << "test3 " << s << std::endl;
    }

    for(auto s : split(";a;",";")) {
        std::cout << "test4 " << s << std::endl;
    }

    for(auto s : split(";",";")) {
        std::cout << "test5 " << s << std::endl;
    }

    for(auto s : split("",";")) {
        std::cout << "test6 " << s << std::endl;
    }

    return 0;
}
