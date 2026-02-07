# Assumes complete binary tree
def inorder(nodes: list[int]):
    indexStack = []
    total = len(nodes)
    results = []
    if total > 1:
        indexStack.append(0)
    while len(indexStack) > 0:
        curr = indexStack.pop()
        results.append(nodes[curr])
        if 2 * curr + 2 <= total - 1:
            indexStack.append(2 * curr + 2)
        if 2 * curr + 1 <= total - 1:
            indexStack.append(2 * curr + 1)
    return results
