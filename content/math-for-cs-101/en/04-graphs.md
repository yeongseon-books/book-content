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

This is post 4 in the Math for CS 101 series.

Here we treat graphs as the baseline language for relationship-heavy systems, with a focus on representation and traversal.

## Questions to Keep in Mind

- Why do relationship-heavy problems become clearer when modeled as graphs?
- What do vertices and edges correspond to in real systems?
- How do directed and undirected graphs change the meaning of a model?

## Big Picture

![math for cs 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/04/04-01-concept-at-a-glance.en.png)

*math for cs 101 chapter 4 flow overview*

This picture places Graphs inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> A graph structures relationships and transforms complex problems into connectivity and pathfinding challenges that become solvable.

## Why It Matters

Friend recommendations, route planning, build dependencies, and service maps all become easier to reason about once you stop pretending they are simple lists. What matters is not just the objects but the shape of the connections between them.

That modeling choice often determines the solution strategy. Once a problem becomes a graph, shortest path, reachability, topological order, or traversal patterns come into play almost immediately.


## Concept at a Glance

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

- **Why do relationship-heavy problems become clearer when modeled as graphs?**
  - The article treats Graphs as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What do vertices and edges correspond to in real systems?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How do directed and undirected graphs change the meaning of a model?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
