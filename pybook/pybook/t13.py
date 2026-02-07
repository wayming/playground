def dfs(metrix: list[list], begin: list[int]):
    x = begin[0]
    y = begin[1]
    if x + 1 < len(metrix) and metrix[x + 1][y] > 0:
        dfs(metrix, [x + 1, y])
    if y + 1 < len(metrix[0]) and metrix[y][x + 1] > 0:
        dfs(metrix, [x, y + 1])
    metrix[x][y] = 0


def count(metrix: list[list]):
    total = 0
    for x in range(len(metrix)):
        for y in range(len(metrix[0])):
            if metrix[x][y] == 1:
                total += 1
                dfs(metrix, [x, y])
    return total
