import collections


def flip_matrix(matrix):
    flipped = []
    for i in range(len(matrix)):
        flipped.append([row[i] for row in matrix])
    return flipped


def t87_typo_sort(matrix):
    flipped = flip_matrix(matrix=matrix)
    print(flipped)
    results = []
    progressing = []
    processed = set()
    while True:
        for n in progressing:
            # Reduce the grade of the dependant
            for row in flipped:
                if row[n] > 0:
                    row[n] -= 1
        progressing.clear()
        for n, row in enumerate(flipped):
            if n in processed:
                continue
            if sum(row) == 0:
                progressing.append(n)
                processed.add(n)
                results.append(n)
        print(progressing)
        if len(progressing) == 0:
            break

    print(results)
    if len(results) != len(matrix):
        raise RuntimeError("Circular Dependency")
    return results


def t87_typo_sort_optimise(matrix):
    n = len(matrix)
    indegress = [0] * n
    results = []
    for x in range(n):
        for y in range(n):
            if matrix[x][y] > 0:
                indegress[y] += matrix[x][y]
    q = collections.deque([idx for idx, x in enumerate(indegress) if x == 0])
    if len(q) == 0:
        raise RuntimeError("Circular Dependency")

    while q:
        x = q.popleft()
        results.append(x)

        for y in range(n):
            if matrix[x][y] > 0:
                indegress[y] -= 1
                if indegress[y] == 0:
                    q.append(y)

    print(results)
    if len(results) != len(matrix):
        raise RuntimeError("Circular Dependency")
