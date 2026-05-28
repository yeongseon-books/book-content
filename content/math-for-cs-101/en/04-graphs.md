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

### Step 2 — Vertex and edge counts

```python
def stats(G):
    return len(G), sum(len(v) for v in G.values())
```

### Step 3 — Neighbors

```python
def neighbors(G, v):
    return G.get(v, [])
```

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

### Step 5 — Tree check

```python
def is_tree(G):
    edges = sum(len(v) for v in G.values())
    return edges == len(G) - 1
```

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
