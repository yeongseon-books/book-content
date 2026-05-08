
# Graph Algorithms

> Algorithms 101 series (8/10)

<!-- a-grade-intro:begin -->

**Core question**: Road networks, social networks, and dependency graphs all live in different domains — why can the same algorithms solve them?

> A graph encodes relationships as nodes and edges, and almost every system can be reasoned about on top of one. The core algorithms are BFS (unweighted shortest paths and layered traversal), DFS (connectivity and topological sort), Dijkstra (weighted shortest paths), and MST (minimum-cost connecting trees). Their cost depends on the representation, so adjacency list vs adjacency matrix is part of the decision. Once you have these tools, recommendations, search, routing, and build systems all start sounding like dialects of the same language.

<!-- a-grade-intro:end -->

## What You Will Learn

- Trade-offs between adjacency list and adjacency matrix
- When to reach for BFS vs DFS
- How Dijkstra's shortest-path algorithm works and how to implement it
- Minimum spanning trees with Kruskal and Prim

## Why It Matters

Most production problems reduce to graph problems eventually: microservice call dependencies, build-tool task graphs, user-item bipartite graphs in recommendation systems, road networks in routing. Without graph algorithms, the cores of all those systems are out of reach.

> Graphs are the shared language of systems thinking.

## Concept at a Glance

> A graph has V nodes and E edges. The adjacency list uses O(V+E) memory; the adjacency matrix uses O(V^2). BFS uses a queue and gives unweighted shortest paths in O(V+E). DFS uses a stack (or recursion) and powers connectivity and topological sort. Dijkstra is greedy + priority queue for non-negative weighted shortest paths, and the canonical MST algorithms are Kruskal (union-find) and Prim (priority queue).

```text
Graph representations
    Adjacency list   memory O(V+E), good for sparse graphs
    Adjacency matrix memory O(V^2),  O(1) edge lookup, good for dense graphs

Core traversals
    BFS  queue   unweighted shortest paths, layered exploration
    DFS  stack   connectivity, cycles, topological sort

Weighted graphs
    Dijkstra   non-negative shortest paths   O((V+E) log V)
    MST        cheapest tree connecting all  Kruskal/Prim
```

## Key Terms

| Term | Description |
| --- | --- |
| Node/edge | Object and relationship |
| Adjacency list | Per-node list of neighbours |
| BFS/DFS | Breadth-first / depth-first search |
| Dijkstra | Shortest paths with non-negative weights |
| MST | Minimum-cost subgraph connecting all nodes |

## Before / After

**Before — adjacency matrix on a sparse graph wastes memory:**

```python
# V=10000, E=30000 sparse graph as a matrix
adj = [[0] * 10000 for _ in range(10000)]   # 100 million cells, mostly zero
```

**After — adjacency list:**

```python
from collections import defaultdict
adj = defaultdict(list)
adj[0].append(1)
adj[1].append(2)
# memory O(V+E)
```

## Hands-On: Step by Step

### Step 1: Adjacency list and BFS

```python
from collections import deque, defaultdict

def bfs(adj, start):
    visited = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in visited:
                visited[v] = visited[u] + 1
                q.append(v)
    return visited

adj = defaultdict(list)
edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
for a, b in edges:
    adj[a].append(b); adj[b].append(a)

print(bfs(adj, 0))   # {0: 0, 1: 1, 2: 1, 3: 2, 4: 3}
```

BFS naturally returns unweighted shortest distances. The queue is a `deque` for O(1) on both ends.

### Step 2: DFS and topological sort

```python
def topological_sort(n, edges):
    adj = defaultdict(list)
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None   # None means a cycle exists

# A -> B, A -> C, B -> D, C -> D
print(topological_sort(4, [(0, 1), (0, 2), (1, 3), (2, 3)]))   # [0, 1, 2, 3]
```

Build-system execution order and course-prerequisite scheduling are topological-sort problems.

### Step 3: Dijkstra with a priority queue

```python
import heapq

def dijkstra(n, edges, start):
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w)); adj[v].append((u, w))
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)]
print(dijkstra(4, edges, 0))   # [0, 3, 1, 4]
```

