---
series: discrete-math-101
episode: 9
title: "Discrete Math 101 (9/10): Trees and Graph Traversal"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Discrete Math
  - Trees
  - BFS
  - DFS
  - Spanning Trees
seo_description: Trees, BFS and DFS, spanning trees, and the minimum spanning tree (MST) — the core graph traversal toolkit, explained with code.
last_reviewed: '2026-05-04'
---

# Discrete Math 101 (9/10): Trees and Graph Traversal

This is post 9 in the Discrete Math 101 series.

> Discrete Math 101 series (9/10)

**Core question**: On a graph, how do we answer "where can we get from here?" or "what is the cheapest way to connect everything?"

> A tree is a connected acyclic graph — the most common substructure in graph algorithms. This article walks through the two fundamental graph traversals, breadth-first search (BFS) and depth-first search (DFS), and the concepts of spanning trees and minimum spanning trees (MST), with working code.


![discrete math 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/09/09-01-big-picture.en.png)
*discrete math 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Trees and Graph Traversal?
- Which signal should the example or diagram make visible for Trees and Graph Traversal?
- What failure should be prevented first when Trees and Graph Traversal reaches a real system?

## What You Will Learn

- The definition and properties of trees (V-1 = E, unique paths)
- BFS — queue-based breadth-first traversal
- DFS — stack/recursion-based depth-first traversal
- The intuition behind spanning trees and MST

## Why It Matters

File systems, the DOM, compiler ASTs, database indexes — almost every system hides a tree. BFS and DFS are the starting points of graph algorithms and underpin shortest-path search, cycle detection, topological sort, and MST.

> A tree is the simplest non-trivial graph; traversal is the basic motion of every graph algorithm.

> Tree: a connected, acyclic, undirected graph. With n vertices it has exactly n-1 edges, and any two vertices are connected by exactly one path.

```text
       tree                    BFS order            DFS order
        1                    1 → 2 → 3            1 → 2 → 4
       / \                   → 4 → 5 → 6          → 5 → 3 → 6
      2   3                  (level by level)     (one branch first)
     / \   \
    4   5   6
```

## Key Terms

| Term | Description |
| --- | --- |
| Tree | Connected acyclic graph |
| Root | Optional starting vertex |
| Leaf | Vertex of degree 1 |
| Spanning tree | Sub-tree containing every vertex |
| MST | Spanning tree of minimum total weight |

## Before / After

**Before — checking every node by hand:**

```python
# Friends-of-friends, written manually — duplicate code per depth
def friends_of_friends(person):
    result = set()
    for f in friends_of(person):
        for ff in friends_of(f):
            result.add(ff)
    return result
```

**After — BFS for arbitrary distance:**

```python
from collections import deque

def reachable_within(graph, start, max_distance):
    """All vertices within distance max_distance from start."""
    visited = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        if visited[v] >= max_distance:
            continue
        for u in graph[v]:
            if u not in visited:
                visited[u] = visited[v] + 1
                queue.append(u)
    return visited
```

## Hands-On: Step by Step

### Step 1: Defining and verifying a tree

```python
from collections import defaultdict

def is_tree(edges: list, n_nodes: int) -> bool:
    """Test whether an undirected graph is a tree — check edge count and connectivity."""
    if len(edges) != n_nodes - 1:
        return False
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    visited = set()
    stack = [next(iter(adj))]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        stack.extend(adj[v] - visited)
    return len(visited) == n_nodes

tree_edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
print(f"is tree: {is_tree(tree_edges, 6)}")
```

The key property: with n vertices a tree has exactly n-1 edges, and removing any edge disconnects it.

### Step 2: BFS — breadth-first search

```python
def bfs(graph: dict, start) -> dict:
    """Minimum number of edges from start to every vertex (assuming weight 1)."""
    distances = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in sorted(graph[v]):
            if u not in distances:
                distances[u] = distances[v] + 1
                queue.append(u)
    return distances

graph = {1: [2, 3], 2: [1, 4, 5], 3: [1, 6], 4: [2], 5: [2], 6: [3]}
print(f"distances from 1: {bfs(graph, 1)}")
```

BFS visits closer vertices first by using a queue. When all edge weights are equal, BFS finds shortest paths.

**Expected output**

```text
distances from 1: {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2}
```

- Vertices `2` and `3` must be one edge away from `1`, and `4`, `5`, `6` must be two edges away.
- If the distances are wrong, the usual bug is marking visited too late or accidentally using stack behavior instead of queue behavior.

### Step 3: DFS — depth-first search

```python
def dfs_recursive(graph: dict, start, visited=None) -> list:
    """Recursive DFS — returns visit order."""
    if visited is None:
        visited = set()
    if start in visited:
        return []
    visited.add(start)
    order = [start]
    for u in sorted(graph[start]):
        order.extend(dfs_recursive(graph, u, visited))
    return order

def dfs_iterative(graph: dict, start) -> list:
    """Stack-based DFS — safe when depth is large."""
    visited, order, stack = set(), [], [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v); order.append(v)
        stack.extend(sorted(graph[v], reverse=True))
    return order

print(f"DFS recursive: {dfs_recursive(graph, 1)}")
print(f"DFS iterative: {dfs_iterative(graph, 1)}")
```

DFS goes deep along a single path before backtracking. It is the engine for cycle detection, topological sort, and strongly connected components.

**Expected output**

```text
DFS recursive: [1, 2, 4, 5, 3, 6]
DFS iterative: [1, 2, 4, 5, 3, 6]
```

- In this walkthrough both versions match because neighbor order is fixed with `sorted(...)`.
- If your order differs, the first thing to inspect is not the DFS idea itself but the neighbor ordering used during traversal.

