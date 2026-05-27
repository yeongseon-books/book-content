---
series: operating-systems-101
episode: 8
title: "Operating Systems 101 (8/10): File Systems"
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
  - File Systems
  - Inode
  - Fsync
  - Journaling
seo_description: Inodes, the directory tree, the page cache, fsync, and journaling — how the file system makes sure your data survives a crash.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (8/10): File Systems

Calling `write()` does not mean your data is safe yet. Between the page cache, the journal, the disk cache, and the storage device itself, there are several layers where a crash can still turn "saved" into "partially written" or "gone."

That is why storage bugs are rarely about syntax. They are about knowing exactly which guarantee the file system is making at each step.

This is the 8th post in the Operating Systems 101 series. It explains inode lookup, page cache behavior, fsync, journaling, and the atomic rename pattern used in real systems.


![operating systems 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.en.png)
*operating systems 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying File Systems?
- Which signal should the example or diagram make visible for File Systems?
- What failure should be prevented first when File Systems reaches a real system?

## Questions this article answers

- How do inodes and directory entries represent a file?
- What do the page cache and `fsync` each guarantee?
- What kinds of recovery does journaling make possible after a crash?
- Why is the atomic rename pattern so common when saving configuration files?

## What You Will Learn

- The structure of inodes and the directory tree
- The roles of the page cache and fsync
- How journaling provides crash safety
- Concurrent writes and the atomic rename pattern

## Why It Matters

Half of all data-loss incidents trace back to "we did not call fsync" or "we assumed rename was atomic when it was not." Without a model of file-system behavior, the same code mysteriously works on one host and loses data on another. Reliable storage comes not from clever code but from precisely using the promises the system actually makes.

> The file system is a spectrum from "slow but safe" to "fast but risky," and choosing where to sit is a developer's decision.

> A file is a combination of an inode (metadata) and data blocks. A directory is just a mapping from name to inode number. write() typically lands in the page cache, and the data hits disk later. fsync is the call that asks the OS to push it to disk now.

### The path from write to durable storage

```text
path: /var/log/app.log
   ↓ directory lookup
 inode #1234 (metadata: perms, size, block pointers)
   ↓
 data blocks → [page cache] → fsync → [disk]
```

## Key Terms

| Term | Description |
| --- | --- |
| Inode | File metadata (owner, perms, block locations) |
| Page cache | RAM that caches disk blocks |
| Fsync | Call that forces dirty changes down to disk |
| Journaling | Record changes before applying so a crash is safe |
| Atomic rename | Within one file system, rename is atomic |

## Before / After

**Before — "I called write, so it is safe":**

```python
with open('config.json', 'w') as f:
    f.write(new_config)
# What if the power dies here? You may end up with an empty or partial file
```

**After — "atomic rename pattern":**

```python
import os, tempfile, json

def save_atomic(path, data):
    d = os.path.dirname(path) or '.'
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)   # atomic rename within the same FS
```

No matter where the crash happens, `path` is either the old content intact or the complete new content.

## Hands-on: Step by Step

### Step 1: Inodes and hard links

```bash
echo hi > a.txt
ln a.txt b.txt
ls -li a.txt b.txt
# Same inode number — two names, one underlying object
```

A directory entry is a name-to-inode pointer. A hard link adds another name to the same inode.

### Step 2: Page cache effect

```bash
# First read goes to disk; second comes from cache
dd if=/dev/zero of=big.bin bs=1M count=100
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches    # clear caches
time wc -c big.bin    # cold (slow)
time wc -c big.bin    # warm (fast)
```

Same file, same command — if the timings differ by a large factor, the page cache is doing its job.

### Step 3: Measure the cost of fsync

```python
import os, time

def write_n(n, do_sync):
    with open('t.bin', 'wb') as f:
        for _ in range(n):
            f.write(b'x' * 4096)
            if do_sync:
                f.flush(); os.fsync(f.fileno())

t = time.time(); write_n(1000, False); print('no sync', time.time()-t)
t = time.time(); write_n(1000, True);  print('with sync', time.time()-t)
```

