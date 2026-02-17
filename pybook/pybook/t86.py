import collections


def t86_graph_dfs(matrix: list[list]):

    visited_edge = set()

    def dfs(matrix, f):
        edges = []
        for t, connected in enumerate(matrix[f]):
            if (
                connected > 0
                and (f, t) not in visited_edge
                and (t, f) not in visited_edge
            ):
                edges.append((f, t))
                visited_edge.add((f, t))
                edges.extend(dfs(matrix, t))
        return edges

    return dfs(matrix, 0)


def t86_graph_bfs(matrix: list[list]):
    def bfs(matrix, x):
        to_visit = collections.deque()
        edges = []
        visited_edge = set()
        to_visit.append(x)
        while len(to_visit) > 0:
            f = to_visit.popleft()

            for t, connected in enumerate(matrix[f]):
                if (
                    connected
                    and (f, t) not in visited_edge
                    and (t, f) not in visited_edge
                ):
                    edges.append((f, t))
                    visited_edge.add((f, t))
                    to_visit.append(t)
        return edges

    return bfs(matrix, 0)
