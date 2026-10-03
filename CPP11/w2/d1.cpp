#include <iostream>
#include <memory>
class Test {
public:
    Test(const std::string& s) : p(std::make_shared<std::string>(s)) {}
    ~Test() noexcept = default;

    Test(const Test& t): p(t.p) {}

    Test& operator= (const Test& t) noexcept {
        if (&t != this) {
            p = t.p;
        }
        return *this;
    }

    Test(Test&& t) noexcept : p(std::move(t.p)) {}

    Test& operator= (Test&& t) noexcept {
        if (&t != this) {
            p = std::move(t.p);
        }   
        return *this;
    }
    void shared() noexcept {
        if (p) {
            std::cout << *p << ":" << p.use_count() << std::endl;
        } else {
            std::cout << 0 << std::endl;
        }
    }
private:
    std::shared_ptr<std::string> p;
};

int main() {
    Test t1("abc");
    Test t2("xyz");
    t1.shared();
    t2.shared();
    Test t3(t1);
    t1.shared();
    t3.shared();
    Test t4 = t3;
    t1.shared();
    t3.shared();
    t4.shared();
    Test t5(std::move(t2));
    t2.shared();
    t5.shared();


    Test t11("abc");
    Test t12 = t11;
    Test t13 = std::move(t11);
    t11.shared();
    t12.shared();
    t13.shared();
}