import collections


def t88_solve_grid_path(grid):

    def bfs(grid):
        if not grid or grid[0][0] == 1:
            return []

        q = collections.deque([(0, 0)])
        rows = len(grid)
        cols = len(grid[0])
        pre_nodes = {}
        visited = {(0, 0)}
        while q:
            x, y = q.popleft()
            if grid[x][y] == 1:
                continue
            if x == rows - 1 and y == cols - 1:
                results = [(x, y)]
                curr = (x, y)
                while curr in pre_nodes:
                    results.append(pre_nodes[curr])
                    curr = pre_nodes.get(curr)
                return results[::-1]
            if x < rows - 1:
                if (x + 1, y) not in visited:
                    visited.add((x + 1, y))
                    pre_nodes[((x + 1), y)] = (x, y)
                    q.append((x + 1, y))

            if y < cols - 1:
                if (x, y + 1) not in visited:
                    visited.add((x, y + 1))
                    pre_nodes[(x, (y + 1))] = (x, y)
                    q.append((x, y + 1))

    return bfs(grid)
