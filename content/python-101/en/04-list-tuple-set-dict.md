---
title: list, tuple, set, dict
series: python-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- list-and-tuple
- dict
- set
- mutability
- comprehensions
- hashable
last_reviewed: '2026-05-03'
seo_description: 'The four collections differ along four axes: mutability, order,
  duplicates allowed, and hashability.'
---

# list, tuple, set, dict

These four collections diverge along four axes: mutability, order, duplicates, and hashability. Picking the right one is really about choosing which trade-offs matter for the job.

This post is the 4th article in the Python 101 series. This is the stage in the series where collection trade-offs become concrete.

## What you will learn

By the end of this chapter you will be able to explain and code the following:

- How to tell list, tuple, set, and dict apart along the axes of mutability, order, duplicates, and hashability
- A first-cut decision rule for which collection to reach for
- Core methods like slicing, `append`/`extend`, `pop`, `update`
- One-line data transformations through list, set, and dict comprehensions
- What "hashable" means and why dict keys and set members must be hashable
- The aliasing accidents that come from confusing assignment with copying
- The mutable-default-argument trap and how to avoid it
- How `dict.get`, `setdefault`, and `collections.defaultdict` keep missing keys safe

Code blocks marked with `>>>` are REPL transcripts you can paste directly. Blocks without `>>>` are illustrative excerpts that assume the surrounding variables already exist.

## Why this matters

Choosing a collection determines both the performance and the meaning of the code. Reach for `dict` where a `list` would do, and the code grows heavy. Reach for a `list` where a `set` belongs, and a single membership check becomes O(n) — slowing down with every new element. Conversely, expressing an immutable bundle as a `list` invites someone to mutate what was supposed to be fixed; the type system gives no warning.

Recurring accidents in production code:

- "Copying" a list with `=`, mutating one side, and finding both sides changed because they shared the same object.
- Writing `def f(items=[]):` and watching the default list grow with every call.
- Crashing with `KeyError` because a missing key was fetched with `d[key]` instead of `d.get(key)`.
- Hitting `TypeError: unhashable type` after putting a `list` or `dict` into a `set`.

This chapter consolidates the four collections onto a single page so the next chapter on control flow can pick the right structure deliberately.

## Mental model

> The four collections differ along four axes: mutability, order, duplicates allowed, and hashability. Choosing a collection is choosing which guarantees on those four axes you accept and which you give up.
Group the four collections along three axes — mutability, order, and hashability — and they sit cleanly in memory.

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/python-101/04/04-01-mental-model.en.png)

*Mental model*
Three rules carry most of the weight.

1. **Mutable (list, dict, set)** can be changed in place after creation; **immutable (tuple, str, int)** cannot.
2. **Dict keys and set elements must be hashable.** A tuple is hashable when every element inside it is hashable.
3. **Dict and set lookup is O(1) on average,** while list membership is O(n). When "is X here?" is a frequent question, reach for set or dict.

## Core concepts

### 1) list — ordered and mutable

```text
>>> nums = [3, 1, 4, 1, 5]
>>> nums.append(9)
>>> nums
[3, 1, 4, 1, 5, 9]
>>> nums[0]
3
>>> nums[-1]
9
>>> nums[1:4]
[1, 4, 1]
>>> sorted(nums)
[1, 1, 3, 4, 5, 9]
>>> nums.sort()      # in place; returns None
>>> nums
[1, 1, 3, 4, 5, 9]
```

`sorted(nums)` returns a **new list**; `nums.sort()` sorts **in place** and returns `None`. The `None` return trips up beginners who try `for n in nums.sort():`.

`append` versus `extend` is another classic confusion.

```text
>>> a = [1, 2]
>>> a.append([3, 4])
>>> a
[1, 2, [3, 4]]            # the whole list is added as one element
>>> a = [1, 2]
>>> a.extend([3, 4])
>>> a
[1, 2, 3, 4]              # elements are added one by one
```

### 2) tuple — ordered and immutable

```text
>>> point = (3, 4)
>>> x, y = point          # unpacking
>>> x, y
(3, 4)
>>> point[0] = 10
Traceback (most recent call last):
  ...
TypeError: 'tuple' object does not support item assignment
```

Tuples express identity for a small bundle of values: a coordinate `(x, y)`, an RGB triple `(255, 0, 0)`, a row from a database. To make the meaning even more explicit, reach for `collections.namedtuple` or `dataclasses.dataclass(frozen=True)`.

A single-element tuple needs the trailing comma. `(1)` is just an integer.

```text
>>> type((1))
<class 'int'>
>>> type((1,))
<class 'tuple'>
```

### 3) set — unordered, no duplicates

Sets shine at membership checks and deduplication.

```text
>>> seen = {1, 2, 3}
>>> seen.add(2)             # already present; ignored
>>> seen
{1, 2, 3}
>>> 2 in seen
True
>>> {1, 2, 3} & {2, 3, 4}   # intersection
{2, 3}
>>> {1, 2, 3} | {2, 3, 4}   # union
{1, 2, 3, 4}
>>> {1, 2, 3} - {2}         # difference
{1, 3}
```

