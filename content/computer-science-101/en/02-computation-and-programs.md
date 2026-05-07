---
series: computer-science-101
episode: 2
title: Computation and Programs
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
  - Computation Models
  - Turing Machine
  - Programming Paradigms
  - Compilers
  - Interpreters
seo_description: The definition of computation, the Turing machine, the evolution of programming languages, and the major paradigms that shape software design.
last_reviewed: '2026-05-04'
---

# Computation and Programs

> Computer Science 101 series (2/10)

<!-- a-grade-intro:begin -->

**Key question**: What does it precisely mean that something is "computable," and how does a program express computation?

> In 1936 Alan Turing gave a mathematical definition of "what can be computed." The surprising conclusion: a simple machine that moves along a tape and reads or writes symbols can carry out *every* computation. That theoretical machine is the foundation of every modern computer. This article covers the definition of computation, problems that cannot be computed, the evolution of programming languages, and the major paradigms.

<!-- a-grade-intro:end -->

## What You Will Learn

- The Turing machine and the idea of computability
- Problems that cannot be computed (the halting problem)
- A short history of programming languages
- The differences between imperative, functional, and object-oriented paradigms

## Why It Matters

The answer to "Can every problem be solved by a program?" is no. Computation theory marks the line between problems we can solve and problems we cannot. Programming paradigms then decide *how* we express the solvable ones. Both are foundations of software design.

> Computation theory = the constitution of CS. A paradigm = a philosophy of organizing code.

## Concept at a Glance

> Computation is the process of transforming input by rules. The Turing machine is the most basic model of that process, and a programming language is how we make it human-readable.

```text
Mathematical functions (theory)
        │
Turing machine (computation model)
        │
Machine code (hardware)
        │
Assembly (low level)
        │
High-level languages (Python, Java)
        │
Paradigms (imperative, functional, OOP)
```

## Key Terms

| Term | Description |
| --- | --- |
| Turing machine | A theoretical model that defines computability |
| Halting problem | The classic uncomputable problem of deciding whether a program halts |
| Compiler | A program that translates source code to machine code |
| Interpreter | A program that executes source code line by line |
| Paradigm | A way of thinking and a principle for organizing code |

## Before / After

**Before — without paradigm awareness:**

```python
# All logic crammed into one procedural function
def process_orders(orders):
    total = 0
    for order in orders:
        if order["status"] == "paid":
            price = order["price"] * order["quantity"]
            if order["discount"]:
                price = price * 0.9
            total += price
    return total
```

**After — with paradigm awareness:**

```python
from dataclasses import dataclass


@dataclass
class Order:
    price: int
    quantity: int
    status: str
    discount: bool

    def total_price(self) -> int:
        base = self.price * self.quantity
        return int(base * 0.9) if self.discount else base


def process_orders(orders: list[Order]) -> int:
    return sum(o.total_price() for o in orders if o.status == "paid")
```

## Hands-On: Step by Step

### Step 1: Computation as a state machine

```python
def simple_state_machine(tape: list[str]) -> list[str]:
    """A tiny state machine that flips 0 to 1 and 1 to 0."""
    state = "flip"
    result = []
    for symbol in tape:
        if state == "flip":
            result.append("1" if symbol == "0" else "0")
    return result


tape = ["1", "0", "1", "1", "0"]
print(simple_state_machine(tape))  # ['0', '1', '0', '0', '1']
```

This is the core idea of a Turing machine: look at the current state and the current symbol, then decide the next action.

### Step 2: A problem that cannot be computed

```python
def halts(program, input_data):
    """This function cannot be implemented."""
    # Decide whether `program` halts on `input_data`.
    # Proof sketch: assuming this function exists leads to a contradiction.
    raise NotImplementedError("The halting problem is undecidable")


# A practical workaround: use a timeout
import signal


def run_with_timeout(func, timeout_sec: int = 5):
    """Abort if the function does not finish within the time limit."""
    signal.alarm(timeout_sec)
    try:
        return func()
    except Exception:
        return None
```

The halting problem is the most famous impossibility result in CS. It is why a perfect debugger or a perfect virus scanner cannot exist.

### Step 3: Imperative programming

```python
# Imperative: you tell the computer "how" step by step
def sum_of_squares_imperative(n: int) -> int:
    total = 0
    for i in range(1, n + 1):
        total += i * i
    return total


print(sum_of_squares_imperative(5))  # 55
```

The imperative paradigm gives the computer step-by-step instructions. C, Go, and early Python code lean this way.

