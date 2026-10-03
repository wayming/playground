#include <iostream>
#include <type_traits>
#include <vector>
struct NoPlus
{
    long value = 0;
    // NoPlus &operator+(const NoPlus &v)
    // {
    //     value += v.value;
    //     return *this;
    // }
};
std::ostream &operator<<(std::ostream &os, const NoPlus &v)
{
    os << v.value;
    return os;
}
template <class T, class = void>
struct has_plus : std::false_type
{
};

template <class T>
struct has_plus<T, std::void_t<decltype(std::declval<T>() + std::declval<T>())>> : std::true_type
{
};

template <class T>
constexpr bool has_plus_v = has_plus<T>::value;

template <class T, class = std::enable_if_t<has_plus_v<T>>>
auto sum(const std::vector<T> &values)
{
    T sum{};
    for (const auto &v : values)
    {
        sum = sum + v;
    }
    return sum;
}

template <class T>
concept Addable = requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
};

template <Addable T>
auto sum2(const std::vector<T> &values)
{
    T sum{};
    for (const auto &v : values)
    {
        sum = sum + v;
    }
    return sum;
}

int main()
{
    std::cout << sum(std::vector<int>{1, 2, 3}) << std::endl;

    NoPlus n1{100}, n2{200};
    auto n3 = n1 + n2;
    std::cout << n3.value << std::endl;

    // std::cout << sum(std::vector<NoPlus>{{1}, {2}, {3}}) << std::endl;
    // std::cout << sum2(std::vector<NoPlus>{{1}, {2}, {3}}) << std::endl;
}