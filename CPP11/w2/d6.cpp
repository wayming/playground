#include <iostream>
#include <typeinfo>
#include <cxxabi.h>
#include <string_view>

template <typename T>
constexpr std::string_view type_name() {
#if defined(__clang__) || defined(__GNUC__)
    std::string_view p = __PRETTY_FUNCTION__;
    auto b = p.find("T = ") + 4;
    auto e = p.find(';', b);
    return p.substr(b, e - b);
#elif defined(_MSC_VER)
    std::string_view p = __FUNCSIG__;
    auto b = p.find("type_name<") + 10;
    auto e = p.rfind(">(");
    return p.substr(b, e - b);
#endif
}

template <class T>
void foo(T& t) {
    std::cout << type_name<decltype(t)>() << std::endl;
}


template <class T>
void foo(T&& t) {
    std::cout << type_name<decltype(t)>() << std::endl;
}


template <class T>
void wrap(T&& t) {
    std::cout << "forward " << type_name<decltype(std::forward<T>(t))>() << std::endl;

    foo(std::forward<T>(t));
}

int main()
{
    std::string str("abc");
    foo(str);
    foo(std::string("abc"));

    wrap(str);
    wrap(std::string("abc"));
}