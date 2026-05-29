---
series: math-for-cs-101
episode: 4
title: "Math for CS 101 (4/10): Graphs"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Math
  - Graphs
  - DataStructure
  - Algorithms
  - Beginner
seo_description: A beginner-friendly intro to graphs covering vertices, edges, directed and undirected, trees, adjacency matrix and list, plus a starter BFS
last_reviewed: '2026-05-04'
---

# Math for CS 101 (4/10): Graphs

Lists and tables are not enough once the important question becomes who is connected to whom, which task depends on which other task, or which route can reach a target. At that point the data is no longer just a collection of values. It is a web of relationships.

Graphs are the standard way to make those relationships explicit. Social networks, road systems, build pipelines, service dependencies, and recommendation paths all look different on the surface, but a graph often exposes the common structure underneath.

This is the 4th post in the Math for CS 101 series.

Here we treat graphs as the baseline language for relationship-heavy systems, with a focus on representation and traversal.


![math for cs 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/04/04-01-concept-at-a-glance.en.png)
*math for cs 101 chapter 4 flow overview*
> A graph structures relationships and transforms complex problems into connectivity and pathfinding challenges that become solvable.

## Questions to Keep in Mind

- Why do relationship-heavy problems become clearer when modeled as graphs?
- What do vertices and edges correspond to in real systems?
- How do directed and undirected graphs change the meaning of a model?

## Why It Matters

Friend recommendations, route planning, build dependencies, and service maps all become easier to reason about once you stop pretending they are simple lists. What matters is not just the objects but the shape of the connections between them.

That modeling choice often determines the solution strategy. Once a problem becomes a graph, shortest path, reachability, topological order, or traversal patterns come into play almost immediately.

Graphs consist of *nodes*, *edges*, and *properties* (directed, weighted, cyclic). Most real problems—networks, dependencies, recommendations, social connections—naturally become graphs.

## Before/After

**Before**: "This is a tangled mess of relationships."

**After**: "This is a graph; now I can ask structured questions about paths, cycles, and reachability.

## Key Terms

- **vertex**: a *node*.
- **edge**: a *connection* between two *vertices*.
- **tree**: a *connected*, *acyclic* graph.
- **adjacency**: the *neighbor* relation.
- **BFS**: *breadth-first search*.

## Before/After

**Before**: store the graph as a *2-D array*.

**After**: use an *adjacency list* for a *sparse* representation.

## Hands-on: A Mini Graph Kit

### Step 1 — Adjacency list

```python
G = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
```

An adjacency list is the most common representation for sparse graphs. It stores only which vertices connect to which, saving memory and fitting traversal algorithms naturally.

### Step 2 — Vertex and edge counts

```python
def stats(G):
    return len(G), sum(len(v) for v in G.values())
```

Counting vertices and edges first gives you an immediate sense of scale and density. From there you can estimate algorithmic complexity before writing any traversal logic.

### Step 3 — Neighbors

```python
def neighbors(G, v):
    return G.get(v, [])
```

Fast neighbor lookup is the foundation of every graph algorithm. Whether you are finding recommendation candidates, next tasks, or next cities, the operation is structurally the same—query adjacency.

### Step 4 — BFS

```python
from collections import deque

def bfs(G, s):
    seen, q = {s}, deque([s])
    while q:
        v = q.popleft()
        for n in G[v]:
            if n not in seen:
                seen.add(n)
                q.append(n)
    return seen
```

BFS visits nodes layer by layer, guaranteeing shortest-path discovery in unweighted graphs. The queue enforces order; the seen set prevents revisits. This two-structure pattern recurs in scheduling, dependency resolution, and network discovery.

### Step 5 — Tree check

```python
def is_tree(G):
    edges = sum(len(v) for v in G.values())
    return edges == len(G) - 1
```

A tree is a connected graph with exactly `vertices - 1` edges. This single arithmetic check distinguishes hierarchical structures from general graphs—useful when validating org charts, file systems, or DOM trees.

## What to Notice in This Code

- An *adjacency list* is just a *dict*.
- *BFS* uses *one queue*.
- A *tree* has *edges = vertices - 1*.

## Five Common Mistakes

1. **Treating a *directed* graph as *undirected*.**
2. **Using an *adjacency matrix* on *sparse* data.**
3. **Forgetting *seen* in *BFS*.**
4. **Ignoring *connectivity* in tree checks.**
5. **Not handling *self loops*.**

## How This Shows Up in Production

*Friend recommendations*, *shortest path*, *dependency build order*, *rating propagation* — all *graph algorithms*.

## How a Senior Engineer Thinks

