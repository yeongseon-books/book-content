---
series: computer-architecture-101
episode: 7
title: "Computer Architecture 101 (7/10): Pipelining"
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
  - Computer Architecture
  - Pipelining
  - Branch Prediction
  - Performance
  - CPU
seo_description: How CPU pipelining lets one instruction complete per cycle on average, what hazards stall it, and why branch prediction changed the game.
last_reviewed: '2026-05-04'
---

# Computer Architecture 101 (7/10): Pipelining

> Computer Architecture 101 series (7/10)

**Core question**: An instruction takes five stages to process, yet on average a CPU completes one instruction per cycle. How is that possible?

> A CPU pipeline is the same idea as a car assembly line. Processing one instruction takes several stages, but if you overlap stages so different instructions occupy them at the same time, throughput rises by the number of stages. The enemies of this trick are branches, data dependencies, and memory latency — and branch prediction is the most interesting weapon in that fight.

This is the 7th post in the Computer Architecture 101 series.


![computer architecture 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/07/07-01-big-picture.en.png)
*computer architecture 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Pipelining?
- Which signal should the example or diagram make visible for Pipelining?
- What failure should be prevented first when Pipelining reaches a real system?

## What You Will Learn

- The pipeline stages and the throughput concept
- Data, control, and structural hazards
- How branch prediction works and the cost of misprediction
- Patterns for writing pipeline-friendly code

## Why It Matters

Modern CPUs have pipelines 14 stages deep or more, and superscalar designs can finish multiple instructions per cycle. But a single branch misprediction flushes the pipeline and refills it, costing 10–20 cycles. Reducing or making predictable the branches in a hot loop is a small optimization that compounds.

> Pipelining makes the average fast, but a single misprediction breaks that average.

> In a 5-stage pipeline (Fetch, Decode, Execute, Memory, Writeback), five instructions are in flight every cycle. One instruction takes 5 cycles end-to-end, but throughput is one instruction per cycle. When a branch fires, the wrongly fetched instructions are discarded and fetching restarts.

```text
cycle:        1    2    3    4    5    6    7
instr 1:      F    D    E    M    W
instr 2:           F    D    E    M    W
instr 3:                F    D    E    M    W
instr 4:                     F    D    E    M
instr 5:                          F    D    E
```

## Key Terms

| Term | Description |
| --- | --- |
| Pipeline | Overlapping instruction stages by stage |
| Hazard | A condition that stalls or breaks the pipeline |
| Data hazard | Next instruction waits on the previous result |
| Control hazard | Branch creates uncertainty about what to fetch |
| Branch prediction | Guess which way a branch will go |
| Stall | A pipeline cycle with no useful work |

## Before / After

**Before — branch-heavy code:**

```python
def count_positive(arr):
    count = 0
    for x in arr:
        if x > 0:           # ~50% mispredict on random data
            count += 1
    return count
```

**After — replace the branch with arithmetic:**

```python
def count_positive_branchless(arr):
    return sum((x > 0) for x in arr)   # bool->int, no branch
```

Arithmetic always follows the same instruction stream, so the pipeline does not stall. From the CPU's view, the best branch is no branch, and the second best is a predictable branch.

## Hands-on: Step by Step

### Step 1: Sorted vs random data and branch cost

```python
import time, numpy as np

N = 10_000_000
sorted_data = np.sort(np.random.randint(-100, 100, N))
random_data = np.random.randint(-100, 100, N)

def count_positive(arr):
    c = 0
    for x in arr:
        if x > 0:
            c += 1
    return c

start = time.perf_counter(); count_positive(sorted_data)
print(f"sorted:   {time.perf_counter() - start:.2f} s")

start = time.perf_counter(); count_positive(random_data)
print(f"random:   {time.perf_counter() - start:.2f} s")
```

Same function, same size. Sorted data hits the predictor almost every time; random data misses about half. The effect is more dramatic in C or Rust.

### Step 2: A pipeline simulator

```python
def pipeline(instructions, stages=("F", "D", "E", "M", "W")):
    """Each instruction advances one stage per cycle."""
    n_inst = len(instructions)
    total_cycles = n_inst + len(stages) - 1
    grid = [[" " for _ in range(total_cycles)] for _ in range(n_inst)]
    for i in range(n_inst):
        for s, name in enumerate(stages):
            grid[i][i + s] = name
    return grid

for row in pipeline(["I1", "I2", "I3", "I4"]):
    print("".join(row))
```

The output shows instructions shifted one stage at a time. Throughput is one instruction per cycle, but a single branch breaks that flow.

### Step 3: Model a data hazard

```python
class HazardCheck:
    """ADD R3, R1, R2 followed by ADD R4, R3, R5 must wait for R3."""
    @staticmethod
    def has_data_hazard(prev, curr):
        return prev["dst"] in curr["src"]

a = {"dst": "R3", "src": ("R1", "R2")}
b = {"dst": "R4", "src": ("R3", "R5")}   # depends on R3
c = {"dst": "R6", "src": ("R7", "R8")}

print(HazardCheck.has_data_hazard(a, b))   # True
print(HazardCheck.has_data_hazard(a, c))   # False
```

