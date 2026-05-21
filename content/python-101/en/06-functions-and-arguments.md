---
title: "Python 101 (6/10): Functions and arguments: def, args, kwargs, default, lambda"
series: python-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- function-definition
- default-arguments
- args-kwargs
- keyword-only
- lambda
- type-hints
last_reviewed: '2026-05-03'
seo_description: 'A function signature is a contract: what the caller must supply
  and what the function returns.'
---

# Python 101 (6/10): Functions and arguments: def, args, kwargs, default, lambda

A function signature is a contract: what the caller must supply and what the function returns. Argument forms, plus `/` and `*`, let you make that contract clearer and harder to misuse.

This post is the 6th article in the Python 101 series. This is the point in the series where reusable code turns into explicit interfaces.

## Questions to Keep in Mind

- How to define a function with `def` and control what `return` hands back?
- The five argument forms — positional, keyword, default, `*args`, `**kwargs` — and how they bind at call time?
- How positional-only (`/`) and keyword-only (`*`) markers shape an API?

## Big Picture

![Python 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-101/06/06-01-mental-model.en.png)

*Python 101 chapter 6 flow overview*

This picture places Functions and arguments: def, args, kwargs, default, lambda inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why it matters

Functions are the smallest unit you bundle code into. Once you carve branches and loops into functions, you stop repeating yourself, and the function becomes the unit of testing and change. Python's argument handling is rich, however, so beginners often struggle to choose between forms. Positional only ties calls to order; bad defaults leak state between calls; overusing `*args` and `**kwargs` makes signatures opaque.

This chapter consolidates the five argument forms onto a single page so you can design signatures deliberately. In the next chapter on modules and packages, function signatures become the public interface across module boundaries — better to settle this first.

There is one more reason: the mutable default argument trap is one of the most common function-related bugs newcomers hit. Understanding it once prevents repeated mistakes.

## Mental model

> A function signature is a contract: what the caller must supply and what the function returns. The five argument forms and the `/` and `*` markers tune how strict that contract is.
Lay the function signature out on a page, and the call-time rules line up in your head.

Three rules carry most of the weight.

1. **Arguments bind at call time and the body runs on top of that binding.** The signature is an interface that promises "this is the name and shape I will accept".
2. **The order inside the signature is fixed:** positional-only → positional/keyword → `*args` or `*` → keyword-only → `**kwargs`. Break the order and you get a `SyntaxError`.
3. **Defaults are evaluated once, at definition time.** Use a mutable object as a default and that single object is shared between calls.

## Core concepts

### 1. `def` and `return`

`def` creates a new function object and binds it to the given name. Functions are first-class objects, so you can store them in variables or pass them as arguments.

```python
def add(a, b):
    return a + b

f = add
print(f(2, 3))   # 5
```

A function without `return` returns `None`. If `None` is what you want, say so in the signature and docstring. A function that focuses on either "compute a value" or "cause a side effect" — but not both — keeps the call site simpler.

### 2. Positional and keyword arguments

The same function can accept arguments either by position or by name.

```python
def greet(name, message):
    return f"{message}, {name}"

greet("ada", "hello")               # positional
greet(name="ada", message="hello")  # keyword
greet("ada", message="hello")       # mixed (positional first)
```

When mixing, every positional argument must come before any keyword argument. The longer the signature, the more keyword calls help the caller see what each value means.

### 3. Default arguments

A default is evaluated once at definition time and used when the caller leaves the argument out.

```python
def power(base, exp=2):
    return base ** exp

power(3)          # 9
power(3, 3)       # 27
power(3, exp=4)   # 81
```

Arguments with defaults sit toward the end of the signature so positional calls line up naturally.

### 4. `*args` and `**kwargs`

`*args` collects positional arguments not bound to a named parameter into a tuple. `**kwargs` collects keyword arguments not bound to a named parameter into a dict.

```python
def collect(*args, **kwargs):
    return list(args), dict(kwargs)

collect(1, 2, 3, x=10, y=20)
# ([1, 2, 3], {'x': 10, 'y': 20})
```

Reach for `*args`/`**kwargs` (a) in decorators or wrappers that must pass everything through, or (b) in APIs that are genuinely variadic. Otherwise, named parameters keep the signature readable.

### 5. Positional-only (`/`) and keyword-only (`*`)

Since Python 3.8, you can add `/` and `*` to enforce how a parameter may be passed.

```python
def write(path, /, *, mode="w", encoding="utf-8"):
    ...
```

Here `path` must be passed positionally, and `mode` and `encoding` must be passed by keyword. Calls look like `write("a.txt", mode="w")`, and the signature evolves more safely. Positional-only means you can later rename the parameter without breaking callers; keyword-only means you can later reorder parameters without breaking callers.

### 6. `lambda`

`lambda` defines a small anonymous function that contains a single expression.

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]
nums.sort(key=lambda n: -n)
print(nums)  # [9, 6, 5, 4, 3, 2, 1, 1]
```

If a named function reads better, write one. `lambda` shines for "a one-line transform used right here, only once". When the body grows past a single line or you need the same logic again, lift it out to a `def`.

### 7. Light type hints

Type hints are not enforced at runtime, but they document intent for readers and IDEs.

```python
def label(score: int) -> str:
    if score >= 60:
        return "pass"
    return "fail"
