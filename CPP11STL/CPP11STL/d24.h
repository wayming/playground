#include <algorithm>
#include <string>
#include <utility>

void handleEscapes(std::string& tpl) {
    auto pos = tpl.find("$$");
    while (pos != std::string::npos) {
        tpl.replace(pos, 2, "$");
        pos = tpl.find("$$", pos+1);
    }
    
}
std::string& renderTemplate(std::string& tpl, const std::unordered_map<std::string, std::string>& params) {
    handleEscapes(tpl);
    auto pos = tpl.find("${");
    while (pos != std::string::npos) {
        auto end = tpl.find("}", pos + 2);
        if (end == std::string::npos) {
            throw std::runtime_error("no closing bracket found");
        }
        auto key = tpl.substr(pos+2, end - pos - 2);
        if (params.find(key) == params.end()) {
            throw std::runtime_error("key " + key + " not found");
        }
        tpl.replace(pos, end - pos + 1, params.at(key));
        pos = tpl.find("${", pos + params.at(key).size());
    }

    return tpl;
}