Data hazards are usually solved by forwarding (passing the EX result directly), but a load followed by a dependent op still incurs a one-cycle stall.

### Step 4: A branch predictor simulator

```python
class BranchPredictor:
    """Simple 2-bit saturating counter."""
    def __init__(self):
        self.state = 2   # 0:strong NT, 1:weak NT, 2:weak T, 3:strong T

    def predict(self):
        return self.state >= 2

    def update(self, taken):
        if taken and self.state < 3: self.state += 1
        if not taken and self.state > 0: self.state -= 1

bp = BranchPredictor()
sequence = [True, True, True, False, True, True, False, True]
hits = 0
for actual in sequence:
    pred = bp.predict()
    hits += (pred == actual)
    bp.update(actual)
print(f"hit rate: {hits}/{len(sequence)}")
```

A 2-bit predictor is simple but achieves 95%+ on branches that almost always go the same way. On random branches it sinks toward 50%.

### Step 5: Branchless patterns

```python
def abs_with_branch(x):
    if x < 0:
        return -x
    return x

def abs_branchless(x):
    mask = x >> 31    # -1 if negative, 0 if positive
    return (x ^ mask) - mask

print(abs_with_branch(-7), abs_branchless(-7))
print(abs_with_branch(5), abs_branchless(5))
```

Patterns that produce the same result without branching can drive misprediction cost to zero in hot loops. They trade readability for speed, so introduce them only after measurement justifies it.

## What to Notice in This Code

- Deeper pipelines mean better throughput but higher misprediction cost
- Branch prediction is great on patterned branches and weak on random ones
- Forwarding handles most data dependencies; load-use stalls remain
- Branchless code is faster but less readable

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Random branches in hot loops | Misprediction explosion | Use arithmetic or masking |
| Ignoring data sort order | Irregular branch patterns | Consider sorting first |
| Deep call chains | Branches and indirect calls accumulate | Inline or flatten |
| Confusing `if x` and `if x > 0` | Wrong comparison | Use explicit comparisons |
| Branchless code without measurement | Loses readability with no gain | Always measure before/after |

## How This Shows Up in Production

- Sorting algorithms: branchless compare for speed
- Graphics and SIMD: mask-based processing removes branches
- JIT compilers: rare branches turned into deopt guards on hot traces
- Database optimizers: batch predicate evaluation to amortize branches
- Security: constant-time comparisons defend against timing attacks

## How a Senior Engineer Thinks

A senior engineer scans hot loops for branches one by one. Branches that almost always go the same way are nearly free; random ones leak 10–20 cycles each. They look for ways to sort data into a pattern, or replace branches with arithmetic.

A senior also remembers that branchless is not always faster. When the predictor is doing well, branched code can win, and short branches often get auto-converted to `cmov` by the compiler. Branchless without measurement just costs readability.

## Checklist

- [ ] You can sketch the five pipeline stages
- [ ] You can distinguish data and control hazards
- [ ] You know branch predictor accuracy depends on code patterns
- [ ] You can explain why sorted data helps the predictor
- [ ] You can summarize branchless tradeoffs in a paragraph

## Practice Problems

1. Run `count_positive` on sorted vs random data and find the size where the gap is widest.

2. Feed your `BranchPredictor` 1000 branches with two distributions (50/50 vs 80/20 True) and compare hit rates.

3. Write branchless versions of `abs`, `min`, `max` and compare runtimes against branched versions. Identify when each is faster.

## Wrap-up and Next Steps

Pipelining lifts CPU throughput by the depth of the pipeline, and branch prediction preserves that gain across branches. Being aware of branch patterns in hot code is a small habit that compounds. As with every optimization, measurement comes before theory.

Next we step outside the CPU, to I/O and devices: how slow components like disks, networks, and keyboards connect to the fast CPU.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Pipelining?**
  - The article treats Pipelining as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Pipelining?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Pipelining reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Architecture 101 (1/10): What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Computer Architecture 101 (2/10): Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [Computer Architecture 101 (3/10): CPU and Instructions](./03-cpu-and-instructions.md)
- [Computer Architecture 101 (4/10): Registers and the ALU](./04-registers-and-alu.md)
- [Computer Architecture 101 (5/10): Memory Organization](./05-memory-organization.md)
- [Computer Architecture 101 (6/10): Cache and Locality](./06-cache-and-locality.md)
- **Pipelining (current)**
- I/O and Devices (upcoming)
- Parallelism and Multicore (upcoming)
- Understanding Performance (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Instruction pipelining](https://en.wikipedia.org/wiki/Instruction_pipelining)
- [Wikipedia — Branch predictor](https://en.wikipedia.org/wiki/Branch_predictor)
- [Stack Overflow — Why is processing a sorted array faster?](https://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-processing-an-unsorted-array)
- [Agner Fog — Software optimization resources](https://www.agner.org/optimize/)

Tags: Computer Science, Computer Architecture, Pipelining, Branch Prediction, Performance, CPU
