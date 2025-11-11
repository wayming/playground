from collections import deque
class Node:
    def __init__(self, val: None, left = None, right= None):
        self.val = val
        self.left = left
        self.right = right
    
    def val(self):
        return self.val

tree = Node(
    10, Node(9, Node(8), Node(7)), Node(6, Node(5), Node(3))
)

results = []
def bfs(root: Node):
    q = deque()
    q.append(root)
    
    while q:
        node = q.popleft()
        results.append(node.val)
        
        if node.left != None:
            q.append(node.left)
        
        if node.right != None:
            q.append(node.right)

#bfs(tree)

def dfs_inorder(root: Node):

    if root.left != None:
        dfs_inorder(root.left)

    results.append(root.val)
    
    if root.right != None:
        dfs_inorder(root.right)
# dfs_inorder(tree)
# print(results)

def dff_inorder_iteration(root: Node):
    stack = deque()
    stack.append(root)
    
    while stack:
        node = stack.pop()
        
        if node.left == None and node.right == None:
            results.append(node.val)
            if stack:
                node = stack.pop()
                results.append(node.val)
            continue
        
        if node.right != None:
            stack.append(node.right)
        stack.append(node)
        if node.left != None:
            stack.append(node.left)

# dff_inorder_iteration(tree)
# print(results)


results = []
pathes = []
path = []
def dfs_preorder(root: Node, path: list):
    if not root:
        return

    results.append(root.val)
    path.append(root.val)

    if not root.left and not root.right:
        pathes.append(path[:])
        return 

    if root.left:
        dfs_preorder(root.left, path)
        path.pop()
    
    if root.right:
        dfs_preorder(root.right, path)
        path.pop()
    
dfs_preorder(tree, path)
print(results)
print(pathes)