For non-negative weights, Dijkstra is the standard. With negative weights you need Bellman-Ford or Johnson.

### Step 4: Kruskal's MST with Union-Find

```python
class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True

def kruskal(n, edges):
    edges = sorted(edges, key=lambda e: e[2])
    dsu = DSU(n)
    total = 0
    for u, v, w in edges:
        if dsu.union(u, v):
            total += w
    return total

print(kruskal(4, [(0, 1, 1), (1, 2, 2), (0, 2, 4), (2, 3, 3)]))   # 6
```

Add the lightest edge that does not create a cycle. The classic greedy + Union-Find combination.

### Step 5: Real-world — connecting cities at minimum cost

```python
roads = [
    (0, 1, 10), (0, 2, 6), (0, 3, 5),
    (1, 3, 15), (2, 3, 4),
]
print("MST cost:", kruskal(4, roads))   # 19 (e.g. 5 + 6 + 4 + ... )
```

MST applies directly to network design, cluster distance analysis, and circuit wiring.

## Notable Points

- Choice of representation drives memory and time
- BFS uses a queue, DFS uses a stack — different tools, different answers
- Dijkstra's heart is the priority queue plus the "already finalised" check
- Union-Find is the universal tool for connectivity questions

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Adjacency matrix on a sparse graph | OOM | Use an adjacency list |
| Dijkstra on negative weights | Wrong answer | Switch to Bellman-Ford |
| BFS distance assuming weights | Wrong answer | Use Dijkstra when there are weights |
| Missing path compression in Union-Find | O(n) per find | Add path compression and union-by-rank |
| Topological sort on a cyclic graph | Forgetting the None case | Detect cycles via result length |

## How This Is Used in Practice

- Build-system task dependencies (topological sort)
- Microservice call-graph analysis
- Map-app shortest paths (Dijkstra plus heuristics yields A*)
- Recommendation user-item graph embeddings
- Circuit wiring and network design (MST)

## How a Senior Engineer Thinks

A senior engineer first asks "is this a graph?" Choosing what counts as a node and what counts as an edge is 90% of the solution; once the framing is right, standard algorithms apply immediately.

A senior engineer also estimates the graph's size up front. The values of V and E, sparsity, and weight distribution drive the choice of representation and algorithm. The same problem at V=10^3 and V=10^7 calls for completely different tools.

## Checklist

- [ ] Do you know the trade-off between adjacency list and matrix?
- [ ] Can you tell when to use BFS vs DFS?
- [ ] Can you describe Dijkstra in one sentence?
- [ ] Can you implement at least one MST algorithm?
- [ ] Do you have a feel for reducing new problems to graphs?

## Practice Problems

1. Write a BFS variant that counts the number of distinct shortest paths between two nodes in an undirected graph.

2. For a directed graph that may contain cycles, decide whether a topological order exists, and print one if it does.

3. Run Dijkstra on a non-negative weighted graph, build the shortest-path tree from the source, and print the parent pointer for each node.

## Wrap-Up and Next Steps

Graph algorithms let us express almost any system problem in the simple vocabulary of nodes and edges. Representation, traversal, shortest paths, and MST cover a large fraction of practical work. Beyond that lie advanced topics like flow networks, strongly connected components, and matching.

The next article covers string algorithm basics: the cost of naive matching, KMP's failure function, the Z function, and the production-grade tools you reach for most often — regular expressions and tries.

- [What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Time and Space Complexity](./02-time-and-space-complexity.md)
- [Search Algorithms](./03-search-algorithms.md)
- [Sorting Algorithms](./04-sorting-algorithms.md)
- [Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Dynamic Programming](./06-dynamic-programming.md)
- [Greedy Algorithms](./07-greedy-algorithms.md)
- **Graph Algorithms (current)**
- String Algorithm Basics (upcoming)
- Algorithm Problem-Solving Strategies (upcoming)
## References

- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)
- [CLRS — Introduction to Algorithms, Chapters 22-24](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, Algorithms, Graphs, BFS, Dijkstra, Minimum Spanning Tree

---

© 2026 YeongseonBooks. All rights reserved.
