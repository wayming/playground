import pybook.t92 as t


def test_t92_permute_unique():
    assert len(t.combination_sum([10, 1, 2, 7, 6, 1, 5], 8)) == 4
