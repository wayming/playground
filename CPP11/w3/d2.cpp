#include <string_view>
#include <variant>
#include <iostream>
#include <optional>
#include <map>
#include <vector>
#include <cctype>
#include <charconv>
#include <format>
#include <sstream>
// {
//  "name": "a",
//  "tags": [1, 2, {"x": null}],
//  "ok": true
// }
namespace json
{
    template <class... Ts>
    struct overloaded : Ts...
    {
        using Ts::operator()...;
    };
    struct Value
    {
        using Object = std::map<std::string, Value, std::less<>>;
        using Array = std::vector<Value>;
        std::variant<double, std::string, Object, Array> value;
        const Value &operator[](std::string_view key) const
        {
            static const Value ValueNull{};

            if (std::holds_alternative<Object>(value))
            {
                auto &obj = std::get<Object>(value);
                auto iter = obj.find(key);
                if (iter != obj.end())
                {
                    return iter->second;
                }
            }
            return ValueNull;
        }
        const Value &operator[](size_t idx) const
        {
            static const Value ValueNull{};

            if (std::holds_alternative<Array>(value))
            {
                auto &arr = std::get<Array>(value);
                if (idx >= arr.size())
                {
                    return ValueNull;
                }
                return arr[idx];
            }
            return ValueNull;
        }
        std::string dump() const
        {
            return std::visit(overloaded{
                                  [](const std::string &s)
                                  { return s; },
                                  [](double d)
                                  { return std::to_string(d); },
                                  [](const Object &obj)
                                  {
                                      std::stringstream ss;
                                      ss << "{";
                                      for (auto &[key, val] : obj)
                                      {
                                          ss << "\"" << key << "\" =>" << val.dump();
                                      }
                                      ss << "}" << std::endl;
                                      return ss.str();
                                  },
                                  [](const Array &arr)
                                  {
                                      std::stringstream ss;
                                      ss << "[";
                                      for (auto &val : arr)
                                      {
                                          ss << val.dump();
                                      }
                                      ss << "]" << std::endl;
                                      return ss.str();
                                  },
                                  [](std::nullptr_t)
                                  {
                                      return std::string("null");
                                  },
                              },
                              value);
        }
    };

    using ParserResult = std::optional<Value>;
    constexpr std::string_view trim(std::string_view src, std::string_view space = std::string_view(" \t\r\n"))
    {
        auto first = src.find_first_not_of(space);
        auto end = src.find_last_not_of(space);
        if (first != std::string::npos && end != std::string::npos)
        {
            return src.substr(first, end - first + 1);
        }
        else
        {
            return std::string_view();
        }
    }
    class Parser
    {
    private:
        std::string_view src_;
        size_t pos_ = 0;
        void nextc()
        {
            while (std::isspace(peek()))
            {
                pos_++;
            }
        }
        bool eof() const { return pos_ >= src_.size(); }
        char peek() const
        {
            return eof() ? '\0' : src_[pos_];
        }

        ParserResult number()
        {
            nextc();
            auto begin = pos_;
            while (!eof())
            {
                if (std::string_view("+-.eE0123456789").find(peek()) == std::string::npos)
                {
                    break;
                }
                pos_++;
            }
            double d;
            auto [ptr, ec] = std::from_chars(src_.data() + begin, src_.data() + pos_, d);
            if (ec != std::errc{} || ptr != src_.data() + pos_)
            {
                return std::nullopt;
            }
            else
            {
                return Value{d};
            }
        }
        ParserResult object()
        {
            Value::Object obj;
            if (peek() != '{')
            {
                return std::nullopt;
            }
            pos_++;
            do
            {
                std::string key;
                nextc();
                if (peek() == '"')
                {
                    ParserResult result = string();
                    if (!result.has_value())
                        return std::nullopt;

                    if (!std::holds_alternative<std::string>(result.value().value))
                        return std::nullopt;
                    key = std::get<std::string>(result.value().value);
                }
                nextc();
                if (peek() != ':')
                {
                    return std::nullopt;
                }
                pos_++;
                nextc();
                ParserResult result = value();
                if (!result.has_value())
                    return std::nullopt;

                obj.insert_or_assign(std::move(key), std::move(result.value()));
                nextc();
                if (peek() != ',')
                {
                    break;
                }
                pos_++; // skip , delimiter
            } while (peek() != '}');
            if (peek() != '}')
            {
                return std::nullopt;
            }
            nextc();
            pos_++;
            return Value{std::move(obj)};
        }
        ParserResult array()
        {
            Value::Array arr;
            nextc();
            if (peek() != '[')
            {
                return std::nullopt;
            }
            pos_++;

            do
            {
                nextc();
                ParserResult element = value();
                if (!element.has_value())
                {
                    return std::nullopt;
                }
                arr.emplace_back(std::move(element.value()));
                nextc();
                if (peek() != ',')
                {
                    break;
                }
                pos_++;
            } while (peek() != ']');
            if (peek() != ']')
            {
                return std::nullopt;
            }
            nextc();
            pos_++;
            return Value{std::move(arr)};
        }
        ParserResult string()
        {
            nextc();
            if (peek() != '"')
            {
                return std::nullopt;
            }
            pos_++;
            auto end_pos = src_.find('"', pos_);
            if (end_pos == std::string::npos)
            {
                return std::nullopt;
            }
            auto v = src_.substr(pos_, end_pos - pos_);
            pos_ = end_pos + 1;
            return Value{std::string(trim(v))};
        }

    public:
        ParserResult value()
        {
            switch (peek())
            {
            case '{':
                return object();
            case '"':
                return string();
            case '[':
                return array();
            default:
                return number();
            }
        }
        Parser(std::string_view text) : src_(text) {}
        ~Parser() {}
    };

    [[nodiscard]] inline ParserResult parse(std::string_view s)
    {
        return Parser(s).value();
    }
}

int main()
{
    auto json_text = std::string_view(R"({"name ": "a", " count ": 100})");
    auto r = json::parse(json_text);
    if (!r)
    {
        throw std::runtime_error(std::format("Failed to parse {}", json_text));
    }
    std::cout << r.value().dump() << std::endl;

    json_text = std::string_view(R"({"name": "p", "object": {"name ": "a", " count ": 100}})");
    r = json::parse(json_text);
    if (!r)
    {
        throw std::runtime_error(std::format("Failed to parse {}", json_text));
    }
    std::cout << r.value().dump() << std::endl;

    json_text = std::string_view(R"({"name": "p", "object": {"name ": "a", " count ": 100, "arr": [1, 2, "w"]}})");
    r = json::parse(json_text);
    if (!r)
    {
        throw std::runtime_error(std::format("Failed to parse {}", json_text));
    }
    auto &v = r.value();
    std::cout << v.dump() << std::endl;
    std::cout << v["name"].dump() << " " << v["object"]["arr"][1].dump() << std::endl;
    return 0;
}