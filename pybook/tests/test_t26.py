import pybook.t26 as t


def test_avg_grades():
    records = [("classA", "Alice", 90), ("classB", "Bob", 85), ("classA", "Tom", 92)]
    assert t.avg_grades(records)["classA"] == 91
