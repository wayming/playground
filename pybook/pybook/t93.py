def t93_ways(num):

    pathes = {}
    idx = 0
    while idx <= num:
        if idx <= 2:
            pathes[idx] = idx
            idx += 1
            continue
        pathes[idx] = pathes[idx - 1] + pathes[idx - 2]
        idx += 1
    print(pathes)
    return pathes[num]


def t93_steps(num):

    steps = {}
    for idx in range(1, num + 1):
        if idx == 1:
            steps[1] = [[1]]
            continue
        if idx == 2:
            steps[2] = [[1, 1], [2]]
            continue
        steps[idx] = [x + [1] for x in steps[idx - 1]] + [
            x + [2] for x in steps[idx - 2]
        ]
    print(steps)
    return steps[num]
