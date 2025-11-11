from collections import deque


edges = []

def shortest_path_bfs(grid: list):
    queue = deque()
    queue.append((0, 0, 0)) #x, y, steps
    while queue:
        x, y, steps = queue.popleft()
        print(x, " ", y, " ", steps)
        if x == len(grid)-1 and y == len(grid[0]) - 1:
            return steps

        if x < len(grid) - 1 and grid[x+1][y] == 0:
            queue.append((x+1, y, steps+1))
            edges.append([(x,y), (x+1, y)])
        if y < len(grid[0]) -1 and grid[x][y+1] == 0:
            queue.append((x, y+1, steps+1))
            edges.append([(x,y), (x, y+1)])
    return -1

    
grid = [
    [0, 0, 1, 0],
    [0, 0, 0, 0],
    [1, 0, 1, 0],
    [0, 0, 0, 0]
]
print(shortest_path_bfs(grid))

print(edges)


path = [(0, 0)]
for (fr, to) in edges:
    print(fr, " => ", to)
    if fr == path[-1]:
        path.append(to)
print(path)
