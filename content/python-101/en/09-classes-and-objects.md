---
title: "Python 101 (9/10): Classes and objects: bundling data with behavior"
series: python-101
episode: 9
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- class-and-instance
- init-method
- self-parameter
- dunder-methods
- inheritance
- dataclass
last_reviewed: '2026-05-03'
seo_description: A class is not a mold for data; it is the definition of behavior
  shared by objects of the same kind.
---

# Python 101 (9/10): Classes and objects: bundling data with behavior

A class is not just a mold for data; it is a shared definition of behavior for objects of the same kind. An instance is one concrete object carrying that behavior with its own state.

This is the 9th post in the Python 101 series.

This post is the 9th article in the Python 101 series. This is the stage in the series where behavior, state, and object design come together.


![Python 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/python-101/09/09-01-mental-model.en.png)
*Python 101 chapter 9 flow overview*

## Questions to Keep in Mind

- Define a class with the `class` statement and create instances from it?
- Explain the role of `__init__` in instance initialization?
- Explain what `self` refers to and why it is the first parameter of a method?

## Why it matters

Functions and modules from earlier chapters kept behavior and data apart. A function takes input and returns output; a module groups related functions. When data and the behavior that operates on it are tightly paired, however, keeping them separate scatters the code.

Imagine modeling user information. You end up with `format_user(name, email)`, `validate_user(name, email)`, `serialize_user(name, email)` — many functions taking the same arguments. Callers have to gather the same fields on each call, and adding a new field forces a change across the related signatures.

A class bundles data (attributes) and behavior (methods) into a single unit. A `User(name, email)` instance carries `format`, `validate`, and `serialize` together. The caller passes one object instead of a list of fields.

This chapter introduces the simplest tools for building that bundle: the `class` statement and dunder methods.

## Mental model

> A class is not a mold for data; it is the definition of behavior shared by objects of the same kind. An instance is an individual object that follows that definition. With that one line in mind, `self`, class attributes, and dunder methods all find their place.
The diagram below shows the path from a class definition to a method call on an instance.

Three ideas hold this together.

- **A class is a template for objects.** The `class User:` statement creates a class object named `User`, and calling `User(...)` produces an instance from that template.
- **`__init__` initializes the instance.** Python calls it right after the instance is created, and it is the place where you set attributes with `self.attr = value`.
- **A method call `obj.method(x)` is really `method(obj, x)`.** Python passes the instance as the first argument automatically, which is why methods take `self` as their first parameter.

## Core concepts

### `class` and instances

The simplest class looks like this.

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

`User("Ada", "a@x")` creates an instance and attaches `name` and `email` to it. Each instance keeps its own copy.

### `__init__` and `self`

`__init__` initializes an instance that has been created already. Python handles object creation behind the scenes, and `__init__` fills in the attributes.

`self` refers to that newly created instance. The name is a convention rather than syntax, but the rest of the Python ecosystem uses `self`, so picking another name confuses readers.

### Instance and class attributes

```python
class User:
    role = "member"  # class attribute

    def __init__(self, name):
        self.name = name  # instance attribute
```

- `User.role` is shared across instances.
- `self.name` is stored per instance.

When you write `u = User("Ada"); u.role = "admin"`, the assignment creates a new attribute on that instance and leaves the class attribute untouched.

### Methods

A method is a function defined inside a class. Its first parameter receives the instance (`self`).

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def label(self):
        return f"{self.name} <{self.email}>"
```

When you call `u = User("Ada", "a@x"); u.label()`, Python rewrites the call as `User.label(u)`. Inside the method, `self.name` reads the instance's data.

### Dunder methods: `__repr__`, `__str__`, `__eq__`

Methods with two underscores on each side of the name are called dunder (double-underscore) methods. Many language constructs are defined to call them.

- `__repr__(self)` — debug-friendly string. Returned by `repr(obj)` and shown when you type the object at a REPL. A reproducible form like `User('Ada', 'a@x')` is a good default.
- `__str__(self)` — human-readable string. Returned by `str(obj)` and used by `print(obj)`. When undefined, Python falls back to `__repr__`.
- `__eq__(self, other)` — equality comparison. `obj1 == obj2` calls this method. When undefined, equality compares object identity (`is`) only.

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"User({self.name!r}, {self.email!r})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return (self.name, self.email) == (other.name, other.email)
```

### Inheritance and method overriding

Inheritance creates a new class on top of an existing one.

```python
class Member(User):
    def label(self):
        return f"[member] {super().label()}"
```

- `Member` inherits attributes and methods from `User`.
- Redefining `label` overrides it for `Member` instances.
- `super().label()` calls the parent's method without rewriting it.

Inheritance is powerful, but deep hierarchies make it hard to track where a method came from. For straightforward cases, composition (holding another object as an attribute) is often the safer first choice.

### Simplifying with `@dataclass`

