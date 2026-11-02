template <class Tag>
class Quantity
{
private:
    double v;

public:
    constexpr explicit Quantity(double d) : v(d) {}
    constexpr double value() const { return v; }
    friend constexpr Quantity<Tag> operator+(const Quantity<Tag> &left, const Quantity<Tag> &right)
    {
        return Quantity(left.value() + right.value());
    }
    friend constexpr Quantity<Tag> operator-(const Quantity<Tag> left, const Quantity<Tag> &right)
    {
        return Quantity(left.value() - right.value());
    }
    friend constexpr auto operator<=>(const Quantity<Tag> &left, const Quantity<Tag> &right) = default;
};
struct MeterTag
{
};
struct SecondTag
{
};
using Meters = Quantity<MeterTag>;
using Seconds = Quantity<SecondTag>;
namespace MyLiteral
{
    constexpr Meters operator""_m(long double d) { return Meters(static_cast<double>(d)); }
    constexpr Seconds operator""_s(long double d) { return Seconds(static_cast<double>(d)); }
    constexpr Meters operator""_m(unsigned long long l) { return Meters(static_cast<double>(l)); }
    constexpr Seconds operator""_s(unsigned long long l) { return Seconds(static_cast<double>(l)); }
} // namespace MyLiteral
int main()
{

    constexpr Meters m1(1.0), m2(2.0);
    static_assert(m1 + m2 == Meters(3.0));

    using namespace MyLiteral;
    static_assert(2.0_m + 3.0_m == 5.0_m);
    static_assert(1_s + 3_s == 4_s);
    return 0;
}