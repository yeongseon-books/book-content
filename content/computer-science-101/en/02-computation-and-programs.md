---
series: computer-science-101
episode: 2
title: "Computer Science 101 (2/10): Computation and Programs"
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
  - Computation Models
  - Turing Machine
  - Programming Paradigms
  - Compilers
  - Interpreters
seo_description: The definition of computation, the Turing machine, the evolution of programming languages, and the major paradigms that shape software design.
last_reviewed: '2026-05-15'
---

# Computer Science 101 (2/10): Computation and Programs

“Can a program solve this?” sounds simple until you ask where the boundary of computability really is. The answer does not stop at theory. It also shapes how we organize code, choose a paradigm, and reason about what a programming language is even doing for us.

This is post 2 in the Computer Science 101 series.

In this article, we'll connect the formal definition of computation, the idea of uncomputable problems, and the way programming languages express those computations for humans.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Computation and Programs?
- Which signal should the example or diagram make visible for Computation and Programs?
- What failure should be prevented first when Computation and Programs reaches a real system?

## Big Picture

![Computer Science 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/02/02-01-concept-at-a-glance.en.png)

*Computer Science 101 chapter 2 flow overview*

This picture places Computation and Programs inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Questions This Article Answers

- What does it actually mean to call a problem computable?
- Why is the Turing machine still the reference model for modern computing?
- What does the halting problem tell us about the limits of software?
- How do imperative, functional, and object-oriented styles express the same computation differently?
- How do compilers and interpreters change the way code reaches execution?

## What You Will Learn

- The Turing machine and the idea of computability
- Problems that cannot be computed (the halting problem)
- A short history of programming languages
- The differences between imperative, functional, and object-oriented paradigms

## Why It Matters

The answer to "Can every problem be solved by a program?" is no. Computation theory marks the line between problems we can solve and problems we cannot. Programming paradigms then decide *how* we express the solvable ones. Both are foundations of software design.

> Computation theory = the constitution of CS. A paradigm = a philosophy of organizing code.

> Computation is the process of transforming input by rules. The Turing machine is the most basic model of that process, and a programming language is how we make it human-readable.

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

**Expected output:** you should see bytecode operations such as `LOAD_FAST`, `BINARY_ADD`, and `RETURN_VALUE`, confirming that Python code is translated into a lower-level form before execution.

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

## Answering the Opening Questions

- **What boundary should you inspect first when applying Computation and Programs?**
  - The article treats Computation and Programs as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Computation and Programs?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Computation and Programs reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science 101 (1/10): What Is Computer Science?](./01-what-is-computer-science.md)
- **Computation and Programs (current)**
- Data Representation (upcoming)
- Algorithms and Complexity (upcoming)
- Computer Architecture (upcoming)
- Operating Systems (upcoming)
- Networks (upcoming)
- Databases (upcoming)
- Software Engineering (upcoming)
- From CS to AI and Data Science (upcoming)

<!-- toc:end -->

## References

- [Alan Turing — On Computable Numbers (1936)](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)
- [Stanford Encyclopedia of Philosophy — The Church-Turing Thesis](https://plato.stanford.edu/entries/church-turing/)
- [SICP — Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Programming Paradigms for Dummies (Peter Van Roy)](https://www.info.ucl.ac.be/~pvr/VanRoyChapter.pdf)

Tags: Computer Science, Computation Models, Turing Machine, Programming Paradigms, Compilers, Interpreters
