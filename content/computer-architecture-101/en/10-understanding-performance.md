---
series: computer-architecture-101
episode: 10
title: Understanding Performance
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
  - Computer Architecture
  - Performance
  - Profiling
  - Optimization
  - Measurement
seo_description: A thinking model for performance analysis — throughput vs latency, finding bottlenecks, and the disciplined principles behind every measurement.
last_reviewed: '2026-05-04'
---

# Understanding Performance

> Computer Architecture 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: What does "slow" actually mean? Where, by how much, and how does anyone justify saying a system "needs optimization"?

> Performance problems almost always begin with a guess — "I think the DB is slow," "I think Python is slow." But a senior engineer never changes a line without a measurement. This final article gathers everything we have built up — CPU, memory, cache, I/O, parallelism — into a thinking tool for understanding performance.

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between throughput and latency
- The USE method (Utilization, Saturation, Errors) for finding bottlenecks
- Two kinds of profiling — sampling and instrumentation
- The principles of measurement — no guessing, start small, change one variable at a time

## Why It Matters

Performance is a feature of every system. A faster page keeps more users, an efficient deployment runs on fewer servers, lower latency yields a better user experience. But the word "optimization" gets paired with assumption and aimed at the wrong place. Knuth's "premature optimization is the root of all evil" gets quoted often; what he meant was "do not optimize without measurement."

> An unmeasured optimization is not optimization. It is faith.

## Concept at a Glance

> Performance has two axes — latency (how long one task takes) and throughput (how many tasks per unit of time). They often trade off. To find bottlenecks, the USE method examines utilization, saturation, and errors of each resource (CPU, memory, disk, network). Profiling comes in two flavors — statistical sampling and precise instrumentation — each with its own tradeoffs.

```text
   latency                       throughput
   --------------------          --------------------
   time per single request       requests per unit time
   ms, us                        req/s, MB/s
   user experience               server cost

   v find bottlenecks
   USE method
   +----------+----------+----------+
   | CPU      | Memory   | Disk/Net |
   | Util %   | Used %   | Util %   |
   | Sat: queue| Sat: swap| Sat: queue|
   | Errors   | OOM      | I/O err  |
   +----------+----------+----------+
```

## Key Terms

| Term | Description |
| --- | --- |
| Latency | Time from start to completion of one task |
| Throughput | Tasks completed per unit time |
| p99 | The slowest of 100 — the tail latency |
| USE | Utilization / Saturation / Errors |
| Sampling profiler | Periodically captures the call stack |
| Instrumentation | Adds measurement code at function boundaries |

## Before / After

**Before — optimization by guess:**

```python
# "Python must be slow" so it gets ported to Cython
# The real bottleneck was an N+1 SQL query
def slow_endpoint(user_ids):
    users = []
    for uid in user_ids:
        users.append(db.query("SELECT * FROM users WHERE id = ?", uid))
    return users
```

**After — fix the real bottleneck after measuring:**

```python
# Profiler shows SQL spending 95% of the time
def fast_endpoint(user_ids):
    return db.query(
        "SELECT * FROM users WHERE id IN (?)",
        user_ids,
    )   # one query, 100x faster
```

Same code, same result, but seeing the real bottleneck makes a 100x difference. Optimization without measurement often makes the wrong place faster while leaving the bottleneck in place.

## Hands-on: Step by Step

### Step 1: Measure latency and throughput

```python
import time

def task():
    return sum(i * i for i in range(10_000))

# Latency: time per call
start = time.time()
task()
print(f"latency: {(time.time()-start)*1000:.2f}ms")

# Throughput: how many in 1 second
end = time.time() + 1.0
count = 0
while time.time() < end:
    task()
    count += 1
print(f"throughput: {count} req/s")
```

Optimizations that lower latency are often different from those that raise throughput. Decide which one matters first.

### Step 2: Look at p50/p95/p99

```python
import time, random

def variable_task():
    time.sleep(random.uniform(0.001, 0.020))   # 1-20ms

samples = []
for _ in range(1000):
    start = time.time()
    variable_task()
    samples.append((time.time() - start) * 1000)

samples.sort()
def pct(p): return samples[int(len(samples) * p / 100)]
print(f"p50={pct(50):.2f}ms  p95={pct(95):.2f}ms  p99={pct(99):.2f}ms")
print(f"max={samples[-1]:.2f}ms")
```

Averages lie. What users actually feel is the tail — p95 and p99. That is why every SLA is defined by tails, not means.

### Step 3: Find the real bottleneck with cProfile

```python
import cProfile, pstats

def heavy():
    total = 0
    for i in range(100_000):
        total += sum(j for j in range(100))
    return total

profiler = cProfile.Profile()
profiler.enable()
heavy()
profiler.disable()

stats = pstats.Stats(profiler).sort_stats("cumulative")
stats.print_stats(10)
```

