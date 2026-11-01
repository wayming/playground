#include <stdlib.h>
#include <array>
#include <iostream>
#include <string>
#include <sstream>
#include <type_traits>
#include <format>

template <class D>
struct MatExpr
{
};

template <class T>
using Bare = std::remove_cvref_t<T>;
template <class E>
concept MatrixExpr = std::derived_from<E, MatExpr<E>>;

template <class L, class R>
    requires MatrixExpr<Bare<L>> && MatrixExpr<Bare<R>>
struct MatExprAdd : MatExpr<MatExprAdd<L, R>>
{
    using value_type = Bare<L>::value_type;
    static constexpr size_t rows = Bare<L>::rows;
    static constexpr size_t cols = Bare<L>::cols;
    const L left;
    const R right;

    template <class X, class Y>
    constexpr MatExprAdd(X &&x, Y &&y) : left(std::forward<X>(x)), right(std::forward<Y>(y)) {}
    constexpr value_type operator()(size_t x, size_t y) const
    {
        return left(x, y) + right(x, y);
    }
};
template <class T, size_t X, size_t Y>
class Matrix : public MatExpr<Matrix<T, X, Y>>
{
private:
    std::array<T, X * Y> mt;

public:
    using value_type = T;
    static constexpr size_t rows = X;
    static constexpr size_t cols = Y;
    constexpr Matrix() = default;
    constexpr Matrix(std::initializer_list<T> elements)
    {
        if (elements.size() != X * Y)
            throw std::runtime_error(std::format(
                "invalid number of elements, {} expected, {} got", X * Y, elements.size()));
        std::move(elements.begin(), elements.end(), mt.begin());
    }
    template <MatrixExpr E>
        requires(E::rows == X && E::cols == Y)
    constexpr Matrix(const E &e)
    {
        for (size_t x = 0; x < rows; x++)
        {
            for (size_t y = 0; y < cols; y++)
            {
                (*this)(x, y) = e(x, y);
            }
        }
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

template <class T>
using ReferenceOrValue = std::conditional_t<
    std::is_lvalue_reference_v<T>, const Bare<T> &, Bare<T>>;

template <class L, class R>
    requires MatrixExpr<Bare<L>> && MatrixExpr<Bare<R>> &&
             (Bare<L>::rows == Bare<R>::rows && Bare<L>::cols == Bare<R>::cols)
constexpr MatExprAdd<ReferenceOrValue<L>, ReferenceOrValue<R>> operator+(L &&left, R &&right)
{
    return MatExprAdd<ReferenceOrValue<L>, ReferenceOrValue<R>>{std::forward<L>(left), std::forward<R>(right)};
}

template <class X, class Y>
concept CanMultiply = requires(X x, Y y) { x * y; };
int main()
{
    constexpr Matrix<int, 2, 3> a{1, 2, 3, 4, 5, 6};
    constexpr Matrix<int, 2, 3> a2{1, 2, 3, 4, 5, 6};
    constexpr Matrix<int, 2, 3> a3{1, 2, 3, 4, 5, 6};

    constexpr Matrix<int, 3, 4> b{1, 2, 3, 4, 3, 4, 5, 6, 5, 6, 7, 8};
    constexpr Matrix<int, 2, 4> c{22, 28, 34, 40, 49, 64, 79, 94};
    static_assert((a * b) == c);
    static_assert(CanMultiply<Matrix<int, 2, 3>, Matrix<int, 3, 14>>);

    constexpr Matrix<int, 2, 3> sum = a + a2 + a3;
    constexpr auto expected = Matrix<int, 2, 3>{3, 6, 9, 12, 15, 18};
    static_assert(sum == expected);
    return 0;
}