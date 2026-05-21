---
series: algorithms-python-101
episode: 7
title: "Algorithms with Python 101 (7/10): Graph Traversal — BFS and DFS"
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
  - Algorithms
  - Graphs
  - BFS
  - DFS
seo_description: Represent graphs in Python and implement BFS and DFS for shortest paths, cycle detection, and connected components.
last_reviewed: '2026-05-04'
---

# Algorithms with Python 101 (7/10): Graph Traversal — BFS and DFS

Networks, maps, dependency trees, and recommendation systems all reduce to relationships between nodes. That is why graph thinking shows up so often once you move past basic arrays and lists.

BFS and DFS are the two foundational traversal strategies. If you can tell when to use each one, shortest paths, cycle checks, and connected-component problems become much easier to reason about.

This is post 7 in the Algorithms with Python 101 series. Here, we'll represent graphs in Python and implement both BFS and DFS with practical use cases in mind.


![Algorithms with Python 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/07/07-01-concept-overview.en.png)
*Algorithms with Python 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Graph Traversal — BFS and DFS?
- Which signal should the example or diagram make visible for Graph Traversal — BFS and DFS?
- What failure should be prevented first when Graph Traversal — BFS and DFS reaches a real system?

## What You Will Learn

- Graph basics and how to represent them in Python
- BFS (Breadth-First Search): principle and implementation
- DFS (Depth-First Search): principle and implementation
- When to use BFS vs DFS

## Why It Matters

Social networks, maps, web page links, and dependency graphs are all modeled as graphs. BFS and DFS are the most fundamental algorithms for exploring these structures.

> BFS explores neighbors layer by layer; DFS follows one path as deep as possible before backtracking.

BFS is ideal for shortest-path problems on unweighted graphs. DFS is preferred for checking path existence, detecting cycles, and topological sorting.

## Concept Overview

> A graph is a collection of nodes (vertices) and edges

```text
Example graph:     BFS order:           DFS order:
  A—B               A (layer 0)         A → B → D → E → C → F
  |\ \              B, C (layer 1)
  | C  D            D, E, F (layer 2)
  |/ \
  E   F
```

## Key Concepts

| Term | Description |
|------|-------------|
| Vertex (node) | An individual element in a graph |
| Edge | A connection between two vertices |
| Adjacency list | Represents a graph as a mapping from each vertex to its neighbors |
| BFS (Breadth-First Search) | Uses a queue to visit the nearest nodes first |
| DFS (Depth-First Search) | Uses a stack (or recursion) to visit as deep as possible first |

## Before / After

Two ways to check whether two nodes are connected.

```python
# before: ad-hoc traversal — risk of infinite loop
def is_connected(graph, start, end):
    # Not systematic, may loop forever
    pass
```

```python
# after: BFS — systematic O(V+E) traversal
from collections import deque

def is_connected(graph, start, end):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == end:
            return True
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False
```

## Hands-On Steps

### Step 1: Representing Graphs

```python
# Adjacency list using a dictionary
graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "E", "F"],
    "D": ["B"],
    "E": ["C"],
    "F": ["C"],
}

# Directed graph
directed_graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["E"],
    "D": [],
    "E": [],
}

# Weighted graph
weighted_graph: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 3)],
    "C": [("A", 2), ("E", 1)],
    "D": [("B", 3)],
    "E": [("C", 1)],
}
```

### Step 2: BFS Implementation

```python
from collections import deque

def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    """BFS — O(V+E), uses a queue."""
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order

print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E', 'F']
```

### Step 3: DFS Implementation (Recursive and Iterative)

```python
def dfs_recursive(
    graph: dict[str, list[str]],
    node: str,
    visited: set[str] | None = None,
) -> list[str]:
    """DFS recursive — O(V+E)."""
    if visited is None:
        visited = set()
    visited.add(node)
    order = [node]
    for neighbor in graph[node]:
        if neighbor not in visited:
            order.extend(dfs_recursive(graph, neighbor, visited))
    return order

print(dfs_recursive(graph, "A"))  # ['A', 'B', 'D', 'C', 'E', 'F']

def dfs_iterative(graph: dict[str, list[str]], start: str) -> list[str]:
    """DFS iterative — O(V+E), uses a stack."""
    visited: set[str] = set()
    stack = [start]
    order: list[str] = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in reversed(graph[node]):
            if neighbor not in visited:
                stack.append(neighbor)

    return order

print(dfs_iterative(graph, "A"))  # ['A', 'B', 'D', 'C', 'E', 'F']
```

### Step 4: BFS Shortest Path

