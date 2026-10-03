#include <ranges>
#include <vector>
#include <iostream>
#include <algorithm>
#include <numeric>
enum class SIDE
{
    BUY,
    SELL
};
struct Order
{
    unsigned long id;
    SIDE side;
    double price;
    unsigned long quantity;
};
std::ostream &operator<<(std::ostream &os, const Order &o)
{
    os << o.id;
    return os;
}

void dump(std::ranges::range auto &&vs)
{
    for (const auto &v : vs)
    {
        std::cout << v << "|";
    }
    std::cout << std::endl;
}
int main()
{
    std::vector<Order> v = {
        {1, SIDE::BUY, 1.0, 100},
        {2, SIDE::SELL, 2.0, 1000},
        {3, SIDE::BUY, 3.0, 1000},
        {4, SIDE::SELL, 4.0, 1000},
        {5, SIDE::BUY, 5.0, 100},
        {6, SIDE::SELL, 6.0, 100},
        {7, SIDE::BUY, 3.0, 10000},
        {8, SIDE::BUY, 3.0, 0},
    };

    std::vector<Order> buys;
    auto buys_view = v | std::views::filter([](const Order &o)
                                            { return o.side == SIDE::BUY; });
    std::copy(buys_view.begin(), buys_view.end(), std::back_inserter(buys));
    std::sort(buys.begin(), buys.end(), [](const Order &a, const Order &b)
              { return (a.price > b.price) || ((a.price == b.price) && (a.quantity > b.quantity)); });
    dump(buys);
    auto buys_view2 = buys_view | std::views::filter([](const Order &o)
                                                     { return o.quantity > 0; });
    dump(buys_view2);
    auto buys_view3 = buys_view2 | std::views::transform([](const Order &o)
                                                         { return o.quantity; });
    std::cout
        << std::accumulate(buys_view3.begin(), buys_view3.end(), 0) << std::endl;
}