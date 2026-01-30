#include <array>
#include <initializer_list>
#include <iostream>
#include <algorithm>

template <size_t X, size_t Y, typename T>
class Matrix {
    using RowType = std::array<T, Y>;
    using MatrixType = std::array<RowType, X>;
    MatrixType data = {};

public:
    Matrix() = default;
    Matrix(std::initializer_list<std::initializer_list<T>> init) {
        if (init.size() != X) {
            std::stringstream ss;
            ss << "Invalid number of rows, " << X << " expected, " << init.size() << " got." << std::endl;
            throw std::runtime_error(ss.str());
        }
        size_t rowIdx = 0;
        for (auto& row : init) {
            if (row.size() > Y) {
                std::stringstream ss;
                ss << "Invalid number of columns, " << Y << " expected, " << row.size() << " got." << std::endl;
                throw std::runtime_error(ss.str());
            }
            // Element in initializer_list is const type. Can not be moved. Degraded to copy.
            std::copy(row.begin(), row.end(), data[rowIdx].begin());
            rowIdx++;
        }
    }

    T& operator()(size_t x, size_t y) { 
        if (x >= X || y >= Y) throw std::out_of_range("Invalid position.");
        return data[x][y];
    }
    const T& operator()(size_t x, size_t y) const {
        return const_cast<Matrix*>(this)->operator()(x,y);
    }

    Matrix operator* (const T& n) {
        Matrix result = *this;
        for(auto& row : result.data) {
            for(auto& col : row) {
                col *= n;
            }
        }
        return result;
    }

    Matrix operator*(const Matrix& other) {
        Matrix result;
        for(int x = 0; x < X; ++x) {
            for(int y = 0; y < Y; ++ y) {
                result.data[x][y] = data[x][y] * other.data[x][y];
            }
        }
        return result;
    }

    Matrix operator+(const Matrix& other) {
        Matrix result;
        for(int x = 0; x < X; ++x) {
            for(int y = 0; y < Y; ++ y) {
                result.data[x][y] = data[x][y] + other.data[x][y];
            }
        }
        return result;
    }


    friend std::ostream& operator<< (std::ostream& os, const Matrix& m) {
        os << "[ " << std::endl;
        for (auto& row : m.data) {
            os << "  [ ";
            for (auto& col : row) {
                os << col << ", ";
            }
            os << "]" << std::endl;
        }
        os << "]" << std::endl;
        return os;
    }
};