mem = {}

def steps(n: int):
    if n <= 0:
        return 0
    
    if n == 1:
        return 1
    
    if n == 2:
        return 2

    if n in mem:
        return mem[n]
    count = steps(n-1) + steps(n - 2)
    mem[n] = count
    return count

print(steps(10))