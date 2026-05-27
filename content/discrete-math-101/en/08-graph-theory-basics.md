---
series: discrete-math-101
episode: 8
title: "Discrete Math 101 (8/10): Graph Theory Basics"
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
  - Graph Theory
  - Vertices and Edges
  - Adjacency List
  - Networks
seo_description: Definitions, representations, degree, paths, and connectivity — the foundations of graph theory and where they show up in real systems.
last_reviewed: '2026-05-04'
---

# Discrete Math 101 (8/10): Graph Theory Basics

This is the 8th post in the Discrete Math 101 series.

> Discrete Math 101 series (8/10)

**Core question**: Social networks, road maps, the internet, dependency trees — can a single mathematical structure model all of them?

> A graph is a set of vertices and edges, the most general structure for representing relationships. From this simple definition flows an enormous range of applications — routing, recommendations, dependency resolution, circuit design, game AI. This article covers the definitions, representations, degree, paths, connectivity, and the special graphs (complete, bipartite, DAG).


![discrete math 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/08/08-01-graph-representations.en.png)
*discrete math 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Graph Theory Basics?
- Which signal should the example or diagram make visible for Graph Theory Basics?
- What failure should be prevented first when Graph Theory Basics reaches a real system?

## What You Will Learn

- Definition and types of graphs (undirected, directed, weighted)
- Adjacency list vs adjacency matrix
- Degree, paths, cycles, and connectivity
- Complete graphs, bipartite graphs, and DAGs

## Why It Matters

Shortest path in navigation, friend recommendations on Instagram, npm dependency resolution, dataflow analysis in compilers — all solved by graph algorithms. Without graph theory you cannot understand the inside of these tools.

> A graph is a universal language for modeling anything with relationships.

> Graph G = (V, E). V is the vertex set, E is the edge set. Variants emerge from direction, weight, and multiplicity.

### One graph, three representations

## Key Terms

| Term | Description |
| --- | --- |
| Vertex (node) | Basic unit of a graph |
| Edge | Connects two vertices |
| Degree | Number of edges incident to a vertex |
| Path | Sequence of edges joining vertices |
| Cycle | Path whose start and end coincide |

## Before / After

**Before — thinking only in flat data structures:**

```python
# Manage friendships as a list — slow lookup
friends = [("alice", "bob"), ("bob", "carol"), ("alice", "carol")]

def is_friend(a, b):
    return (a, b) in friends or (b, a) in friends
```

**After — modeled as a graph:**

```python
# Adjacency list — average O(1) lookup, plus a rich algorithm toolkit
from collections import defaultdict

graph = defaultdict(set)

def add_edge(g, a, b):
    g[a].add(b); g[b].add(a)

def is_adjacent(g, a, b):
    return b in g[a]
```

## Hands-On: Step by Step

### Step 1: Defining and representing a graph

```python
from collections import defaultdict

class Graph:
    def __init__(self, directed: bool = False):
        self.adj = defaultdict(set)
        self.directed = directed

    def add_node(self, v):
        _ = self.adj[v]

    def add_edge(self, u, v):
        self.adj[u].add(v)
        if not self.directed:
            self.adj[v].add(u)

    def neighbors(self, v):
        return sorted(self.adj[v])

    def nodes(self):
        return sorted(self.adj.keys())

    def edges(self):
        seen = set()
        for u in self.adj:
            for v in self.adj[u]:
                e = (u, v) if self.directed else tuple(sorted((u, v)))
                seen.add(e)
        return sorted(seen)

g = Graph()
for u, v in [("A", "B"), ("B", "C"), ("A", "C"), ("C", "D")]:
    g.add_edge(u, v)

print(f"vertices: {g.nodes()}")
print(f"edges:    {g.edges()}")
```

**Expected output**

```text
vertices: ['A', 'B', 'C', 'D']
edges:    [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D')]
```

- The vertex set should contain exactly `A, B, C, D`.
- The edge set should contain four undirected edges, not both `(A, B)` and `(B, A)` separately.
- If your code still prints raw `set(...)` objects, sort before comparing because set order is not stable.

