from collections import Counter, defaultdict, deque

def top5_words(text: str):
    words = text.split(' ')
    words = [ w for w in words if w != '' ]
    counter = Counter(words)
    return counter.most_common(5)

    
print(top5_words("""
    There are hundreds of thousands of wikis in use, both public and private, including wikis functioning
    as knowledge management resources, note-taking tools, community websites, and intranets. Ward Cunningham,
    the developer of the first wiki software, WikiWikiWeb, originally described wiki as 
    the simplest online database that could possibly work
    """))


def avg_grades(grades: list):
    classToGrade = defaultdict(list)
    for v in grades:
        className, student, grade = v
        classToGrade[className].append(grade)
    
    return {k: sum(v)/len(v) for k, v in classToGrade.items()}

grades = [("classA", "Alice", 90), ("classB", "Bob", 85), ("classA", "Tom", 92)]

print(avg_grades(grades))

def count_users(listA: set, listB: set):
    commonSet = listA & listB
    aonlySet = listA - listB
    singleSet = listA ^ listB
    print(f"common len {len(commonSet)}")
    print(f"aonly len {len(aonlySet)}")
    print(f"single len {len(singleSet)}")
count_users({1,2,3,4,5}, {4,5,6,7,8})

class CommandQueue:
    def __init__(self):
        self.q = deque()
    def run(self, command: str):
        cmd = command.split( )
        op = cmd[0]
        if op == "PUSH":
            if len(cmd) < 2:
                raise "missing push parameter"
            self.q.append(cmd[1])
            print(f"push {cmd[1]}")
        elif op == "POP":
            v = self.q.popleft()
            print(f"pop {v}")
        elif op == "SIZE":
            print(f"size {len(self.q)}")
        else:
            raise f"unknown op {op}"
        
cq = CommandQueue()
cq.run("PUSH 100")
cq.run("PUSH 200")
cq.run("POP")
cq.run("SIZE")

l = [x for x in [ x*x for x in range(100)] if x % 2 == 0]
print(l)

def sort_words(words: list):
    words.sort(key=lambda x : (len(x), x))

def sort_samelen(words: list):
    for i in range(len(words) - 1):
        for j in range(len(words) - i - 1):
            if words[j] > words[j+1]:
                words[j], words[j+1] = words[j+1], words[j]
def sort_words2(words: list):
    l = [[] for i in range(1000)]
    for w in words:
        l[len(w)].append(w)
    for sameLen in l:
        sort_samelen(sameLen)
    words[:] = [w for sameLen in l for w in sameLen]


words = ["hello", "world", "python", "is", "awesome"]   
sort_words(words)
print(words)

words2 = ["hello", "world", "python", "is", "awesome"]   
sort_words2(words2)
print(words2)

def sort_grade(grades : dict):
    gradesList = []
    for k, v in grades.items():
        gradesList.append((k, v))
    gradesList.sort(key=lambda x : x[1], reverse=True)
    begin = 0
    score = gradesList[0][1]
    print("gradesList", gradesList)
    for i in range(len(gradesList)):
        if gradesList[i][1] == score:
            continue
        else:
            print("begin", begin, "i", i)
            gradesList[begin:i] = sorted(gradesList[begin:i], key=lambda x : x[0])
            begin = i
            score = gradesList[i][1]
    gradesList[begin:] = sorted(gradesList[begin:], key=lambda x : x[0])
    return gradesList
def sort_grade2(grades: dict):
    gradesList = []
    for k, v in grades.items():
        gradesList.append((k, v))
    gradesList.sort(key=lambda x : (-x[1], x[0]))
    return gradesList
grades = {"Alice": 90, "Bob": 85, "Tom": 90}
print(sort_grade2(grades))
grades = {"Tom": 90, "Bob": 85, "Alice": 90, }
print(sort_grade(grades))

nums = [1,2,3,4,5]
print({x : x * x for x in nums})