#include <array>
#include <initializer_list>
#include <iostream>
#include <algorithm>

template <size_t X, size_t Y, typename T>
class Matrix {
public:
    using row = std::array<T, Y>;

    Matrix(std::initializer_list<std::initializer_list<T>> m) : data{} { // init data
        int x = std::min(X, m.size());
        int i = 0;
        for (auto rowIt = m.begin(); rowIt != m.end() && i < x; ++rowIt, ++i) {
            int y = std::min(Y, rowIt->size());
            std::copy(rowIt->begin(), rowIt->begin() + y, data[i].begin());
        }
    }

    // custom constructor shadows default constructor, so declare explicitly.
    Matrix() = default;
    // Matrix(const Matrix&) = default;
    // Matrix(const Matrix&) { std::cout << "copy" << std::endl; }
    // Matrix(Matrix&&) { std::cout << "move" << std::endl; }
    // Matrix& operator=(const Matrix&) { std::cout << "copy assgin" << std::endl; return *this; }
    // Matrix& operator=(Matrix&&) { std::cout << "move assgin" << std::endl; return *this; }

    constexpr T& operator()(size_t x, size_t y) {
        return data[x][y];
    }

    constexpr const T& operator()(size_t x, size_t y) const {
        return data[x][y];
    }

    Matrix<X, Y, T> operator+(const Matrix<X, Y, T>& other) {
        Matrix<X, Y, T> result;
        for (int x = 0; x < data.size(); ++x) {
            for (int y = 0; y < data[0].size(); ++y) {
                result.data[x][y] = data[x][y] + other.data[x][y];
            }
        }
        return result;
    }

    Matrix<X, Y, T> operator*(const Matrix<X, Y, T>& other) {
        Matrix<X, Y, T> result;
        for (int x = 0; x < data.size(); ++x) {
            for (int y = 0; y < data[0].size(); ++y) {
                result.data[x][y] = data[x][y] * other.data[x][y];
            }
        }
        return result;
    }

    Matrix<X, Y, T>& operator*(const T& op) {
        std::for_each(data.begin(), data.end(), [&op](auto& row){
            std::for_each(row.begin(), row.end(), [&op](auto& col) { col = col * op; });
        });

        return *this;
    }
    void print() {
        std::cout << "[" << std::endl;
        for (auto& row : data) {
            std::cout << "  [";
            int idx = 0;
            for (auto& e : row) {
                std::cout << e;
                if (idx++ < row.size() - 1) {
                    std::cout << ", ";
                }
            }
            std::cout << "]" << std::endl;
        }
        std::cout << "]" << std::endl;
    }

    friend std::ostream& operator<<(std::ostream& os, Matrix<X, Y, T>& matrix) {
        os << "[" << std::endl;
        for (auto& row : matrix.data) {
            os << "  [";
            int idx = 0;
            for (auto& e : row) {
                os << e;
                if (idx++ < row.size() - 1) {
                    os << ", ";
                }
            }
            os << "]" << std::endl;
        }
        os << "]" << std::endl;
        return os;
    }
private:
    std::array<row, X> data;
};