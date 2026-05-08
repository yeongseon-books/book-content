
# Processes and Threads

> Operating Systems 101 series (2/10)

<!-- a-grade-intro:begin -->

**Core question**: "A running program" is too vague. From the OS's point of view, what exactly is it made of?

> A process is the OS's basic unit for handling an application. Memory, open files, permissions, and CPU state are bundled together, and each process is isolated from the others. A thread is a flow of execution that lives inside one process and shares its memory with sibling threads. This article walks through what is inside a process, how threads differ, and when to reach for one over the other.

<!-- a-grade-intro:end -->

## What You Will Learn

- The four resources a process owns (memory, fds, permissions, CPU state)
- What threads share and what they keep private
- The process creation model — `fork` and `exec`, and Windows `CreateProcess`
- Trade-offs between multi-process and multi-threaded designs

## Why It Matters

Processes and threads are the two basic building blocks of concurrency. Mixing them up leads to broken isolation, false thread-safety assumptions, and zombie children. "Why does the same data appear in one place but not the other?" almost always traces back to confusing these two models.

> The process is the unit of isolation; the thread is the unit of concurrency. If you use the same tool for both, something usually leaks or blocks.

## Concept at a Glance

> Each process owns its own virtual address space, file descriptor table, signal handlers, and credentials. Inside it live one or more threads. Threads share memory and fds but have their own stack and registers.

```text
+-----------------------------------------+
|  Process                                |
|  +----------+ +-----------+ +--------+  |
|  | Code     | | Heap      | | Globals|  |
|  +----------+ +-----------+ +--------+  |
|  +-------- File descriptor table -----+ |
|  |  0:stdin  1:stdout  2:stderr  ...  | |
|  +-----------------------------------+  |
|                                         |
|  +-- Thread A --+   +-- Thread B --+    |
|  |  Stack       |   |  Stack       |    |
|  |  Registers   |   |  Registers   |    |
|  +--------------+   +--------------+    |
+-----------------------------------------+
```

## Key Terms

| Term | Description |
| --- | --- |
| Address space | The virtual memory a process sees (code, data, heap, stack) |
| File descriptor table | The integer-indexed table of open files and sockets |
| `fork` | Syscall that duplicates the calling process to create a child |
| `exec` | Replaces the current process image with a new program |
| GIL | CPython's global interpreter lock; only one thread runs Python bytecode at a time |

## Before / After

**Before — "threads and processes are both just concurrent stuff":**

```python
# I want these two tasks to run "at the same time"
import threading, multiprocessing
```

This line does not tell you which to pick.

**After — "they share different things":**

```text
multiprocessing.Process : separate memory, talk via queue/pipe/shared mem
threading.Thread        : same memory, needs locks, GIL applies

CPU-bound (large numpy matmul)  -> multiprocessing usually wins
I/O-bound (100 HTTP requests)   -> threading or asyncio is enough
```

Both look like "concurrent execution" until you ask what is shared.

## Hands-on: Step by Step

### Step 1: PID and parent-child relationships

```python
import os

print(f"Parent PID (this process): {os.getpid()}")

pid = os.fork()
if pid == 0:
    print(f"Child  PID: {os.getpid()}, parent: {os.getppid()}")
else:
    os.waitpid(pid, 0)
    print(f"Parent: child {pid} exited")
```

`fork` is called once and returns twice. The parent gets the child's PID; the child gets `0`. The same source line splits into two execution streams.

### Step 2: Memory isolation after `fork`

```python
import os

x = [1, 2, 3]
if os.fork() == 0:
    x.append(99)
    print(f"Child x:  {x}")
    os._exit(0)
os.wait()
print(f"Parent x: {x}")
```

The child's mutation of `x` does not show up in the parent. The two processes do not see the same memory (under the hood it is copy-on-write).

### Step 3: Threads share memory

```python
import threading

x = [1, 2, 3]
def worker():
    x.append(99)

t = threading.Thread(target=worker)
t.start(); t.join()
print(f"Main x: {x}")
```

The same `x` list is visible. Threads share an address space, which is exactly why synchronization becomes necessary.

### Step 4: Thread vs process performance

```python
import time, math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_heavy(n):
    return sum(math.sqrt(i) for i in range(n))

N = 5_000_000
tasks = [N] * 4

for Pool, label in [(ThreadPoolExecutor, "Thread"), (ProcessPoolExecutor, "Process")]:
    start = time.perf_counter()
    with Pool(max_workers=4) as ex:
        list(ex.map(cpu_heavy, tasks))
    print(f"{label}: {time.perf_counter() - start:.2f} s")
```