### Step 4: Spanning trees from BFS/DFS

```python
def spanning_tree_bfs(graph: dict, start) -> list:
    """Extract a spanning tree via BFS."""
    visited = {start}
    tree = []
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in sorted(graph[v]):
            if u not in visited:
                visited.add(u)
                tree.append((v, u))
                queue.append(u)
    return tree

print(f"spanning tree (BFS): {spanning_tree_bfs(graph, 1)}")
```

Both BFS and DFS produce a spanning tree of the graph — a subgraph that contains every vertex and has no cycles.

**Expected output**

```text
spanning tree (BFS): [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
```

- A BFS spanning tree fixes each parent the first time the vertex is discovered, so this edge list should be stable for the sample graph.
- The tree must contain exactly `|V| - 1 = 5` edges because it spans 6 vertices.

### Step 5: Minimum spanning tree (MST) — Kruskal

```python
def kruskal_mst(n_nodes: int, weighted_edges: list) -> list:
    """Spanning tree of minimum total weight — uses Union-Find."""
    parent = list(range(n_nodes))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[ra] = rb
        return True

    mst = []
    for w, u, v in sorted(weighted_edges):
        if union(u, v):
            mst.append((u, v, w))
        if len(mst) == n_nodes - 1:
            break
    return mst

edges = [(1, 0, 1), (4, 0, 2), (2, 1, 2), (3, 1, 3), (5, 2, 3)]
mst = kruskal_mst(4, edges)
total_weight = sum(w for _, _, w in mst)
print(f"MST: {mst}")
print(f"total weight: {total_weight}")
```

Kruskal sorts edges by weight and picks each one that does not form a cycle. It is used in network design, clustering, and circuit layout.

**Expected output**

```text
MST: [(0, 1, 1), (1, 2, 2), (1, 3, 3)]
total weight: 6
```

- The algorithm should keep the three cheapest non-cycling edges and stop after `n_nodes - 1` edges.
- If you get a different answer, inspect the Union-Find cycle check first; that is the most common Kruskal bug.

## Notable Points

- BFS and DFS share the same skeleton — only the underlying data structure differs (queue vs stack).
- A tree can be verified with the simple V-1 = E property (plus connectivity).
- A BFS spanning tree is also a shortest-path tree (when weights are equal).
- MST is a rare case where a greedy algorithm is provably optimal.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Forgetting to mark visited | Infinite loop | Add to visited the moment you enter |
| Confusing queue and stack | BFS that behaves like DFS | Verify deque.popleft vs pop |
| Stack overflow on recursion | RecursionError | Use iterative DFS for large graphs |
| BFS on weighted graphs | Wrong shortest path | With weights, switch to Dijkstra |
| MST without cycle check | Result is not a tree | Use Union-Find to block cycles |

## How This Is Used in Practice

- Web crawlers paging through links (BFS with depth limits)
- Compiler AST traversal (DFS, post-order)
- Game AI state-space search (BFS, DFS, A*)
- Designing a minimum-cost network (MST)
- React virtual DOM diffing (tree comparison)

## How a Senior Engineer Thinks

When a senior engineer sees a graph problem, the first decision is "BFS or DFS?" Shortest paths and level-by-level work go to BFS; path discovery, topological sort, and cycle detection go to DFS. They are also memory-aware: for large graphs they switch to iterative DFS with an explicit stack rather than risking a recursion blow-up.

## Checklist

- [ ] Do you know the tree definition and the V-1 = E property?
- [ ] Can you describe BFS vs DFS in terms of data structures?
- [ ] Do you know the conditions under which BFS gives shortest paths?
- [ ] Do you understand the difference between a spanning tree and an MST?
- [ ] Do you know the role of Union-Find in Kruskal?

## Practice Problems

1. For a tree with 5 vertices, find the number of edges and the minimum number of leaves.

2. Write a BFS that finds the shortest path from start to goal in a 2D maze grid.

3. With 6 cities and arbitrary weights, work out the MST by hand using Kruskal.

## Wrap-Up and Next Steps

A tree is a connected acyclic graph. BFS and DFS are the most fundamental traversals on graphs, and an MST is the cheapest sub-tree that still connects every vertex.

The next article ties everything together: how all the discrete-math topics covered so far show up in algorithm analysis and real engineering work.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Trees and Graph Traversal?**
  - The article treats Trees and Graph Traversal as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Trees and Graph Traversal?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Trees and Graph Traversal reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Discrete Math 101 (1/10): What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): Propositions and Logic](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): Relations and Equivalence](./04-relations-and-equivalence.md)
- [Discrete Math 101 (5/10): Proof Techniques](./05-proof-techniques.md)
- [Discrete Math 101 (6/10): Sequences and Recurrence](./06-sequences-and-recurrence.md)
- [Discrete Math 101 (7/10): Combinatorics](./07-combinatorics.md)
- [Discrete Math 101 (8/10): Graph Theory Basics](./08-graph-theory-basics.md)
- **Trees and Graph Traversal (current)**
- Discrete Mathematics and Algorithms (upcoming)

<!-- toc:end -->

## References

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 11](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Algorithms — Sedgewick & Wayne, Section 4.1 Undirected Graphs](https://algs4.cs.princeton.edu/41graph/)
- [Algorithms — Sedgewick & Wayne, Chapter 4.3](https://algs4.cs.princeton.edu/43mst/)
- [MIT Mathematics for Computer Science — Trees and Graph Traversal](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)

Tags: Computer Science, Discrete Math, Trees, BFS, DFS, Spanning Trees
