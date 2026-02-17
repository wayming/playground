import collections


def t86_graph_dfs(matrix: list[list]):

    visited = set()

    def dfs(matrix, x, y):
        results = []
        for idx, v in enumerate(matrix[x][y + 1 :], start=y + 1):
            if v > 0:
                if (x, idx) not in visited:
                    results.append((x, idx))
                    visited.add((x, idx))
                results.extend(dfs(matrix, idx, idx))
        return results

    return dfs(matrix, 0, 0)


def t86_graph_bfs(matrix: list[list]):
    def bfs(matrix, x, y):
        to_visit = collections.deque()
        results = []
        to_visit.append((x, y))
        visited = set()
        while len(to_visit) > 0:
            idxx, idxy = to_visit.popleft()
            for idx, v in enumerate(matrix[idxx][idxy + 1 :], start=idxy + 1):
                if v > 0 and (idxx, idx) not in visited:
                    results.append((idxx, idx))
                    visited.add((idxx, idx))
                    to_visit.append((idx, idx))
        return results

    return bfs(matrix, 0, 0)
