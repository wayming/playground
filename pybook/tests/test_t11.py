import pytest

import pybook.t11 as t


def test_user():
    u = t.User("user1", "pass1", 10)
    print(f"{u.user}/{u.password}/{u.age}")

    u.user = "user2"
    u.password = "pass2"
    u.age = 20
    print(f"{u.user}/{u.password}/{u.age}")

    with pytest.raises(ValueError):
        u.user = "在"

    with pytest.raises(ValueError):
        u.password = "1000"

    with pytest.raises(ValueError):
        u.age = 101
