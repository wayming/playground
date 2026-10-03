#include <vector>
#include <iostream>
#include <variant>
#include <numbers>
struct Circle
{
    double diameter;
    double area() const { return std::numbers::pi * 0.25 * diameter * diameter; }
};
struct Rectangle
{
    double width;
    double length;
    double area() const { return width * length; }
};

using Shape = std::variant<Circle, Rectangle>;
double calc_area(const Shape &s)
{
    return std::visit([](auto &&v)
                      { return v.area(); }, s);
}
int main()
{
    std::vector<Shape> shapes{
        Circle{5.0}, Rectangle{2.0, 3.0}};

    for (const auto &s : shapes)
    {
        std::cout << calc_area(s) << std::endl;
    }
}