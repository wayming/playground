#include <string_view>
#include <variant>
#include <stack>
#include <optional>
#include <cctype>
#include <iostream>
#include <format>
#include <cstdint>
#include <sstream>
#include <memory>
#include <string>
#include <exception>
#include <charconv>
struct Node;
using NodePtr = std::unique_ptr<Node>;

struct Number
{
    double val;
    size_t pos;
};
struct Binary
{
    NodePtr left;
    NodePtr right;
    char op;
    size_t pos;
};
struct Neg
{
    NodePtr val;
};
struct Node
{
    std::variant<Number, Binary, Neg> val;
};

using NodePtrResult = std::optional<NodePtr>;
using NumberResult = std::optional<Number>;

template <class T>
NodePtr make_node(T &&t) { return std::make_unique<Node>(std::forward<T>(t)); }

class ParseError : public std::exception
{
    std::string message;

public:
    explicit ParseError(size_t pos, const std::string &error)
    {
        message = std::format("Failed to parse expression at {}, error {}", pos, error);
    }
    const char *what() const noexcept override { return message.c_str(); }
};

class EvalException : public std::exception
{
    std::string message;

public:
    explicit EvalException(size_t pos, const std::string &error)
    {
        message = std::format("Failed to eval expression at {}, error {}", pos, error);
    }
    const char *what() const noexcept override { return message.c_str(); }
};

class Parser
{
public:
    NodePtrResult parse(std::string_view exp_str)
    {
        auto result = exp(exp_str);
        if (pos_ < exp_str.size())
        {
            throw ParseError(pos_, "not all expression processed");
        }
        return result;
    }

private:
    size_t pos_ = {0};
    std::optional<size_t> peek(std::string_view exp_str)
    {
        while (pos_ < exp_str.size() && std::isspace(exp_str[pos_]))
        {
            pos_++;
        }
        if (pos_ == exp_str.size())
        {
            return std::nullopt;
        }
        else
        {
            return pos_;
        }
    }

    NodePtrResult exp(std::string_view exp_str)
    {
        auto left = term(exp_str);
        if (!left)
        {
            return left;
        }
        while (peek(exp_str) && (exp_str[pos_] == '+' || exp_str[pos_] == '-'))
        {
            auto op = exp_str[pos_];
            auto op_pos = pos_;
            ++pos_;
            auto right = term(exp_str);
            if (!right)
            {
                throw ParseError(op_pos, "Failed to find the right oprand");
            }
            left = make_node(Binary{std::move(left.value()), std::move(right.value()), op, op_pos});
        }
        return left;
    }

    NodePtrResult term(std::string_view exp_str)
    {
        auto left = unary(exp_str);
        if (!left)
        {
            return left;
        }
        while (peek(exp_str) && (exp_str[pos_] == '*' || exp_str[pos_] == '/'))
        {
            auto op = exp_str[pos_];
            auto op_pos = pos_;
            ++pos_;
            auto right = unary(exp_str);
            if (!right)
            {
                throw ParseError(op_pos, "Failed to find the right oprand");
            }
            left = make_node(Binary{std::move(left.value()), std::move(right.value()), op, op_pos});
        }
        return left;
    }

    NodePtrResult unary(std::string_view exp_str)
    {
        if (peek(exp_str) && exp_str[pos_] == '-')
        {
            ++pos_;
            auto p = primary(exp_str);
            if (!p)
            {
                throw ParseError(pos_, "negative with no number");
            }
            return make_node(Neg{std::move(p.value())});
        }
        else
        {
            auto p = primary(exp_str);
            return p;
        }
    }

    NodePtrResult primary(std::string_view exp_str)
    {
        if (!peek(exp_str))
        {
            return std::nullopt;
        }

        if (std::isdigit(exp_str[pos_]))
        {
            double d;
            auto [ptr, ec] = std::from_chars(exp_str.data() + pos_, exp_str.data() + exp_str.size(), d);
            if (ec != std::errc{})
            {
                throw ParseError(pos_, std::to_string(static_cast<int>(ec)));
            }
            pos_ = ptr - exp_str.data();
            return make_node(Number{d, pos_});
        }
        if (exp_str[pos_] == '(')
        {
            ++pos_;
            if (!peek(exp_str))
            {
                throw ParseError(pos_, "no closing parenthesis");
            }
            auto ret = std::move(exp(exp_str));
            if (!peek(exp_str) || exp_str[pos_] != ')')
            {
                throw ParseError(pos_, "no closing parenthesis");
            }
            ++pos_;
            return ret;
        }
        throw ParseError(pos_, "unknown data type");
    }
};

template <class... Funcs>
struct Overloaded : Funcs...
{
    using Funcs::operator()...;
};

double eval(const Node &node)
{
    auto NumCalc = [](const Number &n)
    {
        return n.val;
    };
    auto NegCalc = [](const Neg &n)
    {
        return -1 * eval(*n.val);
    };
    auto BinaryCalc = [](const Binary &b)
    {
        switch (b.op)
        {
        case '*':
            return eval(*b.left) * eval(*b.right);
        case '/':
        {
            auto right = eval(*b.right);
            if (right == 0.0)
            {
                throw EvalException(b.pos, "divid by zero");
            }
            return eval(*b.left) / right;
        }
        case '+':
            return eval(*b.left) + eval(*b.right);
        case '-':
            return eval(*b.left) - eval(*b.right);
        default:
            throw ParseError(b.pos, "unknown operator");

            break;
        }
    };
    return std::visit(Overloaded{NumCalc, NegCalc, BinaryCalc},
                      node.val);
}

void calc(std::string_view exp_str)
{
    Parser p;
    auto ast = p.parse(exp_str);
    if (ast)
    {
        std::cout << eval(*ast.value()) << std::endl;
    }
    else
    {
        std::cout << "no parsing result" << std::endl;
    }
}
int main()
{
    calc("5 + 4 * 2 - 1");
    calc("5 + 4 * (2 - 1)");
    calc("5 + 4 * (2 - -1)");
    calc("2*3-1");
    calc("");
    try
    {
        calc("5 +");
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
    }

    try
    {
        calc("5 / (3-3)");
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
    }
}