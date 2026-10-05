#include <cstdint>
#include <array>
#include <vector>
#include <utility>
#include <cassert>
#include <sstream>
#include <iostream>

struct EntityHandle
{
    size_t sparse_idx;
    uint32_t sparse_val;
};
template <class T>
class EntityManager
{
private:
    constexpr static uint32_t INDEX_MASK = (1 << 20) - 1;
    constexpr static uint32_t GENERATION_MASK = (0xFFFFFFFFu << 20);
    constexpr static uint32_t MAX_SIZE = 10 * 1024 * 1024;
    std::vector<T> dense;
    std::vector<uint32_t> dense_to_sparse;
    std::vector<uint32_t> sparse;
    uint32_t free_head_idx = 0;

public:
    EntityManager()
    {
        dense.reserve(MAX_SIZE);
        sparse.reserve(MAX_SIZE);
        dense_to_sparse.reserve(MAX_SIZE);
    }
    uint32_t sparse_val(uint32_t gen, uint32_t dense_idx)
    {
        return (gen << 20) | dense_idx;
    }
    uint32_t gen(uint32_t sparse_idx) { return (sparse_idx & GENERATION_MASK) >> 20; }
    uint32_t idx(uint32_t sparse_idx) { return sparse_idx & INDEX_MASK; }

    EntityHandle insert(T &&t)
    {
        assert(free_head_idx <= sparse.size());

        dense.emplace_back(std::move(t));
        EntityHandle handle;
        if (free_head_idx == sparse.size())
        {
            sparse.emplace_back(sparse_val(1, dense.size() - 1));
            free_head_idx = sparse.size(); // still all used
            handle.sparse_idx = sparse.size() - 1;
            handle.sparse_val = sparse[handle.sparse_idx];
            dense_to_sparse.emplace_back(sparse.size() - 1);
        }
        else
        {
            auto keep_gen = gen(sparse[free_head_idx]);
            auto keep_next_free_idx = gen(sparse[free_head_idx]);
            sparse[free_head_idx] = sparse_val(keep_gen + 1, dense.size() - 1);
            handle.sparse_idx = free_head_idx;
            handle.sparse_val = sparse[handle.sparse_idx];
            free_head_idx = keep_next_free_idx;
            dense_to_sparse.emplace_back(free_head_idx);
        }
        return handle;
    }

    T &get(const EntityHandle &handle)
    {
        assert(handle.sparse_idx < sparse.size());
        assert(handle.sparse_val == sparse[handle.sparse_idx]);
        auto dense_idx = idx(sparse[handle.sparse_idx]);
        assert(dense_idx < dense.size());
        return dense[dense_idx];
    }
    void erase(EntityHandle &&handle)
    {
        assert(handle.sparse_idx < sparse.size());
        assert(handle.sparse_val == sparse[handle.sparse_idx]);
        auto dense_idx = idx(sparse[handle.sparse_idx]);
        assert(dense_idx < dense.size());

        std::exchange(dense.back(), dense[dense_idx]);
        dense.pop_back();
        std::exchange(dense_to_sparse.back(), dense_to_sparse[dense_idx]);
        dense_to_sparse.pop_back();

        sparse[dense_to_sparse[dense_idx]] = sparse_val(gen(sparse[dense_to_sparse[dense_idx]]), dense_idx);
        if (free_head_idx == sparse.size())
        {
            sparse[handle.sparse_idx] = sparse_val(gen(sparse[handle.sparse_idx]), sparse.size());
        }
        else
        {
            sparse[handle.sparse_idx] = sparse_val((gen(sparse[handle.sparse_idx])), idx(sparse[free_head_idx]));
        }
        free_head_idx = handle.sparse_idx;
    }

    std::string dump()
    {
        std::stringstream ss;
        ss << "dense: [";
        for (auto &t : dense)
        {
            ss << t;
            if (&t != &dense[dense.size() - 1])
            {
                ss << ", ";
            }
        }
        ss << "]\n";

        ss << "dense_to_sparse: [";
        for (size_t i = 0; i < dense_to_sparse.size(); i++)
        {
            ss << "dense-" << i << "->" << "sparse-" << dense_to_sparse[i];
            if (i < dense_to_sparse.size() - 1)
            {
                ss << ", ";
            }
        }

        ss << "]\n";

        ss << "sparse: [";
        for (auto &t : sparse)
        {
            ss << (gen(t)) << "-" << idx(t);
            if (&t != &sparse[sparse.size() - 1])
            {
                ss << ", ";
            }
        }
        ss << "]" << std::endl;

        return ss.str();
    }
};

int main()
{
    EntityManager<double> em;
    auto h1 = em.insert(1.5);
    auto h2 = em.insert(2.5);
    auto h3 = em.insert(3.5);
    std::cout << em.dump() << std::endl;

    em.erase(std::move(h2));
    std::cout << em.dump() << std::endl;

    auto h4 = em.insert(4.5);
    std::cout << em.get(h4) << std::endl;
    std::cout << em.dump() << std::endl;

    return 0;
}