---
series: computer-architecture-101
episode: 3
title: "Computer Architecture 101 (3/10): CPU and Instructions"
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
  - CPU
  - Instructions
  - ISA
  - Assembly
seo_description: How a CPU runs the fetch-decode-execute cycle, what an ISA defines, and how high-level code becomes a sequence of machine instructions.
last_reviewed: '2026-05-04'
---

# Computer Architecture 101 (3/10): CPU and Instructions

When a hot loop shows up in a profiler, the next useful question is not "what syntax did I write?" but "what instructions did the compiler emit, and how is the CPU stepping through them?" That is the moment when fetch, decode, execute, and branch behavior stop sounding like textbook terms and start explaining real performance.

This is post 3 in the Computer Architecture 101 series. Here we use x86-64, ARM64, and RISC-V as concrete examples of the ISA contract, then follow one small function down to the instruction stream the CPU actually runs.

## Questions to Keep in Mind

- What boundary should you inspect first when applying CPU and Instructions?
- Which signal should the example or diagram make visible for CPU and Instructions?
- What failure should be prevented first when CPU and Instructions reaches a real system?

## Big Picture

![computer architecture 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/03/03-01-cpu-fetch-decode-execute.en.png)

*computer architecture 101 chapter 3 flow overview*

This picture places CPU and Instructions inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of CPU and Instructions is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- The fetch-decode-execute cycle
- How an instruction is structured (opcode and operands)
- Categories of instructions (arithmetic, memory, branch)
- A first taste of x86-64, ARM, and RISC-V

## Why It Matters

Performance work eventually reduces to "how many instructions does this code become, and how fast can the CPU run them?" Without the cycle in your head, profiler output is opaque, and without ever reading assembly, you cannot tell what the compiler did well and what it missed.

> All high-level code is a sequence of instructions. Keeping that sequence short and simple is a joint effort with the compiler.

## Concept at a Glance

> Each cycle the CPU (1) fetches the instruction at the address in PC, (2) decodes its bit pattern, and (3) executes it. PC then moves to the next instruction unless a branch redirects it.

### CPU fetch decode execute

## Key Terms

| Term | Description |
| --- | --- |
| ISA | The contract for the instruction format |
| opcode | What to do (add, load, ...) |
| operand | What to act on (register, memory address) |
| PC | Program Counter, address of the next instruction |
| Branch | Instruction that redirects PC |
| Cycle | One CPU beat, typically 0.3–1 ns |

## Before / After

**Before — "the code just runs":**

```python
def add(a, b):
    return a + b
```

**After — "how many instructions is this function?":**

```text
# x86-64 assembly (simplified)
add:
    mov   rax, rdi      # first argument (a) into rax
    add   rax, rsi      # add the second argument (b)
    ret                 # return the result

# ~3 instructions, ~3 cycles (cache hits assumed)
```

The same function tells a different story when you read it at the assembly layer.

## Hands-on: Step by Step

### Step 1: Compare bytecode with and without a check

```python
import dis

def add(a, b):
    return a + b

def add_with_check(a, b):
    if a < 0 or b < 0:
        return 0
    return a + b

print("--- add ---")
dis.dis(add)
print("--- add_with_check ---")
dis.dis(add_with_check)
```

A single `if` becomes a few comparisons, branches, and jumps. The instruction count grows quickly with checks.

### Step 2: Compile one loop and read the real x86-64 listing

```c
int count_positive(int *arr, int n) {
    int s = 0;
    for (int i = 0; i < n; ++i) {
        if (arr[i] > 0) s += arr[i];
    }
    return s;
}
```

```bash
clang -target x86_64-apple-macos14 -S -O0 -x c count_positive.c -o -
clang -target x86_64-apple-macos14 -S -O2 -fno-vectorize -fno-slp-vectorize -fno-unroll-loops -x c count_positive.c -o -
```

```text
# x86-64, -O0 (excerpt)
movl    $0, -16(%rbp)      # s lives on the stack
movl    $0, -20(%rbp)      # i lives on the stack
LBB0_1:
movl    -20(%rbp), %eax
cmpl    -12(%rbp), %eax
jge     LBB0_6
cmpl    $0, (%rax,%rcx,4)
jle     LBB0_4
addl    -16(%rbp), %eax
movl    %eax, -16(%rbp)
```

```text
# x86-64, -O2 (excerpt)
testl   %esi, %esi
jle     LBB0_1
LBB0_4:
movl    (%rdi,%rsi,4), %r8d
testl   %r8d, %r8d
cmovlel %edx, %r8d
addl    %r8d, %eax
incq    %rsi
cmpq    %rsi, %rcx
jne     LBB0_4
```

At `-O0`, the compiler keeps reloading `i` and `s` from stack slots, so the instruction stream shows obvious memory traffic. At `-O2`, the same logic stays mostly in registers: `testl` sets condition flags, `cmovlel` keeps non-positive values out of the sum without another branch, and `cmpq`/`jne` drive the loop.

### Step 3: Compare the same logic on ARM64

```bash
clang -target arm64-apple-macos14 -S -O2 -fno-vectorize -fno-slp-vectorize -fno-unroll-loops -x c count_positive.c -o -
```

