import pybook.pybook.t23 as t


def test_avg_by_user():
    print(t.avg_by_user([("Way", 90), ("Way", 80), ("H", 70), ("H", 60), ("Way", 50)]))

    assert (
        t.avg_by_user([("Way", 90), ("Way", 80), ("H", 70), ("H", 60), ("Way", 50)])[
            "Way"
        ]
        == (90 + 80 + 50) / 3
    )