Trust the profiler over your intuition. When the first result surprises you, your intuition is most likely wrong.

### Step 4: Imitate the USE method

```python
import psutil

def use_snapshot(label):
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    print(f"[{label}] CPU util: {cpu:.1f}%   Mem used: {mem:.1f}%")

use_snapshot("idle")
data = [i * i for i in range(10_000_000)]
use_snapshot("after work")
```

Real systems use vmstat, iostat, top for the same job. The point is to find which resource hit its limit first.

### Step 5: Single-variable controlled benchmark

```python
import time

def benchmark(name, fn, runs=5):
    times = []
    for _ in range(runs):
        start = time.time()
        fn()
        times.append(time.time() - start)
    times.sort()
    print(f"{name:20s} median={times[len(times)//2]*1000:.2f}ms")

def loop_method():
    out = []
    for i in range(100_000):
        out.append(i * i)
    return out

def comprehension_method():
    return [i * i for i in range(100_000)]

benchmark("for-append", loop_method)
benchmark("comprehension", comprehension_method)
```

Change one variable at a time so the result is trustworthy. Cache warming, garbage collection, and JIT add noise; that is why we run several iterations and take the median.

## What to Notice in This Code

- Latency and throughput are distinct metrics that need different strategies
- Look at tail latency (p95, p99), not just averages
- Trust profiler results more than intuition
- Use USE to systematically check each resource for saturation

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Optimizing without measurement | Time spent in the wrong place | Profile first |
| Looking at averages only | Users churn at p99 | Look at the whole distribution |
| One measurement, one conclusion | Noise and cache effects ignored | Repeat and take the median |
| Changing several variables at once | Cannot tell what helped | Change one at a time |
| No regression benchmarks | Next PR makes it slow again | Automate benchmarks |

## How This Shows Up in Production

- APM tools: Datadog, New Relic gather USE metrics automatically
- Database tuning: combine query plans with cache hit rates
- Game development: identify hitches with frame-time distributions
- Distributed systems: tail latency dominates the SLA
- Compilers: regression benchmarks guard performance

## How a Senior Engineer Thinks

A senior engineer first asks "do we have measurement data?" Without data, the discussion does not start. It would slide into theory and become an endless guessing game. Even a tiny benchmark, brought to the meeting, is the mark of a good team's culture.

A senior also asks "why is it slow?" before "where is it slow?" The same slow function caused by CPU, memory, disk, or lock pressure needs different treatment. Everything we have built up in this series — CPU cycles, the cache hierarchy, I/O cost, concurrency models — becomes the toolkit for that diagnosis. The biggest difference between an engineer who knows computer architecture and one who does not shows up exactly here.

## Checklist

- [ ] You can describe latency vs throughput
- [ ] You look at tail latency, not just averages
- [ ] You have used cProfile, perf, or py-spy
- [ ] You can use USE to find resource bottlenecks
- [ ] You can write a single-variable controlled benchmark

## Practice Problems

1. Pick a function you use often, profile it with cProfile, and check whether the most expensive function matches your prior expectation.

2. Send 1000 requests to any web API and measure p50, p95, p99, and max. Note how far the average is from p99.

3. Compare two implementations of the same algorithm with single-variable controlled benchmarks. Report median and standard deviation across 5 runs.

## Wrap-up and Next Steps

Performance starts with measurement. Distinguish latency from throughput, watch the tail, find bottlenecks with USE, and validate with controlled benchmarks. Everything in this series — from data representation to multicore — is, in the end, a tool for performance diagnosis.

This concludes the Computer Architecture 101 series. The next series builds on it: how the operating system layers its abstractions on top of this hardware. Once you know the architecture, every system call and scheduling choice in an OS looks different.

<!-- toc:begin -->
- [What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [CPU and Instructions](./03-cpu-and-instructions.md)
- [Registers and the ALU](./04-registers-and-alu.md)
- [Memory Organization](./05-memory-organization.md)
- [Cache and Locality](./06-cache-and-locality.md)
- [Pipelining](./07-pipelining.md)
- [I/O and Devices](./08-io-and-devices.md)
- [Parallelism and Multicore](./09-parallelism-and-multicore.md)
- **Understanding Performance (current)**
<!-- toc:end -->

## References

- [Wikipedia — Profiling (computer programming)](https://en.wikipedia.org/wiki/Profiling_(computer_programming))
- [Brendan Gregg — The USE Method](https://www.brendangregg.com/usemethod.html)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [Donald Knuth — Structured Programming with go to Statements (1974)](https://dl.acm.org/doi/10.1145/356635.356640)

Tags: Computer Science, Computer Architecture, Performance, Profiling, Optimization, Measurement
