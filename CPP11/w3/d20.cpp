#include <memory>
#include <numbers>
#include <vector>
#include <iostream>
#include <algorithm>
#include <iterator>

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

    void areas() const
    {
        for (auto &s : shapes)
        {
            std::cout << s->area() << "\n";
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
        s.areas();
        s2 = s;
    }
    s2.areas();
}