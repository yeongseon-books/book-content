---
series: data-structures-101
episode: 6
title: Trees
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Data Structures
  - Tree
  - Hierarchy
  - Recursion
  - Traversal
seo_description: Tree fundamentals, ways to represent them, and the three depth-first traversals (preorder, inorder, postorder) implemented from scratch.
last_reviewed: '2026-05-04'
---

# Trees

> Data Structures 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: What single data structure powers file systems, the HTML DOM, organization charts, and regex parsers?

> A tree branches out from a starting node into multiple children, forming a hierarchy. With just two rules — no cycles and exactly one parent per node — you can express almost any hierarchy. This article walks through tree terminology, two representations, and the three classic depth-first traversals (preorder, inorder, postorder) implemented from scratch.

<!-- a-grade-intro:end -->

## What You Will Learn

- Core tree terminology (root, leaf, depth, height)
- The difference between a general tree and a binary tree
- The three depth-first traversals: preorder, inorder, postorder
- How depth-first compares with breadth-first traversal

## Why It Matters

Trees are the basic skeleton of nearly every hierarchical dataset: database indexes, the abstract syntax tree (AST) of a compiler, the file system in an operating system, the parsed result of JSON or XML. Without fluency in trees, you cannot handle graphs, BSTs, or heaps with confidence.

> A tree is the structure where recursion feels most natural.

## Concept at a Glance

> A tree is a connected, acyclic graph of nodes and edges. A binary tree is a tree where each node has at most two children — the form algorithms use most often.

```text
            A          ← root, depth 0
          /   \
         B     C       ← depth 1
        / \     \
       D   E     F     ← depth 2 (leaves)

terms:
- A's children: B, C
- B's parent: A
- B's sibling: C
- leaves: D, E, F
- height of the tree: 2
- node count: 6
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Root | The unique node with no parent |
| Leaf | A node with no children |
| Depth | Edges from the root to the node |
| Height | Edges from the node to the farthest leaf |
| Subtree | A node and all its descendants |

## Before / After

**Before — representing hierarchy with a flat list:**

```python
items = [
    ("/", None),
    ("home", "/"),
    ("docs", "/home"),
    ("a.txt", "/home/docs"),
]
# Finding parents, listing children, computing depth — all painful
```

**After — representing hierarchy with tree nodes:**

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

root = Node("/")
home = Node("home"); root.children.append(home)
docs = Node("docs"); home.children.append(docs)
docs.children.append(Node("a.txt"))
# Children and descendants traverse naturally with recursion
```

## Hands-On: Step by Step

### Step 1: Define a General Tree

```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child


root = TreeNode("CEO")
cto = root.add(TreeNode("CTO"))
cfo = root.add(TreeNode("CFO"))
cto.add(TreeNode("Backend Lead"))
cto.add(TreeNode("Frontend Lead"))
cfo.add(TreeNode("Accountant"))
```

Each node holds a value and a list of children. With no cap on the children count, this is a general tree.

### Step 2: Binary Tree

```python
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# Build the tree
#         1
#        / \
#       2   3
#      / \
#     4   5
root = BinaryNode(1,
                  BinaryNode(2, BinaryNode(4), BinaryNode(5)),
                  BinaryNode(3))
```

With at most two children, the memory layout is simpler and the algorithms become more standardized.

### Step 3: The Three Depth-First Traversals

```python
def preorder(node):
    """root -> left -> right"""
    if node is None:
        return
    print(node.value, end=" ")
    preorder(node.left)
    preorder(node.right)


def inorder(node):
    """left -> root -> right"""
    if node is None:
        return
    inorder(node.left)
    print(node.value, end=" ")
    inorder(node.right)


def postorder(node):
    """left -> right -> root"""
    if node is None:
        return
    postorder(node.left)
    postorder(node.right)
    print(node.value, end=" ")


print("preorder: ", end=""); preorder(root); print()
print("inorder:  ", end=""); inorder(root); print()
print("postorder:", end=""); postorder(root); print()
# preorder:  1 2 4 5 3
# inorder:   4 2 5 1 3
# postorder: 4 5 2 3 1
```

When you visit the root determines the traversal. Postorder evaluates expressions, preorder copies trees, and inorder prints a BST in sorted order.

### Step 4: Breadth-First Traversal