```

Adding even input/output types to each function reduces misunderstandings at the call site noticeably.

## Before-after

Rewrite the same behavior from "verbose signature" to "intent-bearing signature". The function builds a greeting from user data.

**Before — a long positional signature**

```python
def make_greeting(name, lang, formal, prefix, suffix):
    head = "Dear" if formal else "Hi"
    if lang == "ko":
        head = "안녕하세요" if formal else "안녕"
    return f"{prefix}{head} {name}{suffix}"

print(make_greeting("ada", "en", True, ">> ", "!"))
```

The call site `make_greeting("ada", "en", True, ">> ", "!")` does not tell the reader what `True` means. The fifth argument `"!"` requires another look at the signature to identify what it appends.

**After — keyword-only options with defaults**

```python
def make_greeting(name: str, *, lang: str = "en", formal: bool = False,
                  prefix: str = "", suffix: str = "") -> str:
    head = "Dear" if formal else "Hi"
    if lang == "ko":
        head = "안녕하세요" if formal else "안녕"
    return f"{prefix}{head} {name}{suffix}"

print(make_greeting("ada", lang="en", formal=True, prefix=">> ", suffix="!"))
```

Each argument labels itself. The arguments after `*` may only be passed by keyword, so the call no longer relies on a meaningless positional boolean. Defaults make the lightweight call possible too.

```python
print(make_greeting("ada"))                # "Hi ada"
print(make_greeting("ada", lang="ko"))     # "안녕 ada"
```

You will see this pattern across library functions. Signatures stay short while expressing the intent: "core arguments are positional, options are keyword-only".

## Step-by-step practice

Run these in the REPL. Lines starting with `>>>` are inputs; the lines below are outputs.

1. **Reproduce the mutable default trap.**

```text
>>> def buggy(item, items=[]):
...     items.append(item)
...     return items
>>> buggy(1)
[1]
>>> buggy(2)
[1, 2]
>>> buggy(3)
[1, 2, 3]
```

The same list object is shared across calls. The safe pattern is:

```text
>>> def safe(item, items=None):
...     items = items if items is not None else []
...     items.append(item)
...     return items
>>> safe(1)
[1]
>>> safe(2)
[2]
```

`items if items is not None else []` distinguishes "the caller explicitly passed `items=[]`" from "the caller omitted the argument". `items or []` collapses both into the same case and blurs the intent.

2. **Collect arguments with `*args` and `**kwargs`.**

```text
>>> def show(*args, **kwargs):
...     print("args =", args)
...     print("kwargs =", kwargs)
>>> show(1, 2, x=10)
args = (1, 2)
kwargs = {'x': 10}
```

Unpacking on the call side uses the same notation:

```text
>>> def add3(a, b, c):
...     return a + b + c
>>> nums = [1, 2, 3]
>>> add3(*nums)
6
>>> kw = {"a": 1, "b": 2, "c": 3}
>>> add3(**kw)
6
```

3. **Lock the signature with positional-only and keyword-only.**

```text
>>> def make_url(host, /, *, scheme="https", path="/"):
...     return f"{scheme}://{host}{path}"
>>> make_url("example.com")
'https://example.com/'
>>> make_url("example.com", scheme="http", path="/api")
'http://example.com/api'
>>> make_url(host="example.com")
Traceback (most recent call last):
    ...
TypeError: make_url() got some positional-only arguments passed as keyword arguments: 'host'
```

`host` is positional-only. `scheme` and `path` are keyword-only. The call shape is enforced, which makes future signature changes easier to roll out without breaking callers.

4. **Use `lambda` as a sort key.**

```text
>>> users = [{"name": "ada", "score": 71}, {"name": "bob", "score": 92}]
>>> sorted(users, key=lambda u: u["score"], reverse=True)
[{'name': 'bob', 'score': 92}, {'name': 'ada', 'score': 71}]
```

When the key function is a single expression, `lambda` is short and clear. Once it grows beyond two lines, lift it into a `def` for readability.

## Common mistakes

1. **Mutable default arguments.**
   `def f(items=[]):` builds the list once at definition time and shares it across calls. As calls accumulate, the list grows. If you really want an empty list as the default, write `def f(items=None): items = items if items is not None else []`.

2. **Forgetting `return`.**
   A function without `return` returns `None`. If `result = compute(...)` keeps coming back as `None`, the body is often missing a `return`.

3. **Mixing positional and keyword arguments and clashing.**
   `f(1, a=2)` raises `TypeError` if the first positional already binds to `a`. Re-check the signature to see which slot maps to which name.

4. **Overusing `*args` and `**kwargs`.**
   Unless the function is genuinely variadic, named parameters keep the signature readable. Hide everything behind `**kwargs` and IDE autocomplete and type checkers can no longer help you.

5. **Cramming a multi-line behavior into `lambda`.**
   `lambda` accepts a single expression. When the logic grows, write a `def` and give it a name. The name itself becomes documentation.

6. **Scope confusion.**
   You can read a module-level variable inside a function, but assigning a new value to the same name creates a local variable. To rebind the global, use the `global` keyword explicitly. Better still, avoid the pattern: take the value as an argument and return the result instead.

## In practice

In production code function signatures act as a public API. Two patterns are worth keeping in mind.

**(1) Make options keyword-only.**

```python
def export_csv(rows, path, *, encoding="utf-8", delimiter=",", quote_all=False):
    ...
