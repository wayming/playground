from itertools import permutations, combinations_with_replacement
def permutation1(elems: tuple, visits: set, path: list, results: list):
    if len(path) == len(elems):
        results.append(path)
        return
    
    duplicates = set()
    for idx in range(len(elems)):
        e = elems[idx]
        if e in duplicates or idx in visits:
            continue
        duplicates.add(e)
        visits.add(idx)
        path.append(e)
        sub_results = permutation1(elems, visits, path, results)
        path.pop()
        visits.remove(idx)
    

def permutation1_w(iterals):
    results = []
    visits = set()
    permutation1(tuple(iterals), visits, [], results)
    return results
print(len(permutation1_w([1, 3, 5, 1, 2, 4, 8])))
print(len(list(permutations([1, 3, 5, 1, 2, 4, 8], 7))))


def combination1(elems: tuple, visits: set, path: list, results: list, r: int):

    if len(path) == r:
        results.append(path[::])
        return
        
    for idx in range(len(elems)):
        e = elems[idx]
        if idx in visits:
            continue
        path.append(e)
        combination1(elems[idx+1:], visits, path, results, r)
        path.pop()

def combination1_w(iterals, r:int):
    results = []
    visits = set()
    combination1(tuple(iterals), visits, [], results, r)
    return results


print(len(combination1_w([1, 3, 5, 2, 4, 1], 3)))
print(combination1_w([1, 3, 5, 2, 4, 1], 3))
# print(len(list(combinations_with_replacement([1, 3, 5, 1, 2, 4, 8], 5))))

#print(list(combinations_with_replacement([1, 3, 5, 1, 2, 4, 8], 7)))

def combination2(elems: tuple, path: list, results: list, target: int):

    if target == 0:
        results.append(path[::])
        return
    if target < 0:
        return
    for idx in range(len(elems)):
        e = elems[idx]
        path.append(e)
        combination2(elems[idx+1:], path, results, target-e)
        path.pop()

def combination2_w(iterals, target:int):
    results = []
    combination2(tuple(iterals), [], results, target)
    return results

print(len(combination2_w([1, 3, 5, 2, 4, 1], 6)))
print(combination2_w([1, 3, 5, 2, 4, 1], 6))



def combination3(elems: tuple, path: list, results: list, target: int):

    if target == 0:
        results.append(path[::])
        return
    if target < 0:
        return
    
    selected = set()
    for idx in range(len(elems)):
        e = elems[idx]
        if e in selected: # e can be selected in the recurision but not this loop
            continue
        selected.add(e)
        path.append(e)
        combination3(elems[idx+1:], path, results, target-e)
        path.pop()

def combination3_w(iterals, target:int):
    results = []
    combination3(tuple(sorted(iterals)), [], results, target)
    return results

print(len(combination3_w([1, 3, 5, 2, 4, 1], 6)))
print(combination3_w([1, 3, 5, 2, 4, 1], 6))