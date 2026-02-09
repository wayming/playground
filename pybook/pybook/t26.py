import collections


def avg_grades(records):
    classGrades = collections.defaultdict(list)
    for className, name, grade in records:
        classGrades[className].append(grade)
    return {k: sum(v) / len(v) for k, v in classGrades.items()}
