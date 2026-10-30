#include <unordered_map>
#include <functional>
#include <string>
#include <memory>
#include <numbers>
#include <iostream>
#include <utility>
#include <format>
#include <concepts>
#include <stdexcept>

struct Shape
{
    virtual ~Shape() = default;
    virtual double area() const = 0;
};

template <class Base, class... Args>
class Factory
{

private:
    using Creator = std::function<std::unique_ptr<Base>(Args...)>;

    static std::unordered_map<std::string, Creator> &registry()
    {
        static std::unordered_map<std::string, Creator> register_;
        return register_;
    }

public:
    class Registrar
    {
    public:
        template <std::derived_from<Base> T>
            requires std::constructible_from<T, Args...>
        Registrar(std::string name, std::in_place_type_t<T>)
        {
            auto creator = [](Args... args) -> std::unique_ptr<Base>
            { return std::make_unique<T>(std::forward<Args>(args)...); };
            if (!Factory::reg(name, std::move(creator)))
            {
                throw std::runtime_error(std::format("Failed to register creator for {}", name));
            };
        }
    };
    static bool reg(std::string name, Creator creator)
    {
        return Factory::registry().emplace(std::move(name), std::move(creator)).second;
    }
    static std::unique_ptr<Base> create(const std::string &name, Args... args)
    {
        auto find = Factory::registry().find(name);
        if (find != Factory::registry().end())
        {
            return find->second(std::forward<Args>(args)...);
        }
        return nullptr;
    }
};

template <class Base, class Derived, class... Args>
struct AutoRegister
{
    static const inline typename Factory<Base, Args...>::Registrar registrar{Derived::name, std::in_place_type<Derived>};
};

struct Circle final : Shape, AutoRegister<Shape, Circle, double>
{
private:
    double r_;

public:
    static constexpr const char *name{"Circle"};
    explicit Circle(double d) : r_(d) {}
    double area() const override { return std::numbers::pi * r_ * r_; }
};
template struct AutoRegister<Shape, Circle, double>;

int main()
{
    auto circle1 = Factory<Shape, double>::create("Circle", 2.0);
    if (circle1)
        std::cout << circle1->area() << std::endl;
    std::cout << (Factory<Shape, double>::create("CircleX", 2.0) ? "found" : "not found") << std::endl;
    return 0;
}