When you write classes that are mostly data containers, you write `__init__`, `__repr__`, and `__eq__` by hand again and again. `@dataclass` generates those three methods for you.

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
```

This block generates field-based `__init__`, `__eq__`, and a default `__repr__` automatically. Its default `__repr__` includes field names, such as `User(name='Ada', email='a@x')`, so it is not identical to the hand-written example above.

## Before-After

The code below models user information.

**Before**

```python
def make_user(name, email):
    return {"name": name, "email": email}

def user_label(user):
    return f"{user['name']} <{user['email']}>"

def user_equal(a, b):
    return a["name"] == b["name"] and a["email"] == b["email"]
```

This snippet has three problems.

- The shape `{"name": ..., "email": ...}` repeats across the codebase. Adding a field forces a change to multiple functions.
- The caller has to remember the dict keys exactly. A typo only shows up at runtime.
- Equality has to be implemented by hand.

**After**

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str

    def label(self):
        return f"{self.name} <{self.email}>"
```

Three changes happened.

- The data shape lives in one class definition. Adding a field is one new line.
- Attribute access lets the IDE and static analyzers help with completion and checks.
- `__init__`, `__repr__`, and `__eq__` are produced by `@dataclass`.

## Step-by-step practice

Open a REPL and follow along. Blocks marked with `>>>` are REPL transcripts; the other code blocks are illustrative snippets.

### 1. Build the simplest class

```text
>>> class User:
...     def __init__(self, name, email):
...         self.name = name
...         self.email = email
...
>>> u = User("Ada", "a@x")
>>> u.name
'Ada'
>>> u.email
'a@x'
```

### 2. Add a method

```text
>>> class User:
...     def __init__(self, name, email):
...         self.name = name
...         self.email = email
...     def label(self):
...         return f"{self.name} <{self.email}>"
...
>>> User("Ada", "a@x").label()
'Ada <a@x>'
```

`label()` receives `self` automatically, so the call site does not pass it.

### 3. Define `__repr__` for a useful display

```text
>>> class User:
...     def __init__(self, name, email):
...         self.name = name
...         self.email = email
...     def __repr__(self):
...         return f"User({self.name!r}, {self.email!r})"
...
>>> User("Ada", "a@x")
User('Ada', 'a@x')
```

Without `__repr__`, the default shows something like `<__main__.User object at 0x...>` with a memory address.

### 4. Define `__eq__` for value comparison

```text
>>> class User:
...     def __init__(self, name, email):
...         self.name = name
...         self.email = email
...     def __eq__(self, other):
...         if not isinstance(other, User):
...             return NotImplemented
...         return (self.name, self.email) == (other.name, other.email)
...
>>> User("Ada", "a@x") == User("Ada", "a@x")
True
>>> User("Ada", "a@x") == User("Bob", "b@x")
False
```

### 5. Inheritance with `super()`

```text
>>> class User:
...     def __init__(self, name, email):
...         self.name = name
...         self.email = email
...     def label(self):
...         return f"{self.name} <{self.email}>"
...
>>> class Member(User):
...     def label(self):
...         return f"[member] {super().label()}"
...
>>> Member("Ada", "a@x").label()
'[member] Ada <a@x>'
```

### 6. Compress with `@dataclass`

```text
>>> from dataclasses import dataclass
>>> @dataclass
... class User:
...     name: str
...     email: str
...
>>> u = User("Ada", "a@x")
>>> u
User(name='Ada', email='a@x')
>>> u == User("Ada", "a@x")
True
```

`__init__`, `__repr__`, and `__eq__` are generated automatically.

## Common mistakes

- **Forgetting `self`** — when the first parameter is missing, calls fail with a `TypeError` about argument count.
- **Mutable class attributes** — writing `class C: items = []` makes one list shared across instances, which is a frequent source of bugs. Build mutable defaults inside `__init__`.
- **Returning a value from `__init__`** — `__init__` is meant to return `None`. Returning anything else raises `TypeError`.
- **Defining only `__str__`** — the REPL and most logs will still show a memory address. Define `__repr__` first as your debug-friendly default.
- **Stacking deep inheritance** — once a hierarchy is three or more layers deep, tracking methods becomes painful. Try composition first.
- **Hand-writing data containers** — `@dataclass` removes much of the boilerplate when the class is mostly fields.
- **Mixing up `is` and `==`** — `is` checks object identity; `==` checks equality. They agree until you define `__eq__`, and then they diverge by design.

## In real projects

Classes tend to show up in these places.

- **Domain models**: business concepts like `User`, `Order`, and `Invoice` map directly to classes. `@dataclass` fits simple models well.
- **External resource handles**: DB connections, HTTP clients, and file handles carry state, and a class is a natural wrapper. Adding `__enter__`/`__exit__` lets the object work inside a `with` block.
- **Policy or strategy objects**: implementations that share an interface (for example `JSONFormatter`, `TextFormatter`) sit naturally in classes, and the caller depends only on the interface.
- **Test doubles**: `Fake`, `Stub`, and `Spy` helpers are usually small classes.
- **State machines**: workflows with explicit state transitions (order status, job stages) gather their transition logic neatly inside one class.

