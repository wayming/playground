def factorial(n : int):
    if n == 1:
        return 1
    return n * factorial(n-1)

print(factorial(5))

def num_of_islands(grid : list):
    accessed = []
    total = 0
    rows = len(grid)
    cols = len(grid[0])
    def dfs(x, y):
        if x >= rows or y >= cols or x < 0 or y < 0 or grid[x][y] == 0 or (x, y) in accessed:
            return
        accessed.append((x, y))
        dfs(x + 1, y)
        dfs(x, y + 1)
        dfs(x - 1, y)
        dfs(x, y - 1)

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y] == 1 and (x, y) not in accessed:
                total += 1
                dfs(x, y)
    return total

def num_of_islands_stack(grid: list):
    total = 0
    visited = set()
    stack = []
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y] == 1 and (x, y) not in visited:
                total += 1
                stack.append((x, y))
                visited.add((x, y))
                process_stack(grid, stack, visited)
    return total

def process_stack(grid: list, stack: list, visited: set):
    while stack:
        (x, y) = stack.pop()
        for next in [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]:
            if next in visited:
                continue
            
            (i, j) = next
            if 0 <= i < len(grid) and 0 <= j < len(grid[0]) and grid[i][j] == 1:
                stack.append(next)
                visited.add(next)
    
    
g = [
  [1,1,0,0],
  [1,0,0,1],
  [0,0,1,1],
  [0,0,0,0]
]
print(num_of_islands(g))

print(num_of_islands_stack(g))


def shortest_path(grid: list):
    if grid[0][0] == 1:
        return -1

    return shortest_path_helper(grid, 0, 0)

def shortest_path_helper(grid: list, x, y):
    steps_down = 0
    steps_right = 0
    if x == len(grid)-1 and y == len(grid[0]) - 1:
        return 1 if grid[x][y]==0 else -1
    
    if x+1 < len(grid) and grid[x+1][y] == 0:
        steps_down = shortest_path_helper(grid, x+1, y)
    elif y+1 < len(grid[0]) and grid[x][y+1] == 0:
        steps_right = shortest_path_helper(grid, x, y+1)
    else:
        return -1
    
    if steps_down == -1 and steps_right == -1:
        return -1
    
    steps = 0
    if steps_down > 0 and steps_right > 0:
        steps = min(steps_down, steps_right)
    else:
        steps = steps_down if steps_down > 0 else steps_right
    return 1 + steps

def shortest_stack(grid: list):

    if grid[0][0] == 1:
        return -1
    rows = len(grid)
    cols = len(grid[0])
    stack = [(0, 0, 1)]
    while stack:
        (x, y, step) = stack.pop()
        if x == rows-1 and y == cols - 1:
            if (grid[x][y] == 0):
                return step
            else:
                return -1
        
        if x < rows - 1 and grid[x+1][y] == 0:
            stack.append((x+1, y, step+1))
        if y < cols - 1 and grid[x][y+1] == 0:
            stack.append((x, y+1, step+1))
    
g = [
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [1, 0, 0, 0]
]
print(shortest_path(g))
print(shortest_stack(g))