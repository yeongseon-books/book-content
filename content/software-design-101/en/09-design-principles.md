---
series: software-design-101
episode: 9
title: Design Principles
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
  - SOLID
  - KISS
  - YAGNI
  - Principles
seo_description: A tour of SOLID, KISS, YAGNI, DRY, and the Law of Demeter, with notes on when to actually reach for each.
last_reviewed: '2026-05-15'
---

# Design Principles

Design principles sound abstract when treated as slogans. They become useful the moment a code smell forces you to ask what kind of structural mistake you are actually looking at.

This is post 9 in the Software Design 101 series.

In this post, we recast SOLID, KISS, YAGNI, DRY, and the Law of Demeter as diagnostic tools. The point is not memorization. The point is knowing which question to ask, and which refactoring direction follows from the answer.

> Principles earn their keep when they turn vague discomfort into a concrete next move.

## What You Will Learn

- The five SOLID principles in plain terms
- Where KISS and YAGNI fit
- The DRY trap
- The Law of Demeter
- *When* to actually pull each principle off the shelf

## Why It Matters

Principles are diagnostic tools, not commandments. When the code smells, they point at which principle was broken and hint at how to fix it.

> Principles make you ask "why?"

## Concept at a Glance

![Concept at a Glance](../../../assets/software-design-101/09/09-01-concept-at-a-glance.en.png)
*Design principles are most useful when they translate a code smell into a refactoring direction*

Smell → principle → refactor.

## Key Terms

- **SRP**: A module should have one reason to change.
- **OCP**: Open for extension, closed for modification.
- **LSP**: Subtypes must be usable in place of their supertypes.
- **ISP**: Callers should not depend on interfaces they do not use.
- **DIP**: Depend on abstractions, not concretions.
- **KISS / YAGNI / DRY / Law of Demeter**: Supporting principles — keep it simple, do not build it yet, suspect repetition, do not talk to your friend's friend.

## Before / After

**Before**

```python
class UserService:
    def signup(self, payload):
        # validation + storage + email + analytics + logging + billing
        ...
```

**After**

```python
class SignupValidator: ...
class UserRepo: ...
class WelcomeMailer: ...
class SignupService:
    def __init__(self, validator, repo, mailer): ...
    def run(self, payload): ...
```

SRP applied — small collaborators in place of one giant class.

## Hands-on: Five Situations Where a Principle Fires

### Step 1 — "Why is this class so big?" → SRP

```python
# 1_srp.py
# More than one reason to change → split.
```

### Step 2 — "Another if-elif chain" → OCP

```python
# 2_ocp.py
# Replace branching with polymorphism or a registry.
```

### Step 3 — "The subclass throws" → LSP

```python
# 3_lsp.py
# Suspect the inheritance hierarchy.
```

### Step 4 — "Methods I never call" → ISP

```python
# 4_isp.py
# Split the interface.
```

### Step 5 — "Domain knows the DB" → DIP

```python
# 5_dip.py
# Move the abstraction to the domain side.
```

## Quick Verification

Knowing the names is less important than knowing which question to ask when a smell appears. Take one recent review example and map it like this.

```text
giant class -> SRP
growing branch chain -> OCP
subtype throws -> LSP
read-only implementation still exposes write -> ISP
domain imports DB -> DIP
```

**Expected output:** if the smell, the principle, and the next refactoring move line up in one sentence, the principle is doing real work.

That is what makes code review sharper. Instead of “this feels wrong,” you can say “this looks like an SRP split candidate.”

## Failure Signals and First Checks

| Failure signal | First check |
| --- | --- |
| You know the principle name but not the next move | Map the smell to the principle first |
| DRY increases coupling instead of lowering it | Check whether the duplicated code truly changes for the same reason |
| A tiny script becomes ceremonially heavy | Recalibrate with YAGNI and KISS |

Principles are not universal rules. They are diagnostic cards that help you choose the next question and the next cut.

## What to Notice in This Code

- Each principle points at a different smell.
- Principles tell you to *fix* code, not just *judge* it.
- Apply one at a time and readability stays intact.

## Five Common Mistakes

1. **DRY overload.** Forcing accidentally similar code together blows up coupling.
2. **Ignoring YAGNI.** Adding abstractions for assumed future needs.
3. **SOLID obsession.** Even a small script gets a five-layer split.
4. **KISS as an excuse for laziness.** Avoidance, not simplicity.
5. **Treating principles as rules.** Context gets lost.

## How This Shows Up in Production

Principles become a shared vocabulary in code review. Saying "this looks like an SRP violation" makes everyone picture the same thing.

## How a Senior Engineer Thinks

- They use principles as diagnostic tools.
- They apply one at a time.
- They check coupling before reaching for DRY.
- They postpone abstraction with YAGNI in mind.
- They calibrate the strength of each principle to the system's size.

## Checklist

- [ ] Does the module have a single reason to change? (SRP)
- [ ] Can new features be added without modifying existing code? (OCP)
- [ ] Do subtypes honor the contract? (LSP)
- [ ] Are interfaces sized to their callers? (ISP)
- [ ] Does the domain depend only on abstractions? (DIP)

## Practice Problems

1. Find one SRP violation in your largest class and split it out.
2. Rewrite an if-elif chain through the lens of OCP.
3. List one abstraction you built last year that violates YAGNI.

## Wrap-up and Next Steps

Principles are guides. In the final episode we apply every tool from this series — to a small project.

<!-- toc:begin -->
- [What Is Software Design?](./01-what-is-software-design.md)
- [Separation of Concerns](./02-separation-of-concerns.md)
- [Modules and Boundaries](./03-modules-and-boundaries.md)
- [Dependency Direction](./04-dependency-direction.md)
- [Interfaces and Abstraction](./05-interfaces-and-abstraction.md)
- [Layered Architecture](./06-layered-architecture.md)
- [Data Flow Design](./07-data-flow-design.md)
- [Reducing Change Impact](./08-reducing-change-impact.md)
- **Design Principles (current)**
- Small Design Practice (upcoming)
<!-- toc:end -->

## References

- [SOLID Principles (Robert C. Martin)](https://web.archive.org/web/20151010224057/http://www.objectmentor.com/resources/articles/Principles_and_Patterns.pdf)
- [Law of Demeter](https://en.wikipedia.org/wiki/Law_of_Demeter)
- [The Wrong Abstraction (Sandi Metz)](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [YAGNI (Martin Fowler)](https://martinfowler.com/bliki/Yagni.html)

### Practical Docs

- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)


Tags: Computer Science, SoftwareDesign, SOLID, KISS, YAGNI, Principles
