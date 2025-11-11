import itertools
def factorial(n: int):
    res = 1
    for i in range(n):
        res = res * (i+1)
    return res

print(factorial(0)) 
print(factorial(1)) 
print(factorial(10)) 

def permutation_self(iteral):
    elems = tuple(iteral)
    results = []
    if len(elems) == 1:
        return [(elems[0],)]
    for i in range(len(elems)):
        remain = elems[:i] + elems[i+1:]
        for r in permutation_self(remain):
            results.append((elems[i],) + r)
    
    return results


def permutation_self2(iteral):
    visited = set()

    def _permutation_helper(elems:tuple, v:set):
        results = []
        selected = set()
        for idx in range(len(elems)):
            if idx in v or elems[idx] in selected:
                continue
            v.add(idx)
            sub_results = _permutation_helper(elems, v)
            if sub_results:
                results.extend([(elems[idx],) + res for res in sub_results])
            else:
                results.append((elems[idx],))
            v.remove(idx)
            selected.add(elems[idx])
        return results
        
    return(_permutation_helper(tuple(iteral), visited))

def combination_self(iteral, r):
    elems = list(iteral)
    results = []
    if r > len(elems):
        return []
    if r == 0:
        return [set()]

    for i in range(len(elems)):
        remain = elems[i+1:]
        for one_res in combination_self(remain, r - 1):
            one_res.add(elems[i])
            results.append(one_res)
            #results.append({elems[i]} | one_res)
    return results

def combination_self2(iteral, r):
    pool = set(iteral)
    
    if r > len(pool):
        return []
    if r == 0:
        return [()]
    results = []
    k = pool.pop()

    results.extend([(k,) + comb for comb in combination_self2(pool, r - 1)])
    results.extend(combination_self2(pool, r))
    return results

def combination_self3(iteral, r):
    pool = tuple(iteral)
    if r > len(pool):
        return []
    if r == 0:
        return [()]
    results = []
    results.extend([(pool[0],) + comb for comb in combination_self3(pool[1:], r - 1)])
    results.extend(combination_self3(pool[1:], r))
    return results

# print(permutation_self(range(5)))
# print(permutation_self2(range(5)))
# print(list(itertools.permutations(range(5))))

print(permutation_self([1,1,2,3,3]))
print(len(permutation_self([1,1,2,3,3])))
print(permutation_self2([1,1,2,3,3]))
print(len(permutation_self2([1,1,2,3,3])))
print(list(itertools.permutations([1,1,2,3,3])))
print(len(list(itertools.permutations([1,1,2,3,3]))))

# print(combination_self(range(5), 3))
# print(combination_self2(range(5), 3))
# print(combination_self3(range(5), 3))
# print(list(itertools.combinations(range(5), 3)))
# print((1, "aa"))
