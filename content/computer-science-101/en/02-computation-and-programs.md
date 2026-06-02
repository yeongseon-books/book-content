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

This is the 2nd post in the Computer Science 101 series.

In this article, we'll connect the formal definition of computation, the idea of uncomputable problems, and the way programming languages express those computations for humans.


![Computer Science 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/02/02-01-concept-at-a-glance.en.png)
*Computer Science 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Computation and Programs?
- Which signal should the example or diagram make visible for Computation and Programs?
- What failure should be prevented first when Computation and Programs reaches a real system?

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

## Simulating a Turing Machine in Python

Let us build a minimal Turing machine that adds 1 to a binary number. This makes the abstract model tangible.

```python
class TuringMachine:
    def __init__(self, tape: list[str], rules: dict, start_state: str, halt_states: set[str]):
        self.tape = tape
        self.rules = rules
        self.state = start_state
        self.halt_states = halt_states
        self.head = 0
        self.steps = 0

    def step(self) -> bool:
        if self.state in self.halt_states:
            return False
        symbol = self.tape[self.head] if self.head < len(self.tape) else "B"
        key = (self.state, symbol)
        if key not in self.rules:
            return False
        new_state, write, direction = self.rules[key]
        if self.head >= len(self.tape):
            self.tape.append("B")
        self.tape[self.head] = write
        self.head += 1 if direction == "R" else -1 if direction == "L" else 0
        self.state = new_state
        self.steps += 1
        return True

    def run(self, max_steps: int = 1000) -> str:
        while self.step() and self.steps < max_steps:
            pass
        return "".join(self.tape).rstrip("B")

# A Turing machine that adds 1 to a binary number
# Input: "1011" (decimal 11) -> Output: "1100" (decimal 12)
rules = {
    # Move to rightmost digit
    ("start", "0"): ("start", "0", "R"),
    ("start", "1"): ("start", "1", "R"),
    ("start", "B"): ("carry", "B", "L"),
    # Carry propagation
    ("carry", "0"): ("done", "1", "L"),
    ("carry", "1"): ("carry", "0", "L"),
    ("carry", "B"): ("done", "1", "S"),
}

tm = TuringMachine(
    tape=list("1011"),
    rules=rules,
    start_state="start",
    halt_states={"done"},
)
result = tm.run()
print(f"1011 + 1 = {result}")  # 1100
print(f"Steps taken: {tm.steps}")
```

The key insight: a Turing machine consists of a tape (memory), a head (current position), a state (program counter), and rules (program). Today's computers are the physical realization of this model. RAM is the tape, CPU registers are the head and state, and the instruction set is the rules.

### Practical Implications of Computability Limits

The fact that the halting problem is unsolvable is not just theoretical curiosity. Several real-world problems derive directly from this limitation.

| Impossible in Theory | Practical Alternative |
| --- | --- |
| Decide termination of all programs | Timeouts, watchdogs |
| Perfect virus detector | Signature-based + behavioral heuristics |
| Perfect static analyzer | Approximate analysis + testing in parallel |
| Decide equivalence of two programs | Same test suite passes |
| Optimal compiler | Heuristic optimization passes |

The message: "perfect automation" is impossible in principle for certain domains. Engineers therefore combine "good enough" approximations with safety mechanisms.

## Comparing Programming Paradigms: Solving One Problem Three Ways

Let us apply imperative, functional, and object-oriented paradigms to the same problem: "filter words of length 4 or more and convert them to uppercase."

```python
words = ["cat", "elephant", "dog", "butterfly", "ant", "whale"]

# Imperative: step-by-step instructions on HOW to do it
result_imperative = []
for word in words:
    if len(word) >= 4:
        result_imperative.append(word.upper())
print(f"Imperative: {result_imperative}")

# Functional: declare WHAT you want
result_functional = list(map(str.upper, filter(lambda w: len(w) >= 4, words)))
print(f"Functional: {result_functional}")

# List comprehension (Python's native declarative style)
result_comprehension = [w.upper() for w in words if len(w) >= 4]
print(f"Comprehension: {result_comprehension}")
```

All three approaches produce the same result. The difference is how they reveal intent.

| Paradigm | Strengths | Weaknesses | Best For |
| --- | --- | --- | --- |
| Imperative | Execution flow is explicit, easy to debug | Intent gets buried in length | Logic where state mutation is central |
| Functional | No side effects, high composability | Deep nesting hurts readability | Data transformation pipelines |
| Object-oriented | Encapsulates state and behavior | Risk of over-engineering class hierarchies | Domain modeling, state management |

### Compilation and Interpretation: A Deeper Look at Bytecode

Let us look one level deeper at Python's execution process.

```python
import dis
import sys

def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Print bytecode
print("=== fibonacci bytecode ===")
dis.dis(fibonacci)

# Inspect the code object's constants and variables
code = fibonacci.__code__
print(f"\nConstants (co_consts): {code.co_consts}")
print(f"Local variables (co_varnames): {code.co_varnames}")
print(f"Bytecode size: {len(code.co_code)} bytes")
print(f"Python version: {sys.version}")
```

