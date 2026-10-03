#include <iostream>
#include <string>

class TestA {
public:
    void func1(const std::string& str) {
        std::cout << "lvalue ref " << str << std::endl;
    }
    void func1(std::string&& str) {
        std::cout << "rvalue ref " << str << std::endl;
    }

    template <typename T>
    void funcWrap(T&& v) {
        func1(std::forward<T>(v));
    }
};

int main() {
    TestA t;
    t.funcWrap(std::string("abc"));
    std::string v = "xyz";
    t.funcWrap(v);
    return 0;
}