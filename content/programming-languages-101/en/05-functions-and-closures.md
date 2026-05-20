---
series: programming-languages-101
episode: 5
title: "Programming Languages 101 (5/10): Functions and Closures"
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
  - Functions
  - Closure
  - FirstClass
  - Capture
seo_description: A closure is not magic. It is what lexical scope and first-class functions naturally produce together. Walk through the mechanism end to end.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (5/10): Functions and Closures

A function sometimes appears to remember variables from the place it was defined. At first that feels like magic. In practice it is the natural result of the scope rules from the previous chapter meeting the fact that functions can be treated as values.

This is post 5 in the Programming Languages 101 series.

In this post, we will treat closures as an ordinary consequence of lexical scope plus first-class functions. Once you see that a closure captures bindings rather than copied values, callbacks, decorators, and late-binding bugs all become much easier to reason about.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Functions and Closures?
- Which signal should the example or diagram make visible for Functions and Closures?
- What failure should be prevented first when Functions and Closures reaches a real system?

## Big Picture

![programming languages 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/05/05-01-concept-at-a-glance.en.png)

*programming languages 101 chapter 5 flow overview*

This picture places Functions and Closures inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Functions and Closures is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions this article answers

- What is the difference between first-class functions and higher-order functions?
- What exactly does a closure capture?
- Why do lambdas created inside a loop print the same value?
- In what way are closures similar to objects?

## Why It Matters

Closures are the foundation of callbacks, decorators, partial application, and module-style encapsulation. Without a clear mental model you fall into classics like "all functions made inside a for-loop print the same value."

> A closure is "a function plus the environment it grew up in."

## Concept at a Glance

The `add` returned by `make_adder` carries the binding `x = 10` along with it. The caller cannot see inside, but `add` computes on top of that environment.

## Key Terms

- **First-class function**: Functions can be assigned to variables, passed as arguments, and returned.
- **Higher-order function**: A function that takes or returns a function.
- **Closure**: A function that captures bindings from its enclosing scope.
- **Capture by reference**: The capture is a reference to the same binding, not a value copy.
- **Late binding**: The captured name's value is resolved at call time, not creation time.

## Before/After

**Before — accumulating with global state**

```python
total = 0
def add(n):
    global total
    total += n
add(3); add(4)
print(total)  # 7
```

A global means you cannot use the same function from two places independently.

**After — isolated state via closure**

```python
def make_accumulator():
    total = 0
    def add(n):
        nonlocal total
        total += n
        return total
    return add

a = make_accumulator()
b = make_accumulator()
print(a(3), a(4))  # 3 7
print(b(10))       # 10  (independent of a)
```

Each call captures its own `total`. That isolation is the essence of an "object" too — a hint for the next episode.

## Hands-on: Five Angles on Closures

### Step 1 — The simplest closure

```python
# 1_basic.py
def make_adder(x):
    def add(n):
        return x + n
    return add

add10 = make_adder(10)
add20 = make_adder(20)
print(add10(5), add20(5))  # 15 25
```

`x` lives inside each closure separately.

### Step 2 — Proof that capture is by reference

```python
# 2_reference.py
def make_pair():
    state = {"n": 0}
    def get(): return state["n"]
    def inc(): state["n"] += 1
    return get, inc

g, i = make_pair()
i(); i(); i()
print(g())  # 3
```

Two functions share the same `state`. Capture is by reference, not value.

### Step 3 — The late-binding pitfall

```python
# 3_late_binding.py
fns = []
for i in range(3):
    fns.append(lambda: i)

print([f() for f in fns])  # [2, 2, 2]  — same i!
```

All three lambdas captured the same `i`, and by call time `i` is already 2.

### Step 4 — Fix with eager capture

```python
# 4_fix.py
fns = [(lambda i=i: i) for i in range(3)]
print([f() for f in fns])  # [0, 1, 2]
```

Default arguments are evaluated at function definition time, freezing the value at that moment.

### Step 5 — Memoization

```python
# 5_memo.py
def memo(fn):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper

@memo
def slow_square(n):
    return n * n

print(slow_square(7), slow_square(7))  # 49 49 — second is cached
```

`cache` lives inside `wrapper`'s closure. Invisible from outside, alive across calls.

## What to Notice in This Code

- A closure is the function and its environment together, not the function alone.
- Capture is a reference to a binding, not the value — multiple closures can share the same one.
- The late-binding pitfall illustrates the difference between "freeze the value at definition" and "keep the reference alive."
- Decorators, callbacks, and factories are mostly closures with a hat on.

## Five Common Mistakes

1. **Forgetting that lambdas in a loop share captured variables.** Step 3 above.
2. **Treating closures as unrelated to objects.** They are two expressions of the same idea (next episode covers it).
3. **Trying to mutate the captured state from outside.** The point of a closure is that you cannot.
4. **Forgetting `nonlocal`.** Updates like `+=` create a new local without it.
5. **Causing memory leaks.** Holding on to a closure that captures a large object keeps that object alive.

## How This Shows Up in Production

JavaScript callbacks, Python decorators, partial application in functional libraries — all sit on closures. UI event handlers can say "update this state when the button is clicked" precisely because of closures.

In library design, "take a user-supplied function and call it inside our environment" is most cleanly expressed as a callback plus a closure.

## How a Senior Engineer Thinks

- Sees closures and objects as two forms of "behavior with state."
- Never forgets capture is by reference; checks if the isolation is truly intended.
- Avoids closing over large objects (leak prevention).
- Writes decorators as closures; promotes to a class when they grow.
- Asks "what state does this function share with the outside world?" — a good closure has a one-line answer.

## Checklist

- [ ] Can you tell first-class and higher-order functions apart in one line?
- [ ] Do you know that closure capture is by reference, not value?
- [ ] Do you know the late-binding pitfall and how to avoid it?
- [ ] Can you explain why `nonlocal` is often needed in closures?
- [ ] Have you ever written a small memoizer using a closure?

## Practice Problems

1. Add a max-size limit to step 5's `memo`, evicting the oldest entry first (a tiny LRU).
2. Describe a scenario where the late-binding pitfall surfaces during callback registration (for example, attaching handlers to N buttons).
3. Build a "private counter" with closures only, then again as a class. Which feels more natural? Answer in one line.

## Wrap-up and Next Steps

A closure is "function plus environment." It falls out naturally where lexical scope meets first-class functions. Next we look at the same idea in a different shape — objects and prototypes.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Functions and Closures?**
  - The article treats Functions and Closures as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Functions and Closures?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Functions and Closures reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Programming Languages 101 (1/10): What Is a Programming Language?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): Syntax and Semantics](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): Type Systems](./03-type-system.md)
- [Programming Languages 101 (4/10): Scope and Binding](./04-scope-and-binding.md)
- **Functions and Closures (current)**
- Objects and Prototypes (upcoming)
- Memory Management (upcoming)
- Interpreters and Compilers (upcoming)
- Static vs Dynamic Languages (upcoming)
- What Makes a Good Language Design? (upcoming)

<!-- toc:end -->

## References

- [SICP — Procedures and the Processes They Generate](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-11.html)
- [MDN — Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures)
- [Python functools — partial, lru_cache](https://docs.python.org/3/library/functools.html)
- [On Lambdas, Captures and Closures (PLT)](https://wiki.c2.com/?ClosuresThatWorkLikeObjects)

Tags: Computer Science, Programming Languages, Functions, Closure, FirstClass, Capture
