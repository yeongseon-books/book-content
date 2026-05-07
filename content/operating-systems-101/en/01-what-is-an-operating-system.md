---
series: operating-systems-101
episode: 1
title: What Is an Operating System?
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
  - Systems
  - Foundations
  - Kernel
  - Abstraction
seo_description: How an operating system manages hardware and exposes clean abstractions like processes, files, and sockets to application code.
last_reviewed: '2026-05-04'
---

# What Is an Operating System?

> Operating Systems 101 series (1/10)

<!-- a-grade-intro:begin -->

**Core question**: How do all the programs on a single computer coexist without trampling each other's CPU, memory, and files?

> An operating system (OS) sits between hardware and applications. It coordinates how CPU, memory, disks, and the network are shared, and it wraps raw hardware in clean abstractions like processes, files, and sockets that application code can use. This series follows both roles end to end and explains the machinery that you depend on every day but rarely see.

<!-- a-grade-intro:end -->

## What You Will Learn

- A working definition of an operating system and its two main roles
- The difference between user mode and kernel mode
- The core abstractions an OS provides — process, virtual memory, file, socket
- Why every developer benefits from understanding the OS

## Why It Matters

The OS is invisible until something breaks. Out-of-memory kills, zombie processes, file-descriptor leaks, slow disks, blocked sockets — almost every production incident is, at its root, a conversation gone wrong with the OS. With a mental model of the OS, error messages stop being vague "system errors" and become traceable signals.

> Your application sits on the OS, the OS sits on the hardware. If you do not know the cost of crossing those boundaries, you cannot reason about performance or stability.

## Concept at a Glance

> The OS is the software layer between user programs and hardware. Above, it exposes a small, simple interface to applications through system calls. Below, it talks directly to hardware via schedulers, memory managers, file systems, and device drivers.

```text
+---------------------------------------------+
|  Application (Python, Browser, IDE, ...)    |
+---------------------------------------------+
|  System Call Interface  (read, write, ...)  |
+---------------------------------------------+
|  Kernel                                     |
|   - Process scheduler                       |
|   - Memory manager                          |
|   - File systems / VFS                      |
|   - Network stack                           |
|   - Device drivers                          |
+---------------------------------------------+
|  Hardware (CPU, RAM, Disk, NIC, ...)        |
+---------------------------------------------+
```

## Key Terms

| Term | Description |
| --- | --- |
| Kernel | The core of the OS, the only code with direct hardware access |
| User mode | Restricted privilege level where ordinary applications run |
| System call | The defined entry point applications use to ask the kernel for work |
| Process | The OS abstraction for a running program (memory plus CPU time) |
| Device driver | A module that wraps a specific piece of hardware behind an OS interface |

## Before / After

**Before — "the OS just turns the computer on":**

```python
with open("data.txt") as f:
    print(f.read())
```

For these three lines to run, something has to find which disk blocks hold `data.txt`, send commands to the disk controller, copy the data into RAM, and map that memory so our process can read it.

**After — "the OS is working on every line":**

```text
open()  -> system call -> kernel walks the file system, finds the inode
                       -> hands a file descriptor back to user space
read()  -> system call -> queues an I/O request to the disk driver
                       -> data flows: kernel buffer -> user buffer
print() -> system call (write to stdout)
                       -> handed to the terminal device driver
```

A three-line Python program is really a sequence of system calls.

## Hands-on: Step by Step

### Step 1: Trace the system calls

```bash
# Linux: see exactly which syscalls one Python line triggers
strace -e trace=openat,read,write,close \
    python3 -c "open('data.txt').read()"
```

You will see lines like `openat(AT_FDCWD, "data.txt", O_RDONLY) = 3`. The `3` is a file descriptor handed back by the kernel; the actual disk work is done inside it.

### Step 2: Measure user time vs system time

```bash
/usr/bin/time -v python3 -c "
with open('/etc/hosts') as f:
    for _ in range(100000):
        f.seek(0); f.read()
" 2>&1 | grep -E "User time|System time"
```

`User time` is what your code spent in user mode; `System time` is what the kernel spent on your behalf. I/O-heavy programs push more time into the second bucket.

### Step 3: Inspect what the OS gave your process

```python
import os, resource

print(f"PID                  : {os.getpid()}")
print(f"Parent PID           : {os.getppid()}")
print(f"Open file limit      : {resource.getrlimit(resource.RLIMIT_NOFILE)}")
print(f"Virtual memory limit : {resource.getrlimit(resource.RLIMIT_AS)}")
```

