#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include <sstream>
#include <fstream>
#include <optional>
#include <iterator>
// std::vector<std::string> split(const std::string& src) {
//     std::stringstream ss(src);
//     std::vector<std::string> tokens;
//     std::string token;
//     while (ss.good()) {
//         if (std::getline(ss, token, ',')) {
//             std::cout << "true" << std::endl;
//         } else {
//             std::cout << "false" << std::endl;
//         }
//         tokens.emplace_back(std::move(token));
//     }
//     return tokens;
// }

std::vector<std::string> split(const std::string& src) {
    std::istringstream ss(src);
    std::vector<std::string> tokens;
    std::string token;

    while (std::getline(ss, token, ',')) {
        tokens.emplace_back(token);
    }

    // handling trailing delimiter
    if (!src.empty() && src.back() == ',') {
        tokens.emplace_back("");
    }
    return tokens;
}

class CSVInputIterator
{
public:
    using iterator_category = std::input_iterator_tag;
    using value_type        = std::vector<std::string>;
    using difference_type   = std::ptrdiff_t;
    using pointer           = value_type*;
    using reference         = value_type&;

    using ElementType = std::vector<std::string>;
    // using iterator_category = std::input_iterator_tag;
    // using value_type = ElementType;
    // using difference_type = std::ptrdiff_t;
    // using pointer = value_type*;
    // using reference = value_type&;

    CSVInputIterator() : end(true) {}
    CSVInputIterator(std::istream& s) : is(s) {
        ++(*this);
    }

    ElementType& operator*() {return element;}
    ElementType* operator->() {return &element;}
    CSVInputIterator& operator++() {
        if (!is.has_value()) throw std::runtime_error("Not initialised.");
        if (end) return *this;
        std::string line;
        if (!std::getline(is->get(), line)) {
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
    std::optional<std::reference_wrapper<std::istream>> is = {};
    ElementType element;
    bool end = false;
};

class JSONOutputIterator {
public:
    using iterator_category = std::output_iterator_tag;
    using value_type = void;
    using difference_type = void;

    JSONOutputIterator(std::ostream& s, std::vector<std::string>&& h) :os(&s), headers(std::move(h)) {}
    ~JSONOutputIterator() {}
    JSONOutputIterator& operator=(const std::vector<std::string>& fields) {
        if (fields.size() != headers.size()) {
            std::stringstream error;
            error << "Number of fields " << fields.size() << " does not match number of header " << headers.size(); 
            throw std::runtime_error(error.str());
        }
        
        if (!first) *os << ", ";
        first = false;

        *os << "{";
        for (int i = 0; i < headers.size(); ++i) {
            *os << '"' << headers.at(i) << '"' << ':';
            *os << '"' << fields.at(i) << '"';
            if (i < headers.size() - 1) {
                *os << ", ";
            }
        }
        *os << "}";

        return *this;
    }


    JSONOutputIterator(const JSONOutputIterator& other) = default;
    JSONOutputIterator(JSONOutputIterator&& other) = default;
    JSONOutputIterator& operator=(const JSONOutputIterator&) = default;
    JSONOutputIterator& operator=(JSONOutputIterator&&) = default;

    JSONOutputIterator& operator*() {return *this;}
    JSONOutputIterator& operator++() {return *this;}
    JSONOutputIterator& operator++(int) {return *this;}

private:
    std::ostream* os;
    std::vector<std::string> headers;
    bool first = true;
};

std::string convertCSVToJSON(const std::string& path) {
    std::ifstream is(path.c_str(), std::ifstream::in);
    if (!is.good()) throw std::runtime_error("Failed to open file " + path);

    std::string line;
    if (!std::getline(is, line)) {
        throw std::runtime_error("Failed to read header line");
    }
    std::vector<std::string> headers = std::move(split(line));
    if (headers.size() == 0) throw std::runtime_error("Failed to read header line");

    std::stringstream os;
    CSVInputIterator it(is);
    CSVInputIterator end;
    JSONOutputIterator out(os, std::move(headers));
    // Not compile on windows
    // std::copy(it, end, out);

    for (; it != end; ++it) {
        out = *it;
        ++out;
    }
    return os.str();
}