### Step 2: Adjacency list vs adjacency matrix

```python
def to_adjacency_matrix(g: Graph) -> tuple:
    nodes = sorted(g.nodes())
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    M = [[0] * n for _ in range(n)]
    for u, v in g.edges():
        M[idx[u]][idx[v]] = 1
        if not g.directed:
            M[idx[v]][idx[u]] = 1
    return nodes, M

nodes, M = to_adjacency_matrix(g)
print(f"node order: {nodes}")
print(f"adjacency matrix:\n{M}")
```

| Representation | Space | Edge check | Neighbor scan |
| --- | --- | --- | --- |
| Adjacency list | O(V + E) | O(deg) | O(deg) |
| Adjacency matrix | O(V²) | O(1) | O(V) |

Sparse graphs (few edges) favor lists; dense graphs (many edges) favor matrices.

**Expected output**

```text
node order: ['A', 'B', 'C', 'D']
adjacency matrix:
[[0, 1, 1, 0],
 [1, 0, 1, 0],
 [1, 1, 0, 1],
 [0, 0, 1, 0]]
```

- The rows and columns must share the same order, here `['A', 'B', 'C', 'D']`.
- `M[0][2] = 1` means `A` is adjacent to `C`.
- If you choose a different vertex order, the matrix layout changes too, so compare the order and the matrix together.

### Step 3: Degree and the handshake lemma

```python
def degree(g: Graph, v) -> int:
    return len(g.adj[v])

total_degree = sum(degree(g, v) for v in g.nodes())
edge_count = len(g.edges())

# Handshake lemma: Σ deg(v) = 2|E|
print(f"sum of degrees = {total_degree}, 2|E| = {2 * edge_count}")
assert total_degree == 2 * edge_count
```

The handshake lemma is the intuition that every edge contributes to two vertices. A useful corollary: the number of odd-degree vertices is always even.

**Expected output**

```text
sum of degrees = 8, 2|E| = 8
```

- Here the degrees are `A=2`, `B=2`, `C=3`, `D=1`, so the total is 8.
- With 4 edges, `2|E|` must also be 8.
- If the two sides differ, suspect duplicated edges or a missing reverse edge in the undirected graph.

### Step 4: Paths and connectivity

```python
from collections import deque

def has_path(g: Graph, start, target) -> bool:
    """Use BFS to test reachability — O(V + E)."""
    visited = {start}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        if v == target:
            return True
        for u in g.adj[v]:
            if u not in visited:
                visited.add(u); queue.append(u)
    return False

def connected_components(g: Graph) -> list:
    """Connected components (undirected only)."""
    visited = set()
    components = []
    for start in g.nodes():
        if start in visited:
            continue
        comp = set()
        queue = deque([start])
        while queue:
            v = queue.popleft()
            if v in comp:
                continue
            comp.add(v); visited.add(v)
            queue.extend(sorted(g.adj[v] - comp))
        components.append(sorted(comp))
    return components

g_disconnected = Graph()
for u, v in [("A", "B"), ("B", "C"), ("C", "D"), ("X", "Y")]:
    g_disconnected.add_edge(u, v)

print(f"path A→D exists: {has_path(g, 'A', 'D')}")
print(f"connected components: {connected_components(g_disconnected)}")
```

**Expected output**

```text
path A→D exists: True
connected components: [['A', 'B', 'C', 'D'], ['X', 'Y']]
```

- `A` can reach `D` through a path like `A → C → D`, so reachability must be `True`.
- `g_disconnected` should split into exactly two components: `{A, B, C, D}` and `{X, Y}`.
- If the component ordering differs, that usually means you skipped sorting during comparison.

### Step 5: Special graphs

