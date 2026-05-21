---
series: data-structures-python-101
episode: 6
title: "Data Structures with Python 101 (6/10): Trees and Binary Trees"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Data Structures
  - Tree
  - Binary Tree
  - BST
seo_description: Implement binary trees and binary search trees in Python and practice traversal algorithms.
last_reviewed: '2026-05-15'
---

# Data Structures with Python 101 (6/10): Trees and Binary Trees

> Data Structures with Python 101 Series (6/10)

**Key Question**: Why do file systems, org charts, and the DOM all use tree structures?

> Trees naturally represent hierarchical relationships. Binary search trees (BSTs) enable O(log n) lookups on sorted data. This article covers tree concepts, binary tree implementation, traversal algorithms, and binary search trees.

This is post 6 in the Data Structures with Python 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Trees and Binary Trees?
- Which signal should the example or diagram make visible for Trees and Binary Trees?
- What failure should be prevented first when Trees and Binary Trees reaches a real system?

## Big Picture

![Data Structures with Python 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/06/06-01-tree-shape-at-a-glance.en.png)

*Data Structures with Python 101 chapter 6 flow overview*

This picture places Trees and Binary Trees inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- Basic tree terminology and structure
- Implementing binary trees in Python
- Preorder, inorder, postorder, and level-order traversals
- How binary search trees (BSTs) work

## Why It Matters

Trees are one of the most important data structures in computer science. File systems, HTML DOMs, database indexes (B-Trees), and JSON parse trees — trees are everywhere.

> Understanding trees dramatically improves your recursive thinking. Most tree algorithms are naturally expressed with recursion.

Binary search trees maintain sorted data while performing insertion, deletion, and lookup in O(log n) — vastly faster than linear search O(n) on a list.

## Concept Overview

> Tree = a hierarchical structure that branches from a root to child nodes

```text
        [root]
       /      \
    [child]  [child]
    /   \       \
 [leaf] [leaf]  [leaf]

Binary Search Tree (BST):
        [8]
       /   \
     [3]   [10]
    /   \      \
  [1]   [6]   [14]
```

## Tree Shape at a Glance

## Key Concepts

| Term | Description |
|------|------------|
| root | The topmost node in a tree |
| leaf | A node with no children |
| depth | The distance from the root to a given node |
| height | The distance from a given node to its farthest leaf |
| Binary Search Tree (BST) | A tree where left child < parent < right child |

## Before / After

Compare searching a sorted list versus searching a BST.

```python
# before: linear search in a sorted list — O(n)
data = [1, 3, 6, 8, 10, 14]
for item in data:
    if item == 10:
        print("found")
        break
```

```python
# after: BST search — O(log n)
# BST: 8 → 10 → found (2 steps)
def search_bst(node, target):
    if node is None:
        return False
    if target == node.data:
        return True
    elif target < node.data:
        return search_bst(node.left, target)
    else:
        return search_bst(node.right, target)
```

## Hands-On Steps

### Step 1: Define a binary tree node

```python
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

    def __repr__(self):
        return f"TreeNode({self.data})"
```

### Step 2: Implement tree traversals

```python
def inorder(node):
    """Inorder traversal: left → root → right"""
    if node is None:
        return []
    return inorder(node.left) + [node.data] + inorder(node.right)

def preorder(node):
    """Preorder traversal: root → left → right"""
    if node is None:
        return []
    return [node.data] + preorder(node.left) + preorder(node.right)

def postorder(node):
    """Postorder traversal: left → right → root"""
    if node is None:
        return []
    return postorder(node.left) + postorder(node.right) + [node.data]

# Build tree:        1
#                  /   \
#                 2     3
#                / \
#               4   5
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(f"inorder:   {inorder(root)}")    # [4, 2, 5, 1, 3]
print(f"preorder:  {preorder(root)}")   # [1, 2, 4, 5, 3]
print(f"postorder: {postorder(root)}")  # [4, 5, 2, 3, 1]
```

### Step 3: Level-order traversal (BFS)

```python
from collections import deque

def level_order(root):
    """Level-order traversal: nodes at the same depth, left to right"""
    if root is None:
        return []
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        result.append(node.data)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return result

print(f"level-order: {level_order(root)}")  # [1, 2, 3, 4, 5]
```

### Step 4: Implement a binary search tree

