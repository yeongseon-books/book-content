---
series: data-structures-python-101
episode: 8
title: "Data Structures with Python 101 (8/10): Graph Representations"
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
  - Graph
  - BFS
  - DFS
seo_description: Represent graphs as adjacency lists and adjacency matrices in Python and implement BFS and DFS traversals.
last_reviewed: '2026-05-15'
---

# Data Structures with Python 101 (8/10): Graph Representations

> Data Structures with Python 101 Series (8/10)

**Key Question**: How do you represent social networks, maps, and dependency relationships in code?

> Graphs represent relationships using nodes (vertices) and edges. In Python, you implement adjacency lists with dict and adjacency matrices with 2D lists. This article covers graph representation methods and BFS/DFS traversals.

This is post 8 in the Data Structures with Python 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Graph Representations?
- Which signal should the example or diagram make visible for Graph Representations?
- What failure should be prevented first when Graph Representations reaches a real system?

## Big Picture

![Data Structures with Python 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/08/08-01-graph-representation-at-a-glance.en.png)

*Data Structures with Python 101 chapter 8 flow overview*

This picture places Graph Representations inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Graph Representations is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- Basic graph terminology and types
- Implementing adjacency lists and adjacency matrices
- BFS (breadth-first search) and DFS (depth-first search)
- Representing directed and weighted graphs

## Why It Matters

Most real-world relationships can be modeled as graphs. Social network friendships, web page links, road networks, and package dependencies are all graphs. The ability to represent and traverse graphs is a core skill for solving complex problems.

> A graph is a generalization of a tree. A tree is a special case — a connected graph with no cycles.

Graph problems appear at medium-to-hard difficulty in coding interviews. You need to be able to implement BFS and DFS fluently.

## Concept Overview

> Graph = a set of nodes (vertices) connected by edges

```text
[Undirected Graph]        [Adjacency List]
  A --- B                  A: [B, C]
  |   / |                  B: [A, C, D]
  |  /  |                  C: [A, B]
  C --- D                  D: [B]
```

## Graph Representation at a Glance

## Key Concepts

| Term | Description |
|------|------------|
| vertex | A node in the graph |
| edge | A connection between two vertices |
| directed graph | A graph where edges have direction |
| weighted graph | A graph where edges carry a cost (weight) |
| adjacency list | A representation that stores each vertex's neighbors as a list |

## Before / After

Compare managing relationship data in loose variables versus structuring it as a graph.

```python
# before: relationships in individual variables — hard to extend
alice_friends = ["bob", "charlie"]
bob_friends = ["alice", "charlie", "diana"]
# adding a new user requires code changes
```

```python
# after: structured as a graph (adjacency list) — easy to extend
graph = {
    "alice": ["bob", "charlie"],
    "bob": ["alice", "charlie", "diana"],
    "charlie": ["alice", "bob"],
    "diana": ["bob"],
}
# new user: graph["eve"] = ["alice"]
```

## Hands-On Steps

### Step 1: Implement a graph with an adjacency list

```python
from collections import defaultdict

class Graph:
    def __init__(self, directed=False):
        self.adj = defaultdict(list)
        self.directed = directed

    def add_edge(self, u, v):
        self.adj[u].append(v)
        if not self.directed:
            self.adj[v].append(u)

    def neighbors(self, node):
        return self.adj[node]

    def __str__(self):
        lines = []
        for node in sorted(self.adj):
            lines.append(f"{node}: {self.adj[node]}")
        return "\n".join(lines)

g = Graph()
g.add_edge("A", "B")
g.add_edge("A", "C")
g.add_edge("B", "C")
g.add_edge("B", "D")
print(g)
# A: ['B', 'C']
# B: ['A', 'C', 'D']
# C: ['A', 'B']
# D: ['B']
```

### Step 2: Implement a graph with an adjacency matrix

```python
class GraphMatrix:
    def __init__(self, vertices: list):
        self.vertices = vertices
        self.index = {v: i for i, v in enumerate(vertices)}
        n = len(vertices)
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v, weight=1):
        i, j = self.index[u], self.index[v]
        self.matrix[i][j] = weight
        self.matrix[j][i] = weight  # undirected

    def has_edge(self, u, v):
        i, j = self.index[u], self.index[v]
        return self.matrix[i][j] != 0

    def print_matrix(self):
        print("  ", " ".join(self.vertices))
        for i, v in enumerate(self.vertices):
            print(f"{v}:", self.matrix[i])

gm = GraphMatrix(["A", "B", "C", "D"])
gm.add_edge("A", "B")
gm.add_edge("A", "C")
gm.add_edge("B", "D")
gm.print_matrix()
```

### Step 3: Implement BFS

```python
from collections import deque

def bfs(graph, start):
    visited = []
    queue = deque([start])
    seen = {start}
    while queue:
        node = queue.popleft()
        visited.append(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return visited

g = Graph()
for u, v in [("A","B"), ("A","C"), ("B","D"), ("C","D"), ("D","E")]:
    g.add_edge(u, v)

print(f"BFS from A: {bfs(g, 'A')}")
# BFS from A: ['A', 'B', 'C', 'D', 'E']
```

