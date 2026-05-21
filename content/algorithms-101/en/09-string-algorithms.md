---
series: algorithms-101
episode: 9
title: "Algorithms 101 (9/10): String Algorithm Basics"
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
  - Algorithms
  - Strings
  - KMP
  - Trie
  - Regex
seo_description: The cost of naive matching, the intuition behind KMP's failure function, the trie data structure, and the cost awareness needed for production regex.
last_reviewed: '2026-05-04'
---

# Algorithms 101 (9/10): String Algorithm Basics

**Core question**: Finding a pattern inside text sounds simple — so why are there so many algorithms for it?

Almost every piece of software does string matching, but the naive comparison can be O(nm). KMP uses a failure function so it never re-examines the same character, getting O(n+m). Tries and regex engines introduce a different kind of trade-off: convenience vs cost awareness.

This is post 9 in the Algorithms 101 series. Here we cover naive matching, KMP, trie-based lookups, and the cost pitfalls that show up in production regex.

## Questions to Keep in Mind

- What boundary should you inspect first when applying String Algorithm Basics?
- Which signal should the example or diagram make visible for String Algorithm Basics?
- What failure should be prevented first when String Algorithm Basics reaches a real system?

## Big Picture

![algorithms 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/09/09-01-big-picture.en.png)

*algorithms 101 chapter 9 flow overview*

This picture places String Algorithm Basics inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The cost and limits of naive matching
- The KMP algorithm and the intuition behind the failure function
- The trie data structure and its uses
- A cost model for regex and the ReDoS trap

## Why It Matters

Strings appear everywhere — logs, documents, code, search, NLP. Naive matching is fine for many cases, but when patterns are long, texts are huge, or many patterns must be searched at once, the right algorithm decides whether your system is fast or grinds. Regex pitfalls also turn into security incidents (ReDoS).

> String algorithms hide explosive cost behind a mask of simplicity.

> Naive matching tries the pattern at every starting position, so the worst case is O(nm). KMP precomputes a failure function — how the pattern overlaps with itself — so we never re-read the same character; it runs in O(n+m). A trie is a tree that shares prefixes, used for multi-pattern search and autocomplete. Regex engines come in NFA/DFA flavours and backtracking flavours; the latter can degrade exponentially on certain inputs.

```text
Naive matching     : O(nm)
KMP                : O(n+m), failure function preprocessing O(m)
Aho-Corasick       : multi-pattern in O(n + matches)
Trie               : prefix sharing, autocomplete, multi-pattern
Regex              : expressive, backtracking engines risk ReDoS
```

## Key Terms

| Term | Description |
| --- | --- |
| Pattern | The string you are looking for inside the text |
| Failure function | KMP's prefix-suffix overlap length |
| Trie | A tree data structure that shares prefixes |
| Aho-Corasick | Trie + failure links for multi-pattern matching |
| ReDoS | Exponential-time attack on backtracking regex |

## Before / After

**Before — naive matching, worst case O(nm):**

```python
def naive_match(text, pat):
    n, m = len(text), len(pat)
    for i in range(n - m + 1):
        if text[i:i + m] == pat:
            return i
    return -1
```

**After — KMP, O(n+m):**

```python
def kmp_search(text, pat):
    fail = compute_failure(pat)
    j = 0
    for i, c in enumerate(text):
        while j > 0 and c != pat[j]:
            j = fail[j - 1]
        if c == pat[j]:
            j += 1
            if j == len(pat):
                return i - j + 1
    return -1
```

## Hands-On: Step by Step

### Step 1: Naive matching's worst case

```python
text = "a" * 100000 + "b"
pat = "a" * 1000 + "b"

import time
t = time.perf_counter()
naive_match(text, pat)
print(f"naive: {time.perf_counter() - t:.3f}s")
```

On repetitive text, naive matching does almost m comparisons at every starting position. It stops being practical as inputs grow.

### Step 2: KMP's failure function

```python
def compute_failure(pat):
    fail = [0] * len(pat)
    k = 0
    for i in range(1, len(pat)):
        while k > 0 and pat[k] != pat[i]:
            k = fail[k - 1]
        if pat[k] == pat[i]:
            k += 1
        fail[i] = k
    return fail

print(compute_failure("ababaca"))   # [0, 0, 1, 2, 3, 0, 1]
```

The failure function precomputes "where to restart comparison after a mismatch at position i." That single table is the heart of KMP.

### Step 3: Running KMP

```python
def kmp_search(text, pat):
    if not pat:
        return 0
    fail = compute_failure(pat)
    j = 0
    for i, c in enumerate(text):
        while j > 0 and c != pat[j]:
            j = fail[j - 1]
        if c == pat[j]:
            j += 1
            if j == len(pat):
                return i - j + 1
    return -1

print(kmp_search("ababcababcabc", "ababcabc"))   # 4
```

We make a single pass over the text, jumping only the j pointer. O(n+m).

