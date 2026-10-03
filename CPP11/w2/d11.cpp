#include <stdlib.h>
#include <memory>
#include <cassert>
#include <stdio.h>
#include <string.h>
#include <iostream>
#include <algorithm>
#include <cstddef>

class MemPool
{
private:
    struct Slot
    {
        Slot *next;
    };
    std::unique_ptr<std::byte[]> memory_;
    Slot *free_list_;
    size_t obj_size_;
    size_t alignment = alignof(std::max_align_t);
    size_t slot_size;
    static size_t align_up(size_t n, size_t a)
    {
        return (n + a - 1) / a * a;
    }

public:
    MemPool(const size_t obj_size, const size_t capacity) : obj_size_(obj_size)
    {
        slot_size = align_up(std::max(obj_size, sizeof(Slot)), alignment);
        memory_ = std::make_unique<std::byte[]>(slot_size * capacity);
        free_list_ = reinterpret_cast<Slot *>(memory_.get());
        auto curr = free_list_;
        for (size_t i = 1; i < capacity; i++)
        {
            curr->next = reinterpret_cast<Slot *>(memory_.get() + i * slot_size);
            std::cout << std::hex << curr << "=>" << curr->next << std::endl;
            curr = curr->next;
        }
        curr->next = nullptr;
    }

    void *allocate()
    {
        auto ptr = free_list_;
        free_list_ = free_list_->next;
        memset(ptr, '\0', slot_size);
        return ptr;
    }
    void free(void *p)
    {
        auto ptr = static_cast<Slot *>(p);
        memset(ptr, '\0', slot_size);
        ptr->next = free_list_;
        free_list_ = ptr;
    }
    ~MemPool() {};
};

int main()
{
    MemPool pool(sizeof(long), 8);
    auto p1 = pool.allocate();
    std::cout << std::hex << p1 << std::endl;
    auto p2 = pool.allocate();
    std::cout << std::hex << p2 << std::endl;
    auto p3 = pool.allocate();
    std::cout << std::hex << p3 << std::endl;
    pool.free(p2);
    auto p4 = pool.allocate();
    std::cout << std::hex << p4 << std::endl;
}