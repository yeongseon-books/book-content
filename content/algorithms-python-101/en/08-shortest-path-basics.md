---
series: algorithms-python-101
episode: 8
title: "Algorithms with Python 101 (8/10): Shortest Path Basics"
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
  - Shortest Path
  - Dijkstra
  - heapq
seo_description: Implement Dijkstra's algorithm in Python using heapq to find shortest paths in weighted graphs with path reconstruction.
last_reviewed: '2026-05-04'
---

# Algorithms with Python 101 (8/10): Shortest Path Basics

Route planning, network latency, and logistics optimization all come down to the same question: what is the cheapest path from here to there?

Once edge weights matter, breadth-first search is no longer enough. You need a better model for prioritizing the next candidate path, and that is where Dijkstra's algorithm earns its place.

This is the 8th post in the Algorithms with Python 101 series. Here, we'll frame the shortest-path problem on weighted graphs and implement Dijkstra's algorithm in Python with `heapq`.


![Algorithms with Python 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/08/08-01-concept-overview.en.png)
*Algorithms with Python 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Shortest Path Basics?
- Which signal should the example or diagram make visible for Shortest Path Basics?
- What failure should be prevented first when Shortest Path Basics reaches a real system?

## What You Will Learn

- The shortest-path problem on weighted graphs
- How Dijkstra's algorithm works
- Implementation with Python's heapq
- Path reconstruction and negative-weight limitations

## Why It Matters

Navigation, network routing, and logistics optimization are all weighted-graph shortest-path problems. Dijkstra's algorithm is the most fundamental tool for solving them efficiently.

> Dijkstra's algorithm finds the shortest path from a single source to all other nodes in a graph with non-negative edge weights.

Dijkstra combines a greedy strategy with a priority queue to run in O((V+E) log V). This principle underpins advanced algorithms like A*.

## Concept Overview

> Shortest path = the path from source to destination with the minimum total edge weight

```text
Weighted graph:
A --4-- B --3-- D
|       |
2       1
|       |
C --5-- E

A→D shortest path: A→B→D (cost 7)
A→E shortest path: A→B→E (cost 5)
```

## Key Concepts

| Term | Description |
|------|-------------|
| Weighted graph | A graph where each edge has an associated cost (weight) |
| Dijkstra's algorithm | Finds single-source shortest paths with non-negative weights |
| Priority queue | A data structure that always dequeues the smallest element first |
| Relaxation | Updating a distance estimate when a shorter path is found |
| Negative weight | Edges with negative costs that Dijkstra cannot handle |

## Before / After

Two approaches to finding the shortest path in a weighted graph.

```python
# before: BFS — ignores weights, gives wrong answer
def shortest(graph, start, end):
    from collections import deque
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path  # minimum hops, NOT minimum cost
        for neighbor, _ in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None
```

```python
# after: Dijkstra — weight-aware shortest path
import heapq

def shortest(graph, start, end):
    dist = {start: 0}
    heap = [(0, start, [start])]
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node == end:
            return cost, path
        if cost > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))
    return None
```

## Hands-On Steps

### Step 1: Representing a Weighted Graph

```python
graph: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 3), ("E", 1)],
    "C": [("A", 2), ("E", 5)],
    "D": [("B", 3)],
    "E": [("B", 1), ("C", 5)],
}

for node, neighbors in graph.items():
    edges = [f"{n}({w})" for n, w in neighbors]
    print(f"  {node} -> {', '.join(edges)}")
```

### Step 2: Dijkstra's Algorithm

```python
import heapq

def dijkstra(
    graph: dict[str, list[tuple[str, int]]], start: str
) -> dict[str, int]:
    """Dijkstra's algorithm — O((V+E) log V)."""
    dist: dict[str, int] = {start: 0}
    heap: list[tuple[int, str]] = [(0, start)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist.get(node, float("inf")):
            continue

        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))

    return dist

distances = dijkstra(graph, "A")
for node, d in sorted(distances.items()):
    print(f"  A -> {node}: {d}")
# A -> A: 0
# A -> B: 4
# A -> C: 2
# A -> D: 7
# A -> E: 5
```

### Step 3: Path Reconstruction

```python
import heapq

def dijkstra_with_path(
    graph: dict[str, list[tuple[str, int]]], start: str
) -> tuple[dict[str, int], dict[str, list[str]]]:
    """Dijkstra with path reconstruction."""
    dist: dict[str, int] = {start: 0}
    prev: dict[str, str | None] = {start: None}
    heap: list[tuple[int, str]] = [(0, start)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                prev[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))

    paths: dict[str, list[str]] = {}
    for node in dist:
        path: list[str] = []
        current: str | None = node
        while current is not None:
            path.append(current)
            current = prev.get(current)
        paths[node] = list(reversed(path))

    return dist, paths

distances, paths = dijkstra_with_path(graph, "A")
for node in sorted(paths):
    print(f"  A -> {node}: cost={distances[node]}, path={' -> '.join(paths[node])}")
```

### Step 4: Grid Shortest Path

