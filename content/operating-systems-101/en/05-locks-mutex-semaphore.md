---
series: operating-systems-101
episode: 5
title: Locks, Mutexes, and Semaphores
status: publish-ready
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
  - Synchronization
  - Mutex
  - Semaphore
  - Concurrency
seo_description: How mutexes, semaphores, and condition variables work, why deadlock happens, and how a single misordered lock can freeze a whole system.
last_reviewed: '2026-05-15'
---

# Locks, Mutexes, and Semaphores

Once you realize a race condition is real, the next instinct is usually "add a lock." That instinct is useful, but incomplete. A badly scoped lock or one inconsistent lock order can freeze an entire system just as effectively as the original bug.

Synchronization primitives are simple only on the surface. Safety depends on the exact rules around ownership, order, and duration.

This is post 5 in the Operating Systems 101 series. It breaks down mutexes, semaphores, reentrant locks, and condition variables, then shows how deadlock appears and how to avoid it.

## Questions this article answers

- What are the actual differences between mutexes, reentrant locks, semaphores, and condition variables?
- Under what conditions does deadlock form?
- Why do throughput and latency both get worse when locks are held too long?
- What alternatives can preserve safety while reducing the amount of locking?

## What You Will Learn

- The differences between mutex, RLock, semaphore, and condition variable
- The four conditions that produce deadlock and how to break them
- The cost of locks — context switches and cache effects
- Lock-free synchronization alternatives — queues, immutability, atomics, RCU

## Why It Matters

A lock is the seat belt of concurrent code, but a wrongly fastened belt can pin you to the seat. Disagreeing on lock order in even one place can stop the whole system, and protecting too small a region leaves the race intact. Treating "just take a lock" as a safety guarantee is a leading cause of mysterious freezes in production.

> A lock does not guarantee safety. It enforces the rules that, if followed, produce safety. Wrong rules produce wrong locks.

## Concept at a Glance

> A mutex lets one flow at a time enter the critical section. A semaphore lets up to N flows enter at once. An RLock (reentrant lock) lets the same flow take the same lock multiple times. A condition variable is a mechanism for waiting until some predicate becomes true and then waking the waiter.

### How synchronization tools gate entry

![How synchronization tools gate entry](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/05/05-01-how-synchronization-tools-gate-entry.en.png)
*Each synchronization primitive controls entry differently, which is why the wrong one changes both safety and throughput.*

```text
Mutex     : capacity = 1
Semaphore : capacity = N (e.g., DB connection pool of 10)
RLock     : same owner can re-enter (recursive functions, etc.)
Condition : "wait until inventory >= 1" style predicate waits
```

## Key Terms

| Term | Description |
| --- | --- |
| Critical section | Code region that must be entered by only one flow at a time |
| Deadlock | Two or more flows wait for each other's locks forever |
| Livelock | No lock is held but flows keep yielding and never progress |
| Starvation | A flow never receives the lock and never makes progress |
| Lock convoy | All flows queue behind a single lock and throughput collapses |

## Before / After

**Before — "a lock is enough":**

```python
import threading
lock_a = threading.Lock()
lock_b = threading.Lock()

def task1():
    with lock_a:
        with lock_b:
            ...

def task2():
    with lock_b:    # different order!
        with lock_a:
            ...
```

When both functions run together they construct a deadlock.

**After — "enforce a single global lock order":**

```text
Rule: always take lock_a first, then lock_b.
Violating it in even one place can stop the whole system.
```

## Hands-on: Step by Step

### Step 1: Basic mutex

```python
import threading
counter = 0
m = threading.Lock()

def add():
    global counter
    for _ in range(100_000):
        with m:
            counter += 1

ts = [threading.Thread(target=add) for _ in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print(counter)
```

The `with m:` block is the critical section. Leaving it releases the lock automatically.

### Step 2: RLock for recursive calls

```python
import threading
lock = threading.RLock()
data = {}

def update(k, v, depth=0):
    with lock:
        data[k] = v
        if depth < 2:
            update(k + '_x', v + 1, depth + 1)
```

A plain `Lock` would block the same thread on the second `acquire`. `RLock` allows reentry by the same owner.

### Step 3: Semaphore to cap concurrency

```python
import threading, time

pool = threading.Semaphore(3)   # at most three at once

def query():
    with pool:
        time.sleep(0.5)         # simulate DB work
        print(threading.current_thread().name, 'done')

ts = [threading.Thread(target=query) for _ in range(10)]
for t in ts: t.start()
for t in ts: t.join()
```

Even with ten threads, only three run at the same time. This is the natural abstraction for resources like database connection pools.

### Step 4: Build a deadlock on purpose