The empty set is `set()`, not `{}`. `{}` is an empty dict.

```text
>>> type({})
<class 'dict'>
>>> type(set())
<class 'set'>
```

A set's iteration order is not guaranteed. When tests compare output, sort first: `sorted(seen)`.

### 4) dict — key-to-value mapping, mutable, keys unique

`dict` is the workhorse. From Python 3.7 onward it preserves insertion order.

```text
>>> user = {"name": "ada", "age": 30}
>>> user["name"]
'ada'
>>> user["email"] = "ada@example.com"
>>> user
{'name': 'ada', 'age': 30, 'email': 'ada@example.com'}
>>> "age" in user
True
>>> user.get("phone")          # missing → None
>>> user.get("phone", "N/A")
'N/A'
>>> list(user.keys())
['name', 'age', 'email']
>>> list(user.items())
[('name', 'ada'), ('age', 30), ('email', 'ada@example.com')]
```

`d[key]` raises `KeyError` for a missing key. When the key may legitimately be absent, use `get`.

### 5) What hashable means

Dict keys and set members must be **hashable** — once created their value cannot change, and they implement `__hash__`.

- Hashable: `int`, `float`, `str`, `bool`, `bytes`, and a `tuple` whose elements are all hashable.
- Not hashable: `list`, `set`, `dict` — being mutable, their hash could change underneath the container.

```text
>>> {(1, 2), (3, 4)}                    # tuples are hashable
{(1, 2), (3, 4)}
>>> {[1, 2], [3, 4]}
Traceback (most recent call last):
  ...
TypeError: unhashable type: 'list'
```

To put a set inside a set, use `frozenset`.

### 6) Comprehensions — transform in one line

list, set, and dict each support comprehension syntax.

```text
>>> [n * n for n in range(5)]
[0, 1, 4, 9, 16]
>>> [n for n in range(10) if n % 2 == 0]
[0, 2, 4, 6, 8]
>>> {word.lower() for word in ["Python", "PYTHON", "python"]}
{'python'}
>>> {n: n * n for n in range(4)}
{0: 0, 1: 1, 2: 4, 3: 9}
```

Comprehensions are short, but as conditions multiply or nesting deepens, readability suffers. Fall back to a regular `for` loop in those cases.

## Before / after

Compare the awkward way with the version that picks the right collection.

```python
# Before: list membership is O(n)
seen = []
duplicates = []
for x in stream:
    if x in seen:                # scans the whole list every time
        duplicates.append(x)
    else:
        seen.append(x)

# After: set membership is O(1) on average
seen = set()
duplicates = []
for x in stream:
    if x in seen:
        duplicates.append(x)
    else:
        seen.add(x)
```

Missing-key handling can shrink too.

```python
# Before: explicit existence check every time
counts = {}
for word in words:
    if word in counts:
        counts[word] = counts[word] + 1
    else:
        counts[word] = 1

# After: dict.get or defaultdict
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

# After (shortest): collections.Counter
from collections import Counter
counts = Counter(words)
```

## Step-by-step practice

Process a list of log lines to compute per-IP access counts and the first-seen timestamp. We will exercise dict, set, tuple, and comprehensions together.

1. **Sample data.**

   ```python
   logs = [
       ("10.0.0.1", "2026-05-03 09:00:01"),
       ("10.0.0.2", "2026-05-03 09:00:02"),
       ("10.0.0.1", "2026-05-03 09:00:05"),
       ("10.0.0.3", "2026-05-03 09:00:07"),
       ("10.0.0.2", "2026-05-03 09:00:10"),
   ]
   ```

2. **Unique IPs.** A set comprehension does it in one line.

   ```python
   unique_ips = {ip for ip, _ in logs}
   # {'10.0.0.1', '10.0.0.2', '10.0.0.3'}
   ```

3. **Per-IP counts.** Use `dict.get`.

   ```python
   counts = {}
   for ip, _ in logs:
       counts[ip] = counts.get(ip, 0) + 1
   # {'10.0.0.1': 2, '10.0.0.2': 2, '10.0.0.3': 1}
   ```

4. **First-seen timestamps.** `dict.setdefault` covers it.

   ```python
   first_seen = {}
   for ip, ts in logs:
       first_seen.setdefault(ip, ts)
   # {'10.0.0.1': '2026-05-03 09:00:01', '10.0.0.2': '...', '10.0.0.3': '...'}
   ```

5. **Sort the result.** Dicts do not sort themselves; `sorted` returns a new list.

   ```python
   ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
   # [('10.0.0.1', 2), ('10.0.0.2', 2), ('10.0.0.3', 1)]
   ```

If you already know `Counter`, steps 2 and 3 collapse into a single line. After the next chapter on functions you can wrap the whole flow into a reusable helper.

## Common mistakes

1. **Treating `b = a` as a copy.**
   `b = a` simply binds another name to the same object. Mutate one side and both change. For a shallow copy use `b = a[:]` or `b = list(a)`; for nested structures use `copy.deepcopy(a)`.

