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

class Parser
{
public:
    NodePtrResult parse(std::string_view exp_str)
    {
        return exp(exp_str);
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
            ++pos_;
            auto right = term(exp_str);
            if (!right)
            {
                return left;
            }
            left = make_node(Binary{std::move(left.value()), std::move(right.value()), op, pos_});
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
            ++pos_;
            auto right = unary(exp_str);
            if (!right)
            {
                return left;
            }
            left = make_node(Binary{std::move(left.value()), std::move(right.value()), op, pos_});
            ++pos_;
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
            return nullptr;
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

NumberResult eval(NodePtr p)
{
    auto NumCalc = [](Number &n)
    {
        return n.val;
    };
    auto NegCalc = [](Neg &n)
    {
        return -1 * eval(std::move(n.val)).value().val;
    };
    auto BinaryCalc = [](Binary &b)
    {
        switch (b.op)
        {
        case '*':
            return eval(std::move(b.left)).value().val * eval(std::move(b.right)).value().val;
        case '/':
            return eval(std::move(b.left)).value().val / eval(std::move(b.right))
                                                             .value()
                                                             .val;
        case '+':
            return eval(std::move(b.left)).value().val + eval(std::move(b.right))
                                                             .value()
                                                             .val;
        case '-':
            return eval(std::move(b.left)).value().val - eval(std::move(b.right))
                                                             .value()
                                                             .val;
        default:
            throw ParseError(b.pos, "unknown operator");

            break;
        }
    };
    return Number{std::visit(Overloaded{
                                 NumCalc,
                                 NegCalc,
                                 BinaryCalc},
                             p->val),
                  0};
}

void calc(std::string_view exp_str)
{
    Parser p;
    auto ast = p.parse(exp_str);
    if (ast)
    {
        std::cout << eval(std::move(ast.value())).value().val << std::endl;
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
}