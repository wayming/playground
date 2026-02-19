import pybook.t91 as t


def test_t91_permute_unique():
    assert len(t.t91_permute_unique([1, 1, 2])) == 3
    assert len(t.t91_permute_unique([3, 5, 7, 5, 7, 3])) == 90
    assert len(t.t91_permute_unique_op([3, 5, 7, 5, 7, 3])) == 90
    assert len(t.t91_permute_unique_op([1, 1, 2])) == 3