Being able to read bytecode provides two practical advantages. First, you can identify performance bottlenecks at the operation level rather than the code level. Second, you can verify whether differently-written code actually produces the same bytecode, avoiding unnecessary micro-optimizations.

## Computation Models and Modern Systems

The Turing machine was proposed in 1936, yet its core principles still apply to today's systems.

| Turing Machine Component | Modern System Counterpart | Explanation |
| --- | --- | --- |
| Infinite tape | RAM + disk + cloud storage | Virtual memory extends capacity nearly infinitely |
| Head movement | Memory address access | Pointers and indexes serve as the head |
| State transition | CPU instruction execution | Program Counter tracks current state |
| Transition rules | Program (instruction set) | Code is the rules |
| Halt state | Program termination, return | Exit code returned |

Distributed systems are an extension of this framework. Multiple Turing machines connected via a network exchanging messages. Consensus algorithms (Raft, Paxos) are methods for ensuring that distributed state machines execute the same state transitions.

### Compilation Pipeline: Step-by-Step Transformation

Let us trace the stages a source file goes through to become an executable, using C.

```text
[Source Code]  →  [Preprocessing]  →  [Compilation]  →  [Assembly]  →  [Linking]  →  [Executable]
 hello.c           hello.i            hello.s          hello.o        a.out
```

```c
// hello.c
#include <stdio.h>
#define MSG "Hello"
int main(void) {
    printf("%s\n", MSG);
    return 0;
}
```

**Preprocessing** (`gcc -E hello.c -o hello.i`): `#include` is replaced by header contents, and `MSG` is substituted with `"Hello"`. This stage is pure text substitution, corresponding to string rewriting systems in computation theory.

**Compilation** (`gcc -S hello.i -o hello.s`): Tokenization → parsing → semantic analysis → intermediate representation (IR) → optimization → assembly generation. Optimizations like constant propagation, dead code elimination, and loop unrolling happen here.

**Assembly** (`as hello.s -o hello.o`): Converts human-readable assembly into machine code bytes. At this point the symbol table is created, and external functions (`printf`) have unresolved addresses.

**Linking** (`ld hello.o -lc -o a.out`): Resolves external symbols by finding addresses in libraries. Static linking copies library code into the binary; dynamic linking loads shared libraries at runtime.

## Learning Roadmap: Connecting This Article to the Curriculum

Rather than rushing through an intro to computer science, building interconnected concepts gradually produces better long-term learning efficiency. The core concepts in this article are not standalone knowledge — they are prerequisites that lead into operating systems, networks, databases, and software engineering. Use this article as a weekly anchor and perform the following connection exercises.

| Learning Axis | Checkpoint in This Article | Connection to Later Subjects |
| --- | --- | --- |
| Computation Model | Clearly define input-state-output relationships | Algorithm design, distributed system modeling |
| Abstraction | Distinguish interfaces from hidden implementations | API design, module boundary design |
| Resource Constraints | Consider time, memory, and I/O costs simultaneously | Performance tuning, infrastructure cost optimization |
| Verifiability | Judge by measurement and counterexamples, not claims | Test strategy, experiment design |

When doing connection learning, repeat the structure "define concept once + apply to two cases + check one counterexample." For instance, after learning time complexity, don't just memorize Big-O — record actual execution-time graphs as input size changes. When the graph deviates from expectations, hypothesize the cause and reason about cache locality or constant-factor effects.

Unifying vocabulary across subjects is important. The same phenomenon might be called scheduling in OS, queueing in networking, and transaction waiting in databases. The names differ, but the essence — "allocating resources under contention" — is identical. A terminology glossary with concept-equivalence mappings makes existing understanding reusable in new fields.

For this article's computation models, expressing the same problem in imperative and functional styles side by side helps you feel the model differences viscerally. Express a problem three times through stepwise refinement: first in natural language, then pseudocode, then real code. At each stage, explicitly state the state changes, termination conditions, and failure conditions.

### Connecting Computation Theory to System Design

Understanding computation models is directly useful when designing distributed systems and data processing pipelines. When deciding where to perform an operation, build the habit of separating computation cost from communication cost. For example, when choosing whether to run an aggregation on the client or the server, compare how computation scales with input size against how much data must cross the network.

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

- **What does it mean to say something is computable?**
  - If a procedure (algorithm) exists that produces an answer in finite steps, it's computable. Problems simulatable by a Turing machine are computable problems. This definition matters because knowing "unsolvable problems" exist lets you choose practical approximations over perfect automation in practice.
- **Why does the Turing machine remain the reference model for explaining today's computers?**
  - As implemented in this article, the Turing machine expresses all computation with minimal components: tape (memory), head (access position), state (program counter), and rules (program). No more powerful computation model is known (Church-Turing thesis), so all programming languages have equivalent computational power.
- **What does it mean that problems like the halting problem are fundamentally unsolvable?**
  - Perfect static analyzers, perfect virus detectors, and tools determining whether two programs produce identical results are impossible in principle. That's why practice combines approximate approaches—timeouts, tests, heuristics—to achieve "good enough" verification.
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
