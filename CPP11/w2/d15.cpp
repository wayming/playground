#include <vector>
#include <string_view>
#include <map>
#include <unordered_map>
#include <iostream>
class WordCounter
{
private:
    std::vector<std::string> words_;
    std::unordered_map<std::string_view, int> counter_;

public:
    WordCounter(std::vector<std::string> words) : words_(std::move(words)) { count_words(); }
    WordCounter(const WordCounter &wc) : words_(wc.words_)
    {
        count_words();
    }
    WordCounter(WordCounter &&wc) noexcept : words_(std::move(wc.words_)), counter_(std::move(wc.counter_))
    {
        wc.words_.clear();
        wc.counter_.clear();
    }

    WordCounter &operator=(const WordCounter &wc)
    {
        if (&wc == this)
        {
            return *this;
        }
        words_ = wc.words_;
        count_words();
        return *this;
    }
    WordCounter &operator=(WordCounter &&wc) noexcept
    {
        if (&wc == this)
        {
            return *this;
        }
        words_ = std::move(wc.words_);
        counter_ = std::move(wc.counter_);
        wc.words_.clear();
        wc.counter_.clear();
        return *this;
    }
    void count_words()
    {
        counter_.clear();
        for (const auto &w : words_)
        {
            counter_[std::string_view(w)] += 1;
        }
    }
    int64_t get(const std::string &word) const
    {
        auto iter = counter_.find(std::string_view(word));
        if (iter != counter_.end())
        {
            return iter->second;
        }
        else
        {
            return 0;
        }
    }
};
int main()
{
    WordCounter c({"aa",
                   "bb",
                   "aa",
                   "cc",
                   "aa"});
    std::cout << c.get("aa");
    std::cout << c.get("bb");
    std::cout << c.get("cc");
}