2. **Mutable default arguments.**
   `def f(items=[]):` evaluates the default list once, at definition time, and shares it across every call. The list grows on every invocation. Use `def f(items=None): items = items if items is not None else []` instead.

3. **Indexing a missing dict key.**
   `d[key]` raises `KeyError`. When the key may be absent, use `d.get(key)` or `d.get(key, default)`. The "create on demand" pattern fits `setdefault` or `defaultdict`.

4. **Trusting set order.**
   Sets do not guarantee iteration order. Sort before comparing in tests. Dicts do guarantee insertion order from 3.7, but do not extend that guarantee to sets.

5. **Using a list as a set member or dict key.**
   You will see `TypeError: unhashable type: 'list'`. Convert with `tuple(seq)` if it really should be a key.

6. **Assuming `dict.keys()` and `dict.values()` are lists.**
   Both are view objects. They reflect later changes to the dict. When a snapshot is needed, materialize: `list(d.keys())`.

## In practice

- **Counting and grouping.** `Counter` and `defaultdict(list)` remove the repeated "if missing, initialize" pattern. When you see `if key not in d: d[key] = []` more than once in your code, switch to `defaultdict`.
- **Ordered dicts.** From Python 3.7 onward, plain `dict` preserves insertion order. Reach for `OrderedDict` only when you need its extras like `move_to_end` or comparison that respects order.
- **Immutable bundles.** Express "do not mutate this bundle" with `tuple`, `frozenset`, or `dataclass(frozen=True)`. The type alone signals intent to the next reader.
- **JSON serialization.** `json.dumps` cannot serialize a set directly. Convert with `list(my_set)` or `sorted(my_set)` right before the call.
- **Bulk membership checks.** A list of 100,000 blocked user IDs costs O(n) per check. Convert to a set once and reuse the structure across checks.

## Checklist

- [ ] I can sketch a small table comparing list / tuple / set / dict on mutability, order, duplicates, hashability
- [ ] I know `=` does not copy a list
- [ ] I know the mutable default argument trap and the standard fix
- [ ] I can pick between `dict.get`, `setdefault`, `defaultdict`, and `Counter` deliberately
- [ ] I can define "hashable" in one sentence
- [ ] I have written a list, set, and dict comprehension at least once
- [ ] I never assume set iteration order
- [ ] I know when `tuple` and `namedtuple`/`dataclass(frozen=True)` are the right choice

## Exercises

1. **Word frequency**
   Write `word_counts(text: str) -> dict[str, int]` returning the count of each word, lowercased and stripped of punctuation.
   - Success criterion: `word_counts("Python is great. PYTHON is fun.")` returns `{'python': 2, 'is': 2, 'great': 1, 'fun': 1}` (key order is free).

2. **Deduplicate while preserving order**
   Write `unique_in_order(items: list) -> list` that drops duplicates yet keeps the first appearance order. Track membership with a single set.
   - Success criterion: `unique_in_order([3, 1, 3, 2, 1, 4])` returns `[3, 1, 2, 4]`.

3. **Group by**
   Given `[("ada", "engineer"), ("bob", "designer"), ("charlie", "engineer")]`, write `group_by_role(rows)` returning a dict mapping each role to the list of names. Use `defaultdict(list)`.
   - Success criterion: the input above produces `{'engineer': ['ada', 'charlie'], 'designer': ['bob']}`.

## Summary and next chapter

- list and tuple are ordered bundles; set is an unordered collection of unique hashable elements; dict is a key→value mapping.
- Mutable (list, set, dict) versus immutable (tuple) is a deliberate choice.
- Dict keys and set members must be hashable; lists are not.
- `b = a` aliases; copy with `list(a)` or `copy.deepcopy(a)` when needed.
- Handle missing keys with `dict.get`, `setdefault`, `defaultdict`, or `Counter`.

The next chapter covers control flow — `if`, `for`, `while` — and shows how `enumerate`, `zip`, `range`, and comprehensions combine into loops that read well.

<!-- toc:begin -->
<!-- toc:end -->

## References

- [Python docs — Built-in Types](https://docs.python.org/3/library/stdtypes.html) — Official behavior reference for list, tuple, set, dict, and hashability constraints.
- [Python tutorial — Data Structures](https://docs.python.org/3/tutorial/datastructures.html) — Walks through list methods, tuples, sets, dictionaries, and comprehensions with beginner-friendly examples.
- [PEP 274 — Dict Comprehensions](https://peps.python.org/pep-0274/) — Primary source for the dict-comprehension syntax discussed in the chapter.
- [Python Wiki — TimeComplexity](https://wiki.python.org/moin/TimeComplexity) — Useful for the chapter’s performance comparison between linear list membership and average O(1) dict/set lookups.
- [Python docs — `collections`](https://docs.python.org/3/library/collections.html) — Introduces supporting containers such as `namedtuple` and `deque` that refine data-structure choices.
- [Python docs — Data Model](https://docs.python.org/3/reference/datamodel.html) — Adds formal background on mutable versus immutable objects.

Tags: list-and-tuple, dict, set, mutability, comprehensions, hashable
