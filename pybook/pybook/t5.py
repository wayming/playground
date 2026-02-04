def log_counter(file, key):
    matchedLines = []
    with open(file, encoding="utf-8") as f:
        matchedLines = [line for line in f if key in line]
    return len(matchedLines)


def log_counter_lazy_eval(file, key):
    def log_lazy_reader(file_path, key):
        with open(file_path, encoding="UTF-8") as f:
            for line in f:
                if key in line:
                    yield line

    count = 0
    for _ in log_lazy_reader(file, key):
        count += 1
    return count
