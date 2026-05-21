---
series: programming-languages-101
episode: 8
title: "Programming Languages 101 (8/10): Interpreters and Compilers"
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
  - Programming Languages
  - Interpreter
  - Compiler
  - JIT
  - Bytecode
seo_description: Interpreters and compilers do the same job at different times. Read Python bytecode with dis and see how JIT bridges the two strategies.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (8/10): Interpreters and Compilers

Python is often called an interpreted language, yet it still produces `.pyc` files. That tension is a useful clue. It means the common “interpreted vs compiled” contrast is too blunt to describe what actually happens at runtime.

This is post 8 in the Programming Languages 101 series.

In this post, we will treat interpreters and compilers as two strategies for the same translation problem. We will use Python bytecode as the concrete example, then connect that path to AOT and JIT so the execution model feels like an engineering choice instead of a slogan.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Interpreters and Compilers?
- Which signal should the example or diagram make visible for Interpreters and Compilers?
- What failure should be prevented first when Interpreters and Compilers reaches a real system?

## Big Picture

![programming languages 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/08/08-01-concept-at-a-glance.en.png)

*programming languages 101 chapter 8 flow overview*

This picture places Interpreters and Compilers inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Questions this article answers

- What is the shortest way to explain the difference between an interpreter and a compiler?
- What execution path does Python actually follow?
- What exactly is a `.pyc` file?
- Why is JIT considered a middle strategy between the two?

## Why It Matters

When performance hurts, being able to answer "what does this line actually run as?" replaces guess-debugging with measurement. Knowing how the same code runs differently under interpreter, JIT, and AOT makes tool choice obvious.

> The same algorithm can run 100x faster or slower depending on the execution model.

Python takes `A → ... → D → E`. JVM bumps hot code to `F`. C and Rust go straight to `G`.

## Key Terms

- **Compiler**: Translates source to another form (bytecode, machine code) ahead of time.
- **Interpreter**: Processes source or bytecode one step at a time during execution.
- **AOT (Ahead-Of-Time)**: Compile the whole thing before running it.
- **JIT (Just-In-Time)**: Compile only the frequently executed parts during execution.
- **Bytecode**: A human-readable but more abstract intermediate form, sitting between source and machine code.

## Before/After

**Before — the vague picture**

```text
.py file → ??? → result
```

**After — what actually happens**

```text
.py → tokenize → parse → AST → compile → .pyc bytecode → VM executes one op at a time
```

A `.pyc` file is cached bytecode. Python clearly has a compile phase; it just runs the result through an interpreter.

## Hands-on: Look Inside CPython

### Step 1 — Read bytecode with `dis`

```python
# 1_dis.py
import dis

def add(a: int, b: int) -> int:
    return a + b

dis.dis(add)
```

You will see `LOAD_FAST a`, `LOAD_FAST b`, `BINARY_OP +`, `RETURN_VALUE`. Each line is one cycle of the Python VM.

### Step 2 — Same algorithm, different op count

```python
# 2_optimization.py
import dis

def slow(xs):
    s = 0
    for x in xs:
        s = s + x
    return s

def fast(xs):
    return sum(xs)

print("--- slow ---"); dis.dis(slow)
print("--- fast ---"); dis.dis(fast)
```

`fast` is dramatically shorter. One function call is one VM op, and the loop inside `sum` is implemented in C.

### Step 3 — Confirm `.pyc` really is bytecode

```python
# 3_pyc.py
import py_compile, dis, marshal, importlib.util, pathlib

src = pathlib.Path("/tmp/sample.py")
src.write_text("def f(): return 42\n")
pyc = py_compile.compile(str(src), doraise=True)

with open(pyc, "rb") as f:
    f.read(16)                # 16-byte header on Python 3.7+
    code = marshal.load(f)
dis.dis(code)
```

A `.pyc` is a header plus a marshalled code object. Subsequent imports skip the parse/compile work and feed the VM directly.

### Step 4 — Compare with AOT, in Python's own terms

```python
# 4_compile_call.py
import time

PY_SRC = "result = sum(range(10_000_000))"
code = compile(PY_SRC, "<inline>", "exec")

t0 = time.perf_counter(); exec(code, {}); t1 = time.perf_counter()
print("compiled-once exec:", t1 - t0)

t0 = time.perf_counter()
for _ in range(3):
    exec(PY_SRC, {})           # compiled fresh each iteration
print("recompiled each time:", time.perf_counter() - t0)
```

