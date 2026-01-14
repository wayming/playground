#include <vector>
#include <numeric>
#include <algorithm>
#include <string>

class SeqGenerator {
public:
    SeqGenerator(int first, int num) {
        nums.resize(num);
        std::iota(nums.begin(), nums.begin() + num, first);
    }

    std::vector<int> genIntegerSeq() {
        return nums;
    }

    std::vector<int> genSquareSeq() {
        std::vector<int> results;
        results.resize(nums.size());
        std::transform(nums.begin(), nums.end(), results.begin(), [](auto x) { return x * x; });
        return results;
    }

    std::vector<std::string> genStringSeq(const std::string& base) {
        std::vector<std::string> results;
        results.resize(nums.size());
        std::transform(nums.begin(), nums.end(), results.begin(), [&base](auto x) { return base + std::to_string(x); });
        return results;
    }
private:
    std::vector<int> nums;

};