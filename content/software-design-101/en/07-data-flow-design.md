---
series: software-design-101
episode: 7
title: "Software Design 101 (7/10): Data Flow Design"
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
  - SoftwareDesign
  - DataFlow
  - Pipelines
  - Immutability
  - FunctionalDesign
seo_description: How to make the direction of data flow explicit, build small transformation pipelines, and use immutable data to keep designs simple.
last_reviewed: '2026-05-15'
---

# Software Design 101 (7/10): Data Flow Design

Data flow becomes painful when values change silently in the middle of the request and no one can explain where the mutation happened. That is a design problem long before it becomes a debugging problem.

This is the 7th post in the Software Design 101 series.

In this post, we design the path from input to output so each transformation step stays visible. The goal is to make data move one way, keep side effects at the edge, and make debugging a step-by-step question instead of a scavenger hunt.

> Data gets easier to trust when you can point to where it came from, how it changed, and where it is going next.


![software design 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/07/07-01-concept-at-a-glance.en.png)
*software design 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Data Flow Design?
- Which signal should the example or diagram make visible for Data Flow Design?
- What failure should be prevented first when Data Flow Design reaches a real system?

## What You Will Learn

- The single-direction principle for data flow
- Building transformation pipelines
- The value of immutable data
- Push versus pull models
- Signals of code with a clear flow

## Why It Matters

Most bugs appear when data changes in unexpected places. A single direction makes the change easy to trace and limits the blast radius.

> Good code keeps a short distance between input and output.

Each step is small and just hands off to the next.

## Key Terms

- **Pipeline**: A chain of small transformation functions.
- **Pure function**: Same input gives same output, with no side effects.
- **Immutability**: Once a value is created, it does not change.
- **Push model**: Producers push to consumers.
- **Pull model**: Consumers pull what they need.

## Before / After

**Before**

```python
def process(req):
    if not req.get("email"): raise ValueError
    req["email"] = req["email"].lower()
    db.save(req)
    send_welcome(req["email"])
    return req
```

**After**

```python
def parse(payload): ...
def validate(user): ...
def normalize(user): ...
def persist(user): ...
def notify(user): ...

def signup(payload):
    return notify(persist(normalize(validate(parse(payload)))))
```

Each step has a clear responsibility.

## Hands-on: Five Steps to Clean Up the Flow

### Step 1 — Write down input and output shapes

```python
# 1_io.py
# In: dict from HTTP
# Out: User row id
# Sketch what happens between, one line per step.
```

Lock down types and shapes before code.

### Step 2 — Split into step functions

```python
# 2_steps.py
def parse(payload) -> SignupCommand: ...
def validate(cmd: SignupCommand) -> SignupCommand: ...
def to_user(cmd: SignupCommand) -> User: ...
```

Every step states what it takes and what it returns.

### Step 3 — Push side effects to the end

```python
# 3_side_effects.py
def signup(payload):
    user = to_user(validate(parse(payload)))   # pure
    repo.save(user)                            # effect
    mailer.send(user.email)                    # effect
```

Validation and transformation stay pure; IO is last.

### Step 4 — Use immutable data

```python
# 4_immutable.py
from dataclasses import dataclass
@dataclass(frozen=True)
class User:
    id: str
    email: str
```

Return new values instead of mutating state.

### Step 5 — One direction only

```python
# 5_one_way.py
# UI -> command -> domain -> event
# events flow back to UI.
# No silent mid-flow data updates.
```

Breaking cycles makes debugging easier.

## Quick Verification

Pick one request that often breaks and write down the input and output shape of every step. That single exercise usually reveals where values change silently.

```text
payload(dict) -> SignupCommand -> User -> saved User -> notification event
```

**Expected output:** you should be able to explain which steps are pure transformations and which steps are side effects.

If it helps, imagine logging the value before and after each step. A one-way flow makes even the log-reading order simple.

## Failure Signals and First Checks

| Failure signal | First check |
| --- | --- |
| Multiple functions mutate the same dict | Check whether you can return new values instead |
| A DB call appears in the middle of validation | Separate pure transformation from side effects again |
| You cannot tell where the value changed | Write down the input/output types step by step first |

