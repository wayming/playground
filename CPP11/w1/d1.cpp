#include <iostream>
#include <type_traits>
#include <vector>
#include <numeric>
#include <algorithm>
#include <variant>

enum class SEQ_TYPE : int {
    SEQ_INVALID = -1,
    SEQ_NUM,
    SEQ_SQUARE,
    SEQ_ITEM,
};
constexpr int SEQ_TYPE_MIN = static_cast<int>(SEQ_TYPE::SEQ_INVALID);
constexpr int SEQ_TYPE_MAX = static_cast<int>(SEQ_TYPE::SEQ_ITEM);
using GEN_RET_TYPE = std::variant<int, std::string>;

template < typename T>
std::vector<T> generate_sequence(const std::vector<int>& src, const std::function<GEN_RET_TYPE(int)>& gen) {
    std::vector<T> results;
    results.reserve(src.size());
    std::transform(src.begin(), src.end(), std::back_inserter(results), [&gen](int x) -> T {
        GEN_RET_TYPE genV = gen(x);
        if (std::holds_alternative<T>(genV)) {
            return std::get<T>(genV);
        }
        throw std::runtime_error("unexpected variant type");
    });
    return results;
}

std::unordered_map<SEQ_TYPE, std::function<GEN_RET_TYPE(int)>> GENERATOR_MAP = {
    {SEQ_TYPE::SEQ_NUM, [](int x) -> GEN_RET_TYPE {return x;}},
    {SEQ_TYPE::SEQ_SQUARE, [](int x) -> GEN_RET_TYPE {return x * x;}},
    {SEQ_TYPE::SEQ_ITEM, [](int x) -> GEN_RET_TYPE {return "item-" + std::to_string(x);}}
};

int main(int argc, char** argv) {
    if (argc != 5) {
        std::cerr << "Invalid number of parameters, " << argc << std::endl;
        return -1;
    }

    SEQ_TYPE seqType = SEQ_TYPE::SEQ_INVALID;
    int begin = -1;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-type") {
            if ((i + 1) < argc) {
                try {
                    int seqTypeVal = std::stoi(argv[++i]);
                    if (seqTypeVal >= SEQ_TYPE_MIN && seqTypeVal <= SEQ_TYPE_MAX) {
                        seqType = static_cast<SEQ_TYPE>(seqTypeVal);
                    }
                } catch (const std::exception&) {
                    std::cerr << "Invalid parameter for option -type" << std::endl;
                }
            }
        } else if (arg == "-begin"){
            if ((i + 1) < argc) {
                try {
                    begin = std::stoi(argv[++i]);
                } catch (const std::exception&) {
                    std::cerr << "Invalid parameter for option -begin" << std::endl;
                }
                i++;
            }
        } else {
            std::cerr << "Unknown parameter " << arg << std::endl;
            return -1;
        }
    }
    
    if (seqType == SEQ_TYPE::SEQ_INVALID ||  begin <= 0) {
        std::cerr << "Invalid parameters. seqType=" << static_cast<std::underlying_type_t<SEQ_TYPE>>(seqType)
             << " begin=" << begin << std::endl;
        return -1;
    }

    int n = 10;
    std::vector<int> src(n);
    std::iota(src.begin(), src.end(), begin);

    std::vector<int> numSqured(n);
    try {
        for (auto v: generate_sequence<int>(src, GENERATOR_MAP.at(SEQ_TYPE::SEQ_NUM))) {
            std::cout << v << std::endl;
        }

        for (auto v: generate_sequence<int>(src, GENERATOR_MAP.at(SEQ_TYPE::SEQ_SQUARE))) {
            std::cout << v << std::endl;
        }

        for (auto v: generate_sequence<std::string>(src, GENERATOR_MAP.at(SEQ_TYPE::SEQ_ITEM))) {
            std::cout << v << std::endl;
        }
    } catch (std::exception&) {
        std::cerr << "Failed to transform the sequences" << std::endl;
        throw;
    }

    return 0;
}