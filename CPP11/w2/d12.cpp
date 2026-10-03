#include <memory>
#include <iostream>
#include <stdio.h>
#include <string.h>
#include <cassert>
#include <utility>
template <class T>
class SimpleVector
{
private:
    std::unique_ptr<T[]> array_;
    size_t cap_;
    size_t size_;

private:
    void resize(size_t s);

public:
    SimpleVector(const T &t, size_t s);
    explicit SimpleVector(size_t s);
    SimpleVector(const SimpleVector &v);
    SimpleVector(SimpleVector &&v) noexcept;
    SimpleVector &operator=(const SimpleVector &v);
    SimpleVector &operator=(SimpleVector &&v) noexcept;
    ~SimpleVector();

    void push_back(const T &t);
    void push_back(T &&t);
    T pop_back();
    void dump() const;
};

template <class T>
SimpleVector<T>::SimpleVector(const T &t, size_t s) : cap_(s)
{
    assert(s > 0);

    array_ = std::make_unique<T[]>(s);
    for (size_t i = 0; i < cap_; i++)
    {
        array_[i] = t;
    }
    size_ = cap_;
}

template <class T>
SimpleVector<T>::SimpleVector(size_t s) : cap_(s), array_(std::make_unique<T[]>(s)), size_(0)
{
    assert(s > 0);
}

template <class T>
SimpleVector<T>::SimpleVector(const SimpleVector &v) : cap_(v.cap_), array_(std::make_unique<T[]>(v.cap_)), size_(v.size_)
{
    std::copy(v.array_.get(), v.array_.get() + v.size_, array_.get());
}

template <class T>
SimpleVector<T>::SimpleVector(SimpleVector &&v) noexcept : cap_(v.cap_), array_(std::move(v.array_)), size_(v.size_)
{
    v.cap_ = 0;
    v.size_ = 0;
}

template <class T>
SimpleVector<T> &SimpleVector<T>::operator=(const SimpleVector &v)
{
    if (&v == this)
        return *this;
    array_ = std::make_unique<T[]>(v.cap_);
    std::copy(v.array_.get(), v.array_.get() + v.size_, array_.get());
    cap_ = v.cap_;
    size_ = v.size_;
    return *this;
}

template <class T>
SimpleVector<T> &SimpleVector<T>::operator=(SimpleVector &&v) noexcept
{
    if (&v == this)
        return *this;
    array_ = std::move(v.array_);
    cap_ = v.cap_;
    size_ = v.size_;
    v.cap_ = 0;
    v.size_ = 0;
    return *this;
}

template <class T>
SimpleVector<T>::~SimpleVector()
{
    array_.reset();
}

template <class T>
void SimpleVector<T>::resize(size_t s)
{
    assert(s > 0);
    if (s > cap_)
    {
        std::unique_ptr<T[]> nptr = std::make_unique<T[]>(s);
        std::move(array_.get(), array_.get() + size_, nptr.get());
        array_.swap(nptr);
        cap_ = s;
    }
}

template <class T>
void SimpleVector<T>::push_back(const T &t)
{
    if (size_ >= cap_)
    {
        resize(cap_ == 0 ? 1 : (2 * cap_));
    }
    array_[size_] = t;
    size_++;
}

template <class T>
void SimpleVector<T>::push_back(T &&t)
{
    if (size_ >= cap_)
    {
        resize(cap_ == 0 ? 1 : (2 * cap_));
    }
    array_[size_] = std::move(t);
    size_++;
}

template <class T>
T SimpleVector<T>::pop_back()
{
    if (size_ <= 0)
    {
        throw std::runtime_error("empty vector");
    }
    T t = std::move(array_[size_ - 1]);
    size_--;
    return t;
}

template <class T>
void SimpleVector<T>::dump() const
{
    for (size_t i = 0; i < size_; i++)
    {
        std::cout << array_[i] << " ";
    }
    std::cout << std::endl;
    std::cout << "size:" << size_ << " cap:" << cap_ << std::endl;
}

int main()
{
    SimpleVector<std::string> v("first", 10);
    v.dump();
    v.push_back("second");
    v.push_back("third");
    v.dump();
    std::cout << v.pop_back() << std::endl;
    v.dump();
}