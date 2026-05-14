---
series: operating-systems-101
episode: 9
title: System Calls
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Operating Systems
  - Syscall
  - Strace
  - Kernel
  - User Space
seo_description: read, write, open, fork — how user code asks the kernel to do work through system calls, and what each call actually costs.
last_reviewed: '2026-05-04'
---

# System Calls

This is post 9 in the Operating Systems 101 series.

> Operating Systems 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: What route does user code take to use kernel resources (files, network, processes), and what is the cost of that route?

> User code never touches the disk or the network card directly. Every request flows through a narrow door called a system call into the kernel. The door is safe but expensive. Once you understand what a system call is and why it costs, you can predict which of two equivalent programs will be faster.

<!-- a-grade-intro:end -->

## What You Will Learn

- The split between user space and kernel space
- How a system call is invoked and how it returns
- Observing real syscalls with strace
- Patterns that reduce syscall cost — buffering, batching, vDSO

## Why It Matters

Two programs processing the same 100MB of data can be many times faster or slower depending only on syscall count. Container security (seccomp), debugging (strace), and performance analysis (perf) all operate at the syscall layer. Without understanding syscalls, half of what happens on top of the OS is invisible to you.

> A system call is the only contract between user code and the kernel, and the count and cost of those calls largely set the system's performance.

## Concept at a Glance

> User space is where ordinary programs run; kernel space is where the OS core runs. There is a privilege boundary between them, and user code can only enter the kernel through the narrow entry of a system call. Each entry pays for context switching and security checks, which is why it costs.

```text
[user space]
  print(...) → write(fd, buf, n)  ← syscall entry
                       ↓
                 mode switch (user → kernel)
                       ↓
                 argument check, resource access
                       ↓
                 mode switch (kernel → user)
                       ↓
                 return value
```

## Key Terms

| Term | Description |
| --- | --- |
| User space | The memory and privilege region where ordinary apps run |
| Kernel space | Where the OS core runs; not directly accessible |
| System call | The only entry from user code into kernel work |
| Context switch | The cost of swapping registers, page tables, etc. on mode change |
| vDSO | Hot syscalls (e.g., gettimeofday) handled in user space to save cost |

## Before / After

**Before — "one byte at a time":**

```python
with open('out.bin', 'wb', buffering=0) as f:
    for c in b'A' * 100_000:
        f.write(bytes([c]))     # one syscall each
# 100,000 write syscalls
```

**After — "buffered":**

```python
with open('out.bin', 'wb') as f:    # default buffering
    f.write(b'A' * 100_000)         # effectively one write
```

Same result, five orders of magnitude fewer calls. Syscalls are billed per call.

## Hands-on: Step by Step

### Step 1: See syscalls with strace

```bash
strace -c python3 -c "print('hello')"
# Summary: which syscalls were called, how often, total time
```

`-c` is the count summary. Use `-e trace=open,read,write` to filter to specific syscalls.

### Step 2: How big should each read be?

```python
import os, time
fd = os.open('big.bin', os.O_RDONLY)
sizes = [1, 64, 4096, 65536]
for s in sizes:
    os.lseek(fd, 0, 0)
    t = time.time()
    while os.read(fd, s):
        pass
    print(s, time.time() - t)
os.close(fd)
```

Small reads are dominated by syscall cost. The sweet spot usually sits between 4KB and 64KB.

### Step 3: vDSO effect — gettimeofday

```python
import time
N = 1_000_000
t = time.time()
for _ in range(N):
    time.time()         # very fast via vDSO
print('time.time x 1M:', time.time() - t)
```

`time.time()` does not enter the kernel each call. It is served by vDSO from user space, which is why it is fast.

### Step 4: readv/writev to cut syscalls

```python
import os
fd = os.open('out.bin', os.O_WRONLY | os.O_CREAT, 0o644)
os.writev(fd, [b'header\n', b'body\n', b'footer\n'])    # one syscall
os.close(fd)
```

Multiple buffers in one call. Useful for grouped log-line writes and similar patterns.

### Step 5: Restrict syscalls with seccomp

```bash
# Container runtimes apply a default seccomp profile
docker info | grep -i seccomp
# If ENABLED, processes inside containers can call only an allowed set of syscalls
```

From a security standpoint, syscalls are an attack surface. Allowing only what you need shrinks the exploit surface significantly.

## What to Notice in This Code

- Syscall cost is per call; the first optimization is fewer calls via buffering or batching
- Mechanisms like vDSO make equivalent syscalls cheaper
- strace gives the fastest "where is time going" clue when you do not know
- syscall filters like seccomp are a basic security tool

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Tiny reads/writes | Syscall storm | Buffer or batch |
| Open/close in a loop | FD leaks plus cost | Open once and reuse |
| Running strace constantly in production | Performance hit | Sample briefly |
| Assuming time queries are syscalls | Misses vDSO | Measure with real tools |
| Allowing every syscall in a container | Security risk | Keep a seccomp profile |

## How This Shows Up in Production

- High-performance I/O: io_uring batches syscalls
- Databases: writev/sendfile minimize syscall count
- Containers: seccomp plus capabilities limit syscall surface
- Debugging: strace, ltrace, perf analyze at the syscall level
- Monitoring: eBPF gathers syscall traces in real time

## How a Senior Engineer Thinks

When a senior engineer hears about a performance problem, they first check syscall counts and types. That signal often tells you "where time is leaking" faster than CPU or memory graphs. A surprising number of production mysteries are solved by a single strace command.

A senior also treats syscalls as a resource from a security viewpoint. Almost no process needs every syscall. Allowing only the necessary ones via seccomp can shrink the same code's attack surface by a digit. For both performance and security, syscalls are a starting point for optimization.

## Checklist

- [ ] I can describe the difference between user space and kernel space
- [ ] I can read syscall counts with strace
- [ ] I have reduced syscall counts with buffering or batching
- [ ] I know what vDSO is for
- [ ] I know how seccomp contributes to security

## Practice Problems

1. Write the same data using 1B, 4KB, and 64KB chunks. Compare strace counts and times. Summarize the result in one paragraph.

2. Pick a frequently called syscall in your service. Measure with `strace -c` and propose a code change that reduces it.

3. Author a seccomp profile that blocks a specific syscall (e.g., ptrace) in a container, and verify it works.

## Wrap-up and Next Steps

System calls are the only contract between user code and the kernel, and count is cost. Buffering, batching, and vDSO make equivalent operations cheaper, while seccomp narrows the security surface. strace is the fastest tool for finding clues about any OS-level mystery.

The next article looks at how all of these fundamentals are reassembled inside a container.

<!-- toc:begin -->
- [What is an Operating System?](./01-what-is-an-operating-system.md)
- [Processes and Threads](./02-processes-and-threads.md)
- [Scheduling](./03-scheduling.md)
- [Concurrency and Race Conditions](./04-concurrency-and-race-conditions.md)
- [Locks, Mutexes, and Semaphores](./05-locks-mutex-semaphore.md)
- [Memory Management](./06-memory-management.md)
- [Virtual Memory](./07-virtual-memory.md)
- [File Systems](./08-file-systems.md)
- **System Calls (current)**
- Containers and the Operating System (upcoming)
<!-- toc:end -->

## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux strace man page](https://man7.org/linux/man-pages/man1/strace.1.html)
- [Linux syscalls overview](https://man7.org/linux/man-pages/man2/syscalls.2.html)
- [seccomp — Secure Computing Mode](https://man7.org/linux/man-pages/man2/seccomp.2.html)

Tags: Computer Science, Operating Systems, Syscall, Strace, Kernel, User Space
