#include <stdlib.h>
#include <array>
#include <iostream>
#include <string>
#include <sstream>

template <class T, size_t X, size_t Y>
class Matrix
{
public:
    std::array<std::array<T, Y>, X> mt;

    template <size_t Z>
    Matrix<T, X, Z> operator*(const Matrix<T, Y, Z> &other)
    {
        Matrix<T, X, Z> res;

        for (size_t m = 0; m < X; m++)
        {
            for (size_t n = 0; n < Y; n++)
            {
                for (size_t o = 0; o < Z; o++)
                {
                    T sum = 0;

                    for (size_t p = 0; p < X; p++)
                    {
                        sum += mt[m][n] * other.mt[p][o];
                    }
                    res.mt[m][o] = sum;
                }
            }
        }
        return res;
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
                ss << mt[m][n];
                first = false;
            }
            ss << "]" << std::endl;
        }
        ss << "]" << std::endl;

        return ss.str();
    }
};

int main()
{
    Matrix<int, 2, 3> a{{std::array<int, 3>{1, 2, 3}, std::array<int, 3>{4, 5, 6}}};
    Matrix<int, 3, 4> b{{std::array<int, 4>{1, 2, 3, 4}, std::array<int, 4>{3, 4, 5, 6}, std::array<int, 4>{5, 6, 7, 8}}};
    std::cout << (a * b).show() << std::endl;
    return 0;
}