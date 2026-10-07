#include <string_view>
#include <variant>
#include <stack>
#include <optional>
#include <cctype>
std::variant<uint32_t, double> number;
using RESULT_TYPE = std::optional<std::variant<uint32_t, double>>;
using NUMBER_TYPE = std::variant<uint32_t, double>;
using OP_TYPE = std::variant<OP_ADD, OP_MINUS, OP_MULTI, OP_DIVIDE>;
struct OP_ADD
{
public:
    template <class T1, class T2>
    RESULT_TYPE operator()(T1 a, T2 b) { return a + b; }
};
struct OP_MINUS
{
public:
    template <class T1, class T2>
    RESULT_TYPE operator()(T1 a, T2 b) { return a - b; }
};
struct OP_MULTI
{
public:
    template <class T1, class T2>
    RESULT_TYPE operator()(T1 a, T2 b) { return a * b; }
};
struct OP_DIVIDE
{
public:
    template <class T1, class T2>
    RESULT_TYPE operator()(T1 a, T2 b) { return a / b; }
};
using OP_TYPE = std::variant<OP_ADD, OP_MINUS, OP_MULTI, OP_DIVIDE>;

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

                break;
            }
        }
    }
}
int main()
{
    auto exp1 = "5 + 6 * 3 - 2";
}