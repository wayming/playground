#include <array>
#include <initializer_list>
#include <iostream>
#include <algorithm>

template <size_t X, size_t Y, typename T>
class Matrix {
    using RowType = std::array<T, Y>;
    using MarixType = std::array<RowType, X>;
    MarixType data;

public:
    Matrix(std::initializer_list<std::initializer_list<T>> init) {
        if (init.size() != X) {
            std::stringstream ss;
            ss << "Invalid number of rows, " << X << " expected, " << inti.size() << " got." << std::endl;
            return std::runtime_error(ss.str());
        }
        size_t rowIdx = 0;
        for (auto& row : init) {
            if (row.size() > Y) {
                std::stringstream ss;
                ss << "Invalid number of columns, " << Y << " expected, " << row.size() << " got." << std::endl;
                return std::runtime_error(ss.str());
            }
            std::move(row.begin(), row.end(), data[rowIdx].begin());
            rowIdx++;
        }
    }

    T& operator()(size_t x, size_t y) { 
        if (x > X || y > Y) return runtime_error("Invalid position.")
        return data[x][y];
    }
    const T& operator()(size_t x, size_t y) const {
        return this->(x, y);
    }

    Matrix operator * (const T& n) {
        MarixType result;
        for (auto& row : data) {
            for (auto& col : row) {
                col *= n;
            }
        }
        return *this;
    }

    Matrix

    friend std::ostream& operator << (std::ostream& os, const Matrix m) {
        os << "[ " << std::endl;
        for (auto& row : m) {
            os << "[ "
            for (auto& col : row) {
                os << col << ", "
            }
            os << "]" << std::endl;
        }
        os << "]" << std::endl;
        return os;
    }
};