```

Calls like `export_csv(rows, "out.csv", quote_all=True)` keep options keyword-only, so reordering the option list later does not break callers. Libraries lean on this pattern heavily.

**(2) Pass everything through in a wrapper.**

```python
def with_logging(fn):
    def wrapper(*args, **kwargs):
        print("call", fn.__name__, args, kwargs)
        result = fn(*args, **kwargs)
        print("done", fn.__name__)
        return result
    return wrapper
```

This is where `*args`/`**kwargs` truly fits — decorators or middleware that must accept any function and pass arguments through unchanged.

Both patterns reappear in the next chapter, where modules and packages introduce import boundaries.

## Checklist

- [ ] I can define a function with `def` and explain the difference between returning a value and causing a side effect.
- [ ] I can mix positional, keyword, default, `*args`, and `**kwargs` in a single signature.
- [ ] I can state the mutable default trap in one sentence and write the safe pattern.
- [ ] I have used `/` and `*` to enforce positional-only and keyword-only arguments.
- [ ] I can give one example each of where `lambda` fits and where it does not.
- [ ] I have added light type hints to a function signature.

## Exercises

1. **Safe accumulator.**
   With the signature `def append_item(item, items=None) -> list:`, append to `items` if the caller provides one, otherwise build a new list and return it.
   - Success criterion: `append_item(1) == [1]` and `append_item(2) == [2]` (no carryover between calls).

2. **Keyword-only option.**
   With the signature `def join_path(*parts, sep="/") -> str:`, join the substrings using `sep`. Force `sep` to be keyword-only.
   - Success criterion: `join_path("a", "b", "c") == "a/b/c"` and `join_path("a", "b", sep="-") == "a-b"`.

3. **Refactor `lambda` to `def`.**
   Refactor `sorted(users, key=lambda u: (u["score"], u["name"]))` into an explicit function `def by_score_then_name(u): ...`, then call `sorted(users, key=by_score_then_name)`.
   - Success criterion: both calls produce the same result.

## Summary and next chapter

- A function signature is the interface between caller and body. Combine positional, keyword, default, `*args`, and `**kwargs` deliberately.
- Defaults are evaluated once at definition time. Use the `None` + `is not None` pattern instead of mutable defaults.
- `/` and `*` lock the call shape, making signature evolution easier.
- `lambda` fits one-line transforms. When it grows, use `def` and a name.
- Light type hints are not enforced at runtime, but they reduce misunderstandings at the call site.

The next chapter covers modules and packages — `import`, `__init__.py`, and `__name__` — and shows how functions are exposed and hidden across module boundaries.

## Answering the Opening Questions

- **How to define a function with `def` and control what `return` hands back?**
  - The article treats Functions and arguments: def, args, kwargs, default, lambda as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The five argument forms — positional, keyword, default, `*args`, `**kwargs` — and how they bind at call time?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How positional-only (`/`) and keyword-only (`*`) markers shape an API?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Python 101 (1/10): Why Python, and how to install and use venv](./01-why-python-and-install.md)
- [Python 101 (2/10): Variables, types, and operators](./02-variables-types-operators.md)
- [Python 101 (3/10): Strings and formatting](./03-strings-and-formatting.md)
- [Python 101 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [Python 101 (5/10): Control flow: if, for, while, comprehension](./05-control-flow.md)
- **Functions and arguments: def, args, kwargs, default, lambda (current)**
- Modules and packages: import, __init__, __name__ (upcoming)
- File I/O and exception handling (upcoming)
- Classes and objects: bundling data with behavior (upcoming)
- Standard library tour: datetime, pathlib, json, collections, itertools (upcoming)

<!-- toc:end -->

## References

- [Python tutorial — More on Defining Functions](https://docs.python.org/3/tutorial/controlflow.html) — Practical overview of defaults, keyword arguments, `*args`, `**kwargs`, and `lambda`.
- [Python docs — Compound Statements](https://docs.python.org/3/reference/compound_stmts.html) — Formal reference for function definitions, parameter kinds, and `return` behavior.
- [Python docs — Expressions](https://docs.python.org/3/reference/expressions.html) — Documents `lambda` as an expression form and clarifies its limitations.
- [PEP 3102 — Keyword-Only Arguments](https://peps.python.org/pep-3102/) — Design rationale for forcing options to be passed by name.
- [PEP 570 — Python Positional-Only Parameters](https://peps.python.org/pep-0570/) — Explains the `/` separator and its API design benefits.
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) — Standard basis for annotating function signatures with types.

Tags: function-definition, default-arguments, args-kwargs, keyword-only, lambda, type-hints
