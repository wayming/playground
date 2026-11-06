#include <memory>
#include <numbers>
#include <vector>
#include <iostream>
#include <algorithm>
#include <iterator>
#include <ranges>

class Shape
{
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    std::unique_ptr<Shape> clone() const
    {
        return std::unique_ptr<Shape>(clone_impl());
    }

protected:
    Shape() = default;
    Shape(const Shape &) = default;
    Shape(Shape &&) = default;
    Shape &operator=(const Shape &) = default;
    Shape &operator=(Shape &&) = default;

    virtual Shape *clone_impl() const = 0;
};

class Circle final : public Shape
{
private:
    double radius = 0.0;
    Circle *clone_impl() const override
    {
        return new Circle(*this);
    }

public:
    explicit Circle(double r) : radius(r) {}
    double area() const override
    {
        return std::numbers::pi * radius * radius;
    }
};

class Rectangle final : public Shape
{
private:
    double x = 0.0;
    double y = 0.0;

    Rectangle *clone_impl() const override
    {
        return new Rectangle(*this);
    }

public:
    explicit Rectangle(double width, double length) : x(width), y(length) {}
    double area() const override
    {
        return x * y;
    }
};

class Scene
{
private:
    std::vector<std::unique_ptr<Shape>> shapes;
    void clone(const Scene &s)
    {
        shapes.clear();
        shapes.reserve(s.shapes.size());
        std::transform(s.shapes.begin(), s.shapes.end(), std::back_inserter(shapes),
                       [](const std::unique_ptr<Shape> &from)
                       {
                           return from->clone();
                       });
    }

public:
    Scene() = default;

    Scene(const Scene &s)
    {
        shapes.reserve(s.shapes.size());
        for (const auto &shape : s.shapes)
        {
            shapes.push_back(shape->clone());
        }
    }
    Scene(Scene &&s) noexcept = default;

    Scene &operator=(const Scene &s)
    {
        Scene tmp(s);
        *this = std::move(tmp);
        return *this;
    }

    Scene &operator=(Scene &&s) noexcept = default;

    void add(std::unique_ptr<Shape> s)
    {
        if (s)
        {
            shapes.push_back(std::move(s));
        }
    }

    template <std::derived_from<Shape> T, class... Args>
    void emplace(Args &&...args)
    {
        shapes.emplace_back(std::make_unique<T>(std::forward<Args>(args)...));
    }

    void remove_at(size_t s)
    {
        if (s >= shapes.size())
            throw std::range_error("invalid index specified");
        shapes.erase(shapes.begin() + s);
    }

    size_t const size() const { return shapes.size(); }

    void areas() const
    {
        for (auto &s : shapes)
        {
            std::cout << s->area() << "\n";
        }
    }

    void sort_by_areas()
    {
        std::ranges::sort(shapes, {}, &Shape::area);
    }

    size_t count_circles() const
    {
        return std::ranges::count_if(shapes.begin(), shapes.end(), [](const auto &ptr)
                                     { return (dynamic_cast<const Circle *>(ptr.get()) != nullptr); });
    }

    template <class F>
    void for_each_circle(F f) const
    {
        for (const auto &s : shapes)
        {
            auto c = dynamic_cast<const Circle *>(s.get());
            if (c)
                f(*c);
        }
    }
};

int main()
{
    Scene s2;
    {
        Scene s;
        s.add(std::make_unique<Circle>(2.0));
        s.add(std::make_unique<Rectangle>(5.0, 6.0));
        s.emplace<Rectangle>(1.0, 2.0);
        s.areas();
        s2 = s;
    }
    s2.sort_by_areas();
    s2.areas();
    std::cout << s2.count_circles() << std::endl;

    size_t counter = 0;
    s2.for_each_circle([&counter](const Circle &c)
                       { std::cout << "circle" << ++counter << ", area " << c.area() << std::endl; });
}