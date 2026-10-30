#include <unordered_map>
#include <functional>
#include <string>
#include <memory>
#include <numbers>
#include <iostream>
#include <utility>

struct Shape
{
    virtual ~Shape() = default;
    virtual double area() const = 0;
};

using ShapeCreator = std::function<std::unique_ptr<Shape>(double)>;

class ShapeFactory
{

private:
    static std::unordered_map<std::string, ShapeCreator> &registry()
    {
        static std::unordered_map<std::string, ShapeCreator> register_;
        return register_;
    }

public:
    template <std::derived_from<Shape> T>
        requires std::constructible_from<T, double>
    class Registar
    {
    public:
        Registar(std::string name, std::in_place_type_t<T>)
        {
            auto creator = [](double d)
            { return std::make_unique<T>(d); };
            ShapeFactory::reg(std::move(name), std::move(creator));
        }
    };
    static bool reg(std::string name, ShapeCreator creator)
    {
        return ShapeFactory::registry().emplace(std::move(name), std::move(creator)).second;
    }
    static std::unique_ptr<Shape> create_shape(const std::string &name, double x)
    {
        auto find = ShapeFactory::registry().find(name);
        if (find != ShapeFactory::registry().end())
        {
            return find->second(x);
        }
        return nullptr;
    }
};

template <class T>
struct AutoRegister
{
    static const inline ShapeFactory::Registar registar{T::name, std::in_place_type<T>};
};

struct Circle final : Shape
{
private:
    double r_;

public:
    static constexpr std::string name{"Circle"};
    explicit Circle(double d) : r_(d) {}
    double area() const override { return std::numbers::pi * r_ * r_; }
};
template struct AutoRegister<Circle>;

int main()
{
    auto circle1 = ShapeFactory::create_shape("Circle", 2.0);
    std::cout << circle1->area() << std::endl;
    std::cout << (ShapeFactory::create_shape("CircleX", 2.0) ? "found" : "not found") << std::endl;
    return 0;
}