import pybook.t28 as t


def test_command_queue():
    q = t.CommandQueue()
    q.execute("PUSH 5")
    q.execute("PUSH 8")
    q.execute("PUSH 20")
    assert q.execute("SHOW") == [5, 8, 20]
    q.execute("POP")
    assert q.execute("SHOW") == [8, 20]
