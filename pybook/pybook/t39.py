class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, n):
        self.stack.append(n)
        if self.min_stack:
            self.min_stack.append(min(self.min(), n))
        else:
            self.min_stack.append(n)

    def pop(self):
        self.min_stack.pop()
        return self.stack.pop()

    def min(self):
        if not self.min_stack:
            return None
        return self.min_stack[-1]
