#include <memory>
#include <iostream>

class Parent;
class Child;

class Parent{
public:
    Parent() {std::cout << "construct parent" << std::endl;}
    ~Parent() {std::cout << "donstruct parent" << std::endl;}
    void set(std::shared_ptr<Child> c) {
        _child = c;
    }

    void count() {
        std::cout << "child " << _child.use_count() << std::endl;
    }
private:
    std::shared_ptr<Child> _child;
};



class Child{
public:
    Child() { std::cout << "construct child" << std::endl; }
    ~Child() { std::cout << "donstruct child" << std::endl; }

    void set(std::shared_ptr<Parent> p) {
        _parent = p;
    }

    std::shared_ptr<Parent> lock() {
        return _parent.lock();
    }

    void count() {
        std::cout << "parent " << _parent.use_count() << std::endl;
    }
private:
    std::weak_ptr<Parent> _parent;
};


int main()
{
    auto p1 = std::make_shared<Parent>();
    auto c1 = std::make_shared<Child>();
    p1->count();
    c1->count();

    p1->set(c1);
    c1->set(p1);

    p1->count();
    c1->count();

    {
        auto myparent = c1->lock();
        p1->count();
        c1->count();
    }

    p1->count();
    c1->count();
}