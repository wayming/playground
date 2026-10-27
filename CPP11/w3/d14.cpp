#include <memory>
#include <iostream>
#include <algorithm>
#include <cstring>
#include <type_traits>
#include <stdexcept>

template <class T, size_t N>
class SmallVector
{
public:
    using iterator = T *;
    using const_iterator = const T *;

private:
    alignas(T) std::byte buffer[N * sizeof(T)];
    T *tdata;
    size_t size_;
    size_t cap_;
    static void relocate(T *src, size_t n, T *dest) noexcept(std::is_trivially_copyable_v<T> || std::is_nothrow_move_constructible_v<T>)
    {
        if constexpr (std::is_trivially_copyable_v<T>)
        {
            std::memcpy(static_cast<void *>(dest), static_cast<void *>(src), n * sizeof(T));
        }
        else if constexpr (std::is_nothrow_move_constructible_v<T> || !std::is_copy_constructible_v<T>)
        {
            std::uninitialized_move_n(src, n, dest);
        }
        else
        {
            std::uninitialized_copy_n(src, n, dest);
        }
    }

public:
    SmallVector() : tdata(inline_ptr()), size_(0), cap_(N) {}
    ~SmallVector()
    {
        clear();
    }
    SmallVector(const SmallVector &other) : size_(other.size_)
    {
        if (size_ <= N)
        {
            std::uninitialized_copy_n(other.tdata, size_, inline_ptr());
            tdata = inline_ptr();
            cap_ = N;
        }
        else
        {
            tdata = std::allocator<T>{}.allocate(size_);
            try
            {
                std::uninitialized_copy_n(other.tdata, size_, tdata);
            }
            catch (...)
            {
                std::allocator<T>{}.deallocate(tdata, size_);
                throw;
            }
            cap_ = size_;
        }
    };
    SmallVector(SmallVector &&other) = delete;
    SmallVector operator=(const SmallVector &other) = delete;
    SmallVector operator=(SmallVector &&other) = delete;

    T *inline_ptr() { return reinterpret_cast<T *>(&buffer); }
    const T *inline_ptr() const { return reinterpret_cast<const T *>(&buffer); }
    bool is_inline() const { return tdata == inline_ptr(); }

    T &operator[](size_t idx) noexcept { return tdata[idx]; }
    const T &operator[](size_t idx) const noexcept { return tdata[idx]; }
    T *data() { return tdata; }
    const T *data() const { return tdata; }

    iterator begin() { return tdata; }
    iterator end() { return tdata + size_; }
    T &back() { return tdata[size_ - 1]; }
    const_iterator cbegin() const { return tdata; }
    const_iterator cend() const { return tdata + size_; }
    const T &cback() const { return tdata[size_ - 1]; }

    template <class... Args>
    T &emplace_back(Args &&...args)
    {
        if (size_ == cap_)
        {
            return emplace_realloc(std::forward<Args>(args)...);
        }
        else
        {
            auto p = std::construct_at(tdata + size_, std::forward<Args>(args)...);
            size_ += 1;
            return *p;
        }
    }
    void push_back(const T &t) { emplace_back(t); }
    void push_back(T &&t) { emplace_back(std::move(t)); }
    void pop_back() noexcept
    {
        std::destroy_at(tdata + size_ - 1);
        --size_;
    }

    void release_heap()
    {
        if (!is_inline())
        {
            std::allocator<T>{}.deallocate(tdata, cap_);
            tdata = reinterpret_cast<T *>(&buffer);
            cap_ = N;
        }
    }

    template <class... Args>
    T &emplace_realloc(Args &&...args)
    {
        auto new_cap = cap_ * 2;
        auto new_data = std::allocator<T>{}.allocate(new_cap);

        T *p = nullptr;
        try
        {
            p = std::construct_at(new_data + size_, std::forward<Args>(args)...);
        }
        catch (...)
        {
            std::allocator<T>{}.deallocate(new_data, new_cap);
            throw;
        }

        try
        {
            if (size_ > 0)
            {
                SmallVector::relocate(tdata, size_, new_data);
            }
        }
        catch (...)
        {
            std::destroy_at(p);
            std::allocator<T>{}.deallocate(new_data, new_cap);
            throw;
        }

        std::destroy(tdata, tdata + size_);
        release_heap();
        tdata = new_data;
        cap_ = new_cap;
        ++size_;
        return *p;
    }

    void grow(size_t new_cap)
    {
        auto new_tdata = std::allocator<T>{}.allocate(new_cap);
        std::uninitialized_move_n<iterator, size_t, iterator>(begin(), size_, new_tdata);
        std::destroy(begin(), end());
        release_heap();
        tdata = new_tdata;
        cap_ = new_cap;
    }

    void clear()
    {
        std::destroy(begin(), end());
        release_heap();
        size_ = 0;
    }
};

int main()
{
    SmallVector<int, 4> vec1;
    vec1.push_back(1);
    vec1.push_back(2);
    vec1.push_back(3);
    vec1.push_back(4);
    std::cout << "is inline?: " << vec1.is_inline() << std::endl;

    vec1.push_back(5);
    std::cout << "is inline?: " << vec1.is_inline() << std::endl;

    std::cout << vec1.cback() << std::endl;
    vec1.pop_back();
    std::cout << vec1.cback() << std::endl;
    vec1.pop_back();
    std::cout << vec1.cback() << std::endl;
    return 0;
}