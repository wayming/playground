import collections
import re


def is_float(n):
    try:
        float(n)
    except:
        return False
    return True


def analyse_csv_text(text: str):
    pattern = re.compile(r"ERROR")
    lines = text.splitlines()
    errors = []
    scores = collections.defaultdict(list)
    for idx, l in enumerate(lines[1:], 1):
        if pattern.search(l):
            errors.append(f"Line {idx}, {l}")
        else:
            cols = [x.strip() for x in l.split(",")]
            print(cols)
            if is_float(cols[2]):
                scores[cols[1]].append(float(cols[2]))

    return errors, {k: sum(v) / len(v) for k, v in scores.items()}
