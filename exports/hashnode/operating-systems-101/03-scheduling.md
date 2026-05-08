
# Scheduling

> Operating Systems 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: Hundreds of processes are alive on your machine. How does the OS decide who gets the next millisecond of CPU?

> The scheduler is one of the most frequently invoked parts of the OS. Every few milliseconds it picks "who runs next?" and that choice shapes responsiveness, throughput, fairness, and power. This article walks through why a scheduler exists, the policies it uses, and why context switch cost keeps showing up in performance discussions.

<!-- a-grade-intro:end -->

## What You Will Learn

- The scheduler's goals and the trade-offs between them
- Major policies (FCFS, RR, Priority, MLFQ, CFS)
- What a context switch is and what it costs
- Knobs you can turn — `nice`, priority, CPU affinity

## Why It Matters

The scheduler is invisible until things slow down or jitter. Why does the system feel sluggish when CPU is idle? Why do identical runs take different times? Why did a container suddenly get sluggish after we set a CPU limit? The answers usually come back to the scheduler's decisions.

> Responsiveness, throughput, fairness, and power — the scheduler cannot maximize all four at once. Push one and another gives.

## Concept at a Glance

> The scheduler picks a runnable task from a queue and puts it on the CPU. It is invoked again whenever a task blocks on I/O, exhausts its time slice, or is preempted by a higher-priority task waking up.

```text
Runnable queue        Running              Blocked (waiting I/O)
+--------------+      +----------+         +-------------------+
| T1, T3, T5   | ---> |   T2     |         |  T4 (read)        |
+--------------+      +----------+         |  T6 (sleep)       |
       ^                   |               +-------------------+
       |                   v
       +-- preempt /  time slice expires --+
                           |
                           +--> back to runnable queue
```

## Key Terms

| Term | Description |
| --- | --- |
| Context switch | Saving one task's CPU state and restoring another's |
| Time slice | The chunk of CPU a preemptive scheduler hands to one task at a time |
| Priority | The weight that decides who runs first or more often |
| `nice` | A user-tunable priority hint on Linux (lower is more aggressive) |
| CFS | Linux's Completely Fair Scheduler, dividing virtual time fairly |

## Before / After

**Before — "the OS will share things fairly":**

```bash
# Run four heavy background tasks at once
./heavy_task & ./heavy_task & ./heavy_task & ./heavy_task &
```

Will they finish at the same time? Will one starve another? How does this affect interactive responsiveness? Guessing will not tell you.

**After — "you can track each task's state and time":**

```text
T1: ran 50ms -> time slice expired -> back to runnable
T2: blocked on I/O -> data arrived -> runnable again
T3: high priority -> preempts T2 the moment it wakes up
T4: nice +10 -> gets less of the shared CPU
```

The scheduler makes thousands of decisions like this per second.

## Hands-on: Step by Step

### Step 1: Count context switches

```bash
/usr/bin/time -v python3 -c "
import threading
def loop():
    for _ in range(10**6): pass
ts = [threading.Thread(target=loop) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
" 2>&1 | grep -E "context switches"
```

You will see voluntary (the task yielded) and involuntary (the scheduler preempted) counts. Their ratio hints at how loaded the system is.

### Step 2: Adjust priority with `nice`

```bash
# Default priority
nice -n 0  python3 -c "x=0
for _ in range(10**8): x+=1" &
# Lower priority
nice -n 19 python3 -c "x=0
for _ in range(10**8): x+=1" &
wait
```

In `top` or `htop` you can compare CPU shares. The `nice 19` task only gets the slack the other one leaves.

### Step 3: Pin to a specific core with affinity

```bash
# Run only on CPU 0
taskset -c 0 python3 my_workload.py
# Inspect the affinity mask
taskset -p $(pgrep -f my_workload.py)
```

CPU affinity is used to keep cache locality high or to protect a core from competing work.

### Step 4: Watch per-thread state

```bash
# All threads of a PID, refreshed once per second
ps -L -p <PID> -o pid,tid,stat,wchan,comm
```

`stat` shows `R` (runnable/running), `S` (sleeping), or `D` (uninterruptible disk wait). Looking at the distribution often points straight to a culprit.

### Step 5: Switch to a real-time policy