```python
import heapq

def grid_shortest_path(grid: list[list[int]]) -> int:
    """Minimum-cost path from top-left to bottom-right in a grid."""
    rows, cols = len(grid), len(grid[0])
    dist = [[float("inf")] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    heap: list[tuple[int, int, int]] = [(grid[0][0], 0, 0)]

    while heap:
        cost, r, c = heapq.heappop(heap)
        if r == rows - 1 and c == cols - 1:
            return cost
        if cost > dist[r][c]:
            continue
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_cost = cost + grid[nr][nc]
                if new_cost < dist[nr][nc]:
                    dist[nr][nc] = new_cost
                    heapq.heappush(heap, (new_cost, nr, nc))

    return dist[rows - 1][cols - 1]

grid = [
    [1, 3, 1],
    [1, 5, 1],
    [4, 2, 1],
]
print(grid_shortest_path(grid))  # 7 (1→1→1→1→2→1)
```

### Step 5: Algorithm Comparison

```python
comparison = [
    ("Unweighted graph", "BFS — O(V+E)"),
    ("Non-negative weights", "Dijkstra — O((V+E) log V)"),
    ("Negative weights allowed", "Bellman-Ford — O(V*E)"),
    ("All-pairs shortest path", "Floyd-Warshall — O(V^3)"),
]

print("Shortest-path algorithm selection guide:")
for condition, algorithm in comparison:
    print(f"  {condition}: {algorithm}")
```

## What to Notice in This Code

- heapq is a min-heap, so the node with the smallest distance is always processed first
- The `cost > dist.get(node, float("inf"))` check skips already-finalized nodes
- Path reconstruction uses a prev dictionary and backtracks from destination to source
- Grid problems are a common interview application of Dijkstra

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Using Dijkstra with negative weights | Produces incorrect results | Use Bellman-Ford instead |
| Skipping the finalized-node check | Wastes time on redundant processing | Compare heap cost with recorded distance |
| Using a list as a priority queue | insert/remove is O(n) | Use heapq |
| Wrong initial distance | Source node distance is incorrect | Initialize source distance to 0 |
| Not handling unreachable nodes | KeyError when accessing distance | Use dist.get(node, float("inf")) |

## Real-World Applications

- Navigation apps use Dijkstra (or A*) to compute optimal driving routes
- Network routing protocols like OSPF use Dijkstra internally
- Logistics systems optimize delivery routes across warehouses
- Game engines compute NPC movement paths
- Social networks analyze shortest connection paths between users

## How Senior Engineers Think About This

You rarely implement Dijkstra yourself, but recognizing that a problem is a shortest-path problem is the critical skill. Once you make that connection, you can reach for the right library or algorithm.

In production, you use NetworkX's shortest_path() or a mapping API. But understanding the internals helps you diagnose performance issues and select the right algorithm.

## What to check when Dijkstra looks wrong or slow

- Verify the graph has no negative edges before debugging the implementation. That one assumption breaks the whole algorithm.
- Skip stale heap entries aggressively. Many “Dijkstra is too slow” reports are really about reprocessing outdated candidates.
- If reconstructed paths look wrong, inspect when `prev` changes. It should only move when you discover a genuinely shorter route.
- In systems with constantly changing topology, the operational trade-off is not just correctness. Rebuild cost, cache invalidation, and acceptable staleness matter too.

## Checklist

- [ ] Explain how Dijkstra's algorithm works
- [ ] Implement Dijkstra with heapq in Python
- [ ] Reconstruct the shortest path from source to destination
- [ ] Explain Dijkstra's limitation with negative weights
- [ ] Choose the appropriate shortest-path algorithm for a given problem

## Exercises

1. Find the shortest path and cost between two specific nodes in a weighted directed graph.
2. Find the shortest path in a grid with obstacles (impassable cells).
3. Write a function that finds the k-th shortest path using Dijkstra.

## Summary and Next Steps

Dijkstra's algorithm finds shortest paths in non-negative weighted graphs in O((V+E) log V). The key insight is processing the nearest unfinalized node first via a priority queue. In the next article, we explore greedy algorithms — the strategy of always making the locally optimal choice.

## Answering the Opening Questions

- **How is the shortest-path problem defined in a weighted graph?**
  - The shortest-path problem in a weighted graph is finding the path from start to destination whose edge-weight sum is minimal among all possible paths. The article first noted that BFS only guarantees minimum edge count, and that once costs are involved, a `("neighbor", weight)` graph and a different algorithm are needed.
- **What principle drives Dijkstra's algorithm?**
  - Dijkstra extracts the candidate with the currently known shortest distance first, then updates distance estimates via relaxation when a shorter path is found. The `new_cost < dist.get(...)` condition and the stale-heap-entry skip in `dijkstra()` ensure correct shortest distances in non-negative-weight graphs.
- **How do you implement a priority queue with Python's `heapq`?**
  - Push `(distance, node)` or `(distance, node, path)` tuples onto the heap and `heappop()` the smallest-distance candidate first. The `dijkstra_with_path()` and `grid_shortest_path()` examples handled not only distance computation but also path reconstruction via `prev` and grid-problem extensions—all using the same priority-queue pattern.
<!-- toc:begin -->
## In this series

- [Algorithms with Python 101 (1/10): What Are Algorithms?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): Linear Search and Binary Search](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): Sorting Algorithms](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): Dynamic Programming Basics](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): Graph Traversal — BFS and DFS](./07-graph-traversal-bfs-dfs.md)
- **Shortest Path Basics (current)**
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python Documentation — heapq](https://docs.python.org/3/library/heapq.html)
- [Visualgo — Single-Source Shortest Path](https://visualgo.net/en/sssp)
- [Real Python — Priority Queue in Python](https://realpython.com/python-heapq-module/)

Tags: Python, Algorithms, Shortest Path, Dijkstra, heapq
