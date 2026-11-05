#include <memory>
#include <numbers>
#include <vector>
#include <iostream>

class Shape
{
public:
    virtual ~Shape() = default;
    virtual double area() = 0;
};

class Circle : public Shape
{
private:
    double radius = 0.0;

public:
    Circle(double r) : radius(r) {}
    double area()
    {
        return std::numbers::pi * radius * radius;
    }
};

class Rectangle : public Shape
{
private:
    double x = 0.0;
    double y = 0.0;

public:
    Rectangle(double width, double length) : x(width), y(length) {}
    double area()
    {
        return x * y;
    }
};

class Scene
{
private:
    std::vector<std::unique_ptr<Shape>> shapes;

public:
    void add(std::unique_ptr<Shape> s)
    {
        shapes.push_back(std::move(s));
    }

    void areas()
    {
        for (auto &s : shapes)
        {
            std::cout << s->area() << std::endl;
        }
    }
};

int main()
{
    Scene s;
    s.add(std::make_unique<Circle>(2.0));
    s.add(std::make_unique<Rectangle>(5.0, 6.0));
    s.areas();
}