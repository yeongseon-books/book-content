---
series: computer-architecture-101
episode: 4
title: Registers and the ALU
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

# Registers and the ALU

> Computer Architecture 101 series (4/10)

<!-- a-grade-intro:begin -->

**Core question**: When you run `x = 3`, where does that 3 actually live for a moment, and who carries out the addition?

> Inside a CPU, data shuttles constantly between memory and registers. Registers are the smallest and fastest storage, and the ALU (Arithmetic Logic Unit) is the circuit that actually performs operations. Every add, compare, and bit operation is one ALU cycle, and every variable's temporary home is a register. This article looks inside.

<!-- a-grade-intro:end -->

This is post 4 in the Computer Architecture 101 series.

## What You Will Learn

- What a register is and how it differs from memory
- General-purpose and special registers (PC, SP, FLAGS)
- The role of the ALU and its core operations
- An intuition for compiler register allocation

## Why It Matters

The number of registers is the number of variables a CPU can hold at once. Too few and the code keeps bouncing through memory (slow). More allows the compiler more freedom. ALU throughput sets the upper bound on how many operations finish per cycle. Both shape the performance ceiling of code you write every day.

> "Is this variable in a register or in memory?" is the starting question for nearly every hot-path optimization.

## Concept at a Glance

> A register is small storage inside a CPU core: typically a few dozen, each 64 bits wide, and accessible in less than a cycle. The ALU takes two register values as inputs and produces a result in one cycle. All arithmetic and logic happens here.

```text
   +----------------------- CPU Core ----------------------+
   |                                                       |
   |   +--------+    +-------+    +---------+              |
   |   |  RAX   |--->|       |    |         |              |
   |   |  RBX   |--->|  ALU  |--->|  RAX    |              |
   |   |  RCX   |    |       |    | (result)|              |
   |   |  ...   |    +-------+    +---------+              |
   |   +--------+                                          |
   |                                                       |
   |   PC | SP | FLAGS  <- special registers               |
   +-------------------------------------------------------+
```

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

### Step 1: Build a tiny ALU

```python
class ALU:
    """A few basic arithmetic and logic operations."""
    def execute(self, op, a, b):
        if op == "ADD": return a + b
        if op == "SUB": return a - b
        if op == "AND": return a & b
        if op == "OR":  return a | b
        if op == "XOR": return a ^ b
        if op == "SHL": return a << b
        if op == "SHR": return a >> b
        raise ValueError(op)

alu = ALU()
print(alu.execute("ADD", 3, 5))   # 8
print(alu.execute("SHL", 1, 4))   # 16
```

The ALU is a set of simple two-input, one-output functions. Real circuits hew close to this abstraction.

### Step 2: Build a tiny register file

```python
class RegisterFile:
    def __init__(self, n=8):
        self.regs = [0] * n

    def read(self, idx):
        return self.regs[idx]

    def write(self, idx, value):
        self.regs[idx] = value

    def __repr__(self):
        return " ".join(f"R{i}={v}" for i, v in enumerate(self.regs))

rf = RegisterFile()
rf.write(0, 3)
rf.write(1, 5)
print(rf)   # R0=3 R1=5 R2=0 ...
```

A register file looks like a small array. In hardware it supports several simultaneous reads and writes per cycle through multiple ports.

### Step 3: Combine ALU, registers, and instructions

```python
def run(program, rf, alu):
    for instr in program:
        op, dst, src1, src2 = instr
        a = rf.read(src1)
        b = src2 if isinstance(src2, int) else rf.read(src2)
        result = alu.execute(op, a, b)
        rf.write(dst, result)

rf, alu = RegisterFile(), ALU()
rf.write(0, 7)
rf.write(1, 3)

# R2 = R0 + R1; R3 = R2 << 1; R4 = R3 - R0
run([
    ("ADD", 2, 0, 1),
    ("SHL", 3, 2, 1),     # immediate 1
    ("SUB", 4, 3, 0),
], rf, alu)
print(rf)   # R0=7 R1=3 R2=10 R3=20 R4=13
```

Register-to-register instructions dominate any ISA. Code that rarely touches memory is the fastest code.

### Step 4: Use a FLAGS register for comparisons

```python
class CPU:
    def __init__(self):
        self.rf = RegisterFile()
        self.alu = ALU()
        self.flags = {"Z": 0, "N": 0}   # zero, negative

    def cmp(self, src1, src2):
        diff = self.alu.execute("SUB", self.rf.read(src1), self.rf.read(src2))
        self.flags["Z"] = int(diff == 0)
        self.flags["N"] = int(diff < 0)

cpu = CPU()
cpu.rf.write(0, 10); cpu.rf.write(1, 10)
cpu.cmp(0, 1); print(cpu.flags)   # Z=1, N=0  (equal)
cpu.rf.write(1, 11)
cpu.cmp(0, 1); print(cpu.flags)   # Z=0, N=1  (less)
```

Conditions like `if a == b` and `if a < b` are implemented as a SUB followed by a FLAGS check.

### Step 5: Mimic compiler register allocation

```python
def assign_registers(variables, num_regs=4):
    """Simplest first-fit allocator."""
    mapping = {}
    free = list(range(num_regs))
    for v in variables:
        if not free:
            mapping[v] = "STACK"   # spill
        else:
            mapping[v] = f"R{free.pop(0)}"
    return mapping

print(assign_registers(["a", "b", "c", "d"]))
print(assign_registers(["a", "b", "c", "d", "e", "f"]))
```

When registers run out, some variables spill to the stack (memory). Deep functions and large expressions therefore see more memory traffic.

## What to Notice in This Code

- The ALU is a simple two-input, one-output circuit
- Registers are few and fast (dozens, sub-cycle access)
- FLAGS is set by comparisons and consumed by branches
- Variables that do not fit in registers are spilled to the stack

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

1. Use `RegisterFile` and `ALU` to compute the sum of 1..N using only registers — no memory access.

2. Use FLAGS to implement `c = 1 if a < b else 0` at the instruction level. Combine CMP, JL, and MOV.

3. Compile a function you wrote on godbolt.org and count the registers used. Push variables past 16 and compare -O0 with -O2 output.

## Wrap-up and Next Steps

Registers are the fastest storage the CPU can hold at hand, and the ALU is where computation actually happens. Every variable passes through registers, and when they run out the surplus spills to memory. Watching the variable count of hot functions is the start of small wins.

Next we zoom out to the larger landscape of memory: how RAM is addressed and how virtual memory builds on top of it.

<!-- toc:begin -->
- [What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [CPU and Instructions](./03-cpu-and-instructions.md)
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
- [Wikipedia — Arithmetic logic unit](https://en.wikipedia.org/wiki/Arithmetic_logic_unit)
- [Wikipedia — Processor register](https://en.wikipedia.org/wiki/Processor_register)
- [Intel x86-64 Register Reference](https://wiki.osdev.org/CPU_Registers_x86-64)

Tags: Computer Science, Computer Architecture, Registers, ALU, CPU, Computation