```python
class BST:
    def __init__(self):
        self.root = None

    def insert(self, data):
        self.root = self._insert(self.root, data)

    def _insert(self, node, data):
        if node is None:
            return TreeNode(data)
        if data < node.data:
            node.left = self._insert(node.left, data)
        elif data > node.data:
            node.right = self._insert(node.right, data)
        return node

    def search(self, data):
        return self._search(self.root, data)

    def _search(self, node, data):
        if node is None:
            return False
        if data == node.data:
            return True
        elif data < node.data:
            return self._search(node.left, data)
        else:
            return self._search(node.right, data)

    def inorder(self):
        return inorder(self.root)

bst = BST()
for val in [8, 3, 10, 1, 6, 14]:
    bst.insert(val)

print(bst.inorder())       # [1, 3, 6, 8, 10, 14] — sorted result
print(bst.search(6))       # True
print(bst.search(7))       # False
```

### Step 5: Compute tree height and node count

```python
def tree_height(node):
    if node is None:
        return -1
    return 1 + max(tree_height(node.left), tree_height(node.right))

def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

print(f"height: {tree_height(bst.root)}")      # 2
print(f"node count: {count_nodes(bst.root)}")   # 6
```

## What to Notice in This Code

- Tree algorithms are naturally expressed with recursion — the base case is node is None
- Inorder traversal of a BST returns a sorted result
- Level-order traversal uses a queue (deque) — this is the BFS pattern
- BST search discards half the tree at each step, achieving O(log n)

That O(log n) story holds only while the tree stays reasonably balanced. Insert already-sorted data into a naive BST and it degenerates into a linked-list-shaped structure, pushing search and insert back toward O(n). Production systems avoid that failure mode with self-balancing trees or B-Tree variants.

There is also a Python-specific constraint: recursion depth. Recursive traversal is elegant, but very deep trees can trigger RecursionError and large node graphs can add heavy object overhead. In production, the right question is not just "is a tree correct?" but also "how deep can it get, and who maintains balance?"

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Missing recursive base case | Causes infinite recursion and RecursionError | Always check node is None first |
| Not handling duplicate values in BST | Produces an unexpected tree structure | Define a clear duplicate policy (ignore or count) |
| Not recognizing skewed trees | BST degenerates to O(n) | Consider balanced trees (AVL, Red-Black) |
| Confusing traversal orders | Produces wrong results | Memorize: preorder (NLR), inorder (LNR), postorder (LRN) |
| Underestimating delete complexity | Deleting a node with two children is tricky | Learn the in-order successor pattern |

## Real-World Applications

- Database indexes are implemented as B-Trees/B+Trees
- File system directory structures are trees
- HTML/XML DOMs are tree structures
- Expression parsers generate ASTs (abstract syntax trees)
- Autocomplete features are implemented with tries (prefix trees)

## How Senior Engineers Think About This

In practice, you rarely implement a BST from scratch. Python's sorted(), the bisect module, and database indexes handle most sorting and searching needs. But understanding tree internals helps you grasp how those tools work under the hood.

There is no better data structure than trees for practicing recursive thinking. The more tree problems you solve, the more natural recursion becomes.

## Checklist

- [ ] Can explain root, leaf, depth, and height of a tree
- [ ] Can implement preorder, inorder, postorder, and level-order traversals
- [ ] Can implement insertion and search in a BST
- [ ] Can explain why inorder traversal of a BST returns a sorted result
- [ ] Can compute tree height and node count recursively

## Exercises

1. Write a function that validates whether a binary tree is a BST. (Hint: the inorder traversal result must be sorted)
2. Write a function that checks whether two binary trees are structurally identical.
3. Implement a function that deletes a value from a BST. (Handle cases with 0, 1, and 2 children)

## Summary and Next Steps

Trees represent hierarchical structures, and BSTs search sorted data in O(log n). Tree traversals are naturally implemented with recursion. The next article covers heaps and priority queues — a specialized form of trees.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Trees and Binary Trees?**
  - The article treats Trees and Binary Trees as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Trees and Binary Trees?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Trees and Binary Trees reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures with Python 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): Arrays and Lists](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): Stacks and Queues](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): Hash Tables and dict](./04-hash-tables-and-dict.md)
- [Data Structures with Python 101 (5/10): Linked Lists](./05-linked-lists.md)
- **Trees and Binary Trees (current)**
- Heaps and Priority Queues (upcoming)
- Graph Representations (upcoming)
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)

<!-- toc:end -->

## References

- [Runestone Academy — Trees](https://runestone.academy/ns/books/published/pythonds3/Trees/toctree.html)
- [Python Docs — bisect](https://docs.python.org/3/library/bisect.html)
- [SQLite File Format — B-Tree Pages](https://www.sqlite.org/fileformat.html#b_tree_pages)
- [Real Python — Binary Trees in Python](https://realpython.com/binary-search-python/)

Tags: Python, Data Structures, Tree, Binary Tree, BST