- The *graph* is the *model*.
- *Sparser* data prefers a *list*.
- *BFS* and *DFS* are *fundamentals*.
- A *tree* is a *subset* of graphs.
- *Direction* is *explicit*.

## Choosing a Representation: Adjacency List vs Adjacency Matrix

Before solving a graph problem, choose the representation. The same algorithm can have vastly different time and memory costs depending on how the graph is stored.

| Criterion | Adjacency list | Adjacency matrix |
|---|---|---|
| Memory | `O(V + E)` | `O(V^2)` |
| Neighbor traversal | Fast | Requires full row scan |
| Edge existence query | `O(deg(v))` or auxiliary structure | `O(1)` |
| Sparse graphs | Favorable | Unfavorable |
| Dense graphs | Acceptable | Can be favorable |

Most service data is sparse, so the adjacency list is the default. When vertex count is small and edge-existence queries dominate, a matrix becomes practical.

```python
def to_adj_list(edges):
    g = {}
    for u, v in edges:
        g.setdefault(u, []).append(v)
        g.setdefault(v, [])
    return g

def to_adj_matrix(nodes, edges):
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    m = [[0] * n for _ in range(n)]
    for u, v in edges:
        m[idx[u]][idx[v]] = 1
    return m
```

The adjacency matrix gives O(1) edge-existence checks but costs O(V^2) memory. The adjacency list makes traversal natural and costs O(V+E), which is why it dominates in practice.

## BFS and DFS with a Unified Interface

Comparing traversal strategies becomes structural when you unify the interface.

```python
from collections import deque

def bfs_order(graph: dict[str, list[str]], start: str) -> list[str]:
    q = deque([start])
    seen = {start}
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for nxt in graph.get(v, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order

def dfs_order(graph: dict[str, list[str]], start: str) -> list[str]:
    stack = [start]
    seen = set()
    order = []
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        order.append(v)
        for nxt in reversed(graph.get(v, [])):
            if nxt not in seen:
                stack.append(nxt)
    return order
```

BFS expands level by level; DFS explores paths. The difference shows directly in the code: a queue vs a stack. For quickly mapping the blast radius of a failure, BFS is intuitive. For detecting dependency cycles, DFS variants are better suited.

## Validating Models with networkx

During early design, `networkx` lets you quickly verify whether a relationship model is correct.

```python
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([
    ('auth', 'user-db'),
    ('api', 'auth'),
    ('api', 'cache'),
    ('worker', 'queue'),
    ('queue', 'api'),
])

is_dag = nx.is_directed_acyclic_graph(G)
```

Checking DAG status, connected component count, or shortest-path existence before implementation reduces model errors early. For batch pipelines and build dependencies, automating the DAG check alone prevents a significant class of failures.

## Graph Application Map

| Domain | Vertex | Edge | Representative question |
|---|---|---|---|
| Social | User | Follow/friendship | Who are the recommendation candidates? |
| Infrastructure | Service | Call dependency | How far does a failure propagate? |
| CI/CD | Task | Precedence | What is the next executable task? |
| Maps | Location | Road | What is the minimum-cost route? |
| Security | Asset | Access path | Does an attack path exist? |

Using this table during modeling shifts thinking from "value-centric" to "relationship-centric."

## Graph Design Checklist

1. Is directionality explicitly specified?
2. Are multi-edge/weight requirements defined?
3. Does cycle-allowance match the requirements?
4. Is there a policy for disconnected vertices?

Anchoring these four items in the design document before reaching for algorithms increases design stability significantly.

## Classifying Path Problems Quickly

When facing a graph problem, start with these four questions to narrow algorithm selection:

1. Are edges weighted?
2. Are there negative-weight edges?
3. Do you need full paths, or just reachability?
4. Single source or multiple sources?

```python
def problem_type(weighted: bool, negative_edge: bool, reachability_only: bool) -> str:
    if reachability_only:
        return 'BFS/DFS'
    if weighted and negative_edge:
        return 'Bellman-Ford family'
    if weighted:
        return 'Dijkstra family'
    return 'BFS shortest-edge-count'
```

This classification is not a complete answer but a safety net against early misjudgment. Running through these questions in a modeling meeting before implementation reduces rework significantly.

## Dijkstra's Shortest Path

Dijkstra's algorithm finds shortest paths in weighted graphs and appears in network routing, API gateway cost optimization, and map navigation.

