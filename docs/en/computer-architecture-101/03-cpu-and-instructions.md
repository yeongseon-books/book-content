---
series: computer-architecture-101
episode: 3
title: CPU and Instructions
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
  - CPU
  - Instructions
  - ISA
  - Assembly
seo_description: How a CPU runs the fetch-decode-execute cycle, what an ISA defines, and how high-level code becomes a sequence of machine instructions.
last_reviewed: '2026-05-04'
---

# CPU and Instructions

> Computer Architecture 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: What does a CPU actually do in one cycle, and how does that single cycle connect to the code we write?

> The CPU pulls one instruction at a time from memory, decodes it, and executes it. The contract that defines which instructions exist and how they are encoded is called the ISA. x86-64, ARM, and RISC-V are different versions of that contract. This article walks the cycle end to end and shows what your code actually becomes.

<!-- a-grade-intro:end -->

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

```text
            +------ Fetch ------+
            |                   |
            |   PC --> Memory   |
            |        |          |
            |        v          |
            |   Instruction     |
            +---------+---------+
                      |
                      v
            +------ Decode -----+
            |   opcode + operand|
            +---------+---------+
                      |
                      v
            +------ Execute ----+
            | ALU / Mem / Branch|
            +-------------------+
```

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

### Step 2: Build a tiny fetch-decode-execute simulator

```python
class TinyCPU:
    """Toy CPU: memory, registers, and PC."""
    def __init__(self, program):
        self.memory = list(program)
        self.regs = {"R0": 0, "R1": 0, "R2": 0}
        self.pc = 0

    def step(self):
        instr = self.memory[self.pc]   # fetch
        op, *args = instr              # decode
        if op == "MOV":
            self.regs[args[0]] = args[1]
        elif op == "ADD":
            self.regs[args[0]] = self.regs[args[1]] + self.regs[args[2]]
        elif op == "PRINT":
            print(self.regs[args[0]])
        self.pc += 1                   # advance PC

cpu = TinyCPU([
    ("MOV", "R0", 3),
    ("MOV", "R1", 5),
    ("ADD", "R2", "R0", "R1"),
    ("PRINT", "R2"),
])
for _ in range(4):
    cpu.step()
```

Every CPU repeats these three steps. Real CPUs do the same thing about 100 million times faster than this simulator.

### Step 3: Add branch instructions

```python
class TinyCPU2(TinyCPU):
    def step(self):
        instr = self.memory[self.pc]
        op, *args = instr
        if op == "JMP":
            self.pc = args[0]          # move PC directly
            return
        if op == "JNZ":                # jump if non-zero
            if self.regs[args[0]] != 0:
                self.pc = args[1]
                return
        super().step()
        return
```

With branches PC no longer just advances by one. This is the entry point for the next article on pipelining and branch prediction.

### Step 4: Categorize instruction types

```python
INSTRUCTION_CATEGORIES = {
    "Arithmetic/Logic": ["ADD", "SUB", "MUL", "DIV", "AND", "OR", "XOR", "SHL", "SHR"],
    "Memory":           ["LOAD", "STORE", "MOV"],
    "Branch":           ["JMP", "JNZ", "JE", "CALL", "RET"],
    "Special":          ["NOP", "HLT", "SYSCALL"],
}

for cat, ops in INSTRUCTION_CATEGORIES.items():
    print(f"{cat}: {', '.join(ops)}")
```

Most ISAs offer these four categories. They differ in encoding, count, and per-cycle cost.

### Step 5: Read real compiler output

```text
# C source compiled with gcc -O2 -S (excerpt)
#
# int sum_to_n(int n) {
#     int s = 0;
#     for (int i = 1; i <= n; i++) s += i;
#     return s;
# }
#
# The compiler rewrites the loop as n * (n + 1) / 2:
#
#   lea     eax, [rdi + 1]
#   imul    eax, edi
#   sar     eax, 1
#   ret
```

A whole loop can collapse into a single multiply. Compilers are very good at instruction reduction; reading their output makes collaboration easy.

## What to Notice in This Code

- Every CPU loops on fetch-decode-execute
- An instruction is opcode plus operands
- Branch instructions change PC directly
- Compilers often rewrite your loop into a much shorter sequence

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

2. Extend `TinyCPU` with `SUB`, `JZ` (jump if zero), and `HLT`. Write a program that sums 1 to 10.

3. On godbolt.org, paste a short function in C or Rust and compare -O0 with -O2 output. Note which optimizations the compiler applied.

## Wrap-up and Next Steps

The CPU is a simple machine: pull one instruction from memory, decode it, run it, repeat. That simplicity sits beneath every abstraction, and serious performance work eventually drops to assembly. Keep the ISA-vs-microarchitecture distinction in mind.

Next we look at the place where computation actually happens inside the CPU: registers and the ALU. We will see where data sits during execution and how the ALU performs its operations.

<!-- toc:begin -->
- [What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
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
- [Compiler Explorer (godbolt.org)](https://godbolt.org/)