Plenty of business logic is fine as plain functions. Classes earn their cost when data and behavior are tightly paired or when several implementations need to share an interface.

## Checklist

- [ ] You can define a class with `class` and create instances from it.
- [ ] You can describe the role of `__init__` and `self` in one sentence each.
- [ ] You can tell instance attributes apart from class attributes.
- [ ] You can describe the basic role of `__repr__`, `__str__`, and `__eq__`.
- [ ] You can use single inheritance and call `super()`.
- [ ] You can apply `@dataclass` to a simple data container.
- [ ] You can describe the difference between `is` and `==` in one sentence.

## Exercises

1. Define a `Point` class with `__init__(x, y)` and a `distance_to(other)` method that returns the distance between two points.
2. Add `__repr__` and `__eq__` to `Point` so that `Point(1, 2) == Point(1, 2)` evaluates to `True`.
3. Rewrite `Point` using `@dataclass` and confirm in a REPL that the behavior matches.
4. Define an `Animal` class and a `Dog(Animal)` subclass that overrides `speak()`. Have `Dog.speak` call `super().speak()` as part of its result.

## Summary and next chapter

- A class bundles data and behavior so the caller can pass one object instead of a list of fields.
- `__init__` initializes an instance, and `self` refers to that instance inside methods.
- Dunder methods like `__repr__`, `__str__`, and `__eq__` define how language constructs interact with your objects.
- Inheritance is powerful but harder to follow as it deepens, so composition is often a safer first option.
- `@dataclass` removes the `__init__`/`__repr__`/`__eq__` boilerplate for simple data containers.

The next chapter is a tour of the standard library. Now that functions, modules, and classes are in place, you will see what Python ships with by default.

## Answering the Opening Questions

- **What changes when you move user data from multiple dicts to a class or `@dataclass`?**
  - The article consolidated scattered `{"name": ..., "email": ...}` dicts and helper functions into a single `User` class—and for simpler cases used `@dataclass` to auto-generate `__init__`, `__repr__`, and `__eq__`. Fields live in one place, `self.name` replaces `user['name']`, and static analysis plus autocomplete start working.
- **How do `self`, `__repr__`, `__eq__`, and `super()` reveal how objects display, compare, and extend?**
  - `obj.method(x)` internally becomes `Class.method(obj, x)`, so `self` anchors every method to its instance. `__repr__` like `User('Ada', 'a@x')` shows the object's identity; `__eq__` enables value-based comparison; `super().label()` demonstrates inheritance extension—each making object behavior visible.
- **Why does putting a mutable object in a class attribute or stacking deep inheritance make debugging hard?**
  - `class C: items = []` shares one list across all instances, making state-change origin untraceable. Deep inheritance forces `__mro__` traversal to find which parent owns a method. The article recommended composition and flat structures like `@dataclass` as safer defaults.

<!-- toc:begin -->
## In this series

- [Python 101 (1/10): Why Python, and how to install and use venv](./01-why-python-and-install.md)
- [Python 101 (2/10): Variables, types, and operators](./02-variables-types-operators.md)
- [Python 101 (3/10): Strings and formatting](./03-strings-and-formatting.md)
- [Python 101 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [Python 101 (5/10): Control flow: if, for, while, comprehension](./05-control-flow.md)
- [Python 101 (6/10): Functions and arguments: def, args, kwargs, default, lambda](./06-functions-and-arguments.md)
- [Python 101 (7/10): Modules and packages: import, __init__, __name__](./07-modules-and-packages.md)
- [Python 101 (8/10): File I/O and exception handling](./08-file-io-and-exceptions.md)
- **Classes and objects: bundling data with behavior (current)**
- Standard library tour: datetime, pathlib, json, collections, itertools (upcoming)

<!-- toc:end -->

## References

- [Python tutorial — Classes](https://docs.python.org/3/tutorial/classes.html) — Core guide to `class`, instances, methods, inheritance, and class-versus-instance variables.
- [Python docs — Data model](https://docs.python.org/3/reference/datamodel.html) — Formal source for attribute lookup, method binding, and special method behavior.
- [Python docs — Built-in Functions](https://docs.python.org/3/library/functions.html) — Useful reference for `isinstance()`, `super()`, and related builtins used with classes.
- [Python docs — `dataclasses`](https://docs.python.org/3/library/dataclasses.html) — Standard-library tool for generating `__init__`, `__repr__`, and comparison methods automatically.
- [PEP 557 — Data Classes](https://peps.python.org/pep-0557/) — Explains the rationale and semantics behind dataclass generation.

Tags: class-and-instance, init-method, self-parameter, dunder-methods, inheritance, dataclass
