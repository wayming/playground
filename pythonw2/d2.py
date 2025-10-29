from collections import deque, Counter
import heapq

def parentheses_match(s: str):
    stack = deque()
    match = {'{' : '}', '[' : ']', '(' : ')'}
    for c in s :
        if c in match: 
            stack.append(c)
        else:
            if match[stack.pop()] != c:
                return False
    if stack:
        return False
    return True

print(parentheses_match("{}[(())]")) # True
print(parentheses_match("(()")) # False
print(parentheses_match("[())]")) # False
print(parentheses_match("{}[(())]")) # True

class MinStack:
    def __init__(self):
        self.data = []
        self.mins = []
    
    def push(self, num: int):
        self.data.append(num)
        if not self.mins or num <= self.mins[-1]:
            self.mins.append(num)
    
    def pop(self):
        n = self.data.pop()
        if n == self.mins[-1]:
            self.mins.pop()
        
    def top(self):
        return self.data[-1]
    
    def getMin(self):
        return self.mins[-1]

s = MinStack()
s.push(-2)
s.push(0)
s.push(-3)
s.push(-3)
print(s.getMin())  # -3
s.pop()
print(s.top())     # -3
print(s.getMin())  # -3
s.pop()
print(s.top())     # 0
print(s.getMin())  # -2

def first_distinct(s: str):
    c = Counter(s)
    for k, v in c.items():
        if v == 1:
            return k
    
    raise "no distinct char found"

print(first_distinct("leetcode"))

def first_k(nums: list, k: int):
    c = Counter(nums)
    print(c.most_common(k))


print(first_k([1, 1, 1, 2, 2, 3], 2))

def max_k(nums: list, k: int):
    h = [-x for x in nums]
    heapq.heapify(h)
    for _ in range(k):
        yield -heapq.heappop(h)

print(list(max_k([3,7,9,2,9,0,1,9,3,8], 5)))
    