### Step 4: Implement DFS (recursive and iterative)

```python
def dfs_recursive(graph, node, visited=None):
    if visited is None:
        visited = []
    visited.append(node)
    for neighbor in graph.neighbors(node):
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited

def dfs_iterative(graph, start):
    visited = []
    stack = [start]
    seen = set()
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        visited.append(node)
        for neighbor in reversed(graph.neighbors(node)):
            if neighbor not in seen:
                stack.append(neighbor)
    return visited

print(f"DFS recursive: {dfs_recursive(g, 'A')}")
print(f"DFS iterative: {dfs_iterative(g, 'A')}")
```

### Step 5: Weighted graph and shortest path

```python
import heapq
from collections import defaultdict

class WeightedGraph:
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u, v, weight):
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))

def dijkstra(graph, start):
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph.adj[node]:
            new_dist = d + weight
            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return dist

wg = WeightedGraph()
wg.add_edge("A", "B", 4)
wg.add_edge("A", "C", 2)
wg.add_edge("B", "D", 3)
wg.add_edge("C", "D", 1)
wg.add_edge("D", "E", 5)

distances = dijkstra(wg, "A")
print(distances)  # {'A': 0, 'C': 2, 'B': 4, 'D': 3, 'E': 8}
```

## What to Notice in This Code

- Adjacency lists suit sparse graphs; adjacency matrices suit dense graphs
- BFS uses a queue (deque); DFS uses a stack (list or recursion)
- BFS guarantees shortest paths in unweighted graphs
- Dijkstra finds shortest paths in weighted graphs using a heap

In production, representation choice is often a memory decision before it becomes an algorithm decision. An adjacency matrix gives constant-time edge checks, but it burns O(V^2) space even when the graph has very few edges. Adjacency lists scale far better for sparse graphs, but frequent edge-existence checks can still add noticeable traversal cost.

Failure modes matter too. BFS can explode memory on wide graphs because the frontier grows level by level. Recursive DFS can blow the call stack on deep graphs. And Dijkstra quietly becomes the wrong tool the moment negative edges enter the model. A good graph design starts by naming those constraints, not just by picking BFS or DFS from habit.

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Traversing without visit checks | Causes infinite loops in cyclic graphs | Use a seen/visited set to track visits |
| Adding edges in only one direction for undirected graphs | Some paths are missed during traversal | Add both directions in add_edge |
| Using adjacency matrices for sparse graphs | Wastes O(V^2) memory | Use adjacency lists instead |
| Using a queue instead of a stack for DFS | Produces BFS instead of DFS | DFS uses pop (stack); BFS uses popleft (queue) |
| Using Dijkstra with negative weights | Does not guarantee correct results | Use Bellman-Ford for negative weights |

## Real-World Applications

- Social networks implement friend recommendations with BFS (2-hop search)
- Package managers topologically sort dependency graphs
- Navigation apps compute shortest paths with Dijkstra
- Web crawlers visit pages using BFS
- CI/CD pipelines manage task dependencies as DAGs (directed acyclic graphs)

## How Senior Engineers Think About This

In practice, you rarely implement graphs from scratch. You use libraries like NetworkX or graph databases like Neo4j. But understanding BFS, DFS, and shortest-path internals helps you use those tools more effectively.

The ability to model problems as graphs is the key skill. Recognizing "is this a graph problem?" is often harder than solving it.

## Checklist

- [ ] Can explain the difference between adjacency lists and adjacency matrices
- [ ] Can implement BFS and DFS
- [ ] Can distinguish directed and undirected graphs
- [ ] Can apply Dijkstra to a weighted graph
- [ ] Can choose the right graph representation for the situation

## Exercises

1. Write a function that finds the shortest path (by edge count) between two nodes using BFS.
2. Write a function that finds all connected components in a graph using DFS.
3. Write a function that detects whether a directed graph contains a cycle.

## Summary and Next Steps

Graphs are general-purpose data structures for representing relationships. You represent them with adjacency lists or adjacency matrices and traverse them with BFS and DFS. The next article covers sets — data structures that perform set operations efficiently.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Graph Representations?**
  - The article treats Graph Representations as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Graph Representations?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Graph Representations reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures with Python 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): Arrays and Lists](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): Stacks and Queues](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): Hash Tables and dict](./04-hash-tables-and-dict.md)
- [Data Structures with Python 101 (5/10): Linked Lists](./05-linked-lists.md)
- [Data Structures with Python 101 (6/10): Trees and Binary Trees](./06-trees-and-binary-trees.md)
- [Data Structures with Python 101 (7/10): Heaps and Priority Queues](./07-heaps-and-priority-queues.md)
- **Graph Representations (current)**
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)

<!-- toc:end -->

## References

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Python Docs — heapq](https://docs.python.org/3/library/heapq.html)
- [Runestone Academy — Graphs](https://runestone.academy/ns/books/published/pythonds3/Graphs/toctree.html)
- [Real Python — Graphs in Python](https://realpython.com/python-graph-algorithm/)

Tags: Python, Data Structures, Graph, BFS, DFS
