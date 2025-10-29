from collections import deque, defaultdict

def topo_sort(edges: list):
    nodes = defaultdict(list)
    degrees = defaultdict(int)
    for (fr, to) in edges:
        nodes[fr].append(to)
        degrees[to] += 1
        degrees.setdefault(fr, 0)    
    visits = {}
    results = []
    no_degrees_queue = deque([x for x, y in degrees.items() if y == 0])
    print(no_degrees_queue)
    while no_degrees_queue:
        n = no_degrees_queue.popleft()
        if n in visits:
            continue
        results.append(n)
        visits[n] = 1
        for to in nodes[n]:
            degrees[to] -= 1
            if degrees[to] == 0:
                no_degrees_queue.append(to)
    return results

edges = [[5,2],[5,0],[4,0],[4,1],[2,3],[3,1]]
print(topo_sort(edges))