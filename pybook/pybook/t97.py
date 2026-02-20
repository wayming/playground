def max_sub_len(s: str):
    max_begin = 0
    max_len = 0
    char_set = set()
    slow = 0
    for fast in range(len(s)):
        while s[fast] in char_set:
            char_set.remove(s[fast])
            slow += 1
        char_set.add(s[fast])
        if fast - slow + 1 > max_len:
            max_len = fast - slow + 1
            max_begin = slow
    print(max_len)
    return s[max_begin : max_begin + max_len]
