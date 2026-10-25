#include <memory>

template <class T, size_t N>
class SmallVector
{
public:
    using iterator = T *;
    using const_iterator = const T *;

private:
    alignas(T) std::byte buffer[N * sizeof(T)];
    T *tdata;
    size_t size;
    size_t cap;

public:
    SmallVector() : tdata(inline_ptr), size(0), cap(N) {}
    ~SmallVector()
    {
        clear();
    }
    SmallVector(const SmallVector &other) = delete;
    SmallVector(SmallVector &&other) = delete;
    SmallVector operator=(const SmallVector &other) = delete;
    SmallVector operator=(SmallVector &&other) = delete;

    T *inline_ptr() { return reinterpret_cast<T *>(&buffer); }
    const T *inline_ptr() const { return reinterpret_cast<const T *>(&buffer); }
    bool is_inline() { return tdata == &buffer; }

    T &operator[](size_t idx) noexcept { return tdata[idx]; }
    const T &operator[](size_t idx) const noexcept { return tdata[idx]; }
    T *data() { return tdata; }
    const T *data() const { return tdata; }

    iterator begin() { return tdata; }
    iterator end() { return tdata + size; }
    const_iterator cbegin() { return tdata; }
    const_iterator cend() { return tdata + size; }

    template <class... Args>
    T &emplace_back(Args &&...args)
    {
        if (size == cap)
        {
            grow(cap * 2);
        }
        auto p = std::construct_at(data + size, std::forward<Args>(args)...);
        size += 1;
        return *p;
    }
    void push_back(const T &t) { emplace_back(t); }
    void push_back(T &&t) { emplace_back(std::move(t)); }
    void pop_back() noexcept { std::destroy_at(tdata + size - 1); }

    void release_heap()
    {
        if (!is_inline)
        {
            std::allocator<T>{}.deallocate(data, cap);
            data = &buffer;
            cap = N;
        }
    }

    void grow(size_t new_cap)
    {
        static_assert(new_cap > cap);
        auto new_tdata = std::allocator<T>{}.allocate(new_cap);
        std::uninitialized_move_n<iterator, size_t, iterator>(begin(), size, new_tdata);
        std::destroy(begin(), end());
        release_heap();
        tdata = new_tdata;
        cap = new_cap;
    }

    void clear()
    {
        std::destroy(begin(), end());
        release_heap();
        memset(tdata, size, '\0');
    }
};

int main()
{
    return 0;
}