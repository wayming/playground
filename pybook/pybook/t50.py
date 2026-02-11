import collections


def t71_top_k(nums: list, topn):
    count = collections.defaultdict(int)
    for n in nums:
        count[n] += 1
    countPairs = [(v, k) for k, v in count.items()]
    return [y for _, y in sorted(countPairs, reverse=True)][0:topn]


def t72_factorial(n):
    return 1 if n == 1 else n * t72_factorial(n - 1)


def t73_islands(grid):
    visited = set()
    count = 0

    def dfs(x, y):
        if x >= len(grid) or y >= len(grid[0]) or x < 0 or y < 0:
            return

        if grid[x][y] == 0 or (x, y) in visited:
            return
        visited.add((x, y))
        dfs(x + 1, y)
        dfs(x, y + 1)
        dfs(x, y - 1)
        dfs(x - 1, y)

    for x, row in enumerate(grid):
        for y, col in enumerate(row):
            if col == 1 and (x, y) not in visited:
                print((x, y))
                count += 1
                dfs(x, y)
    return count
