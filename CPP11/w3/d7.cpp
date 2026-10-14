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
#include <array>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <assert.h>
inline constexpr std::size_t OFFSET_MAGIC = 0;
inline constexpr std::size_t OFFSET_VER_FLAGS = 2;
inline constexpr std::size_t OFFSET_RESERVED = 3;
inline constexpr std::size_t OFFSET_LEN = 4;
inline constexpr std::size_t OFFSET_SEQ = 6;
inline constexpr std::size_t OFFSET_CKSUM = 10;
inline constexpr std::size_t OFFSET_HEADER_END = 12;
inline constexpr std::uint16_t MAX_LEN = 0xFFFF;
inline constexpr uint16_t MAGIC = 0x1010;
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
    constexpr std::size_t diff = to - from;
    static_assert(sizeof(T) == diff, "size of source and destination is not the same");
    static_assert(from < to);
    static_assert(to <= OFFSET_HEADER_END);

    std::memcpy(&stream[from], &t, to - from);
};
template <std::unsigned_integral T, std::size_t from, std::size_t to>
T read(std::span<std::byte> stream)
{
    constexpr std::size_t diff = to - from;
    static_assert(sizeof(T) == diff, "size of source and destination is not the same");
    static_assert(from < to);
    static_assert(to <= OFFSET_HEADER_END);

    T t;
    std::memcpy(&t, &stream[from], to - from);
    return t;
}

// template <uint32_t In>
// uint16_t u32_to_16()
// {
//     constexpr std::array<uint16_t, 2> v = std::bit_cast<std::array<uint16_t, 2>>(In);
//     static_assert(In <= UINT16_MAX, "input must not exceed maximum uin16_t");
//     if constexpr (std::endian::native == std::endian::little)
//     {
//         return v[0];
//     }
//     else
//     {
//         return v[1];
//     }
// }

uint16_t u32_to_16(uint32_t In)
{
    std::array<uint16_t, 2> v = std::bit_cast<std::array<uint16_t, 2>>(In);
    assert(In <= UINT16_MAX);
    if constexpr (std::endian::native == std::endian::little)
    {
        return v[0];
    }
    else
    {
        return v[1];
    }
}

uint16_t cksum(std::span<const std::byte> bytes)
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

    return hash_result;
};

std::string dump_stream(const std::span<const std::byte> stream)
{
    std::stringstream ss;
    ss << std::hex << std::setfill('0');
    for (auto b : stream)
    {
        ss << std::setw(2) << std::to_integer<uint8_t>(b) << " ";
    }
    return ss.str();
}
std::vector<std::byte> encode(std::uint8_t version, std::uint8_t flags, std::uint32_t seq, const std::span<const std::byte> payload)
{
    std::vector<std::byte> bytes_stream(sizeof(Header) + payload.size());
    write<uint16_t, OFFSET_MAGIC, OFFSET_VER_FLAGS>(bytes_stream, MAGIC);
    // uint8_t ver_flags = (version << 4) | (flags & 0xF);
    // write<uint8_t, OFFSET_VER_FLAGS, OFFSET_RESERVED>(bytes_stream, ver_flags);
    std::uint8_t ver_flags[2] = {version, flags};
    write<uint8_t, OFFSET_VER_FLAGS, OFFSET_RESERVED>(bytes_stream, std::bit_cast<uint16_t>(ver_flags));
    const auto len = payload.size();
    write<uint16_t, OFFSET_LEN, OFFSET_SEQ>(bytes_stream, u32_to_16(len));

    write<uint32_t, OFFSET_SEQ, OFFSET_CKSUM>(bytes_stream, seq);

    write<uint16_t, OFFSET_CKSUM, OFFSET_HEADER_END>(bytes_stream, cksum(payload));
    memcpy(&bytes_stream[OFFSET_HEADER_END], &payload, len);
    return bytes_stream;
};

Message decode(std::vector<std::byte> &stream)
{
    Message msg;
    msg.header.magic = read<uint16_t, OFFSET_MAGIC, OFFSET_VER_FLAGS>(stream);
    msg.header.ver_flags = read<uint8_t, OFFSET_VER_FLAGS, OFFSET_RESERVED>(stream);
    msg.header.reserved = uint8_t(0);
    msg.header.len = read<uint16_t, OFFSET_LEN, OFFSET_SEQ>(stream);
    msg.header.seq = read<uint32_t, OFFSET_SEQ, OFFSET_CKSUM>(stream);
    msg.header.cksum = read<uint16_t, OFFSET_CKSUM, OFFSET_HEADER_END>(stream);
    return msg;
}
int main()
{
    std::array<std::byte, 100> arr;
    arr.fill(std::byte{0x11});
    auto encoded = encode(0x01, 0x01, 1001, arr);
    std::cout << dump_stream(encoded) << std::endl;
    return 0;
}