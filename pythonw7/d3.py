def two_sum(nums:list, target: int):
    idxes = {}
    for idx, n in enumerate(nums):
        if target - n in idxes:
            return (idx, idxes[target-n])
        else:
            idxes[n] = idx
    print(idxes)
    return (-1, -1)

idx1, idx2 = two_sum([1,2,3,4,5,6], 6)
print(idx1, " + ", idx2)

class ListNode:
    def __init__(self, val, next = None):
        self.data = val
        self.next = next

root = ListNode(
    1, ListNode(2, ListNode(3, ListNode(4, ListNode(5))))
)

def reverse(head: ListNode):
    if not head:
        return head
    curr = head
    next = curr.next
    pre = None
    while next:
        tmp = next.next
        next.next = curr
        curr.next = pre
        pre = curr
        curr = next
        next = tmp
    return curr

l = root
while l:
    print(l.data)
    l = l.next

l = root
l = reverse(l)
while l:
    print(l.data)
    l = l.next
    
