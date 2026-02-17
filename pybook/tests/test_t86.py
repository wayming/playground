import pybook.t86 as t


def test_t86_graph_1():
    # 节点编号: 0, 1, 2, 3, 4, 5
    matrix = [
        [0, 1, 1, 0, 0, 0],  # 0 连向 1, 2
        [1, 0, 1, 1, 0, 0],  # 1 连向 0, 2, 3
        [1, 1, 0, 0, 1, 0],  # 2 连向 0, 1, 4
        [0, 1, 0, 0, 1, 1],  # 3 连向 1, 4, 5
        [0, 0, 1, 1, 0, 1],  # 4 连向 2, 3, 5
        [0, 0, 0, 1, 1, 0],  # 5 连向 3, 4
    ]
    print(t.t86_graph_dfs(matrix))
    print(t.t86_graph_bfs(matrix))

    assert sorted(t.t86_graph_dfs(matrix)) == sorted(t.t86_graph_bfs(matrix))


def test_t86_graph_2():
    # 节点索引：0, 1, 2
    matrix = [
        [0, 0, 1],  # 0 连向 2
        [0, 0, 1],  # 1 连向 2
        [1, 1, 0],  # 2 连向 0, 1
    ]
    print(t.t86_graph_dfs(matrix))
    print(t.t86_graph_bfs(matrix))
