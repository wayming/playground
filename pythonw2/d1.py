def remove_duplicate(nums: list):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] == nums[slow]:
            continue
        else:
            nums[slow+1] = nums[fast]
            slow = slow + 1
    del nums[slow+1:]

l = [1, 3, 4, 4, 7, 8, 8, 9]
remove_duplicate(l)
print(l)


def reverse(s :str):
    l = list(s)
    pre = 0
    post = len(l)- 1
    for _ in range(int(len(l)/2)) :
        l[pre], l[post] = l[post], l[pre]
        pre += 1
        post -= 1
    return ''.join(l)

s = "this is a test string"
print(reverse(s))

def is_palin(s: str):
    s2 = [c.lower() for c in s if c.isalpha()]
    print(''.join(s2))
    m = len(s2)//2
    if len(s2) % 2 == 0:
        return s2[:m] == s2[m:][::-1]
    else:
        return s2[:m] == s2[m+1:][::-1]
    

print(is_palin("A man, a plan, a canal: Panama"))

def two_sum(nums: list, target: int):
    d1 = {}
    for n in nums:
        d1[n] = True
    l = []
    for n in nums:
        if target - n in d1:
            l.append((n, target -n))
            d1.pop((target - n))
            d1.pop(n)
    return l
print(two_sum([2, 7, 11, 15, 2, 7, 3, 8, 6], 9))