class t96_Node:
    def __init__(self, v, next):
        self.v = v
        self.next = next

    def values(self):
        v = [self.v]
        next = self.next
        while next:
            v.append(next.v)
            next = next.next
        return v

    def reverse(self):
        fast = self.next
        slow = self
        slow.next = None
        while fast:
            ffast = fast.next
            fast.next = slow
            slow = fast
            fast = ffast
        return slow
