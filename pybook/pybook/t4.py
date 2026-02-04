def validate_exp(exp) -> bool:
    closeOps = {"}": "{", "]": "[", ")": "("}
    openOps = {"{", "[", "("}
    stack = []
    for c in exp:
        if c in openOps:
            stack.append(c)
        elif c in closeOps:
            if not stack:
                return False
            if stack.pop() != closeOps[c]:
                return False
    print(stack)
    return not stack
