#include <type_traits>
#include <unordered_map>
#include <string>

template <class A, class B>
concept Addable = requires(A a, B b) { a + b; };

template <int M, int L>
class Quantity
{
private:
    double v;

public:
    constexpr explicit Quantity(double d) : v(d) {}
    constexpr double value() const { return v; }
    friend constexpr Quantity<M, L> operator+(const Quantity<M, L> &left, const Quantity<M, L> &right)
    {
        return Quantity(left.value() + right.value());
    }
    friend constexpr Quantity<M, L> operator-(const Quantity<M, L> left, const Quantity<M, L> &right)
    {
        return Quantity(left.value() - right.value());
    }
    friend constexpr auto operator<=>(const Quantity<M, L> &left, const Quantity<M, L> &right) = default;
};
struct MeterTag
{
};
struct SecondTag
{
};
using Meters = Quantity<1, 0>;
using Seconds = Quantity<0, 1>;
using Speed = Quantity<1, -1>;
using Acceleration = Quantity<1, -2>;

template <class Tag, class T>
class StrongId
{
private:
    T v;

public:
    constexpr explicit StrongId(T t) : v(t) {}
    constexpr T value() const { return v; }
    constexpr friend auto operator<=>(const StrongId<Tag, T> &t1, const StrongId<Tag, T> &t2) = default;
};

template <class Tag, class T>
struct std::hash<StrongId<Tag, T>>
{
    size_t operator()(const StrongId<Tag, T> &k) const noexcept
    {
        return hash<T>{}(k.value());
    }
};
struct UserTag
{
};
struct OrderTag
{
};

namespace MyLiteral
{
    constexpr Meters operator""_m(long double d) { return Meters(static_cast<double>(d)); }
    constexpr Seconds operator""_s(long double d) { return Seconds(static_cast<double>(d)); }
    constexpr Meters operator""_m(unsigned long long l) { return Meters(static_cast<double>(l)); }
    constexpr Seconds operator""_s(unsigned long long l) { return Seconds(static_cast<double>(l)); }

    template <int M1, int L1, int M2, int L2>
    constexpr Quantity<M1 - M2, L1 - L2> operator/(Quantity<M1, L1> m, Quantity<M2, L2> s)
    {
        return Quantity<M1 - M2, L1 - L2>(m.value() / s.value());
    }
    template <int M1, int L1>
    constexpr Quantity<M1, L1> operator/(double d, Quantity<M1, L1> s)
    {
        return Quantity<M1, L1>(d / s.value());
    }
    template <int M1, int L1>
    constexpr Quantity<M1, L1> operator/(Quantity<M1, L1> s, double d)
    {
        return Quantity<M1, L1>(s.value() / d);
    }
    template <int M1, int L1, int M2, int L2>
    constexpr Quantity<M1 + M2, L1 + L2> operator*(Quantity<M1, L1> m, Quantity<M2, L2> s)
    {
        return Quantity<M1 + M2, L1 + L2>(m.value() * s.value());
    }
    template <int M1, int L1>
    constexpr Quantity<M1, L1> operator*(double d, Quantity<M1, L1> s)
    {
        return Quantity<M1, L1>(d / s.value());
    }
    template <int M1, int L1>
    constexpr Quantity<M1, L1> operator*(Quantity<M1, L1> s, double d)
    {
        return Quantity<M1, L1>(d * s.value());
    }

    static_assert(sizeof(Meters) == sizeof(double));
    static_assert(std::is_trivially_copyable_v<Meters>);
    static_assert(!std::is_convertible_v<double, Meters>);
    static_assert(std::is_same_v<decltype(1.0_m / 2.0_s), Speed>);
    static_assert(std::is_same_v<decltype(1.0_m / 2.0_s / 3.0_s), Acceleration>);

    static_assert(!Addable<Meters, Seconds>);
    static_assert(Addable<Meters, Meters>);
} // namespace MyLiteral

int main()
{

    constexpr Meters m1(1.0), m2(2.0);
    static_assert(m1 + m2 == Meters(3.0));

    using namespace MyLiteral;
    static_assert(2.0_m + 3.0_m == 5.0_m);
    static_assert(1_s + 3_s == 4_s);

    constexpr Speed v = 5_m / 2_s;
    static_assert(v == Speed(2.5));
    constexpr Acceleration a = v / 5_s;
    static_assert(a == Acceleration(0.5));

    static_assert(5_m * 2.5 == 12.5_m);

    using UserId = StrongId<UserTag, int>;
    using OrderId = StrongId<OrderTag, int>;
    static_assert(sizeof(UserId) == sizeof(int));
    static_assert(!std::is_convertible_v<UserId, OrderId>);

    std::unordered_map<UserId, std::string> users;
    users[UserId(1001)] = "user1";

    return 0;
}