### Step 4: Functional programming

```python
from functools import reduce

# Functional: you declare "what" to compute
def sum_of_squares_functional(n: int) -> int:
    return reduce(lambda acc, x: acc + x * x, range(1, n + 1), 0)


print(sum_of_squares_functional(5))  # 55
```

The functional paradigm expresses computation by composing functions instead of mutating state. Haskell, Scala, and Python's `map` / `filter` belong here.

### Step 5: Compilation and interpretation

```python
# Python is an interpreted language
# Source code -> bytecode -> executed on a virtual machine

import dis


def add(a: int, b: int) -> int:
    return a + b


# Inspect the Python bytecode
dis.dis(add)
# LOAD_FAST    0 (a)
# LOAD_FAST    1 (b)
# BINARY_ADD
# RETURN_VALUE
```

A compiler translates the entire program ahead of time, while an interpreter runs it line by line. Python is a hybrid: it compiles to bytecode and then interprets that bytecode on a virtual machine.

## Notable Points in This Code

- A state machine is a simplified Turing machine and shows the essence of computation.
- The halting problem is theoretically unsolvable, but practical workarounds (timeouts) exist.
- The same computation can be expressed in either imperative or functional style.
- Python is a hybrid that uses both compilation and interpretation.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Assuming every problem is solvable by a program | Uncomputable problems exist | Study the halting problem and computation theory |
| Sticking to one paradigm dogmatically | The code does not fit the situation | Pick the paradigm that fits the problem |
| Confusing compilers and interpreters | You misunderstand language properties | Distinguish the two execution models clearly |
| Using only high-level languages and ignoring the low level | You cannot reason about performance | Learn machine code and memory at a basic level |
| Dismissing theory as irrelevant | You miss fundamental limits | Notice how theory drives practical decisions |

## How This Is Used in Practice

- Multi-paradigm languages (Python, Kotlin) let you pick the right style per situation.
- Understanding compile-time vs runtime errors lets you exploit the type system.
- Practical workarounds for the halting problem appear as timeouts and circuit breakers.
- Bytecode inspection helps locate Python performance bottlenecks.
- Functional patterns (map, filter, reduce) shape data pipelines.

## How a Senior Engineer Thinks

Senior engineers are not dogmatic about paradigms. They write imperative code where it is clearest and functional code where it is more concise. What matters is not the paradigm but whether the code clearly conveys intent.

Knowing the limits of computation theory matters in practice too. Once you accept that a "perfect static analyzer" or a "test suite that catches every bug" is impossible in principle, you can focus on building practical workarounds instead.

## Checklist

- [ ] I can explain what a Turing machine is
- [ ] I understand why the halting problem is unsolvable
- [ ] I can distinguish imperative, functional, and object-oriented styles
- [ ] I understand the difference between compilers and interpreters
- [ ] I can describe how Python runs (bytecode + VM)

## Practice Problems

1. Implement a simple state machine that decides whether the parentheses in an input string are balanced.

2. Write the same feature in two styles, imperative and functional: take a list, keep the even numbers, and sum their squares.

3. Use `dis.dis()` to compare the bytecode of three small functions and analyze the operations performed.

## Wrap-Up and Next Steps

Computation is the process of transforming input by rules, and the Turing machine is its theoretical model. Not every problem can be solved by computation (the halting problem). A programming language is how humans express computation, and a paradigm is the philosophy of organizing that code.

The next article looks at how computers represent data — binary, character encodings, and types.

<!-- toc:begin -->
- [What Is Computer Science?](./01-what-is-computer-science.md)
- **Computation and Programs (current)**
- [Data Representation](./03-data-representation.md)
- [Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Architecture](./05-computer-architecture.md)
- [Operating Systems](./06-operating-systems.md)
- [Networks](./07-networks.md)
- [Databases](./08-databases.md)
- [Software Engineering](./09-software-engineering.md)
- [From CS to AI and Data Science](./10-ai-and-data-science.md)
<!-- toc:end -->

## References

- [Alan Turing — On Computable Numbers (1936)](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)
- [Wikipedia — Halting Problem](https://en.wikipedia.org/wiki/Halting_problem)
- [SICP — Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Programming Paradigms for Dummies (Peter Van Roy)](https://www.info.ucl.ac.be/~pvr/VanRoyChapter.pdf)

Tags: Computer Science, Computation Models, Turing Machine, Programming Paradigms, Compilers, Interpreters
