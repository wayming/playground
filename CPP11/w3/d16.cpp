#include <stdlib.h>
#include <array>
#include <iostream>
#include <string>
#include <sstream>
#include <type_traits>
#include <format>

template <class T, size_t X, size_t Y>
class Matrix
{
private:
    std::array<T, X * Y> mt;

public:
    constexpr Matrix() = default;
    constexpr Matrix(std::initializer_list<T> elements)
    {
        if (elements.size() != X * Y)
            throw std::runtime_error(std::format(
                "invalid number of elements, {} expected, {} got", X * Y, elements.size()));
        std::move(elements.begin(), elements.end(), mt.begin());
    }
    template <size_t Z>
    constexpr Matrix<T, X, Z> operator*(const Matrix<T, Y, Z> &other) const
    {
        Matrix<T, X, Z> res;

        for (size_t m = 0; m < X; m++)
        {
            for (size_t n = 0; n < Z; n++)
            {
                T sum = 0;
                for (size_t o = 0; o < Y; o++)
                {
                    sum += (*this)(m, o) * other(o, n);
                }
                res(m, n) = sum;
            }
        }
        return res;
    }

    constexpr T &operator()(size_t x, size_t y) { return mt[x * Y + y]; }
    constexpr const T &operator()(size_t x, size_t y) const { return mt[x * Y + y]; }

    constexpr bool operator==(const Matrix<T, X, Y> &other) const
    {
        return mt == other.mt;
    }
    std::string show()
    {
        std::stringstream ss;
        ss << "[" << std::endl;
        for (size_t m = 0; m < X; m++)
        {
            bool first = true;
            ss << "[";
            for (size_t n = 0; n < Y; n++)
            {
                if (!first)
                    ss << ", ";
                ss << (*this)(m, n);
                first = false;
            }
            ss << "]" << std::endl;
        }
        ss << "]" << std::endl;

        return ss.str();
    }
};
template <class X, class Y>
concept CanMultiply = requires(X x, Y y) { x * y; };
int main()
{
    constexpr Matrix<int, 2, 3> a{1, 2, 3, 4, 5, 6};

    constexpr Matrix<int, 3, 4> b{1, 2, 3, 4, 3, 4, 5, 6, 5, 6, 7, 8};
    constexpr Matrix<int, 2, 4> c{22, 28, 34, 40, 49, 64, 79, 94};
    static_assert((a * b) == c);
    static_assert(CanMultiply<Matrix<int, 2, 3>, Matrix<int, 3, 14>>);
    return 0;
}