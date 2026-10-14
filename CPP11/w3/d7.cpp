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
#include <algorithm>
#include <optional>

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

template <std::unsigned_integral T>
T swap_bytes(T t)
{
    if constexpr (std::endian::native == std::endian::little)
    {
        constexpr size_t len = sizeof(T);

        auto arr = std::bit_cast<std::array<std::byte, len>>(t);
        for (size_t i = 0; i < len / 2; i++)
        {
            std::swap(arr[i], arr[len - i - 1]);
        }
        return std::bit_cast<T>(arr);
    }
    else
    {
        return t;
    }
}
template <std::unsigned_integral T, std::size_t from, std::size_t to>
void write(std::vector<std::byte> &stream, T t)
{
    constexpr std::size_t diff = to - from;
    static_assert(sizeof(T) == diff, "size of source and destination is not the same");
    static_assert(from < to);
    static_assert(to <= OFFSET_HEADER_END);
    t = swap_bytes<T>(t);
    std::memcpy(&stream[from], &t, to - from);
};
template <std::unsigned_integral T, std::size_t from, std::size_t to>
T read(std::span<std::byte> stream)
{
    constexpr std::size_t diff = to - from;
    static_assert(sizeof(T) == diff, "size of source and destination is not the same");
    static_assert(from < to);
    static_assert(to <= OFFSET_HEADER_END);
    assert(to <= stream.size());

    T t;
    std::memcpy(&t, &stream[from], to - from);
    t = swap_bytes<T>(t);

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
    uint16_t hash_result = 0;

    bool high = false;
    for (auto &b : bytes)
    {
        uint16_t v = std::to_integer<uint8_t>(b);
        if (high)
        {
            hash_result ^= (v << 8);
            high = false;
        }
        else
        {
            hash_result ^= v;
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
    std::vector<std::byte> bytes_stream(OFFSET_HEADER_END + payload.size());
    write<uint16_t, OFFSET_MAGIC, OFFSET_VER_FLAGS>(bytes_stream, MAGIC);
    uint8_t ver_flags = (version << 4) | (flags & 0xF);
    write<uint8_t, OFFSET_VER_FLAGS, OFFSET_RESERVED>(bytes_stream, ver_flags);
    const auto len = payload.size();
    write<uint16_t, OFFSET_LEN, OFFSET_SEQ>(bytes_stream, u32_to_16(len));

    write<uint32_t, OFFSET_SEQ, OFFSET_CKSUM>(bytes_stream, seq);

    write<uint16_t, OFFSET_CKSUM, OFFSET_HEADER_END>(bytes_stream, cksum(payload));
    if (payload.size() > 0)
    {
        std::copy(payload.begin(), payload.end(), bytes_stream.begin() + OFFSET_HEADER_END);
    }
    return bytes_stream;
};

class Decoder
{
    std::vector<std::byte> cache;
    std::optional<Message> msg{std::nullopt};
    void reset()
    {
        cache.clear();
        msg = std::nullopt;
    }

public:
    std::optional<Message> feed(std::vector<std::byte> &stream)
    {
        cache.insert(cache.end(), stream.begin(), stream.end());

        if (!msg && cache.size() >= OFFSET_HEADER_END)
        {
            // consume to fill header
            Message new_msg;
            new_msg.header.magic = read<uint16_t, OFFSET_MAGIC, OFFSET_VER_FLAGS>(cache);
            new_msg.header.ver_flags = read<uint8_t, OFFSET_VER_FLAGS, OFFSET_RESERVED>(cache);
            new_msg.header.reserved = uint8_t(0);
            new_msg.header.len = read<uint16_t, OFFSET_LEN, OFFSET_SEQ>(cache);
            new_msg.header.seq = read<uint32_t, OFFSET_SEQ, OFFSET_CKSUM>(cache);
            new_msg.header.cksum = read<uint16_t, OFFSET_CKSUM, OFFSET_HEADER_END>(cache);
            msg = new_msg;
            cache.erase(cache.begin(), cache.begin() + OFFSET_HEADER_END);
        }

        if (msg && cache.size() >= msg.value().header.len)
        {

            msg.value().payload.assign(cache.begin(), cache.begin() + msg.value().header.len);
            cache.erase(cache.begin(), cache.begin() + msg.value().header.len);
            if (msg.value().header.cksum != cksum(msg.value().payload))
            {
                throw std::runtime_error("unmatched cksum");
            }
            auto ret = msg.value();
            msg = std::nullopt;
            return ret;
        }
        else
        {
            return std::nullopt;
        }
    }
};

int main()
{
    std::array<std::byte, 100> arr;
    arr.fill(std::byte{0x11});

    auto encoded = encode(0x01, 0x01, 1001, arr);
    std::cout << "In stream: " << dump_stream(encoded) << std::endl;

    Decoder decoder;
    auto decoded = decoder.feed(encoded);
    if (decoded)
    {
        std::cout << "Out stream: " << dump_stream(decoded.value().payload);
    }
    return 0;
}