#include <set>
#include <iostream>
#include <map>
#include <vector>

enum class SIDE
{
    BUY,
    SELL
};
using OrderId = unsigned long;
struct Order
{
    OrderId id;
    SIDE side;
    double price;
    unsigned long quantity;
};
struct OrderIndex
{
    OrderId id;
    double price;
};

auto higher_price_front_cmp_ = [](const OrderIndex &a, const OrderIndex &b)
{
    if (a.price > b.price)
    {
        return true;
    }
    if (a.price == b.price && a.id < b.id)
    {
        return true;
    }
    return false;
};

class OrderBook
{
private:
    std::set<OrderIndex, decltype(higher_price_front_cmp_)> buy_index_;
    std::set<OrderIndex, decltype(higher_price_front_cmp_)> sell_index_;
    std::map<OrderId, Order> order_book_;
    unsigned long last_order_id = 0;

public:
    OrderBook(/* args */);
    ~OrderBook();
    OrderId add_order(Order o)
    {
        Order order = std::move(o);

        switch (order.side)
        {
        case SIDE::BUY:
            order.id = ++last_order_id;
            buy_index_.emplace(OrderIndex{order.id, order.price});
            order_book_.emplace(order.id, std::move(order));
            break;
        case SIDE::SELL:
            order.id = ++last_order_id;
            sell_index_.emplace(OrderIndex{order.id, order.price});
            order_book_.emplace(order.id, std::move(order));
            break;
        default:
            throw std::runtime_error("invalid order type");
            break;
        }
        return last_order_id;
    }

    Order search_order(OrderId id)
    {
        auto order_iter = order_book_.find(id);
        if (order_iter == order_book_.end())
        {
            throw std::runtime_error("id not found");
        }

        return order_iter->second;
    }

    void cancel_order(OrderId id)
    {
        auto order_iter = order_book_.find(id);
        if (order_iter == order_book_.end())
        {
            throw std::runtime_error("id not found");
        }
        switch (order_iter->second.side)
        {
        case SIDE::BUY:
            buy_index_.erase(OrderIndex{id, order_iter->second.price});
            break;
        case SIDE::SELL:
            sell_index_.erase(OrderIndex{id, order_iter->second.price});
            break;
        default:
            throw std::runtime_error("invalid order type");
            break;
        }
        order_book_.erase(id);
    }

    void match()
    {
        std::set<OrderIndex, decltype(higher_price_front_cmp_)> order_to_remove(higher_price_front_cmp_);

        for (auto &[id, price] : buy_index_)
        {
            auto quantity = order_book_.at(id).quantity;
            if (quantity == 0)
            {
                continue;
            }
            for (auto &[sell_id, sell_price] : sell_index_)
            {
                if (sell_price <= price)
                {
                    auto sell_quantity = order_book_.at(sell_id).quantity;
                    if (sell_quantity == 0)
                    {
                        continue;
                    }
                    if (sell_quantity >= quantity)
                    {
                        if (sell_quantity == quantity)
                        {
                            order_to_remove.emplace(OrderIndex{sell_id, sell_price});
                        }
                        std::cout << "deal sell order [" << sell_id << "] at price " << sell_price
                                  << ", buy order [" << id << "] at price " << price << ". deal quantity " << quantity << std::endl;
                        order_to_remove.emplace(OrderIndex{id, price});

                        order_book_.at(sell_id).quantity = sell_quantity - quantity;
                        order_book_.at(id).quantity = 0;
                        quantity = 0;
                        break;
                    }
                    else if (sell_quantity < quantity)
                    {
                        std::cout << "deal sell order [" << sell_id << "] at price " << sell_price
                                  << ", buy order [" << id << "] at price " << price << ". deal quantity " << sell_quantity << std::endl;
                        order_to_remove.emplace(OrderIndex{sell_id, sell_price});
                        order_book_.at(sell_id).quantity = 0;
                        quantity -= sell_quantity;
                        order_book_.at(id).quantity = quantity;
                    }
                }
            }
        }

        for (const auto &order_index : order_to_remove)
        {
            if (sell_index_.erase(order_index) == 0)
            {
                buy_index_.erase(order_index);
            }
            order_book_.erase(order_index.id);
        }
        std::cout << "done" << std::endl;
        return;
    }

    void dump()
    {
        std::cout << "==== Sell Order ====" << std::endl;
        for (auto &o : sell_index_)
        {
            std::cout << o.price << " [" << o.id << "]" << std::endl;
        }
        std::cout << "==== Buy Order ====" << std::endl;
        for (auto &o : buy_index_)
        {
            std::cout << o.price << " [" << o.id << "]" << std::endl;
        }
    }
};

OrderBook::OrderBook(/* args */) : buy_index_(higher_price_front_cmp_), sell_index_(higher_price_front_cmp_)
{
}

OrderBook::~OrderBook()
{
}

int main()
{
    OrderBook book;
    book.add_order({0, SIDE::SELL, 10.0, 100});
    book.add_order({0, SIDE::BUY, 15.0, 10});
    book.add_order({0, SIDE::SELL, 20.0, 5});
    book.add_order({0, SIDE::BUY, 20.0, 100});
    book.add_order({0, SIDE::SELL, 100.0, 20});
    book.add_order({0, SIDE::BUY, 5.0, 10});
    book.dump();
    book.match();
    return 0;
}