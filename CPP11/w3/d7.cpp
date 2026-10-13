#include <bit>
#include <cstdint>
#include <cstring>
#include <vector>
#include <span>
#include <cstddef>
#include <concepts>
#include <exception>
#include <stdexcept>
#include <functional>

inline constexpr std::size_t OFFSET_MAGIC = 0;
inline constexpr std::size_t OFFSET_VER_FLAGS = 2;
inline constexpr std::size_t OFFSET_RESERVED = 3;
inline constexpr std::size_t OFFSET_LEN = 4;
inline constexpr std::size_t OFFSET_SEQ = 6;
inline constexpr std::size_t OFFSET_CKSUM = 10;
inline constexpr std::size_t OFFSET_HEADER_END = 12;

inline constexpr uint8_t MAGIC = 0x6;
struct Header
{
    std::uint16_t magic;
    std::uint8_t ver_flags;
    std::uint8_t reserved;
    std::uint32_t len;
    std::uint32_t seq;
    std::uint16_t cksum;
};

struct Message
{
    Header header;
    std::vector<std::byte> payload;
};

template <std::unsigned_integral T, std::size_t from, std::size_t to>
void write(std::vector<std::byte> &stream, T t)
{
    if (sizeof(T) < (to - from))
    {
        throw std::runtime_error("Not enough bytes to write");
    }
    std::memcpy(&stream[from], &t, to - from);
};
uint16_t cksum(std::span<const std::byte> &bytes)
{
    uint16_t hash_result;

    bool high = false;
    for (auto &b : bytes)
    {
        uint16_t v = std::to_integer<uint8_t>(b);
        if (high)
        {
            hash_result &= (v << 8);
            high = false;
        }
        else
        {
            hash_result &= v;
            high = true;
        }
    }
}
std::vector<std::byte> encode(std::uint8_t version, std::uint8_t flags, std::uint32_t seq, std::span<const std::byte> &payload)
{
    std::vector<std::byte> bytes_stream(sizeof(Header) + payload.size());
    write<uint8_t, OFFSET_MAGIC, OFFSET_VER_FLAGS>(bytes_stream, MAGIC);
    uint8_t ver_flags = (version << 4) | (flags & 0xF);
    write<uint8_t, OFFSET_VER_FLAGS, OFFSET_RESERVED>(bytes_stream, ver_flags);

    auto len = payload.size();
    write<size_t, OFFSET_LEN, OFFSET_SEQ>(bytes_stream, len);

    write<uint32_t, OFFSET_SEQ, OFFSET_CKSUM>(bytes_stream, seq);
}

int main()
{
    return 0;
}