```python
from collections import deque


def bfs(root):
    if root is None:
        return
    queue = deque([root])
    while queue:
        node = queue.popleft()
        print(node.value, end=" ")
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)


print("BFS:", end=" "); bfs(root); print()   # 1 2 3 4 5
```

You visit every node at the same depth before moving deeper. Use it for shortest paths or per-level processing.

### Step 5: Compute Height and Size

```python
def height(node):
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def count(node):
    if node is None:
        return 0
    return 1 + count(node.left) + count(node.right)


print(f"height: {height(root)}")    # 2
print(f"count:  {count(root)}")     # 5
```

Recursion fits trees naturally because the definition is itself recursive: "a tree is a root and a list of subtrees."

## Notable Points

- Trees are recursive by definition, which pairs well with recursive functions
- The difference between depth-first and breadth-first is the choice of stack vs queue
- Binary trees are simpler than general trees but support a richer set of algorithms
- Very deep trees can blow up the recursion stack

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Mixing children list and left/right | Bugs from blending general and binary code | Keep the two representations distinct |
| Missing the empty-node branch | NoneType errors | Check for None at the top of recursive calls |
| Confusing depth with height | Wrong analysis | Depth measures from the top; height from the bottom |
| Recursion on deep trees | RecursionError | Convert to an explicit stack |
| Using a list for BFS | Slow O(n) pop | Use `collections.deque` |

## How This Is Used in Practice

- File systems are the canonical example of a general tree
- Browsers parse HTML and XML into a DOM tree
- Compilers turn source code into an abstract syntax tree (AST) before generating output
- Databases use B-Tree and B+Tree indexes to accelerate sorted-key search
- Decision trees are the foundation of many machine-learning classifiers and regressors

## How a Senior Engineer Thinks

A senior engineer asks first whether a tree is balanced. A balanced tree guarantees O(log n), but a tree degenerated into a single line is effectively a linked list with O(n) operations. AVL, Red-Black, and B-Trees exist precisely to address this limit.

A senior engineer also fears deep recursion. When the tree depth depends on user input (like JSON parsing), they convert to an explicit stack to keep things safe in production. Elegant code and operationally safe code are not the same thing.

## Checklist

- [ ] I can use root, leaf, depth, and height precisely
- [ ] I can distinguish a general tree from a binary tree
- [ ] I know how preorder, inorder, and postorder differ
- [ ] I see DFS vs BFS as a choice of data structure
- [ ] I understand the time-complexity gap between balanced and unbalanced trees

## Practice Problems

1. Write a function that prints the average value at each level of the binary tree above. Combine BFS with a dict.

2. Define a notion of "balanced" for a tree, then write a function that verifies your definition.

3. For a general tree (children list), write a recursive function that returns the depth of the deepest leaf. Then write the same function with an explicit stack and compare them.

## Wrap-Up and Next Steps

A tree is a hierarchical structure with no cycles and exactly one parent per node — the form that meshes most naturally with recursion. The three depth-first traversals and breadth-first traversal are the basic toolkit, and switching between them is just a choice of data structure (stack vs queue). Binary trees are a special case but support a richer set of algorithms.

Next we look at the binary search tree (BST), a sorted binary tree. It offers average O(log n) lookups, but degrades to O(n) when balance is lost — a subtle structure worth careful attention.

<!-- toc:begin -->
- [What Are Data Structures?](./01-what-are-data-structures.md)
- [Arrays and Dynamic Arrays](./02-arrays-and-dynamic-arrays.md)
- [Linked Lists](./03-linked-lists.md)
- [Stacks and Queues](./04-stacks-and-queues.md)
- [Hash Tables](./05-hash-tables.md)
- **Trees (current)**
- Binary Search Trees (upcoming)
- Heaps (upcoming)
- Graphs (upcoming)
- Choosing Data Structures (upcoming)
<!-- toc:end -->

## References

- [Open Data Structures — Binary Trees](https://opendatastructures.org/ods-python/6_Binary_Trees.html)
- [Wikipedia — Tree (data structure)](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Wikipedia — Tree Traversal](https://en.wikipedia.org/wiki/Tree_traversal)
- [Python `ast` module docs](https://docs.python.org/3/library/ast.html)

Tags: Computer Science, Data Structures, Tree, Hierarchy, Recursion, Traversal