```python
import threading, time

a = threading.Lock(); b = threading.Lock()

def t1():
    with a:
        time.sleep(0.1)
        with b:  pass

def t2():
    with b:
        time.sleep(0.1)
        with a:  pass

threading.Thread(target=t1).start()
threading.Thread(target=t2).start()
# Both threads wait forever (Ctrl+C to stop)
```

All four classic deadlock conditions hold (mutual exclusion, hold-and-wait, no-preemption, circular wait). The most common fix in practice is breaking circular wait by forcing one global lock order.

### Step 5: Lock-free alternative — communicate via a queue

```python
from queue import Queue
import threading

q = Queue()

def producer():
    for i in range(5):
        q.put(i)

def consumer():
    while True:
        item = q.get()
        if item is None: break
        print('got', item)
        q.task_done()

threading.Thread(target=producer).start()
c = threading.Thread(target=consumer)
c.start()
q.join(); q.put(None); c.join()
```

You take no locks yourself, but the queue synchronizes internally. This is why communicating beats sharing memory.

## What to Notice in This Code

- Locks enforce rules (lock order and lock scope), they do not invent safety
- A semaphore is a counting lock and the natural abstraction for resource pools
- Breaking just one of the four deadlock conditions is enough to remove the deadlock
- When locks are not the answer, queues and message passing often win on clarity

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| No agreed lock order | Deadlock | Document a global lock order in code comments |
| Heavy I/O inside the lock | Other threads stall, throughput collapses | Keep critical sections short, do I/O outside |
| Using `Lock` in recursion | Thread blocks itself | Use `RLock` |
| Lock not released on exception | Deadlock or zombie lock | Always use `with lock:` |
| One global lock for everything | Effectively serialized, multithreading wasted | Split protection into finer units |

## How This Shows Up in Production

- DB connection pool: a semaphore caps concurrent usage
- Cache refresh: a mutex or read-write lock guards the rebuild
- Backend job queues: producer/consumer pattern avoids explicit locks
- GUI/games: single owner thread plus a queue for external input
- Distributed systems: the same idea reappears as distributed locks (Redis SETNX, etcd lease)

## How a Senior Engineer Thinks

A senior engineer writes down what a lock protects, who is responsible for releasing it, and the order in which it must be taken before adding it. If they cannot write those rules down, they refuse to add the lock. That written rule lives as a code comment so the next person does not repeat the same mistake.

A senior also asks first whether the design can avoid locks entirely. Message passing, immutable data, and single ownership remove the chance to misuse synchronization. Concurrent code is best when fewer locks are taken and they are taken for less time.

## Checklist

- [ ] I can describe mutex, RLock, semaphore, and condition variable
- [ ] I can name the four deadlock conditions
- [ ] I understand why a global lock order matters
- [ ] I know the cost of locks (context switches, convoys)
- [ ] I know at least one alternative to locks (queues, immutability, atomics)

## Practice Problems

1. Build a deadlock on purpose, then fix it by enforcing a single lock order. Write up in one paragraph what changed.

2. Build a worker pool that runs at most three jobs concurrently using a semaphore. Throw ten jobs at it and observe the order and timing.

3. Take a piece of locking code and rewrite it as a queue-based producer/consumer. Compare code length and how easy each version is to understand.

## Wrap-up and Next Steps

Mutex, semaphore, RLock, and condition variable are the basic synchronization tools the OS provides. Locks are safe only when their order, scope, and duration are clearly defined, and breaking just one of the four deadlock conditions is enough to eliminate deadlock. The safest lock is the one you do not need.

The next article moves on to another OS fundamental — memory management. We will look at how a process gets its memory and how the OS divides limited RAM across many processes.

<!-- toc:begin -->
- [What is an Operating System?](./01-what-is-an-operating-system.md)
- [Processes and Threads](./02-processes-and-threads.md)
- [Scheduling](./03-scheduling.md)
- [Concurrency and Race Conditions](./04-concurrency-and-race-conditions.md)
- **Locks, Mutexes, and Semaphores (current)**
- Memory Management (upcoming)
- Virtual Memory (upcoming)
- File Systems (upcoming)
- System Calls (upcoming)
- Containers and the Operating System (upcoming)
<!-- toc:end -->

## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [The Art of Multiprocessor Programming — Herlihy & Shavit](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0-12-415950-1)
- [Java Concurrency in Practice — Brian Goetz](https://jcip.net/)
- [Python threading.Semaphore](https://docs.python.org/3/library/threading.html#semaphore-objects)

Tags: Computer Science, Operating Systems, Synchronization, Mutex, Semaphore, Concurrency
