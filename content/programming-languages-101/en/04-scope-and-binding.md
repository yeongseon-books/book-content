---
series: programming-languages-101
episode: 4
title: "Programming Languages 101 (4/10): Scope and Binding"
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
  - Scope
  - Binding
  - Lexical
  - Dynamic
seo_description: Where a name resolves to which value is one of the most foundational language design decisions. Compare lexical and dynamic scope.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (4/10): Scope and Binding

The same variable name can refer to different values inside and outside a function, and yet the program still behaves predictably. That ordinary-looking fact rests on one of the most important rule sets in language design.

This is the 4th post in the Programming Languages 101 series.

In this post, we will look at binding — attaching a value to a name — and scope — the region where that attachment is visible. Once lexical scope feels concrete, closures, modules, and shadowing stop looking like separate topics.


![programming languages 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/04/04-01-concept-at-a-glance.en.png)
*programming languages 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Scope and Binding?
- Which signal should the example or diagram make visible for Scope and Binding?
- What failure should be prevented first when Scope and Binding reaches a real system?

## Questions this article answers

- What is the precise difference between scope and binding?
- How do lexical scope and dynamic scope change the result?
- Why can shadowing the same name in an inner scope be risky?
- In what order does Python's LEGB rule resolve names?

## Why It Matters

Without a grasp of scope, "why isn't this variable updating?" or "why am I suddenly getting NameError?" become mysteries. With it, you see that functions, modules, and closures are all variations of the same rule.

> Binding ties a name to a value; scope is the region where that tie is visible.

Python's LEGB rule is the order — innermost to outermost — in which a name is looked up. The first binding found wins.

## Key Terms

- **Binding**: Attaching a value to a name.
- **Scope**: The region of code in which a binding is visible.
- **Lexical scope**: Scope determined by where the code is written.
- **Dynamic scope**: Scope determined by the call chain at runtime (rare in modern languages).
- **Shadowing**: An inner scope hides an outer binding of the same name.

## Before/After

**Before — relying on a global**

```python
LIMIT = 10

def is_ok(x):
    return x < LIMIT

def main():
    LIMIT = 5      # a new local — has no effect on is_ok
    print(is_ok(7))  # True
```

`main`'s `LIMIT` is not visible inside `is_ok`. That is lexical scope.

**After — make the dependency explicit**

```python
def is_ok(x, limit=10):
    return x < limit

print(is_ok(7, limit=5))  # False
```

Pulling the hidden dependency into the parameter list makes the intent obvious.

## Hands-on: Four Examples That Matter Most

### Step 1 — Watch LEGB

```python
# 1_legb.py
x = "global"
def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)
    inner()
    print(x)

outer()
print(x)
# local / enclosing / global
```

The same name resolves to the innermost binding first.

### Step 2 — The real cause of UnboundLocalError

```python
# 2_unbound.py
x = 1
def f():
    print(x)   # UnboundLocalError
    x = 2

f()
```

The moment Python sees `x = 2` inside the function, it treats `x` as local for the entire function. So `print(x)` references a local that has not yet been bound.

### Step 3 — `nonlocal` to update the enclosing scope

```python
# 3_nonlocal.py
def make_counter():
    n = 0
    def step():
        nonlocal n
        n += 1
        return n
    return step

c = make_counter()
print(c(), c(), c())  # 1 2 3
```

Without `nonlocal`, `n += 1` would try to create a new local and trigger the same error as above.

### Step 4 — A lexical vs dynamic thought experiment

```python
# 4_lexical.py
y = "outer"
def show():
    print(y)

def caller():
    y = "inner"
    show()   # lexical scope → prints 'outer'

caller()
```

Under dynamic scope, `show()` would see the caller's `y` and print `'inner'`. Modern languages chose lexical because **just reading the source tells you where a value comes from**.

### Step 5 — The trap of shadowing

```python
# 5_shadow.py
def total(items):
    sum = 0   # shadowed the built-in sum
    for x in items:
        sum += x
    return sum  # works, but you cannot call sum(...) in this function anymore
```

The shadow only causes pain when you suddenly need the original name back. Avoid unintentional shadowing even in short functions.

## What to Notice in This Code

