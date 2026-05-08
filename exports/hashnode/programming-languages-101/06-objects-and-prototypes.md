
# Objects and Prototypes

> Programming Languages 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: We call both Java classes and JavaScript prototypes "OOP," so why do they look so different?

> An object bundles **state and the methods that operate on it**. There are two ways to make that bundle — **class-based**, where you stamp out instances from a blueprint, and **prototype-based**, where you make new objects by extending an existing one. The decisive difference is how method lookup happens.

<!-- a-grade-intro:end -->

## What You Will Learn

- A precise definition of "object" under two models
- The method-lookup difference between class-based and prototype-based
- That Python classes are themselves objects
- The relationship between inheritance and delegation
- That closures and objects are two views of the same idea

## Why It Matters

Once you understand the object model precisely, "why is this method being called?" or "why does super behave this way?" becomes a single answer. Knowing both models lets you adapt to any new OOP language fast.

> Object = state + behavior. Classes and prototypes are different tools for making the same kind of bundle.

## Concept at a Glance

```mermaid
flowchart LR
    A["instance"] -->|not found| B["class"]
    B -->|not found| C["parent class"]
    C -->|not found| D["object (root)"]
    E["JS instance"] -->|prototype chain| F["prototype object"]
    F --> G["Object.prototype"]
```

Class-based on top, prototype-based below. Same idea: **delegate one level up when not found**.

## Key Terms

- **Instance**: A concrete object holding state at a moment in time.
- **Class**: A blueprint defining shape and behavior for instances.
- **Prototype**: A base object that other objects can delegate to.
- **Method resolution**: The rule for how far up the chain to search.
- **Delegation**: When an attribute is missing, hand the lookup to another object.

## Before/After

**Before — data and functions live apart**

```python
def make_user(name, age):
    return {"name": name, "age": age}

def greet(user):
    return f"hi, {user['name']}"

u = make_user("kim", 30)
print(greet(u))
```

Callers always have to carry both pieces.

**After — bundled as a class**

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name, self.age = name, age
    def greet(self) -> str:
        return f"hi, {self.name}"

print(User("kim", 30).greet())
```

State and behavior travel as one unit, so the caller carries one thing.

## Hands-on: Trace Both Models

### Step 1 — Class-based lookup

```python
# 1_class.py
class A:
    def hi(self): return "A.hi"

class B(A):
    pass

print(B().hi())          # 'A.hi' — not on B, delegated upward
print(B.__mro__)          # the lookup order
```

The MRO (method resolution order) is exactly the search path.

### Step 2 — A class is also an object

```python
# 2_class_is_object.py
class A: ...
print(type(A))         # <class 'type'>  — a class is an instance of type
A.tag = "v1"            # you can attach attributes to a class object
print(A.tag)
```

Classes are first-class objects too, and you can manipulate them dynamically.

### Step 3 — A prototype-style table in Python

```python
# 3_prototype.py
base = {"hi": lambda self: "base.hi"}

def lookup(obj, key):
    if key in obj: return obj[key]
    if "__proto__" in obj: return lookup(obj["__proto__"], key)
    raise KeyError(key)

inst = {"__proto__": base}
print(lookup(inst, "hi")(inst))   # 'base.hi'
```

Python has no real prototype chain, but "missing → delegate upward" is the same idea.

### Step 4 — Method override and super

```python
# 4_super.py
class A:
    def hi(self): return "A"
class B(A):
    def hi(self): return "B+" + super().hi()

print(B().hi())  # B+A
```

`super` delegates to the next entry in the MRO. Even with multiple inheritance, a single line walks every relevant parent.

### Step 5 — Imitate an object with a closure

```python
# 5_object_as_closure.py
def make_user(name):
    def greet(): return f"hi, {name}"
    return {"greet": greet}

u = make_user("kim")
print(u["greet"]())  # hi, kim
```

State (`name`) and behavior (`greet`) bundled by closure. Proof that the essence of an object exists without a class keyword.

## What to Notice in This Code

- Both models reduce to "missing → delegate upward."
- A Python class is an object, and that fact is what makes metaprogramming possible.
- `super` is an arrow to the next entry in the MRO.
- Closures can mimic objects, showing the two ideas are duals of each other.

## Five Common Mistakes

1. **Inheritance trees four levels deep.** Almost always better flattened with delegation or composition.
2. **Not knowing the MRO.** With multiple inheritance, `super` becomes opaque without it.
3. **Classes with methods but no state.** That is a module or namespace, not an object.
4. **Treating prototypes as just a class lookalike.** The real power is being able to add or replace methods on an individual object.
5. **Treating closures and objects as unrelated.** Accepting they are dual makes you better at picking either.

## How This Shows Up in Production

Most backend code is class-based OOP — domain models as classes, behavior as methods. JavaScript added class syntax, but the engine still uses prototypes underneath, which is why `Object.create` and `Object.getPrototypeOf` survive.

When designing, write down "what state does this object hold?" first. If the answer is empty, you probably do not need a class. Composition is the default; inheritance is reserved for true is-a relationships.

## How a Senior Engineer Thinks

- Asks "what state does this class hold?" before writing the body.
- Composes by default, inherits as a last resort.
- Mentally draws the MRO before using multiple inheritance.
- Treats class, object, and prototype as tools — fitness first.
- Weighs closure-based and object-based solutions equally.

## Checklist

- [ ] Can you state the difference between class-based and prototype-based in one line?
- [ ] Have you ever printed a Python `__mro__`?
- [ ] Can you say what `super` does in one sentence?
- [ ] Do you favor composition over inheritance by default?
- [ ] Have you ever imitated an object with a closure?

## Practice Problems

1. Build two multi-inheritance classes, print `__mro__`, and explain in a paragraph why the order is what it is.
2. Add a "state-mutating" operation to the closure-style object in step 5. You will need `nonlocal`.
3. Pick a recent class of yours that uses inheritance and design a composition-based replacement.

## Wrap-up and Next Steps

Objects bundle state and behavior; the two models are different ways of building that bundle. Either way, the essence is delegation. Next we look at how those objects live and die in memory — memory management.

- [What Is a Programming Language?](./01-what-is-a-programming-language.md)
- [Syntax and Semantics](./02-syntax-and-semantics.md)
- [Type Systems](./03-type-system.md)
- [Scope and Binding](./04-scope-and-binding.md)
- [Functions and Closures](./05-functions-and-closures.md)
- **Objects and Prototypes (current)**
- Memory Management (upcoming)
- Interpreters and Compilers (upcoming)
- Static vs Dynamic Languages (upcoming)
- What Makes a Good Language Design? (upcoming)
## References

- [Python Data Model — object](https://docs.python.org/3/reference/datamodel.html)
- [MDN — Inheritance and the prototype chain](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Inheritance_and_the_prototype_chain)
- [Self: The Power of Simplicity (Ungar & Smith)](https://bibliography.selflanguage.org/_static/self-power.pdf)
- [Composition over inheritance (Wikipedia)](https://en.wikipedia.org/wiki/Composition_over_inheritance)

Tags: Computer Science, Programming Languages, Objects, Prototype, Class, Inheritance

---

© 2026 YeongseonBooks. All rights reserved.