For CPU-bound work, processes typically win. CPython's GIL prevents two threads from running Python bytecode at the same time.

### Step 5: `exec` to become a different program

```python
import os

if os.fork() == 0:
    os.execvp("ls", ["ls", "-la"])  # child becomes ls
    # this line is never reached
os.wait()
```

`fork` then `exec` is the standard way a shell runs commands. The child's memory image is fully replaced by the new program.

## What to Notice in This Code

- `fork` is called once and returns twice
- Process memory is isolated; thread memory is shared
- CPython's GIL makes CPU-bound threading often slower than expected
- `fork`+`exec` is the foundation of shells and container runtimes

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using threads for everything | CPU-bound work is blocked by the GIL | Processes for CPU-bound, threads or asyncio for I/O |
| Not reaping children | Zombie processes accumulate | Call `os.wait`/`waitpid` |
| No locks on shared thread state | Race conditions, mystery bugs | Use `threading.Lock` or queues |
| Assuming `fork` is safe with anything | macOS-specific issues, library state corruption | Consider `multiprocessing.set_start_method('spawn')` |
| Treating processes as cheap | OOMs and resource exhaustion at scale | Reuse via worker pools |

## How This Shows Up in Production

- Web servers: gunicorn uses worker processes; uvicorn pairs with async; combinations are common
- Data processing: `multiprocessing.Pool` parallelizes CPU-bound ETL work
- Containers: container runtimes use `clone`+`exec` variants for isolated children
- Backend debugging: `ps -ef`, `pstree`, and `htop` show process/thread trees
- Data science: `joblib` picks a backend (threads vs processes) per workload

## How a Senior Engineer Thinks

A senior engineer hearing "let's run this concurrently" first asks about the workload. Is it burning CPU? Waiting on I/O? How much state needs to be shared? Should a failure be contained? The answers usually pick the tool — process, thread, or async — almost automatically.

A senior also resists the simple "processes are heavy, threads are cheap" comparison. Processes also bring isolation and crash-safety. A system whose worker can die without taking the others with it is often more valuable in production than one that is slightly faster on a microbenchmark.

## Checklist

- [ ] You can name the four resources a process owns
- [ ] You know what threads share and what they keep separate
- [ ] You know which tool fits CPU-bound vs I/O-bound work
- [ ] You can explain why `fork` and `exec` are split into two calls
- [ ] You understand why children must be reaped

## Practice Problems

1. Pick the heaviest function in a project and run it with (a) a single thread, (b) a 4-thread pool, (c) a 4-process pool. Compare the wall-clock times and write a paragraph explaining the result.

2. Write a tiny script that uses `os.fork` and never reaps the child. Watch a zombie (state `Z`) appear in `ps -ef`. Then add `os.wait` and confirm it disappears.

3. With `threading`, have two threads each increment the same counter 100 million times. Compare the result with and without a lock. Explain in one paragraph why the unlocked version produces a wrong answer.

## Wrap-up and Next Steps

A process is an isolated bundle of resources; a thread is a unit of execution flowing inside it. Mixing them up tends to make concurrent code subtly broken or surprisingly slow. Three axes — CPU vs I/O, isolation needs, and how much memory you must share — usually pick the right tool.

The next article zooms into the OS function that decides which of these many processes and threads gets the CPU next: scheduling.

- [What Is an Operating System?](./01-what-is-an-operating-system.md)
- **Processes and Threads (current)**
- Scheduling (upcoming)
- Concurrency and Race Conditions (upcoming)
- Locks, Mutexes, and Semaphores (upcoming)
- Memory Management (upcoming)
- Virtual Memory (upcoming)
- File Systems (upcoming)
- System Calls (upcoming)
- Containers and the Operating System (upcoming)
## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [The Linux Programming Interface — Michael Kerrisk](https://man7.org/tlpi/)
- [Python multiprocessing documentation](https://docs.python.org/3/library/multiprocessing.html)
- [Python threading documentation](https://docs.python.org/3/library/threading.html)

Tags: Computer Science, Operating Systems, Processes, Threads, Concurrency, Systems

---

© 2026 YeongseonBooks. All rights reserved.
