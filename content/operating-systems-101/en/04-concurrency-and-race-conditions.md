---
series: operating-systems-101
episode: 4
title: Concurrency and Race Conditions
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
  - Operating Systems
  - Concurrency
  - Race Conditions
  - Debugging
  - Systems
seo_description: What race conditions are, why they hide so well, and the three axes of concurrency violation — atomicity, visibility, and ordering.
last_reviewed: '2026-05-04'
---

# Concurrency and Race Conditions

This is post 4 in the Operating Systems 101 series.

> Operating Systems 101 series (4/10)

<!-- a-grade-intro:begin -->

**Core question**: Why does code that works perfectly with one thread break in strange, hard-to-reproduce ways once you go multi-threaded?

> A race condition happens when two or more flows touch the same data at the same time, and the result depends on who got there first. Even a single line like `count += 1` is read-modify-write, and another thread can sneak in between those steps. This article explains why concurrency bugs hide so well, what kinds exist, and which design principles keep them out.

<!-- a-grade-intro:end -->

## What You Will Learn

- A precise definition of race conditions and why they are hard to reproduce
- Three axes of concurrency violation — atomicity, visibility, ordering
- How memory models relate to visibility
- Design principles that reduce concurrency bugs

## Why It Matters

Concurrency bugs are quiet during development and loud in production, especially under load. A bug that never appeared in tests corrupts data at 2am when traffic peaks. After living through this once, "be careful with concurrent code" stops being a slogan.

> A race condition is worse than a wrong answer; it is a state where you cannot say which answer you will get.

## Concept at a Glance

> When two threads touch the same variable, the OS scheduler can interrupt either of them at any time. Steps from the two flows interleave, and the final state can differ from what either flow intended.

```text
Initial: count = 0   (both threads want to add 1)

Ideal                          Real
T1 read  0                     T1 read  0
T1 add   1                     T2 read  0   <- interleaves
T1 write 1                     T1 add   1
T2 read  1                     T1 write 1
T2 add   2                     T2 add   1
T2 write 2  -> 2               T2 write 1  -> 1 (lost update)
```

## Key Terms

| Term | Description |
| --- | --- |
| Race condition | A bug whose outcome depends on execution order |
| Critical section | A region of code only one flow may run at a time |
| Atomicity | A step appears indivisible from the outside |
| Visibility | When one thread's write becomes visible to another |
| Memory model | The rules a language or hardware promises about concurrent access |

## Before / After

**Before — "it is one line, so it is safe":**

```python
count = 0
def add():
    global count
    for _ in range(100_000):
        count += 1   # one line
```

That one line is really three: read, add, write.

**After — "the steps can interleave":**

```text
T1: load count -> 100
T2: load count -> 100   <- same value
T1: add  -> 101
T2: add  -> 101
T1: store -> 101
T2: store -> 101         <- one increment vanished
```

Increments quietly disappearing is the textbook race outcome.

## Hands-on: Step by Step

### Step 1: Reproduce the simplest race

```python
import threading

count = 0
def add():
    global count
    for _ in range(100_000):
        count += 1

ts = [threading.Thread(target=add) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
print(count)   # expected: 800_000, actual: usually less, varies per run
```

Run it several times. The non-determinism is the strongest clue something is racing.

### Step 2: Show with `dis` that one line is many steps

```python
import dis

def add_one(d):
    d['k'] += 1

dis.dis(add_one)
```

You see `LOAD_FAST`, `LOAD_CONST`, `INPLACE_ADD`, `STORE_SUBSCR`. Another thread can wedge in between any two of them.

### Step 3: Protect with a lock

```python
import threading

count = 0
lock = threading.Lock()

def add():
    global count
    for _ in range(100_000):
        with lock:
            count += 1

ts = [threading.Thread(target=add) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
print(count)   # always 800_000
```

The lock makes the critical section enter-once at a time. Determinism returns.

### Step 4: Visibility intuition

```python
import threading, time

stop = False
def worker():
    while not stop:
        pass

t = threading.Thread(target=worker)
t.start()
time.sleep(0.1)
stop = True
t.join()
```