### Step 4: Trie — the autocomplete data structure

```python
class Trie:
    def __init__(self):
        self.root = {}
        self.END = "$"
    def insert(self, word):
        node = self.root
        for c in word:
            node = node.setdefault(c, {})
        node[self.END] = True
    def starts_with(self, prefix):
        node = self.root
        for c in prefix:
            if c not in node:
                return []
            node = node[c]
        out = []
        def dfs(n, path):
            if self.END in n:
                out.append(prefix + "".join(path))
            for c, child in n.items():
                if c == self.END:
                    continue
                path.append(c); dfs(child, path); path.pop()
        dfs(node, [])
        return out

t = Trie()
for w in ["car", "card", "care", "cargo", "cat"]:
    t.insert(w)
print(t.starts_with("car"))   # ['car', 'card', 'care', 'cargo']
```

Tries share common prefixes, so they are memory-efficient relative to dictionary size and very fast at prefix queries.

### Step 5: Regex pitfall — ReDoS

```python
import re, time

# A pattern that triggers catastrophic backtracking
pat = re.compile(r"^(a+)+$")
text = "a" * 30 + "!"

t = time.perf_counter()
pat.match(text)
print(f"regex: {time.perf_counter() - t:.3f}s")
# Add a few more characters and the time explodes
```

Greedy quantifiers nested inside groups can take exponential time on a backtracking engine. For untrusted input, simplify the pattern or consider a linear-time engine like RE2.

## Notable Points

- Naive matching is fine for short patterns and short texts but has clear limits
- Once the failure function is built, KMP is clean
- Tries are the first-choice data structure for any prefix-sharing problem
- Regex is powerful, but its cost depends heavily on the input you let in

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Naive matching on large text | Slow | Use KMP or stdlib (`str.find` / `re`) |
| Off-by-one in handcrafted KMP | Wrong matches | Follow standard pseudocode exactly |
| Missing trie end marker | Cannot distinguish "car" from "card" | Tag terminal nodes with END |
| Using ReDoS-prone patterns | Service stalls | Simplify, consider RE2, set timeouts |
| Doing too much in one regex | Hurts readability | Split into a verifiable parser |

## How This Is Used in Practice

- Inverted-index construction and prefix search in search engines
- Autocomplete in code editors (trie or fuzzy match)
- Signature matching in security tools (Aho-Corasick)
- Pattern extraction in log pipelines (regex with a safe engine)
- Tokenisers in NLP preprocessing

## How a Senior Engineer Thinks

A senior engineer first asks "is the pattern short and one-off, or long and repeated?" Short and one-off — the standard library is enough. Many or repeated patterns — consider tries, KMP, or Aho-Corasick.

A senior engineer also stays mindful of where regex input comes from. For user input or external data, simplify the pattern, prefer linear-time engines when possible, and always set a timeout. ReDoS is a real production incident pattern.

## Checklist

- [ ] Do you know the worst-case cost of naive matching?
- [ ] Can you describe KMP's failure-function intuition in one sentence?
- [ ] Can you implement a trie?
- [ ] Are you aware of regex cost and security risks?
- [ ] Can you pick the right tool when multi-pattern matching is needed?

## Practice Problems

1. Using only KMP's failure function, write a function that returns every position where a pattern appears in the text. Extend a single-match version to keep going after each match.

2. Using a trie, return the prefix-autocomplete results in lexicographic order. Extend the function to return only the top k results when there are too many.

3. Design a simple static heuristic that flags regex patterns at risk of ReDoS. Start with rules like "nested quantifiers."

## Wrap-Up and Next Steps

String algorithms balance simplicity against explosive cost. Naive matching, KMP, tries, and a healthy respect for regex cover most everyday string work safely. Beyond that lie suffix arrays, suffix automata, and bit-parallel matching.

The next and final article in this series gathers algorithm problem-solving strategies — how to map problems to patterns, how to organise your thinking, and what it really means to be good at algorithms in interviews and in production.

## Answering the Opening Questions

- **What boundary should you inspect first when applying String Algorithm Basics?**
  - The article treats String Algorithm Basics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for String Algorithm Basics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when String Algorithm Basics reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Algorithms 101 (1/10): What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): Time and Space Complexity](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): Search Algorithms](./03-search-algorithms.md)
- [Algorithms 101 (4/10): Sorting Algorithms](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): Dynamic Programming](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): Greedy Algorithms](./07-greedy-algorithms.md)
- [Algorithms 101 (8/10): Graph Algorithms](./08-graph-algorithms.md)
- **String Algorithm Basics (current)**
- Algorithm Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Python `re` documentation](https://docs.python.org/3/library/re.html)
- [Wikipedia — Knuth-Morris-Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)
- [Wikipedia — Aho-Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
- [OWASP — Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)

Tags: Computer Science, Algorithms, Strings, KMP, Trie, Regex
