---
series: computer-architecture-101
episode: 4
title: "Computer Architecture 101 (4/10): Registers and the ALU"
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
  - Registers
  - ALU
  - CPU
  - Computation
seo_description: How registers and the ALU sit at the heart of every CPU, where data lives during execution, and why register pressure shapes performance.
last_reviewed: '2026-05-04'
---

# Computer Architecture 101 (4/10): Registers and the ALU

A loop can look unchanged in source code and still slow down because one more live variable forced the compiler to spill a value to the stack. When that happens, the story is no longer just "the ALU did an add." It is about where values lived, which instruction set FLAGS, and how often execution had to leave the register file.

This is post 4 in the Computer Architecture 101 series. Here we look at registers, FLAGS, and the ALU as the CPU's immediate working set, then use real assembly to show what register pressure and spills look like in practice.


![computer architecture 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/04/04-01-registers-alu-dataflow.en.png)
*computer architecture 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Registers and the ALU?
- Which signal should the example or diagram make visible for Registers and the ALU?
- What failure should be prevented first when Registers and the ALU reaches a real system?

## What You Will Learn

- What a register is and how it differs from memory
- General-purpose and special registers (PC, SP, FLAGS)
- The role of the ALU and its core operations
- An intuition for compiler register allocation

## Why It Matters

The number of registers is the number of variables a CPU can hold at once. Too few and the code keeps bouncing through memory (slow). More allows the compiler more freedom. ALU throughput sets the upper bound on how many operations finish per cycle. Both shape the performance ceiling of code you write every day.

> "Is this variable in a register or in memory?" is the starting question for nearly every hot-path optimization.

> A register is small storage inside a CPU core: typically a few dozen, each 64 bits wide, and accessible in less than a cycle. The ALU takes two register values as inputs and produces a result in one cycle. All arithmetic and logic happens here.

### Registers ALU dataflow

## Key Terms

| Term | Description |
| --- | --- |
| Register | The fastest storage in a CPU core |
| General-purpose | Holds arbitrary data (R0..R15, etc.) |
| PC | Program counter, address of the next instruction |
| SP | Stack pointer, used in function calls |
| FLAGS | Comparison results (zero, sign, overflow, ...) |
| ALU | Circuit that performs arithmetic and logic |

## Before / After

**Before — "a variable is just a variable":**

```python
def hot_loop():
    s = 0
    for i in range(1000):
        s += i * 2 + 1
    return s
```

**After — "a variable occupies a register":**

```text
On entry the compiler may assign:
- s   -> R0
- i   -> R1
- temp (i*2+1) -> R2

One iteration:
- R2 = R1 << 1    # i * 2 via shift
- R2 = R2 + 1
- R0 = R0 + R2
- R1 = R1 + 1
- compare and branch
```

When the loop fits in registers, no memory access is needed.

## Hands-on: Step by Step

### Step 1: Start from a real hot loop

```c
long low_pressure(long *a, long n) {
    long acc = 0;
    for (long i = 0; i < n; ++i) {
        long x = a[i] + i;
        long y = x * 3;
        acc += keep3(x, y, acc);
    }
    return acc;
}

long high_pressure(long *a, long n, long bias) {
    long acc = bias;
    for (long i = 0; i < n; ++i) {
        long v0 = a[i] + bias;
        long v1 = a[i] + i;
        long v2 = v0 ^ v1;
        long v3 = v2 + acc;
        long v4 = v3 + v1;
        long v5 = v4 + v0;
        long v6 = v5 + i;
        long v7 = v6 + bias;
        long v8 = v7 ^ acc;
        long v9 = v8 + v3;
        acc += keep10(v0, v1, v2, v3, v4, v5, v6, v7, v8, v9);
    }
    return acc;
}
```

```bash
clang -target x86_64-apple-macos14 -S -O2 -fno-unroll-loops -x c pressure.c -o -
```

Both functions do arithmetic, but the second one keeps far more intermediate values alive at the same time. That is exactly the situation where register pressure becomes visible in emitted code.

### Step 2: Watch FLAGS feed a control-flow decision

```text
# x86-64 excerpt
testl   %esi, %esi
jle     LBB0_1
...
cmpq    %r12, %rbx
jne     LBB2_4

# ARM64 excerpt
subs    x9, x9, #1
b.ne    LBB0_2
```

`testl`, `cmpq`, and `subs` are not interesting because they store a user-visible value. They are interesting because they set condition codes, and the next branch consumes those flags immediately. That is the practical role of FLAGS in real machine code.

### Step 3: Read the low-pressure version

```text
# x86-64, low_pressure (excerpt)
movq    (%r14,%r12,8), %rdi
addq    %r12, %rdi
leaq    (%rdi,%rdi,2), %rsi
movq    %r15, %rdx
callq   _keep3
addq    %r15, %rax
incq    %r12
movq    %rax, %r15
```

The key pattern is what you do **not** see: no spill comments, no extra stack pushes for live temporaries, and no reload storm around the call. The compiler is still doing loads, ALU work, and a call, but most live values fit in registers.

