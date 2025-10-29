def remove_even(nums: list):
    nums = [n for n in nums if n % 2 != 0]

    for m in range(len(nums)-1):
        for n in range(len(nums) - m - 1):
            if nums[n] > nums[n+1]:
                nums[n], nums[n+1] = nums[n+1], nums[n]

    return nums

print(remove_even([5, 3, 2, 8, 1, 4, 10, 7, 6, 9, 0]))

def distinct(nums: list):
    num_dict = {}
    for n in nums:
        if num_dict.get(n, 0) == 0:
            num_dict[n] = 1
    return len(num_dict)
print(distinct([5, 3, 0, 8, 1, 7, 10, 7, 6, 9, 0]))

def average_grade(grades: list):
    grade_by_student = {}
    for t in grades:
        name, grade = t
        if name not in grade_by_student:
            grade_by_student[name] = [grade]
        else:
            grade_by_student[name].append(grade)
    
    for key, val in grade_by_student.items():
        grade_by_student[key] = sum(val) / len(val)
    
    return grade_by_student
print(average_grade([('Way', 90), ('Way', 80), ('H', 70), ('H', 60), ('Way', 50)]))

def order_by_age_and_city(persons: list):
    for m in range(len(persons)):
        for n in range(len(persons) - m - 1):
            if persons[n][1] > persons[n+1][1]:
                persons[n], persons[n+1] = persons[n+1], persons[n]
                continue
            if persons[n][1] == persons[n+1][1] and persons[n][2] > persons[n+1][2]:
                persons[n], persons[n+1] = persons[n+1], persons[n]
                continue
    
    return persons

print(order_by_age_and_city([('bob', 10, 'Brisbane'), ('alice',30, 'Sydney'), ('tom', 10, 'Brisbane'), ('jane', 20, 'Sydney'), ('harry', 20, 'Brisbane')]))

