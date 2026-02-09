def sort_grades(grades: list):
    return sorted(grades.items(), key=lambda x: (-x[1], x[0]))
