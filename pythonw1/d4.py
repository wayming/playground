from functools import reduce
from itertools import permutations, combinations, combinations_with_replacement
l1 = [1,3,10,2,9,7]
for x in map(lambda x: x * x, filter(lambda x : x % 2 == 0, l1)):
    print(x)

print(reduce(lambda x, y: x * y, l1))

l2 = 'abc'
for x in permutations(l2):
    print(x)
print("end of permutations")
for x in (combinations(l2, 3)):
    print(x)
print("end of combinations")
for x in combinations_with_replacement(l2, 3):
    print(x)
print("end of combinations_with_replacement")

def permutations(iterable, r = None):
    pool = tuple(iterable)
    r = len(pool) if r == None else r
    if len(pool) == 0 or r == 0:
        return [()]
    if len(pool) == 1:
        return [pool]
    
    results = []
    for i in range(len(pool)):
        remain = pool[:i] if i == len(pool) -1 else pool[:i] + pool[i+1:]
        for re in permutations(remain, r - 1):
            results.append((pool[i],) + re)
    return results

# for i in permutations(set('abca')):
#     print(i)

# for i in permutations('abc', 2):
#     print(i)


def combination(iterable, r = None):
    pool = tuple(iterable)
    r = len(pool) if r == None else r
    
    if len(pool) == 0 or r == 0:
        return [()]
    
    if len(pool) == 1:
        if r == 1:
            return [pool]
        elif r > 1:
            return []
    
    results = []
    #print(pool)
    results.extend([(pool[0],) + x for x in combination(pool[1:], r - 1)])
    results.extend(combination(pool[1:], r))
    
    return results

for i in combination('abc', 2):
    print(i)
    

for i in combination('abca', 3):
    print(i)
    
def fab():
    x = 1
    y = 2
    while True:
        yield x
        x, y = y, x + y
        

f = fab()
for _ in range(1000):
    print(next(f))
    