#include <array>
#include <initializer_list>
#include <iostream>

template <size_t X, size_t Y, typename T>
class Matrix {
public:
    using row = std::array<T, Y>;

    Matrix(std::initializer_list<std::initializer_list<T>> m) {
        for (auto& r : data) {
            r.fill(T{});
        }

        int x = std::min(X, m.size());
        int i = 0;
        for (auto rowIt = m.begin(); rowIt != m.end() && i < x; ++rowIt, ++i) {
            int y = std::min(Y, rowIt->size());
            std::copy(rowIt->begin(), rowIt->begin() + y, data[i].begin());
        }
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
private:
    std::array<row, X> data;
};