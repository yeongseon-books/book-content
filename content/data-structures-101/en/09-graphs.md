---
series: data-structures-101
episode: 9
title: Graphs
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
  - Graph
  - Adjacency List
  - Adjacency Matrix
  - Graph Traversal
seo_description: How to represent graphs (adjacency list vs matrix), the meaning of direction, weight, and connectivity, and how to implement BFS and DFS.
last_reviewed: '2026-05-04'
---

# Graphs

> Data Structures 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: What does friend networks, road maps, dependency trees, routing tables, and recommendation systems have in common?

> A graph is a data structure that captures arbitrary relationships between vertices using edges. A tree is just a special case of a graph (a connected, acyclic graph), and graphs are the basic vocabulary of nearly all relational modelling. This article walks through how to represent a graph, the basic properties (direction, weight, connectivity), and the two foundational traversal algorithms — BFS and DFS — by implementing them by hand.

<!-- a-grade-intro:end -->

## What You Will Learn

- Core graph terminology (vertex, edge, degree, path)
- The trade-off between adjacency lists and adjacency matrices
- The difference between directed and undirected, weighted and unweighted, connected and disconnected graphs
- How BFS and DFS differ in implementation and which problems each is suited to

## Why It Matters

Graphs are the most general and powerful data structure in computer science. Social networks, maps, the internet, dependency managers, and recommendation algorithms all run on graphs. Without comfortable graph traversal skills, more than half of typical coding interview problems become hard.

> A tree is the simplest possible relationship; the real world is best described as a graph.

## Concept at a Glance

> A graph G = (V, E) is a vertex set V and an edge set E. If edges have direction, you have a directed graph; if they carry weights, you have a weighted graph. Adjacency lists are memory efficient, while adjacency matrices answer "is there an edge between u and v?" in O(1).

```text
Undirected graph             Directed graph
    A ─── B                   A ──→ B
    │     │                   │     ↓
    C ─── D                   C ←── D

Adjacency list               Adjacency matrix
A: [B, C]                      A B C D
B: [A, D]                    A 0 1 1 0
C: [A, D]                    B 1 0 0 1
D: [B, C]                    C 1 0 0 1
                             D 0 1 1 0
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Vertex | A node in the graph |
| Edge | A connection between two vertices |
| Degree | The number of edges touching a vertex |
| Path | A sequence of vertices linked by edges |
| Cycle | A path whose start and end are the same vertex |

## Before / After

**Before — ad-hoc dict-of-dict representation:**

```python
graph = {"A": {"B": 1}, "B": {"A": 1, "C": 2}, ...}
# It works, but with no consistent interface every algorithm becomes awkward
```

**After — an explicit Graph class:**

```python
class Graph:
    def __init__(self): self._adj = {}
    def add_edge(self, u, v, w=1): ...
    def neighbors(self, u): ...
# Every algorithm can rely on the same surface
```

## Hands-On: Step by Step

### Step 1: Represent a graph with an adjacency list

```python
class Graph:
    def __init__(self, directed=False):
        self._adj = {}
        self._directed = directed

    def add_node(self, u):
        self._adj.setdefault(u, [])

    def add_edge(self, u, v, weight=1):
        self.add_node(u); self.add_node(v)
        self._adj[u].append((v, weight))
        if not self._directed:
            self._adj[v].append((u, weight))

    def neighbors(self, u):
        return self._adj.get(u, [])

    def __iter__(self):
        return iter(self._adj)


g = Graph()
for u, v in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
    g.add_edge(u, v)

for node in g:
    print(node, g.neighbors(node))
```

This stores the adjacency list as dict + list. Memory usage is O(V + E).

### Step 2: Represent a graph with an adjacency matrix

```python
class MatrixGraph:
    def __init__(self, n):
        self.n = n
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v, weight=1):
        self.matrix[u][v] = weight
        self.matrix[v][u] = weight   # undirected

    def has_edge(self, u, v):
        return self.matrix[u][v] != 0


g = MatrixGraph(5)
g.add_edge(0, 1); g.add_edge(0, 2); g.add_edge(1, 3); g.add_edge(2, 3); g.add_edge(3, 4)
print(g.has_edge(0, 1))   # True
print(g.has_edge(1, 2))   # False
```

The matrix uses O(V^2) memory but answers "is there an edge?" in O(1). It is a good fit when the vertex count is small and the graph is dense.

### Step 3: BFS (shortest path length)

```python
from collections import deque


def bfs_shortest(g, start, target):
    visited = {start: 0}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        if u == target:
            return visited[u]
        for v, _ in g.neighbors(u):
            if v not in visited:
                visited[v] = visited[u] + 1
                queue.append(v)
    return -1


print(bfs_shortest(g, "A", "E"))   # 3
```

BFS visits closer vertices first, so it naturally yields the shortest path in an unweighted graph.

### Step 4: DFS (recursive)

```python
def dfs(g, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start, end=" ")
    for v, _ in g.neighbors(start):
        if v not in visited:
            dfs(g, v, visited)


