#include <variant>
#include <numbers>
#include <vector>
#include <ranges>
#include <algorithm>
#include <iostream>
struct Circle
{
    double radius;
    double area() const { return std::numbers::pi * radius * radius; }
};

struct Rectangle
{
    double width;
    double length;
    double area() const { return width * length; }
};

using Shape = std::variant<Circle, Rectangle>;

class Scene
{
private:
    std::vector<Shape> shapes;

public:
    void add(Shape s)
    {
        shapes.push_back(std::move(s));
    }

    template <class T, class... Args>
        requires std::constructible_from<Shape, std::in_place_type_t<T>, Args...>
    T &emplace(Args &&...args)
    {
        return std::get<T>(shapes.emplace_back(std::in_place_type<T>, std::forward<Args>(args)...));
    }

    void remove_at(size_t s)
    {
        if (s >= shapes.size())
            throw std::range_error("invalid index specified");
        shapes.erase(shapes.begin() + s);
    }

    double area(const Shape &s) const
    {
        return std::visit([](const auto &x)
                          { return x.area(); }, s);
    }

    void areas() const
    {
        for (auto &s : shapes)
        {
            std::cout << area(s) << "\n";
        }
    }
    void sort_by_area()
    {
        std::ranges::sort(shapes, {}, [this](const Shape &s)
                          { return area(s); });
    }
};

int main()
{
    Scene s1;
    s1.add(Circle{2.0});
    s1.add(Rectangle{2.0, 3.0});
    s1.emplace<Circle>(4.0);
    s1.emplace<Rectangle>(1.0, 2.0);

    s1.areas();
    s1.sort_by_area();
    s1.areas();
    return 0;
}