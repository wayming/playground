def parentheses_match(s: str):
    match = {"{": "}", "[": "]", "(": ")"}
    stack = []
    for c in s:
        if c in match:
            stack.append(match[c])
            print(stack)
        elif c in match.values() and (not stack or stack.pop() != c):
            return False

    return not stack
