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

class CSVInputIterator {
public:
    using ElementType = std::vector<std::string>;

    CSVInputIterator(std::istream& s) : is(s) {
        ++(*this);
    }

    ElementType& operator*() {return element;}
    ElementType* operator->() {return &element;}
    CSVInputIterator& operator++() {
        if (end) return *this;
        std::string line;
        if (!std::getline(is, line)) {
            end = true;
            return *this;
        }

        element = std::move(split(line));
        if (element.size() == 0) return ++(*this);
        return *this;
    }
    CSVInputIterator& operator++(int) {
        return ++(*this);
    }
    bool operator==(const CSVInputIterator& other) {
        return end && other.end;
    }
    bool operator!=(const CSVInputIterator& other) {
        return !(*this == other);
    }
private:
    std::istream& is;
    ElementType element;
    bool end = false;
};

class JSONOutputIterator {
public:
    JSONOutputIterator(std::ostream& s, std::vector<std::string>&& h) :os(s), headers(std::move(h)) {}
    ~JSONOutputIterator() {}
    JSONOutputIterator& operator=(const std::vector<std::string>& fields) {
        if (fields.size() != headers.size()) {
            std::stringstream error;
            error << "Number of fields " << fields.size() << " does not match number of header " << headers.size(); 
            throw std::runtime_error(error.str());
        }
        
        if (!first) os << ", ";
        first = false;

        os << "{";
        for (int i = 0; i < headers.size(); ++i) {
            os << '"' << headers.at(i) << '"' << ':';
            os << '"' << fields.at(i) << '"';
            if (i < headers.size() - 1) {
                os << ", ";
            }
        }
        os << "}";

        return *this;
    }
    JSONOutputIterator& operator*() {return *this;}
    JSONOutputIterator& operator++() {return *this;}
    JSONOutputIterator& operator++(int) {return *this;}

private:
    std::ostream& os;
    std::vector<std::string> headers;
    bool first = true;
};