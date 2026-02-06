import pytest

import pybook.t9 as t


def test_run_succeeded():
    with t.transaction():
        print("insert")


def test_run_fail():
    with pytest.raises(RuntimeError), t.transaction():
        raise RuntimeError("primary key conflicts")
