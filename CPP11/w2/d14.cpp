#include <stdlib.h>
#include <exception>
#include <iostream>
class InsufficientBalance : public std::exception
{
public:
    const char *what() const noexcept override { return "not enough balance"; }
};
class ExceedAccountCap : public std::exception
{
public:
    const char *what() const noexcept override { return "exceed account cap amount"; }
};
class Account
{
private:
    int balance_;

public:
    Account(int init_val) : balance_(init_val) {};
    ~Account() = default;
    void credit(int val)
    {
        if (val + balance_ > 1000)
        {
            throw ExceedAccountCap();
        }
        balance_ += val;
    }
    void debit(int val)
    {
        if (balance_ < val)
        {
            throw InsufficientBalance();
        }

        balance_ -= val;
    }
    void force_credit(int val) noexcept { balance_ += val; }
    void force_debit(int val) noexcept { balance_ -= val; }
    void show() const { std::cout << balance_ << std::endl; }
};

class TransferGuard
{
private:
    bool from_commit_ = false;
    bool to_commit_ = false;
    Account &from_;
    Account &to_;
    int amount_;

public:
    TransferGuard(Account &from, Account &to, int transfer) : from_(from), to_(to), amount_(transfer) {}
    ~TransferGuard()
    {
        if (from_commit_ && to_commit_)
        {
            return;
        }
        else if (from_commit_)
        {
            from_.force_credit(amount_);
        }
        else if (to_commit_)
        {
            to_.force_debit(amount_);
        }
    }
    void from_commit() { from_commit_ = true; }
    void to_commit() { to_commit_ = true; }
};
void transfer(Account &from, Account &to, int transfer)
{
    if (transfer <= 0)
    {
        return;
    }
    TransferGuard g(from, to, transfer);
    from.debit(transfer);
    g.from_commit();
    to.credit(transfer);
    g.to_commit();
}
int main()
{
    Account a(400);
    Account b(800);
    try
    {
        transfer(a, b, 300);
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
    }
    a.show();
    b.show();

    try
    {
        transfer(a, b, 100);
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
    }
    a.show();
    b.show();

    try
    {

        transfer(a, b, 400);
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
    }
    a.show();
    b.show();
}