### Step 4: Read the high-pressure version

```text
# x86-64, high_pressure (excerpt)
movq    %rdx, -48(%rbp)      ## 8-byte Spill
movq    %rsi, -64(%rbp)      ## 8-byte Spill
movq    %rdi, -56(%rbp)      ## 8-byte Spill
...
pushq   %r14
pushq   %r11
pushq   %rax
pushq   %r10
callq   _keep10
addq    $32, %rsp
```

This is the evidence the toy allocator could never show clearly. The function is still compiled at `-O2`, yet extra live values force spills to stack slots and extra push/pop traffic around the call. The ALU is not the only cost anymore; memory traffic entered the hot path.

### Step 5: Translate the listing back into architecture terms

| Signal in the assembly | What it means |
| --- | --- |
| `movq ... %rdi`, `movq ... %rsi`, `leaq ...` | Register-to-register ALU setup before the call |
| `testl`, `cmpq`, `subs` | Set FLAGS for a later branch decision |
| `## Spill`, `pushq`, stack slot offsets like `-48(%rbp)` | Register pressure exceeded the easy register budget |
| `callq _keep3` vs `callq _keep10` | Calls amplify pressure because argument registers and caller-saved registers must be managed together |

That is the production meaning of register allocation: not a coloring diagram on a whiteboard, but whether the compiler can keep the working set in registers or has to bounce through the stack.

## What to Notice in This Code

- The ALU only looks cheap when its operands are already in registers
- Registers are few and fast (dozens, sub-cycle access)
- FLAGS is set by comparisons and consumed immediately by branches or conditional moves
- Register pressure shows up as spill slots, pushes, reloads, and extra memory traffic

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Variable explosion | Register pressure causes spills | Reduce variables in hot functions |
| Inlining everything | Inlined code worsens register pressure | Consider function splitting |
| Equating float and integer ALU | FPU and SIMD units are separate | Measure float costs separately |
| Treating compares as expensive | They are one-cycle SUB+FLAG | Branches, not compares, are costly |
| Treating registers as named variables | Register numbers != source names | Keep them separate when reading assembly |

## How This Shows Up in Production

- Embedded firmware: data type choices match register width
- ML inference: SIMD registers (AVX, NEON) for many values per instruction
- Graphics: GPU shaders use thousands of registers
- Compilers: graph-coloring register allocation to minimize spills
- Security: prevent FLAGS leakage in side-channel-resistant code

## How a Senior Engineer Thinks

A senior engineer notices the local-variable count of hot functions. When live variables exceed the architectural registers (e.g., 16 on x86-64), the compiler starts using the stack and the per-iteration cost rises. Decisions to slim variables or split a large function come from that intuition.

A senior also remembers that "FLAGS is an invisible byproduct." Branches that depend on a recent comparison can misbehave if other instructions land in between. They rarely write assembly by hand, but they can read it well enough to trust the compiler.

## Checklist

- [ ] You can name the difference between a register and memory in one sentence
- [ ] You can list examples of general-purpose and special registers
- [ ] You can sketch what the ALU does in one cycle
- [ ] You know the role of FLAGS
- [ ] You can explain why register spills are expensive

## Practice Problems

1. Compile one loop with 2-3 live temporaries and another with 8-10 live temporaries. Mark every stack slot that appears only in the high-pressure version.

2. Find one `cmp`, `test`, or `subs` instruction in your own disassembly and trace which later branch or conditional move consumes its FLAGS.

3. Compile a function you wrote on godbolt.org or locally, then compare a version with a helper taking 3 arguments and one taking 10 arguments. Note when stack-passed arguments and spill slots begin to appear.

## Wrap-up and Next Steps

Registers are the fastest storage the CPU can hold at hand, and the ALU is where computation actually happens. Every variable passes through registers, and when they run out the surplus spills to memory. Watching the variable count of hot functions is the start of small wins.

Next we zoom out to the larger landscape of memory: how RAM is addressed and how virtual memory builds on top of it.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Registers and the ALU?**
  - The article treats Registers and the ALU as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Registers and the ALU?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Registers and the ALU reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Architecture 101 (1/10): What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Computer Architecture 101 (2/10): Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [Computer Architecture 101 (3/10): CPU and Instructions](./03-cpu-and-instructions.md)
- **Registers and the ALU (current)**
- Memory Organization (upcoming)
- Cache and Locality (upcoming)
- Pipelining (upcoming)
- I/O and Devices (upcoming)
- Parallelism and Multicore (upcoming)
- Understanding Performance (upcoming)

<!-- toc:end -->

## References

- [Patterson & Hennessy — Computer Organization and Design](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Intel 64 and IA-32 Architectures Software Developer's Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [Intel 64 and IA-32 Architectures Optimization Reference Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel64-and-ia32-architectures-optimization.html)
- [ARM Architecture Reference Manual](https://developer.arm.com/documentation)
- [Agner Fog — Optimization Manuals](https://www.agner.org/optimize/)

Tags: Computer Science, Computer Architecture, Registers, ALU, CPU, Computation
