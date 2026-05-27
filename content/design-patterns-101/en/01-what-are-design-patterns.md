---
series: design-patterns-101
episode: 1
title: "Design Patterns 101 (1/10): What Are Design Patterns?"
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
  - DesignPatterns
  - SoftwareDesign
  - GoF
  - Architecture
  - Foundations
seo_description: A practical introduction to design patterns, the GoF families, and the recurring design problems patterns help teams name and solve.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (1/10): What Are Design Patterns?

When I first learned design patterns, I started by memorizing names. Singleton, Strategy, Adapter, Observer, Factory. The GoF book lines up 23 of them, so the natural impression is "I need to know all of these to write good code." But the moment patterns actually prove their worth in practice is different. It is not on an exam. It is in a code review, when someone writes "this branching keeps growing — how about pulling it into a Strategy?" and every person on the team pictures the same structure instantly.

This is the first post in the Design Patterns 101 series. I want to redefine design patterns not as "23 answers to memorize" but as **shared vocabulary for naming recurring design problems and reaching agreement quickly**. The weight of the names comes after that.

![Design Patterns 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/01/01-01-concept-at-a-glance.en.png)

*From problem recognition to pattern selection*

## Questions to Keep in Mind

- What does the term "design pattern" actually refer to?
- How is memorizing pattern names different from understanding patterns?
- Where does the gap show up between a team that uses patterns and one that does not?

## Redefining Design Patterns in One Sentence

A design pattern is not "write this code in this shape." More precisely, it is **a name attached to a solution that people have repeatedly reached when the same kind of problem keeps appearing**. The core of a pattern is not code — it is a problem-solution pair.

Why does this matter? Because the same pattern looks completely different depending on the language. In Java, Singleton typically means a `private` constructor plus a `static` instance. In Python, a module is imported only once, so a plain module-level variable is more natural. The code differs, but both are the same pattern — because the problem they solve, "share a single instance globally," is the same.

So learning a pattern means acquiring two things simultaneously:

1. Which problem signals should trigger which pattern candidates in my head
2. How to express that pattern most naturally in the language I use

If these two are not separated, the result is knowing "how to write a Singleton class" without knowing "what problem Singleton is trying to solve." Applying patterns from that state almost always produces over-engineering.

## Why the GoF's 23 Patterns Split Into Three Groups

The 1994 book *Design Patterns: Elements of Reusable Object-Oriented Software* — commonly called the GoF (Gang of Four) book — classifies 23 patterns into three families.

| Family | Problem it addresses | Representative patterns |
| --- | --- | --- |
| Creational | How objects are created and who makes that decision | Factory Method, Builder, Singleton |
| Structural | How objects are composed and how interfaces are aligned | Adapter, Decorator, Facade |
| Behavioral | How responsibility is distributed and how objects communicate | Strategy, Observer, Command |

This classification is not exam trivia. It is a tool for quickly narrowing down "which pattern fits here" during a code review. When object-creation code keeps getting complicated, I look at Creational first. When an external API does not match the shape I need, I look at Structural. When the same action needs to be swapped between multiple implementations at runtime, I look at Behavioral.

Articles 2 through 4 in this series cover each family in one chapter, and articles 5 through 7 go deep on Strategy, Adapter, and Observer — the three I reach for most often in production. For now, the goal is not memorizing the classification itself but developing a feel for which family a given problem belongs to.

## The Value of a Pattern, Shown in One Code Block

Theory is less clear than a short code sample. Suppose a payment-processing function started like this:

```python
def charge(kind: str, amount: int) -> None:
    if kind == "credit":
        # Call Stripe API
        ...
    elif kind == "paypal":
        # Call PayPal API
        ...
    elif kind == "kakao_pay":
        # Call KakaoPay API
        ...
    else:
        raise ValueError(f"unsupported: {kind}")
```

At first this is fine. With two payment methods, it is the most readable option. But once payment methods grow to five, each one needs refund logic, and some require webhook verification, this single function balloons. The same `if kind == ...` shape gets copied across the codebase. Adding a new payment method means opening multiple files simultaneously, and forgetting one of them produces a subtle bug.

Someone who knows the Strategy pattern sees this moment and one phrase surfaces: "branch explosion." The restructuring looks like this:

```python
from typing import Protocol

class PaymentProcessor(Protocol):
    def charge(self, amount: int) -> None: ...
    def refund(self, amount: int) -> None: ...

PROCESSORS: dict[str, PaymentProcessor] = {
    "credit": StripeProcessor(),
    "paypal": PaypalProcessor(),
    "kakao_pay": KakaoPayProcessor(),
}

def charge(kind: str, amount: int) -> None:
    PROCESSORS[kind].charge(amount)
```

The point is not that the code got shorter. The point is that **adding a new payment method changed from "modify an existing function" to "add one new class + one dict entry."** The shape of change itself changed. Being able to name that difference in a single word is exactly the value of a pattern. Anyone on the team can share this intent with one phrase: "pull it into a Strategy."

## The Real Effect Patterns Create: Agreement Speed