```text
# ARM64, -O2 (excerpt)
cmp     w1, #1
b.lt    LBB0_4
LBB0_2:
ldr     w10, [x0], #4
bic     w10, w10, w10, asr #31
add     w8, w10, w8
subs    x9, x9, #1
b.ne    LBB0_2
```

The ISA changes, but the contract is recognizably the same. `ldr` fetches an element, `add` updates the running sum, `subs` both subtracts and updates FLAGS, and `b.ne` consumes those flags for the loop branch. RISC-V would encode the same intent with different instruction names and register conventions, not a different fetch-decode-execute model.

### Step 4: Categorize the instructions you just saw

| Category | x86-64 example | ARM64 example | What it did in the listing |
| --- | --- | --- | --- |
| Arithmetic / logic | `addl`, `testl` | `add`, `subs`, `bic` | Update the sum, test sign, update flags |
| Memory | `movl (%rdi,%rsi,4), %r8d` | `ldr w10, [x0], #4` | Load the next array element |
| Branch / control flow | `jle`, `jne` | `b.lt`, `b.ne` | Skip work or loop again |
| Data movement | `movl`, `cmovlel` | `mov` | Move values between registers or from memory |

Most ISAs expose these same broad categories. What changes is the encoding, the register file, and how aggressively a compiler can fuse or reorder them.

### Step 5: Reproduce the disassembly on your own code

```text
1. Write a 5-10 line C, Rust, or Zig function with a branch and a loop.
2. Compile once with `-O0` and once with `-O2`.
3. Highlight three things in the output: where the loop counter lives, which instruction sets flags, and which branch consumes them.
4. If you want fast iteration, Compiler Explorer is a great tool, but use the architecture manuals when you need authoritative instruction semantics.
```

This is where fetch-decode-execute becomes concrete. You stop imagining a generic CPU and start seeing real loads, compares, branches, and register updates.

## What to Notice in This Code

- Every CPU loops on fetch-decode-execute
- An instruction is opcode plus operands
- Branch instructions change PC directly or choose a different fall-through path
- Optimized code usually keeps hot values in registers and uses fewer memory touches

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| "One line equals one instruction" | Wrong cost estimates | Check with `dis` or assembly |
| Treating branches as free | Big penalty when mispredicted | Reduce branches in hot loops |
| Distrusting the compiler | Hand-tuned code becomes slower | Read -O2 output first |
| Confusing ISA with CPU | Same ISA, different chips, different speed | Check microarchitecture too |
| Relying on interpreter optimization | Hot paths stay slow | Use compiled languages for hot paths |

## How This Shows Up in Production

- Game engines: hand-checked assembly and SIMD in hot loops
- Compiler development: instruction selection and scheduling for an ISA
- Embedded systems: real-time guarantees from instruction-level cycle counts
- Security analysis: disassemblers tracing malicious instruction flow
- Databases: hand-tuned assembly for core operators

## How a Senior Engineer Thinks

A senior engineer estimates "how many instructions is this function?" for hot code. They picture the branches, memory loads, and system calls in their head, and when in doubt they reach for `dis`, `objdump`, or `perf`. They do not write assembly daily, but they think about its shape daily.

A senior also keeps the rule "ISA is the contract, microarchitecture is the implementation" close. The same x86-64 instruction has different cycle costs across Intel, AMD, and CPU generations. They trust measurements over universal claims.

## Checklist

- [ ] You can sketch the three stages of fetch-decode-execute
- [ ] You know an instruction is opcode plus operands
- [ ] You understand that branches change PC
- [ ] You know x86-64, ARM, and RISC-V are different ISAs
- [ ] You have read at least one assembly listing of your own code

## Practice Problems

1. Compare the bytecode of `sum(range(n))` and `n * (n - 1) // 2` with `dis`. Match the instruction counts to the measured times.

2. Compile the same small loop to x86-64 and ARM64. Identify the load, the arithmetic update, and the branch in both listings.

3. On godbolt.org or with local `clang -S`, paste a short function in C or Rust and compare `-O0` with `-O2` output. Note which values moved from stack slots into registers.

## Wrap-up and Next Steps

The CPU is a simple machine: pull one instruction from memory, decode it, run it, repeat. That simplicity sits beneath every abstraction, and serious performance work eventually drops to assembly. Keep the ISA-vs-microarchitecture distinction in mind.

Next we look at the place where computation actually happens inside the CPU: registers and the ALU. We will see where data sits during execution and how the ALU performs its operations.

## Answering the Opening Questions

- **What boundary should you inspect first when applying CPU and Instructions?**
  - The article treats CPU and Instructions as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for CPU and Instructions?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when CPU and Instructions reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Architecture 101 (1/10): What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Computer Architecture 101 (2/10): Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- **CPU and Instructions (current)**
- Registers and the ALU (upcoming)
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
- [ARM Architecture Reference Manual](https://developer.arm.com/documentation)
- [RISC-V Specifications](https://riscv.org/technical/specifications/)

Tags: Computer Science, Computer Architecture, CPU, Instructions, ISA, Assembly