- The same name does not always refer to the same value — scope decides.
- A single assignment inside a function changes how that function treats the name everywhere.
- `nonlocal`/`global` are not common needs; they mark intentional updates.
- Lexical scope gives you "I can tell by reading" — dynamic does not.

## Five Common Mistakes

1. **Using globals to share state between functions.** The source of changes blurs and debugging gets harder.
2. **Shadowing built-ins.** Naming a variable `list`, `dict`, `id`, or `sum` bites you much later.
3. **Sprinkling `global` everywhere.** Cleaning up the module interface with explicit parameters and return values is almost always better.
4. **Causing UnboundLocalError by reassigning a name partway through a function.** Step 2 above is the canonical case.
5. **Assuming dynamic-scope behavior.** Almost always wrong in modern languages.

## How This Shows Up in Production

Scope is a frequent topic in code review. Code where "where does this name come from?" is obvious at a glance is good code. Splitting big functions, lifting dependencies into parameters, and concentrating mutation of module variables in one place all amplify the benefits of lexical scope.

Testing follows the same pattern. A function that depends on global state is hard to unit test; the same function with dependencies as parameters is trivially testable.

## How a Senior Engineer Thinks

- Believes good code lets you answer "where was this name bound?" instantly.
- Routinely refactors hidden dependencies into parameters.
- Leaves a short comment when `nonlocal`/`global` is unavoidable.
- Configures linters to catch built-in shadowing.
- When meeting a new language, looks at scope rules first — function and closure behavior follows from them.

## Checklist

- [ ] Can you list the four levels of LEGB?
- [ ] Can you explain UnboundLocalError in one line?
- [ ] Do you know when to reach for `nonlocal` vs `global`?
- [ ] Have you ever lifted a hidden dependency into an explicit parameter?
- [ ] Can you state the readability advantage of lexical scope in one sentence?

## Practice Problems

1. Fix the shadowing of `sum` in step 5's `total` so that the function can still call the built-in `sum(...)` inside.
2. Pick a function that depends on one module-level variable and rewrite it to take that variable as a parameter. Which version is easier to unit test?
3. Write a small piece of imaginary code where the difference between lexical and dynamic scope changes the result.

## Wrap-up and Next Steps

Scope is the region a name is visible in; binding is the act of attaching a value to a name. Once you understand lexical scope deeply, the next episode — closures — falls out of it naturally, because closures are what lexical scope plus first-class functions allow.

## Answering the Opening Questions

- **What exactly differentiates scope from binding?**
  - Binding is the act of connecting a name to a value; scope is the range determining where that connection is visible. The reason the same name `x` could bind to `"global"`, `"enclosing"`, and `"local"` in the example is that binding and scope work together.
- **How do lexical scope and dynamic scope change the result?**
  - Even when `show()` is called inside `caller()`, it printed the outer `y = "outer"` instead of `y = "inner"` because Python uses lexical scope—resolving names based on definition site. Under dynamic scope, it would follow the call path and read `caller()`'s `y`, producing different results from the same code.
- **Why is shadowing—reusing a name in an inner scope—dangerous?**
  - `sum = 0` shadows the built-in `sum(...)` making the original tool unusable within that function, and writing `print(x)` before `x = 2` in a function triggers `UnboundLocalError`. A single inner assignment changes name resolution for the entire function, making shadowing more dangerous in large code than short examples.
<!-- toc:begin -->
## In this series

- [Programming Languages 101 (1/10): What Is a Programming Language?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): Syntax and Semantics](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): Type Systems](./03-type-system.md)
- **Scope and Binding (current)**
- Functions and Closures (upcoming)
- Objects and Prototypes (upcoming)
- Memory Management (upcoming)
- Interpreters and Compilers (upcoming)
- Static vs Dynamic Languages (upcoming)
- What Makes a Good Language Design? (upcoming)

<!-- toc:end -->

## References

- [Python Language Reference — Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
- [Structure and Interpretation of Computer Programs — Chapter 3](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book-Z-H-21.html)
- [Programming Language Pragmatics (Scott) — Chapter 3 Names, Scopes, and Bindings](https://www.elsevier.com/books/programming-language-pragmatics/scott/978-0-12-410409-9)
- [MDN — Scope](https://developer.mozilla.org/en-US/docs/Glossary/Scope)

Tags: Computer Science, Programming Languages, Scope, Binding, Lexical, Dynamic