I believe the biggest gap between a senior engineer and a junior is not "writing code faster" but "reaching agreement with the team faster." Patterns raise that agreement speed decisively.

Imagine this comment appears in a review:

> "Instead of calling the external SDK directly here, wrap it in an Adapter. That way tests can cut the SDK dependency, and if the SDK gets swapped later, domain code stays untouched."

Writing that paragraph without the pattern name takes two paragraphs. What interface to create, why it is needed, what the benefit is — all spelled out. The single word "Adapter" compresses those two paragraphs. The reader also thinks "right, Adapter — I can picture the structure" and moves on.

The flip side is more dangerous. If someone knows only the name and not the problem, saying "Observer fits here" without being able to explain why turns the pattern from a tool that creates simplicity into **a label that justifies complexity**. That is why, whenever introducing a pattern, the habit of first articulating "what problem am I solving" matters.

## The Cost of Misapplying a Pattern

Patterns are not free. Gaining something on one side means losing something on the other. Without accounting for this cost upfront, a pattern degrades code quality.

Honestly listing what the Strategy refactoring above lost:

- **More classes to read.** A flow that used to end in one function now requires following a Protocol, multiple implementations, and a dict.
- **An extra level of indirection.** Tracing "where exactly does this payment get processed" now requires one more dict lookup.
- **Slightly longer tests.** Cases arise where a fake Processor must be created and injected.

If these costs are smaller than the gains, the pattern is worth introducing. If there are only two payment methods and that number is clearly staying at two, the costs above outweigh the branch-explosion cost. In that case, plain `if/elif` is the right answer. Deciding whether to apply a pattern is closer to a bet on future change likelihood.

I recommend that teams leave a short note every time they introduce a pattern. It does not need to be long:

```text
# decisions/payment-strategy.md
- Pattern: Strategy
- Reason: payment methods grew from 2 to 5; each has distinct charge/refund/webhook flows
- Cost: +5 classes, 1 dict lookup
- Revisit when: payment methods drop back to 2 or fewer, or behaviors become identical
```

With a record like this, when a new teammate joins six months later and asks "why is this so complex," the answer takes thirty seconds: "branching was at five back then, and here is the tradeoff we chose." A pattern is a decision, and decisions become assets only when recorded.

## Not Everything Is a Pattern

One last distinction is necessary. Many shapes that appear frequently in code are not patterns — they are **idioms** or **language features**.

- Python's context manager (`with` statement) is not a pattern but a **language feature**. It is closer to the language directly supporting a concept like RAII.
- List comprehensions (`[x*2 for x in items]`) are not a pattern but an **idiom**. They are a natural expression in a specific language, not a structural solution portable to other languages.
- Expressing value objects with `dataclass` is also more language feature than pattern.

Why does this distinction matter? If every good coding habit gets called a "pattern," the agreement-speed value that the word "pattern" carries gets diluted. Keeping "pattern" reserved for language-independent problem-solution structures is cleaner.

## One Takeaway From This Chapter

If I had to pick a single thing to carry away from this chapter, it would be this: **before memorizing a pattern name, be able to state in one sentence what problem it solves and what cost it introduces.** With that ability, five to seven patterns are powerful enough for production work without memorizing all twenty-three. Without it, memorizing all twenty-three still creates a burden on the team every time one gets applied.

The next chapter covers Creational patterns, the first of the GoF families. Starting from the question "how are objects created, and who makes that decision," it begins with why Factory Method and Builder exist.

## Answering the Opening Questions

- **What does the term "design pattern" actually refer to?**
  - Not code but a **problem-solution pair**. It is a name attached to "a shape people have repeatedly used when this kind of problem keeps appearing," which is why the same pattern has different implementations across languages. Singleton is a `private` constructor plus `static` instance in Java but a module variable in Python — same pattern, same problem.
- **How is memorizing pattern names different from understanding patterns?**
  - Memorizing names tells you "what code to write" but not "why." As the payment-branching example showed, the same Strategy is over-engineering with two payment methods and appropriate abstraction with five. The core of understanding a pattern is **being able to judge when the cost is worth paying**.
- **Where does the gap show up between a team that uses patterns and one that does not?**
  - More in **agreement speed** than in code quality. One sentence — "wrap it in an Adapter here" — compresses two paragraphs of explanation. But this effect appears only when the entire team shares the same vocabulary. If only one person uses pattern names, communication cost actually increases.

<!-- toc:begin -->
## In this series

- **What Are Design Patterns? (current)**
- Creational Patterns (upcoming)
- Structural Patterns (upcoming)
- Behavioral Patterns (upcoming)
- The Strategy Pattern (upcoming)
- The Adapter Pattern (upcoming)
- The Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)

<!-- toc:end -->

## References

### Core References

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [refactoring.guru — Design Patterns](https://refactoring.guru/design-patterns)
- [Patterns of Enterprise Application Architecture (Fowler)](https://martinfowler.com/eaaCatalog/)

### Practical Extensions

- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)
- [Refactoring (Martin Fowler)](https://martinfowler.com/books/refactoring.html)
- [Series example code (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, SoftwareDesign, GoF, Architecture, Foundations
