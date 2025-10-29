from collections import defaultdict
import heapq
def shortest_path(edges: list, src: int, n: int):
    results = [float('inf')]*n
    visited = [False]*n
    def _shorest_path(edges, src, target):
        if src == target:
            results[src] = 0
            return 0
        if visited[target]:
            return results[target]
        
        distance = float('inf')
        for f, t, w in edges:
            if t == target:
                distance = min(distance, w + _shorest_path(edges, src, f))
        results[target] = distance
        visited[target] = True
        return distance
    _shorest_path(edges, src, n-1)
    return results

def shortest_path2(edges: list, src: int, n: int):
    nodes_map = defaultdict(list)
    for fr, to, weight in edges:
        nodes_map[fr].append((to, weight))
    print(nodes_map)
    distances = [float('inf')] * n
    processed = [(src, 0)]
    distances[src] = 0
    while processed:
        curr, dist = heapq.heappop(processed)
        if dist > distances[curr]:
            continue
        
        for to, weight in nodes_map[curr]:
            if dist + weight < distances[to]:
                distances[to] = dist + weight
                heapq.heappush(processed, (to, distances[to]))
        print(processed)
    return distances
n = 5
edges = [
    [0, 1, 2],
    [0, 2, 4],
    [1, 2, 1],
    [1, 3, 7],
    [2, 4, 3],
    [3, 4, 1]
]
src = 0

print(shortest_path2(edges, src, n))

