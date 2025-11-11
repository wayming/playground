from collections import deque
import asyncio

def max_sub(s: str):
    nonduplicated = set()
    low = 0
    high = low + 1
    maxlen = 0
    nonduplicated.add(s[low])
    while high < len(s):
        if s[high] not in nonduplicated:
            nonduplicated.add(s[high])
            maxlen = max(maxlen, high-low+1)
            high += 1
        else:
            nonduplicated.clear()
            low = high
            high += 1
            nonduplicated.add(s[low])

    print(nonduplicated)
    return maxlen

print(max_sub("abccdefgg"))

def valida_parentheses(l:str):
    p = {'[': ']', '(': ')', '{': '}'}
    stack = deque()
    for e in l:
        if e in p:
            stack.append(e)
        elif e in p.values():
            r = stack.pop()
            if e != p[r]:
                return False
    return not stack
            
print(valida_parentheses('([{x}x]x)'))
print(valida_parentheses('({x}x]x)'))


def readf(filename: str):
    with open(filename, encoding="UTF-8") as f:
        for l in f:
            print(l)
            print("\n")


def merge_intervals(l:list):
    s = sorted(l)
    print(s)
    res = [s[0]]
    for idx, (x, y) in enumerate(s[1:]):
        if res and x > res[-1][1]:
            res.append(s[idx])
        else:
            res[-1][1] = max(y, res[-1][1])
    return res
print(merge_intervals([[15,18],[2,6],[8,10],[1,3]]))

def fib(n):
    res = [0, 1, 2]
    if n < 3:
        return res[n]
    
    for i in range(3, n+1):
        res.append(res[i-1] + res[i-2])
    
    return res[n]

print(fib(2))
print(fib(3))
assert fib(5) == 8

class MyIterator:
    def __init__(self, n):
        self.n = n
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.n:
            raise StopIteration
        
        res = self.n
        self.n -= 1
        return res
    
it = MyIterator(10)

for i in it:
    print(i)
    