dfs(g, "A")   # e.g. A B D C E
print()
```

DFS walks one branch all the way down before backtracking. It is the workhorse of cycle detection, topological sort, and connected-component traversal.

### Step 5: Cycle detection and connected components

```python
def has_cycle(g, start, visited=None, parent=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for v, _ in g.neighbors(start):
        if v not in visited:
            if has_cycle(g, v, visited, start):
                return True
        elif v != parent:
            return True
    return False


def connected_components(g):
    visited = set()
    components = []
    for node in g:
        if node not in visited:
            comp = set()
            stack = [node]
            while stack:
                u = stack.pop()
                if u in comp:
                    continue
                comp.add(u)
                for v, _ in g.neighbors(u):
                    stack.append(v)
            components.append(comp)
            visited.update(comp)
    return components


print(has_cycle(g, "A"))           # True (A-B-D-C-A)
print(connected_components(g))     # [{'A','B','C','D','E'}]
```

Both are applications of DFS. Cycle detection shows up in friend-network validation and dependency-graph validation; connected components power clustering and network analysis.

## Notable Points

- An adjacency list suits sparse graphs, while a matrix suits dense graphs
- BFS and DFS share the same code; only the data structure changes (queue vs stack)
- In an undirected graph, cycle detection has to track the parent vertex to be correct
- A graph is the generalisation of a tree and is the basic vocabulary of relational modelling

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Forgetting to flag direction | Algorithms produce wrong answers | Make directed or undirected explicit in code |
| Missing the visited set | Infinite loops | Mark as visited when you enqueue or push |
| Ignoring weights | Applying unweighted BFS to a weighted problem | Switch to Dijkstra when weights matter |
| Reaching for an adjacency matrix when V is large | Memory blows up | Use an adjacency list for sparse graphs |
| Recursive DFS on a deep graph | RecursionError | Convert to an explicit stack |

## How This Is Used in Practice

- Social networks: friendships, influence analysis, community detection
- Maps and navigation: Dijkstra and A* over road networks
- Dependency managers (npm, pip): topological sort to decide build order
- Recommendation systems: collaborative filtering as embeddings on a graph
- Distributed systems: topology, consistency, and routing all use graph algorithms

## How a Senior Engineer Thinks

A senior engineer asks first: "Is this a graph problem?" If you can recast it in the vocabulary of vertices, edges, and relationships, you can immediately reach for off-the-shelf algorithms — BFS, DFS, Dijkstra, topological sort.

A senior also knows about graph libraries (NetworkX, igraph) and graph databases (Neo4j) and uses them when they fit. They do not implement every graph by hand. But they keep the basic algorithms in muscle memory so they understand what those libraries do internally.

## Checklist

- [ ] Can you use vertex, edge, degree, and path correctly
- [ ] Do you know the memory and time trade-offs between an adjacency list and a matrix
- [ ] Can you tell directed from undirected and weighted from unweighted graphs
- [ ] Can you explain the implementation difference between BFS and DFS
- [ ] Do you understand that a tree is a special case of a graph

## Practice Problems

1. Add a `bfs_path(start, target)` method to `Graph` that returns the actual path (a list of vertices), not just the distance. Hint: store the predecessor of each visited vertex in a dict.

2. Implement topological sort on a directed graph two ways: (a) the reverse of DFS post-order finishing time, (b) BFS starting from in-degree-zero vertices (Kahn's algorithm). Compare the two.

3. Implement Dijkstra's algorithm on a weighted graph using a priority queue (`heapq`). Why does it stop working in the presence of negative edge weights?

## Wrap-Up and Next Steps

A graph captures arbitrary relationships using vertices and edges, and it is the most general and most powerful model in computer science. Understand the trade-off between adjacency lists and matrices, and handle the basic properties — direction, weight, connectivity — precisely. BFS and DFS are the foundation of every graph algorithm, and the same skeleton becomes one or the other purely by choice of data structure.

The next article closes the series with a practical guide to choosing among the data structures we've covered, given a particular situation.

<!-- toc:begin -->
- [What Are Data Structures?](./01-what-are-data-structures.md)
- [Arrays and Dynamic Arrays](./02-arrays-and-dynamic-arrays.md)
- [Linked Lists](./03-linked-lists.md)
- [Stacks and Queues](./04-stacks-and-queues.md)
- [Hash Tables](./05-hash-tables.md)
- [Trees](./06-trees.md)
- [Binary Search Trees](./07-binary-search-trees.md)
- [Heaps](./08-heaps.md)
- **Graphs (current)**
- Choosing Data Structures (upcoming)
<!-- toc:end -->

## References

- [Open Data Structures — Graphs](https://opendatastructures.org/ods-python/12_Graphs.html)
- [NetworkX documentation](https://networkx.org/)
- [Wikipedia — Graph (abstract data type)](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- [Sedgewick & Wayne — Algorithms 4ed, Graph chapters](https://algs4.cs.princeton.edu/40graphs/)

Tags: Computer Science, Data Structures, Graph, Adjacency List, Adjacency Matrix, Graph Traversal