```python
from itertools import combinations

def is_complete(g: Graph) -> bool:
    """Complete graph K_n: every pair connected."""
    n = len(g.nodes())
    return len(g.edges()) == n * (n - 1) // 2

def is_bipartite(g: Graph) -> bool:
    """Bipartite: vertices split into two groups with no intra-group edges."""
    color = {}
    for start in g.nodes():
        if start in color:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            v = queue.popleft()
            for u in g.adj[v]:
                if u not in color:
                    color[u] = 1 - color[v]
                    queue.append(u)
                elif color[u] == color[v]:
                    return False
    return True

k4 = Graph()
for u, v in combinations(["a", "b", "c", "d"], 2):
    k4.add_edge(u, v)
print(f"K4 is complete: {is_complete(k4)}")

bipart = Graph()
for u, v in [("u1", "v1"), ("u1", "v2"), ("u2", "v1")]:
    bipart.add_edge(u, v)
print(f"bipartite: {is_bipartite(bipart)}")
```

A DAG (directed acyclic graph) is a directed graph with no cycles, and topological sort applies. Bipartite graphs model matching problems such as assignment.

**Expected output**

```text
K4 is complete: True
bipartite: True
```

- `K4` is complete because every pair of its four vertices is connected.
- `bipart` is bipartite because its vertices can be split into `{u1, u2}` and `{v1, v2}`.
- If `bipartite` becomes `False`, check the coloring logic first — especially whether opposite colors are assigned when a neighbor is first discovered.

## Notable Points

- From the simple definition of vertices and edges flows enormous expressive power.
- Adjacency lists and matrices trade off space for query speed.
- The handshake lemma is the basic identity of every undirected graph.
- Complete, bipartite, and DAG are the standard categories that drive algorithm choice.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Confusing directed and undirected | Adding the edge only once | Add both directions for undirected |
| Forgetting self-loops | (v, v) contributes +2 to degree | Take care when applying the handshake lemma |
| Ignoring multi-edges | set vs list semantics differ | Use a set if you assume a simple graph |
| Using adjacency matrix unconditionally | Wastes memory on sparse graphs | If E ≪ V², prefer the list |
| Skipping cycle checks | Topological sort spins forever on cyclic input | Verify acyclicity first |

## How This Is Used in Practice

- Social networks: friend recommendations (graph embeddings, common neighbors)
- Navigation: shortest paths (Dijkstra, A*)
- Package managers: dependency resolution (topological sort)
- Database query optimization: join graphs
- Recommender systems: graph neural networks (GNN)

## How a Senior Engineer Thinks

When a senior engineer meets a new domain, the first question is "Can I model this as a graph?" If the answer is yes, a battle-tested algorithm library is one step away. They also pick the representation carefully — adjacency list vs matrix often determines memory and performance.

## Checklist

- [ ] Can you state the definitions of vertex, edge, and degree?
- [ ] Do you know the trade-off between adjacency list and matrix?
- [ ] Can you apply the handshake lemma?
- [ ] Can you find connected components with BFS?
- [ ] Do you understand the differences between complete, bipartite, and DAG?

## Practice Problems

1. Find the maximum number of edges in an undirected graph on 6 vertices. What kind of graph achieves this?

2. Represent your own social network as an adjacency list, and compute the size of the connected component containing yourself.

3. Use the handshake lemma to prove that the number of odd-degree vertices is always even.

## Wrap-Up and Next Steps

Graphs use vertices and edges to model relationships, the most general structure available. Representations, degree, paths, connectivity, and the special graph families form the launchpad for every graph algorithm.

The next article looks at the most important algorithms on graphs — trees, BFS, and DFS.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Graph Theory Basics?**
  - The article treats Graph Theory Basics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Graph Theory Basics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Graph Theory Basics reaches a real system?**
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
- **Graph Theory Basics (current)**
- Trees and Graph Traversal (upcoming)
- Discrete Mathematics and Algorithms (upcoming)

<!-- toc:end -->

## References

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 10](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Algorithms — Sedgewick & Wayne, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)
- [MIT Mathematics for Computer Science — Graphs and Trees](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [NetworkX Documentation — Graph types and representations](https://networkx.org/documentation/stable/reference/classes/index.html)

Tags: Computer Science, Discrete Math, Graph Theory, Vertices and Edges, Adjacency List, Networks