```python
from collections import deque

def bfs_shortest_path(
    graph: dict[str, list[str]], start: str, end: str
) -> list[str] | None:
    """BFS shortest path — unweighted graph."""
    if start == end:
        return [start]

    visited = {start}
    queue: deque[list[str]] = deque([[start]])

    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None

print(bfs_shortest_path(graph, "A", "F"))  # ['A', 'C', 'F']
print(bfs_shortest_path(graph, "D", "E"))  # ['D', 'B', 'A', 'C', 'E']
```

### Step 5: Connected Components and Cycle Detection

```python
def find_connected_components(
    graph: dict[str, list[str]],
) -> list[list[str]]:
    """Find all connected components."""
    visited: set[str] = set()
    components: list[list[str]] = []

    for node in graph:
        if node not in visited:
            component = bfs(graph, node)
            visited.update(component)
            components.append(component)

    return components

split_graph: dict[str, list[str]] = {
    "A": ["B"], "B": ["A"],
    "C": ["D"], "D": ["C"],
}
print(find_connected_components(split_graph))
# [['A', 'B'], ['C', 'D']]

def has_cycle(graph: dict[str, list[str]], start: str) -> bool:
    """Cycle detection in an undirected graph using DFS."""
    visited: set[str] = set()

    def _dfs(node: str, parent: str | None) -> bool:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if _dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True
        return False

    return _dfs(start, None)

print(has_cycle(graph, "A"))  # True
```

## What to Notice in This Code

- BFS uses a queue (deque); DFS uses a stack (or recursion)
- BFS guarantees the shortest path on unweighted graphs; DFS does not
- The visited set prevents infinite loops by tracking already-visited nodes
- Cycle detection tracks the parent node to avoid false positives in undirected graphs

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Forgetting the visited check | Infinite loop | Always check visited before processing a node |
| Using a list as a queue for BFS | list.pop(0) is O(n) | Use collections.deque |
| Exceeding recursion depth in DFS | RecursionError on large graphs | Use iterative DFS |
| Confusing directed and undirected | Traversal results differ | Be explicit about the graph type |
| Missing disconnected nodes | Some nodes are never visited | Start traversal from every unvisited node |

## Real-World Applications

- Social networks use BFS for "friend of a friend" recommendations
- Web crawlers use BFS to visit pages layer by layer
- Package managers use DFS-based topological sort for dependency resolution
- Maze solvers and game AI use graph traversal for pathfinding
- Network topology analysis uses graph traversal to map infrastructure

## How Senior Engineers Think About This

BFS and DFS are the building blocks of graph algorithms. Once you understand these two, advanced algorithms like Dijkstra, topological sort, and minimum spanning tree follow naturally.

In production, you would use libraries like NetworkX, but knowing BFS/DFS internals helps you choose the right algorithm for the job.

## What to check before choosing BFS or DFS

- If you need the minimum number of hops, start with BFS. On unweighted graphs, arrival order is already the answer.
- If you need structure-oriented answers like cycle detection, dependency ordering, or full path exploration, DFS is usually the more natural fit.
- If the graph can become very deep, prefer iterative DFS over recursive DFS. Stack-depth failures are a production bug, not just an interview concern.
- When traversal looks too slow or memory-heavy, check visited-state handling before changing algorithms. Duplicate visits are the most common real-world failure mode.

## Checklist

- [ ] Represent a graph using an adjacency list
- [ ] Explain the difference between BFS and DFS
- [ ] Find the shortest path using BFS
- [ ] Detect cycles using DFS
- [ ] Find connected components in an undirected graph

## Exercises

1. Write a BFS function that finds the shortest path in a 2D grid (maze).
2. Implement topological sort on a directed graph using DFS.
3. Determine whether a given graph is bipartite using BFS.

## Summary and Next Steps

BFS explores nodes layer by layer and guarantees shortest paths on unweighted graphs. DFS goes deep first and is well-suited for cycle detection and topological sorting. In the next article, we tackle shortest paths on weighted graphs with Dijkstra's algorithm.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Graph Traversal — BFS and DFS?**
  - The article treats Graph Traversal — BFS and DFS as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Graph Traversal — BFS and DFS?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Graph Traversal — BFS and DFS reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Algorithms with Python 101 (1/10): What Are Algorithms?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): Linear Search and Binary Search](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): Sorting Algorithms](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): Dynamic Programming Basics](./06-dynamic-programming-basics.md)
- **Graph Traversal — BFS and DFS (current)**
- Shortest Path Basics (upcoming)
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Wikipedia — Depth-First Search](https://en.wikipedia.org/wiki/Depth-first_search)
- [Real Python — Graphs in Python](https://realpython.com/python-graph/)
- [Visualgo — Graph Traversal](https://visualgo.net/en/dfsbfs)

Tags: Python, Algorithms, Graphs, BFS, DFS
