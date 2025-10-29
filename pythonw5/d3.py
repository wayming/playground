import queue
from collections import deque
def dfs(nums: list, head: int):
    if not nums:
        return None
    
    stack = deque()
    stack.append(head)
    results = []
    while stack:
        e = stack.pop()
        results.append(e)
        children = [y for x, y in nums if x == e]
        stack.extend(reversed(children))
    return results

def bfs(nums: list, head: int):
    if not nums:
        return None
    
    q = deque()
    q.append(head)
    results = []  
    while q:
        e = q.popleft()
        results.append(e)
        for i in [y for x, y in nums if x == e]:
            q.append(i)
    return results

edges = [[0,1],[0,2],[1,3],[1,4]]
print(dfs(edges, 0))
print(bfs(edges, 0))