Your PID is the OS-assigned identity. The fd and memory limits are caps the OS enforces. You live within the budget the OS gives you.

### Step 4: Look at how the kernel sees you via `/proc`

```bash
# Kernel-side view of this process
cat /proc/self/status | head -20
# File descriptors currently open
ls -l /proc/self/fd
```

On Linux, `/proc` is a virtual file system that exposes kernel data as files. The kernel knows everything about your process: state, memory usage, open files, threads.

### Step 5: Imagine a world without an OS

```text
[No OS]                              [With OS]
- Apps poke disk sectors directly    - open()/read() abstract files
- Apps overwrite each other's RAM    - virtual memory isolates them
- One app monopolizes the CPU         - scheduler shares CPU time
- Each app ships device-specific code - drivers expose one interface
```

The value of the OS is the gap between these two columns. Everything that "just works" in normal operation rests on these abstractions.

## What to Notice in This Code

- File operations are sequences of system calls, not magic
- Crossing the user/kernel boundary has a real cost
- Each process gets a budget; the OS enforces it
- Virtual file systems like `/proc` and `/sys` let you talk to the kernel

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Treating the OS as a boot loader | Cannot debug system issues | Think of the OS as a resource manager |
| Ignoring user/kernel transition cost | Many small syscalls slow code down | Buffer and batch work |
| Assuming unlimited file descriptors | "Too many open files" errors | Know your rlimits and close handles |
| Assuming all OSes behave the same | Linux code that breaks on Windows | Learn the syscall differences |
| Treating errors as opaque failures | Lost debugging information | Read errno and the syscall man pages |

## How This Shows Up in Production

- Backend operations: `top`, `htop`, `iostat` interpret OS-level resource numbers
- Container debugging: `strace` from inside a container to follow syscalls
- Security: `auditd` watches syscall patterns from suspicious processes
- Performance: epoll and io_uring exploit OS-provided async I/O
- Embedded and IoT: small OSes like FreeRTOS and Zephyr are chosen and tuned by hand

## How a Senior Engineer Thinks

A senior engineer reads application code and constantly asks "what is this code asking the OS to do?" — which lines are system calls, whether they block or are async, how much resource they hold and for how long. With that overlay you can quickly narrow down memory leaks, disk saturation, and runaway context switches.

A senior also treats the OS as a collaborator, not as a fixed runtime. Kernel parameters, fd limits, scheduler policy, and page cache behavior are all knobs. Production performance and stability are decided as much by these knobs as by the application code itself.

## Checklist

- [ ] You can describe the OS's two roles (resource manager and abstraction provider)
- [ ] You can explain user mode versus kernel mode
- [ ] You know what a system call is and why it costs something
- [ ] You can talk to the OS using `strace` or `/proc`
- [ ] You sense that OS resources are bounded but tunable

## Practice Problems

1. Run `strace -c python3 your_script.py` on something you wrote. Make a small table of the top three syscalls by count and explain in one paragraph what each one does.

2. Check your file-descriptor limit with `ulimit -n`. Write a small Python script that opens files in a loop until it hits the limit. Note exactly what error appears.

3. Read three fields from `/proc/self/status` — VmRSS, Threads, State — and write a one-line explanation of each in your own words.

## Wrap-up and Next Steps

An operating system is the software layer that manages hardware on behalf of applications and gives them clean abstractions to work with. The split between user mode and kernel mode, the system call as a defined boundary, and the process as the basic abstraction — these three ideas are the entry point to OS thinking.

The next article zooms into the most fundamental abstraction: the process. We look at what a process actually contains, how a thread differs from a process, and how new processes are born.

<!-- toc:begin -->
- **What Is an Operating System? (current)**
- Processes and Threads (upcoming)
- Scheduling (upcoming)
- Concurrency and Race Conditions (upcoming)
- Locks, Mutexes, and Semaphores (upcoming)
- Memory Management (upcoming)
- Virtual Memory (upcoming)
- File Systems (upcoming)
- System Calls (upcoming)
- Containers and the Operating System (upcoming)
<!-- toc:end -->

## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Silberschatz, Galvin, Gagne — Operating System Concepts](https://www.os-book.com/)
- [Linux man-pages project](https://man7.org/linux/man-pages/)
- [The Linux Programming Interface — Michael Kerrisk](https://man7.org/tlpi/)

Tags: Computer Science, Operating Systems, Systems, Foundations, Kernel, Abstraction
