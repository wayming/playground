def revert(s: str):
    front = 0
    end = len(s) - 1
    l = list(s)
    while front <= end:
        l[front], l[end] = l[end], l[front]
        front += 1
        end -= 1
    return "".join(l)
