#include <stdlib.h>
#include <array>
#include <iostream>
#include <string>
#include <sstream>

template <class T, size_t X, size_t Y>
class Matrix
{
public:
    std::array<T, X * Y> mt;

    template <size_t Z>
    Matrix<T, X, Z> operator*(const Matrix<T, Y, Z> &other)
    {
        Matrix<T, X, Z> res;

        for (size_t m = 0; m < X; m++)
        {
            for (size_t n = 0; n < Z; n++)
            {
                T sum = 0;
                for (size_t o = 0; o < Y; o++)
                {
                    sum += mt[m * Y + o] * other.mt[o * Z + n];
                }
                res.mt[m * Z + n] = sum;
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
                ss << mt[m * Y + n];
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
    Matrix<int, 2, 3>
        a{1, 2, 3, 4, 5, 6};

    Matrix<int, 3, 4> b{1, 2, 3, 4, 3, 4, 5, 6, 5, 6, 7, 8};
    std::cout << (a * b).show() << std::endl;
    return 0;
}