import pybook.t5 as t


def test_log_counter():
    lines = ["line" + str(i) + " ERROR message" for i in range(10)]
    lines += ["line" + str(i) + " WARNING message" for i in range(5)]
    lines += ["line" + str(i) + " INFO message" for i in range(3)]
    with open("test_log_counter.txt", mode="w") as f:
        f.writelines([line + "\n" for line in lines])
    assert t.log_counter("test_log_counter.txt", "ERROR") == 10
    assert t.log_counter("test_log_counter.txt", "WARNING") == 5
    assert t.log_counter("test_log_counter.txt", "INFO") == 3
    assert t.log_counter_lazy_eval("test_log_counter.txt", "ERROR") == 10
    assert t.log_counter_lazy_eval("test_log_counter.txt", "WARNING") == 5
    assert t.log_counter_lazy_eval("test_log_counter.txt", "INFO") == 3