Pre-compiling makes repeated execution faster. That is the AOT idea — translate once, run many times.

### Step 5 — The JIT intuition: measure the hot path

```python
# 5_hot_path.py
from collections import Counter

calls: Counter[str] = Counter()

def trace(name: str) -> None:
    calls[name] += 1

for _ in range(1_000_000):
    trace("inner")             # one million calls — JIT would target this
trace("outer")                  # only once

print(calls.most_common(2))
```

A JIT watches call frequency in real time and compiles only the functions that cross a threshold to native code. PyPy, V8, and HotSpot all use variations of this same trick.

## What to Notice in This Code

- Calling Python "interpreted" describes the **execution** stage. The compile stage exists too.
- One line of `dis` output is one VM cycle — your basic unit for performance reasoning.
- A `.pyc` is not magic. It is cached bytecode.
- JIT is a pragmatic middle between "compile everything" and "compile nothing."

## Five Common Mistakes

1. **Treating "interpreter vs compiler" as warring camps.** They are two timings of the same job.
2. **Believing `.pyc` is an executable.** It still needs the Python VM to run.
3. **Rewriting algorithms when the real fix is moving the loop into C.** `sum`, `numpy`, and friends are usually the right answer first.
4. **Assuming JIT is always faster.** For short scripts, warm-up cost can dominate.
5. **Guessing about performance without ever opening `dis`.** A 30-second answer is one import away.

## How This Shows Up in Production

CPython covers most cases with interpretation plus the bytecode cache. Hot numeric work delegates to NumPy or PyTorch (C/C++ underneath). PyPy runs the same Python through a JIT and crushes simple-loop workloads.

The JVM defaults to JIT — start with interpretation, compile hot paths to native, and gradually speed up. Go, Rust, and C compile AOT and start fast immediately.

## How a Senior Engineer Thinks

- Reads `dis` before talking about performance.
- Treats interpreter, JIT, and AOT as tools and picks by fit.
- Does not say "Python is slow." Says "this function runs as N VM ops."
- Remembers JIT warm-up costs.
- Knows that pushing hot loops down to a library (C-implemented) is often the fastest answer.

## Checklist

- [ ] Can you state the interpreter–compiler distinction in one line?
- [ ] Have you ever read a function's bytecode with `dis`?
- [ ] Can you describe what a `.pyc` is in one sentence?
- [ ] Can you state the AOT–JIT distinction in one line?
- [ ] Do you know at least one pattern for moving hot loops into C?

## Practice Problems

1. Time the `slow` and `fast` functions on a large input, then connect the gap to the `dis` output in one paragraph.
2. Run the same `slow` on PyPy (or Codon, Cython) and measure the difference.
3. Pick a module you use often, run `python -m compileall .`, and measure how import times change.

## Wrap-up and Next Steps

Interpreters, compilers, and JITs are not enemies; they are different answers to the same question. Next we look at the other big axis that shapes execution — the static vs dynamic typing tradeoff.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Interpreters and Compilers?**
  - The article treats Interpreters and Compilers as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Interpreters and Compilers?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Interpreters and Compilers reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Programming Languages 101 (1/10): What Is a Programming Language?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): Syntax and Semantics](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): Type Systems](./03-type-system.md)
- [Programming Languages 101 (4/10): Scope and Binding](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): Functions and Closures](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): Objects and Prototypes](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): Memory Management](./07-memory-management.md)
- **Interpreters and Compilers (current)**
- Static vs Dynamic Languages (upcoming)
- What Makes a Good Language Design? (upcoming)

<!-- toc:end -->

## References

- [Python — dis module](https://docs.python.org/3/library/dis.html)
- [Python — py_compile module](https://docs.python.org/3/library/py_compile.html)
- [PyPy — How does PyPy work?](https://doc.pypy.org/en/latest/architecture.html)
- [Just-in-time compilation (Wikipedia)](https://en.wikipedia.org/wiki/Just-in-time_compilation)

Tags: Computer Science, Programming Languages, Interpreter, Compiler, JIT, Bytecode
