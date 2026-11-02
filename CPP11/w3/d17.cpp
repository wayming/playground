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
    friend constexpr bool operator==(const Quantity<Tag> left, const Quantity<Tag> &right)
    {
        return left.value() == right.value();
    }
};

int main()
{
    struct MeterTag
    {
    };
    struct SecondTag
    {
    };
    using Meters = Quantity<MeterTag>;
    using Seconds = Quantity<SecondTag>;
    constexpr Meters m1(1.0), m2(2.0);
    static_assert(m1 + m2 == Meters(3.0));
    return 0;
}