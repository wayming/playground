import pybook.t24 as t


def test_order_by():
    people = [
        ("bob", 10, "Melbourne"),
        ("alice", 30, "Sydney"),
        ("tom", 10, "Brisbane"),
    ]
    t.order_by_age_city(people)
    assert people[0][0] == "tom"