```bash
# Inspect current policy
chrt -p $(pgrep -f my_workload.py)
# Switch to round-robin real-time (root required)
sudo chrt -r -p 50 $(pgrep -f my_workload.py)
```

Linux supports SCHED_FIFO and SCHED_RR alongside the default SCHED_OTHER (CFS). They are powerful but can ruin overall responsiveness; use them only when real-time guarantees are truly needed.

## What to Notice in This Code

- Context switches are not free, even when they look invisible (typically a few microseconds)
- `nice` is a hint, not an absolute priority
- Distinguishing `S`, `D`, and `R` is decisive when debugging
- Real-time policies are powerful but can starve everything else

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Reading only CPU% | Misses context switches and wait time | Combine `vmstat` and `pidstat` |
| Assuming more threads is always faster | Excessive context switches make it slower | Tune around core count and measure |
| Believing `nice -n -20` magically helps | Starves siblings, destabilizes system | Use sparingly and measure |
| Ignoring container CPU limits | cgroup throttling tanks responsiveness | Know `cpu.cfs_quota_us` etc. |
| Trying to `kill` `D`-state processes | Signal does not arrive; they linger | Fix the underlying disk/network cause |

## How This Shows Up in Production

- Container ops: Kubernetes CPU request/limit maps to cgroup scheduler controls
- Database tuning: I/O wait vs CPU usage ratio identifies the bottleneck
- Games and audio: latency-sensitive threads run at real-time priorities
- Background jobs: ETL workers are `nice`'d down to protect interactive paths
- Laptop power: scheduler cooperates with frequency scaling for battery and speed

## How a Senior Engineer Thinks

A senior engineer hearing "it is slow" does not ask only "is CPU 100%?" Worse than 100% CPU is 50% CPU with hundreds of thousands of context switches per second. Senior people reach for `vmstat`, `pidstat`, and `perf sched` and look at the system from the scheduler's point of view.

A senior also treats the scheduler as a collaborator. Code that does small bursts and yields often makes the scheduler's life easy. Code that holds locks for a long time or blocks signals defeats it. Smooth latency comes as much from code patterns as from policy settings.

## Checklist

- [ ] You can name the four scheduler goals
- [ ] You know roughly how expensive a context switch is
- [ ] You can distinguish `nice`, priority, and affinity
- [ ] You can read `R`/`S`/`D` and act on them
- [ ] You have a sense of how container CPU limits map to the scheduler

## Practice Problems

1. Run `vmstat 1` for 10 seconds and average the `cs` column. Then start a heavy build in the background and repeat. Compare the two averages.

2. Run the same Python script as both `nice -n 0` and `nice -n 19` simultaneously. Watch CPU% in `top` for one minute. Note how the difference changes when the system goes from idle to busy.

3. Write a script with 8 CPU-bound threads. Run it with `taskset -c 0` and again without affinity. Compare the times. If the result surprises you, explain why.

## Wrap-up and Next Steps

The scheduler picks the next CPU runner from the runnable queue. The decision balances responsiveness, throughput, fairness, and power, and context switches are the cost of executing it. Knobs like `nice` and affinity let you nudge it, but the scheduler also depends on well-behaved code.

The next article looks at what happens when several flows touch the same data at once: race conditions. Knowing when the scheduler can interrupt a flow makes it obvious why these bugs are everywhere.

- [What Is an Operating System?](./01-what-is-an-operating-system.md)
- [Processes and Threads](./02-processes-and-threads.md)
- **Scheduling (current)**
- Concurrency and Race Conditions (upcoming)
- Locks, Mutexes, and Semaphores (upcoming)
- Memory Management (upcoming)
- Virtual Memory (upcoming)
- File Systems (upcoming)
- System Calls (upcoming)
- Containers and the Operating System (upcoming)
## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux Kernel Documentation — Scheduler](https://www.kernel.org/doc/html/latest/scheduler/index.html)
- [Brendan Gregg — Linux Performance](https://www.brendangregg.com/linuxperf.html)
- [LWN — The CFS scheduler](https://lwn.net/Articles/230501/)

Tags: Computer Science, Operating Systems, Scheduling, CPU, Systems, Performance

---

© 2026 YeongseonBooks. All rights reserved.
