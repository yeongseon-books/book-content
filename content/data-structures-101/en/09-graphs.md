---
series: data-structures-101
episode: 9
title: "Data Structures 101 (9/10): Graphs"
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
  - Data Structures
  - Graph
  - Adjacency List
  - Adjacency Matrix
  - Graph Traversal
seo_description: How to represent graphs (adjacency list vs matrix), the meaning of direction, weight, and connectivity, and how to implement BFS and DFS.
last_reviewed: '2026-05-04'
---

# Data Structures 101 (9/10): Graphs

This is the ninth post in the Data Structures 101 series.

**Core question**: What does friend networks, road maps, dependency trees, routing tables, and recommendation systems have in common?

> A graph is a data structure that captures arbitrary relationships between vertices using edges. A tree is just a special case of a graph (a connected, acyclic graph), and graphs are the basic vocabulary of nearly all relational modelling. This article walks through how to represent a graph, the basic properties (direction, weight, connectivity), and the two foundational traversal algorithms — BFS and DFS — by implementing them by hand.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Graphs?
- Which signal should the example or diagram make visible for Graphs?
- What failure should be prevented first when Graphs reaches a real system?

## Big Picture

![data structures 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/09/09-01-graph-representations.en.png)

*data structures 101 chapter 9 flow overview*

This picture places Graphs inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Graphs is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

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

### Graph representations

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

```text
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

service_graph = Graph(directed=True)
for u, v in [
    ("api-gateway", "auth-service"),
    ("api-gateway", "catalog-service"),
    ("auth-service", "user-db"),
    ("catalog-service", "inventory-service"),
    ("inventory-service", "warehouse-db"),
    ("inventory-service", "cache"),
    ("cache", "warehouse-db"),
]:
    service_graph.add_edge(u, v)

for node in service_graph:
    print(node, service_graph.neighbors(node))
```

This stores the adjacency list as dict + list. Memory usage is O(V + E), which is why it is the right default for sparse real-world graphs such as service dependencies.

### Step 2: Represent a graph with an adjacency matrix

```python
class MatrixGraph:
    def __init__(self, n, directed=False):
        self.n = n
        self.directed = directed
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v, weight=1):
        self.matrix[u][v] = weight
        if not self.directed:
            self.matrix[v][u] = weight

    def has_edge(self, u, v):
        return self.matrix[u][v] != 0

matrix_graph = MatrixGraph(4, directed=True)
matrix_graph.add_edge(0, 1); matrix_graph.add_edge(0, 2); matrix_graph.add_edge(1, 3); matrix_graph.add_edge(2, 3)
print(matrix_graph.has_edge(0, 1))   # True
print(matrix_graph.has_edge(1, 0))   # False
```

The matrix uses O(V^2) memory but answers "is there an edge?" in O(1). It is a good fit when the vertex count is small and the graph is dense.

### Step 3: BFS (shortest path)

```python
from collections import deque

def bfs_path(g, start, target):
    visited = {start}
    prev = {start: None}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        if u == target:
            path = []
            while u is not None:
                path.append(u)
                u = prev[u]
            return list(reversed(path))
        for v, _ in g.neighbors(u):
            if v not in visited:
                visited.add(v)
                prev[v] = u
                queue.append(v)
    return []

path = bfs_path(service_graph, "api-gateway", "warehouse-db")
print(path)
print(f"hop count: {len(path) - 1}")

expected = [
    "api-gateway",
    "catalog-service",
    "inventory-service",
    "warehouse-db",
]
print(f"path matches expectation: {path == expected}")

# ['api-gateway', 'catalog-service', 'inventory-service', 'warehouse-db']
# hop count: 3
# path matches expectation: True
```

BFS visits closer vertices first, so it naturally yields the shortest path in an unweighted graph. If this path or hop count differs, you probably lost the queue discipline, marked `visited` too late, or mixed edge direction by mistake.

### Step 4: DFS (recursive)

```python
def dfs(g, start, visited=None, order=None):
    if visited is None:
        visited = set()
    if order is None:
        order = []
    visited.add(start)
    order.append(start)
    for v, _ in g.neighbors(start):
        if v not in visited:
            dfs(g, v, visited, order)
    return order

print(dfs(service_graph, "api-gateway"))
# ['api-gateway', 'auth-service', 'user-db', 'catalog-service', 'inventory-service', 'warehouse-db', 'cache']
```

DFS walks one branch all the way down before backtracking. It is the workhorse of cycle detection, topological sort, and connected-component traversal.

### Step 5: Cycle detection in a dependency graph

```python
def has_cycle_directed(g):
    visited = set()
    active = set()

    def walk(node):
        visited.add(node)
        active.add(node)
        for neighbor, _ in g.neighbors(node):
            if neighbor not in visited and walk(neighbor):
                return True
            if neighbor in active:
                return True
        active.remove(node)
        return False

    return any(node not in visited and walk(node) for node in g)

dependency_graph = Graph(directed=True)
for u, v in [
    ("web", "auth"),
    ("auth", "payments"),
    ("payments", "ledger"),
    ("ledger", "web"),
]:
    dependency_graph.add_edge(u, v)

cycle_found = has_cycle_directed(dependency_graph)
print(cycle_found)
print(f"topological traversal possible: {not cycle_found}")

# True
# topological traversal possible: False
```

This is the DFS-style verification loop you need in practice: a back edge means the dependency graph cannot be topologically ordered. If `cycle_found` is `False` here, you probably treated a directed graph as undirected or forgot to track the active recursion stack.

## Notable Points

- An adjacency list suits sparse graphs, while a matrix suits dense graphs
- BFS and DFS share the same traversal skeleton; queue vs recursion/stack changes the behaviour
- In a directed graph, cycle detection has to track the active recursion stack to be correct
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

## Answering the Opening Questions

- **What boundary should you inspect first when applying Graphs?**
  - The article treats Graphs as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Graphs?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Graphs reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): Arrays and Dynamic Arrays](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): Linked Lists](./03-linked-lists.md)
- [Data Structures 101 (4/10): Stacks and Queues](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): Hash Tables](./05-hash-tables.md)
- [Data Structures 101 (6/10): Trees](./06-trees.md)
- [Data Structures 101 (7/10): Binary Search Trees](./07-binary-search-trees.md)
- [Data Structures 101 (8/10): Heaps](./08-heaps.md)
- **Graphs (current)**
- Choosing Data Structures (upcoming)

<!-- toc:end -->

## References

- [Open Data Structures — Graphs](https://opendatastructures.org/ods-python/12_Graphs.html)
- [NetworkX documentation](https://networkx.org/)
- [Wikipedia — Graph (abstract data type)](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- [Sedgewick & Wayne — Algorithms 4ed, Graph chapters](https://algs4.cs.princeton.edu/40graphs/)

Tags: Computer Science, Data Structures, Graph, Adjacency List, Adjacency Matrix, Graph Traversal