Once the flow is visible, debugging changes from “read everything” to “which step distorted the data?”

## What to Notice in This Code

- Each step has a narrow responsibility.
- Side effects are concentrated on one side.
- Data does not flow backwards.

## Five Common Mistakes

1. **Mixing side effects into transformation functions.** Tests get hard.
2. **Multiple steps mutate a shared mutable object.** You cannot tell who changed it.
3. **IO calls in the middle of the flow.** The flow turns to mud.
4. **Untyped dicts as the only data shape.** Shape varies on every call.
5. **Two-way binding everywhere.** Cause and effect blur.

## How This Shows Up in Production

ETL jobs, request processing pipelines, unidirectional UI flows like React — data flow design is everywhere once you start looking.

## How a Senior Engineer Thinks

- They check whether the flow is one-directional first.
- They push side effects to the edge.
- They make immutable data the default.
- They cut steps small and compose them.
- When debugging, they pinpoint which step changed the data.

## Checklist

- [ ] Does the data flow in a single direction?
- [ ] Are side effects at the edges?
- [ ] Are steps small with clear responsibilities?
- [ ] Is the data immutable?
- [ ] Are shapes guaranteed by types?

## Practice Problems

1. Pick one function in your code and split side effects from pure transformation.
2. Convert a dict-based input into a dataclass.
3. Find a place where the flow goes backwards and write down what you would do about it.

## Wrap-up and Next Steps

Once the flow is visible, change is no longer scary. Next up we look at the design that limits how far that change can spread — reducing change impact.

## Answering the Opening Questions

- **What does "designing data flow" concretely mean?**
  It means specifying the data shape and transformation stages from input to output—like `payload(dict) -> SignupCommand -> User -> saved User -> notification event`. Making each stage's input/output explicit (`parse`, `validate`, `normalize`, `persist`, `notify`) is the core.
- **Why should data flow in only one direction between input and output?**
  When multiple functions mutate the same `req` dict, tracking where values went wrong is hard. A unidirectional pipeline narrows the problem stage immediately. Maintaining the flow from UI → command → domain → event keeps debugging and log interpretation simple.
- **How should you separate transformation stages from side effects?**
  Keep pure transformations like `to_user(validate(parse(payload)))` on the inside, and push side effects like `repo.save(user)` and `mailer.send(user.email)` to the edges. Using `@dataclass(frozen=True)` for immutable data further prevents sneaky mid-pipeline mutations.

<!-- toc:begin -->
## In this series

- [Software Design 101 (1/10): What Is Software Design?](./01-what-is-software-design.md)
- [Software Design 101 (2/10): Separation of Concerns](./02-separation-of-concerns.md)
- [Software Design 101 (3/10): Modules and Boundaries](./03-modules-and-boundaries.md)
- [Software Design 101 (4/10): Dependency Direction](./04-dependency-direction.md)
- [Software Design 101 (5/10): Interfaces and Abstraction](./05-interfaces-and-abstraction.md)
- [Software Design 101 (6/10): Layered Architecture](./06-layered-architecture.md)
- **Data Flow Design (current)**
- Reducing Change Impact (upcoming)
- Design Principles (upcoming)
- Practicing Design with a Small Project (upcoming)

<!-- toc:end -->

## References

- [Functional Core, Imperative Shell (Gary Bernhardt)](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Out of the Tar Pit (Moseley & Marks)](https://curtclifton.net/papers/MoseleyMarks06a.pdf)
- [Flux Architecture — Unidirectional Data Flow](https://facebookarchive.github.io/flux/)
- [Designing Data-Intensive Applications — Batch and Stream](https://dataintensive.net/)

### Practical Docs

- [dataclasses — Data Classes](https://docs.python.org/3/library/dataclasses.html)
- [typing.NamedTuple](https://docs.python.org/3/library/typing.html#typing.NamedTuple)

Tags: Computer Science, SoftwareDesign, DataFlow, Pipelines, Immutability, FunctionalDesign