CPython usually behaves here, but in general (other runtimes, JITs) the change to `stop` may not become visible to the worker promptly. Visibility issues persist as long as a value lives in a per-CPU register or cache.

### Step 5: Avoid the race by reducing sharing

```python
from queue import Queue
import threading

q = Queue()
def safe_add():
    local = 0
    for _ in range(100_000):
        local += 1
    q.put(local)

ts = [threading.Thread(target=safe_add) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()

total = 0
while not q.empty():
    total += q.get()
print(total)
```

Reducing shared state is often safer than locking it.

## What to Notice in This Code

- A single source line says nothing about atomicity
- Same code, different result every run -> suspect a race
- Locks are powerful but kill performance if held too long
- Designs that minimize shared state often beat well-locked designs

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| "Tests passed, must be safe" | Only fails under load | Add load and fuzz tests |
| Lock too narrow | Race in the unprotected step | Wrap the full critical section |
| Lock too wide | Effectively serialized, performance dies | Narrow it, then measure |
| Debug with `print` | The print itself synchronizes, hiding the bug | Use logging or deterministic tests |
| Ignoring visibility | One thread's write is invisible elsewhere | Learn the memory model and synchronize |

## How This Shows Up in Production

- Backend caches: concurrent updates protected by locks or compare-and-swap
- Counters and metrics: thread-local accumulation then periodic merge
- Databases: isolation levels are essentially race-prevention mechanisms
- Distributed systems: cross-node races handled by distributed locks or atomic ops
- UI frameworks: single-owner main thread blocks concurrent access

## How a Senior Engineer Thinks

A senior engineer hearing "we sometimes see a concurrency bug" does not jump to a fix. First they make a small table: which data is shared, who reads, who writes, what the locks are claiming to protect. Only after that table is clean does any code change become meaningful.

A senior also knows "locking is often not the answer." Removing shared state, communicating by messages, using immutable data — these designs cut down the surface where bugs can live. The safest critical section is the one that does not exist.

## Checklist

- [ ] You can define a race condition in one sentence
- [ ] You can distinguish atomicity, visibility, and ordering
- [ ] You know that "one line" says nothing about atomicity
- [ ] You know strategies beyond locks (immutable, messages, thread-local)
- [ ] You treat non-determinism as a clue when debugging concurrency

## Practice Problems

1. Have 8 threads each increment a shared counter 10,000 times. Run three versions: (a) no lock, (b) narrow lock, (c) wide lock. Compare outcomes and runtimes in a small table.

2. Find shared state in one of your own projects and rewrite that part to "share less." Note in a paragraph what got simpler and what got harder.

3. Switch your concurrency debug code from `print` to `logging`. Note how interleaved output changes and explain why.

## Wrap-up and Next Steps

Race conditions hide behind the appearance of "one line" because steps interleave. The three axes — atomicity, visibility, ordering — give you a vocabulary for them, and tools beyond locks (immutability, messages, thread-local accumulation) reduce the surface from the design stage.

Next we look at the most common synchronization primitives in detail: locks (mutexes) and their cousin the semaphore.

<!-- toc:begin -->
- [What Is an Operating System?](./01-what-is-an-operating-system.md)
- [Processes and Threads](./02-processes-and-threads.md)
- [Scheduling](./03-scheduling.md)
- **Concurrency and Race Conditions (current)**
- Locks, Mutexes, and Semaphores (upcoming)
- Memory Management (upcoming)
- Virtual Memory (upcoming)
- File Systems (upcoming)
- System Calls (upcoming)
- Containers and the Operating System (upcoming)
<!-- toc:end -->

## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Java Concurrency in Practice — Brian Goetz](https://jcip.net/)
- [The Art of Multiprocessor Programming — Herlihy & Shavit](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0-12-415950-1)
- [Python threading documentation](https://docs.python.org/3/library/threading.html)

Tags: Computer Science, Operating Systems, Concurrency, Race Conditions, Debugging, Systems