fsync waits for the disk every time, which can be tens to hundreds of times slower. That is why databases use group commit.

### Step 4: Implement atomic rename yourself

Run the "After" code above and verify that even if you raise an exception in the middle, the original file is untouched.

### Step 5: Concurrent writes to one file

```python
import threading

def write_lines(name, n):
    with open('shared.log', 'a') as f:
        for i in range(n):
            f.write(f'{name} {i}\n')

ts = [threading.Thread(target=write_lines, args=(f't{i}', 100)) for i in range(4)]
for t in ts: t.start()
for t in ts: t.join()

# Lines may interleave — append does not give per-line atomicity
```

POSIX promises atomicity for small appends, but record framing is the application's responsibility.

## What to Notice in This Code

- write only reaches the page cache; disk is safe only after fsync
- Atomic rename is the simplest and strongest data-safety pattern
- Page cache makes the second access dramatically faster
- Concurrent appends do not automatically give line-level atomicity

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Forgetting fsync | Loss on crash | Call fsync for important changes |
| Overwriting the target file directly | Risk of partial write | Temp file plus atomic rename |
| Renaming across file systems | Atomicity broken | Rename only within the same FS |
| fsync on every write | Throughput collapse | Group commit or batching |
| Assuming append is always atomic | Interleaved lines | Explicit lock or queue |

## How This Shows Up in Production

- Databases: WAL plus group commit get safety and throughput together
- Config files: atomic rename for hot reloads without downtime
- Logs: one file per worker, or syslog, to dodge concurrent writes
- Containers: overlayfs builds layered file systems
- Backups: hard links enable increment-only snapshots

## How a Senior Engineer Thinks

A senior engineer is always conscious of the boundary between memory and disk. Page cache, OS, disk cache, disk media — data sitting in each layer carries a different kind of risk. If you cannot say which layer your data has reached, the system cannot honestly claim to "store" it.

A senior also treats small patterns like atomic rename as default code-review tools. Data safety comes less from grand systems than from consistent use of small patterns. That use is not "always be slow" but a deliberate choice of "fast here, safe there."

## Checklist

- [ ] I can describe the relationship between inodes and directory entries
- [ ] I know the difference between write and fsync
- [ ] I can write the atomic rename pattern from memory
- [ ] I know how the page cache changes apparent timing
- [ ] I know what atomicity concurrent writes do and do not guarantee

## Practice Problems

1. Measure throughput with and without fsync. Explain in one paragraph why they differ.

2. Build a config save function using atomic rename. Verify the original is intact even if you raise mid-way.

3. Have four threads append to the same log file. See whether lines interleave and write up the result.

## Wrap-up and Next Steps

A file system is not "write and you are done." Page cache, fsync, and atomic rename are promises that must be used precisely. Where you sit on the spectrum from fast to safe is a deliberate developer choice.

The next article moves on to the way your code actually invokes everything we have seen so far — system calls.

## Answering the Opening Questions

- **What boundary should you inspect first when applying File Systems?**
  - The article treats File Systems as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for File Systems?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when File Systems reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Operating Systems 101 (1/10): What Is an Operating System?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): Processes and Threads](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): Scheduling](./03-scheduling.md)
- [Operating Systems 101 (4/10): Concurrency and Race Conditions](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): Locks, Mutexes, and Semaphores](./05-locks-mutex-semaphore.md)
- [Operating Systems 101 (6/10): Memory Management](./06-memory-management.md)
- [Operating Systems 101 (7/10): Virtual Memory](./07-virtual-memory.md)
- **File Systems (current)**
- System Calls (upcoming)
- Containers and the Operating System (upcoming)

<!-- toc:end -->

## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux fsync(2) man page](https://man7.org/linux/man-pages/man2/fsync.2.html)
- [PostgreSQL — Reliability and the Write-Ahead Log](https://www.postgresql.org/docs/current/wal-reliability.html)
- [LWN — Ensuring data reaches disk](https://lwn.net/Articles/457667/)

Tags: Computer Science, Operating Systems, File Systems, Inode, Fsync, Journaling
