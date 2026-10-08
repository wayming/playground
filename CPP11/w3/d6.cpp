#include <string_view>
#include <variant>
#include <stack>
#include <optional>
#include <cctype>
#include <iostream>
#include <format>
#include <cstdint>
#include <sstream>
std::variant<uint32_t, double> number;
using RESULT_TYPE = std::optional<std::variant<uint32_t, double>>;
using NUMBER_TYPE = std::variant<uint32_t, double>;
enum class OP_PRECEDENCE
{
    OP_LEVEL1,
    OP_LEVEL2,
};
template <class T>
class StackDumper : public std::stack<T>
{
public:
    std::string to_string()
    {
        std::stringstream ss;
        bool first = true;
        ss << "[";
        for (auto const &t : this->c)
        {
            if (!first)
            {
                ss << ", ";
            }
            std::visit([&ss](auto &value)
                       { ss << value; }, t);
            first = false;
        }
        ss << "]" << std::endl;
        return ss.str();
    }
};
template <class T>
std::string dump_stack(const std::stack<T> &s)
{
    auto dumper = static_cast<const StackDumper<T> &>(s);
    return dumper.to_string();
}

struct OP_ADD
{
public:
    template <class T1, class T2>
    NUMBER_TYPE operator()(const T1 a, const T2 b) const noexcept
    {
        return std::visit([](const auto &v1, const auto &v2) -> NUMBER_TYPE
                          { return v1 + v2; }, a, b);
    }
    static constexpr std::string name{"ADD"};
    static constexpr OP_PRECEDENCE prec{OP_PRECEDENCE::OP_LEVEL1};
};
struct OP_MINUS
{
public:
    template <class T1, class T2>
    NUMBER_TYPE operator()(const T1 a, const T2 b) const noexcept
    {
        return std::visit([](const auto &v1, const auto &v2) -> NUMBER_TYPE
                          { return v1 - v2; }, a, b);
    }
    static constexpr std::string name{"MINUS"};
    static constexpr OP_PRECEDENCE prec{OP_PRECEDENCE::OP_LEVEL1};
};
struct OP_MULTI
{
public:
    template <class T1, class T2>
    NUMBER_TYPE operator()(const T1 a, const T2 b) const noexcept
    {
        return std::visit([](const auto &v1, const auto &v2) -> NUMBER_TYPE
                          { return v1 * v2; }, a, b);
    }
    static constexpr std::string name{"MULTI"};
    static constexpr OP_PRECEDENCE prec{OP_PRECEDENCE::OP_LEVEL2};
};
struct OP_DIVIDE
{
public:
    template <class T1, class T2>
    NUMBER_TYPE operator()(const T1 a, const T2 b) const noexcept
    {
        return std::visit([](const auto &v1, const auto &v2) -> NUMBER_TYPE
                          { return v1 / v2; }, a, b);
    }
    static constexpr std::string name{"DIVIDE"};
    static constexpr OP_PRECEDENCE prec{OP_PRECEDENCE::OP_LEVEL2};
};

using OP_TYPE = std::variant<OP_ADD, OP_MINUS, OP_MULTI, OP_DIVIDE>;
OP_PRECEDENCE op_type_prec(const OP_TYPE &op)
{
    return std::visit([](const auto &t)
                      { return std::decay_t<decltype(t)>::prec; }, op);
}
NUMBER_TYPE op_type_op(const OP_TYPE &op, const NUMBER_TYPE left, const NUMBER_TYPE right)
{
    return std::visit([left, right](auto &callable)
                      { return callable(left, right); }, op);
}
std::string_view op_type_name(const OP_TYPE &op)
{
    return std::visit([](const auto &t)
                      { return std::string_view(t.name.c_str()); }, op);
}
std::ostream &operator<<(std::ostream &os, const OP_TYPE &op)
{
    os << op_type_name(op);
    return os;
}

std::ostream &operator<<(std::ostream &os, const NUMBER_TYPE &op)
{
    std::visit([&os](const auto &value)
               { os << value; }, op);
    return os;
}