```python
import heapq
from typing import Dict, List, Tuple

def dijkstra(graph: Dict[str, List[Tuple[str, int]]], start: str) -> Dict[str, int]:
    """Compute shortest distances in a weighted graph."""
    dist = {start: 0}
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float('inf')):
            continue
        for v, w in graph.get(u, []):
            new_dist = d + w
            if new_dist < dist.get(v, float('inf')):
                dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

    return dist

# Example: compute inter-service latency
network = {
    "gateway": [("auth", 2), ("cache", 1)],
    "auth": [("db", 5), ("cache", 2)],
    "cache": [("db", 3)],
    "db": [],
}
print(dijkstra(network, "gateway"))
# {'gateway': 0, 'cache': 1, 'auth': 2, 'db': 4}
```

The key constraint is that edge weights must be non-negative. If negative edges exist, use Bellman-Ford. In practice, latency, cost, and distance are all naturally non-negative, making Dijkstra the default choice.

## Topological Sort for Dependency Ordering

Build systems, package installation order, and data pipeline stage sequencing are all topological sort problems.

```python
from collections import deque

def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """Kahn's algorithm for topological ordering."""
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] = in_degree.get(v, 0) + 1

    queue = deque([u for u in in_degree if in_degree[u] == 0])
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(order) != len(graph):
        raise ValueError("Cycle detected — topological sort impossible")
    return order

# Build dependency example
build_deps = {
    "app": ["lib", "config"],
    "lib": ["utils"],
    "config": [],
    "utils": [],
}
print(topological_sort(build_deps))
# ['config', 'utils', 'lib', 'app'] or equivalent valid ordering
```

When topological sort fails (cycle found), it signals that the build cannot proceed. Adding this check to CI catches circular dependencies the moment they are introduced.

## Cycle Detection with 3-Color DFS

In directed graphs, cycles cause deadlocks, infinite loops, and circular references.

```python
def has_cycle(graph: Dict[str, List[str]]) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {u: WHITE for u in graph}

    def visit(u):
        color[u] = GRAY
        for v in graph.get(u, []):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and visit(v):
                return True
        color[u] = BLACK
        return False

    return any(color[u] == WHITE and visit(u) for u in graph)

print(has_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}))  # True
print(has_cycle({"a": ["b"], "b": ["c"], "c": []}))      # False
```

3-color DFS is the standard cycle detection pattern. Encountering a GRAY node again means a back edge exists, which proves a cycle. This is essential for validating dependency graphs, import chains, and state machine transitions.

## Checklist

- [ ] Decide *directed/undirected*.
- [ ] Pick the *adjacency representation*.
- [ ] Implement *BFS*.
- [ ] Verify *tree conditions*.

## Practice Problems

1. Distinguish *vertex* and *edge* in one line.
2. Define *BFS* in one line.
3. Define *tree* in one line.

## Wrap-up and Next Steps

Graphs give you a way to describe systems where connections drive the behavior. Once that model is explicit, traversal and path questions become much easier to phrase and solve.

Next, we turn to combinatorics, where the focus shifts from connection structure to counting how quickly possibilities grow.

## Answering the Opening Questions

- **Why represent relational data as a graph?**
  - Graphs expose connection structure that flat lists hide, using vertices and edges. Social ties, service calls, and build dependencies become `G = {"A": ["B", "C"] ...}` adjacency lists, unlocking BFS, DFS, shortest path, and topological sort as ready-made solutions.
- **What do vertices and edges correspond to in real-world models?**
  - As the article's application table showed: vertices are users, services, tasks, or locations; edges are friendships, call dependencies, precedence constraints, or road connections. So `topological_sort(build_deps)` computes task ordering and `dijkstra(network, "gateway")` computes cost paths—same grammar reused across domains.
- **How do directed and undirected graphs differ?**
  - Directed edges like `api -> auth` carry order and dependency meaning, enabling topological sort and cycle detection. Symmetric connections like friendships or two-way roads read naturally as undirected. Missing this distinction changes BFS distance, DAG determination, and failure-propagation analysis entirely.
<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- **Graphs (current)**
- Combinatorics (upcoming)
- Probability (upcoming)
- Linear Algebra (upcoming)
- Calculus (upcoming)
- Information Theory (upcoming)
- Algorithms and Math (upcoming)

<!-- toc:end -->

## References

- [Graph Theory - Wolfram MathWorld](https://mathworld.wolfram.com/GraphTheory.html)
- [Graphs - Khan Academy](https://www.khanacademy.org/computing/computer-science/algorithms/graph-representation/a/representing-graphs)
- [Introduction to Algorithms - CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [NetworkX Documentation](https://networkx.org/)
- [NetworkX GitHub repository](https://github.com/networkx/networkx)

Tags: Math, Graphs, DataStructure, Algorithms, Beginner
