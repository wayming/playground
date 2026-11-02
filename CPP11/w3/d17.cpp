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
namespace MyLiteral
{
    constexpr Meters operator""_m(long double d) { return Meters(static_cast<double>(d)); }
    constexpr Seconds operator""_s(long double d) { return Seconds(static_cast<double>(d)); }
    constexpr Meters operator""_m(unsigned long long l) { return Meters(static_cast<double>(l)); }
    constexpr Seconds operator""_s(unsigned long long l) { return Seconds(static_cast<double>(l)); }
    template <int M1, int L1, int M2, int L2>
    constexpr Quantity<M1 - M2, L1 - L2> operator/(Quantity<M1, L1> m, Quantity<M2, L2> s) { return Quantity<M1 - M2, L1 - L2>(m.value() / s.value()); }
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

    return 0;
}