class ParseError : std::exception
{
    std::string message;

public:
    explicit ParseError(const std::string exp, uint32_t pos)
        : message(std::format("Failed to process {} at {}", std::move(exp), pos)) {}
    const char *what() const noexcept override { return message.c_str(); }
};

class EvaluateError : std::exception
{
    std::string message;

public:
    explicit EvaluateError(std::string op_dump, std::string oprand_dump)
        : message(std::format("Failed to evaluate, operators {}, operands{}", std::move(op_dump), std::move(oprand_dump))) {}
    const char *what() const noexcept override { return message.c_str(); }
};
NUMBER_TYPE parse_num(std::string_view exp, std::string_view::iterator &it)
{
    auto begin = exp.data() + (it - exp.begin());
    auto end = exp.data() + exp.size();
    {
        // try integer first
        uint32_t n;
        auto [ptr, ec] = std::from_chars(begin, end, n);
        if (ec == std::errc() && *ptr != '.')
        {
            it += ptr - begin;
            return n;
        }
    }

    {
        // try double
        double d;
        auto [ptr, ec] = std::from_chars(begin, end, d);
        if (ec == std::errc())
        {
            it += ptr - begin;
            return d;
        }
        else
        {
            throw ParseError(std::string(exp), ptr - exp.begin());
        }
    }
}

RESULT_TYPE eval(std::stack<OP_TYPE> &ops, std::stack<NUMBER_TYPE> &oprand)
{
    if (ops.size() == 0)

    {
        if (oprand.size() == 1)
        {
            return oprand.top();
        }
        else
        {
            throw EvaluateError(dump_stack(ops), dump_stack(oprand));
        }
    }
    else
    {
        if (oprand.size() < 2)
        {
            throw EvaluateError(dump_stack(ops), dump_stack(oprand));
        }
    }

    OP_TYPE op1 = std::move(ops.top());
    ops.pop();
    NUMBER_TYPE right1 = std::move(oprand.top());
    oprand.pop();
    if (!ops.empty() && op_type_prec(ops.top()) > op_type_prec(op1))
    {
        if (oprand.size() < 2)
        {
            throw EvaluateError(dump_stack(ops), dump_stack(oprand));
        }
        NUMBER_TYPE right2 = std::move(oprand.top());
        oprand.pop();
        NUMBER_TYPE left2 = std::move(oprand.top());
        oprand.pop();
        OP_TYPE op2 = std::move(ops.top());
        ops.pop();

        oprand.emplace(op_type_op(op2, left2, right2));
        ops.emplace(std::move(op1));
        oprand.emplace(std::move(right1));
        return eval(ops, oprand);
    }
    else
    {
        NUMBER_TYPE left1 = std::move(oprand.top());
        oprand.pop();

        oprand.emplace(op_type_op(op1, left1, right1));
        return eval(ops, oprand);
    }
}

RESULT_TYPE calc(std::string_view exp)
{
    std::string_view op_chars("+-*/");
    std::stack<int> v;
    std::stack<OP_TYPE> ops;
    std::stack<NUMBER_TYPE> oprands;
    for (auto it = exp.begin(); it < exp.end();)
    {
        if (std::isspace(*it))
        {
            ++it;
            continue;
        }

        if (op_chars.find(*it) != std::string_view::npos)
        {
            switch (*it)
            {
            case '+':
                ops.emplace(OP_ADD{});
                break;
            case '-':
                ops.emplace(OP_MINUS{});
                break;
            case '*':
                ops.emplace(OP_MULTI{});
                break;
            case '/':
                ops.emplace(OP_DIVIDE{});
                break;
            default:
                throw ParseError(std::string(exp), std::distance(exp.begin(), it));
            }
            ++it;
            continue;
        }

        if (std::isdigit(*it))
        {
            oprands.emplace(parse_num(exp, it));
            ++it;
            continue;
        }
        throw ParseError(std::string(exp), std::distance(exp.begin(), it));
    }
    std::cout << dump_stack(ops) << std::endl;
    std::cout << dump_stack(oprands) << std::endl;
    return eval(ops, oprands);
}

int main()
{
    std::string_view exp1 = "5 + 6 * 3 - 2";
    std::cout << calc(exp1).value() << std::endl;
    return 0;
}