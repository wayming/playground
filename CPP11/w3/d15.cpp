#include <unordered_map>
#include <functional>
#include <string>
#include <memory>
#include <numbers>
#include <iostream>

struct Shape
{
    virtual ~Shape() = default;
    virtual double area() const = 0;
};

using ShapeCreator = std::function<std::unique_ptr<Shape>(double)>;

class ShapeFactory
{

private:
    std::unordered_map<std::string, ShapeCreator> register_;

public:
    bool reg(std::string name, ShapeCreator creator)
    {
        return register_.emplace(std::move(name), std::move(creator)).second;
    }
    std::unique_ptr<Shape> create_shape(const std::string &name, double x)
    {
        auto find = register_.find(name);
        if (find != register_.end())
        {
            return find->second(x);
        }
        return nullptr;
    }
};

struct Circle final : Shape
{
private:
    double r_;

public:
    explicit Circle(double d) : r_(d) {}
    double area() const override { return std::numbers::pi * r_ * r_; }
};

int main()
{
    ShapeFactory fac;
    fac.reg("Circle", [](double d) -> std::unique_ptr<Shape>
            { return std::make_unique<Circle>(d); });
    auto circle1 = fac.create_shape("Circle", 2.0);
    std::cout << circle1->area() << std::endl;
    std::cout << (fac.create_shape("CircleX", 2.0) ? "found" : "not found") << std::endl;
    return 0;
}