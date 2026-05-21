---
series: developer-career-101
episode: 6
title: "Developer Career 101 (6/10): System Design Interviews"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
- Career
- Interview
- SystemDesign
- Architecture
- Beginner
seo_description: A beginner-friendly tour of the four-step system design interview
  procedure and evaluation criteria.
last_reviewed: '2026-05-14'
---

# Developer Career 101 (6/10): System Design Interviews

System design interviews can look like a whiteboard drawing exercise from the outside. What interviewers actually value is whether you can frame requirements, make rough estimates, propose a plausible architecture, and explain trade-offs in a way that shows judgment under constraints.

This is post 6 in the Developer Career 101 series.


![developer career 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/developer-career-101/06/06-01-concept-at-a-glance.en.png)
*developer career 101 chapter 6 flow overview*
> System design is not about the perfect answer; it is about understanding requirements, making assumptions explicit, and explaining your tradeoffs clearly.

## Questions to Keep in Mind

- What are interviewers truly evaluating in a system design round?
- In what order should you move through requirements, estimates, high-level design, and deep dives?
- Why do trade-offs and bottlenecks separate shallow answers from senior ones?

## What You Will Learn

- The *four-step* procedure
- Eliciting *requirements*
- *Back-of-envelope* estimates
- *Component* design
- *Deep dive* and trade-offs

## Why It Matters

Design is the senior-level filter.

System design is about making requirements explicit, exploring tradeoffs, and defending your choices.

## Key Terms

- **functional**: Feature requirements.
- **non-functional**: Performance and availability.
- **estimate**: Rough calculation.
- **trade-off**: Cost of a choice.
- **bottleneck**: The limiting component.

## Before/After

**Before**: "I just sketch boxes."

**After**: "I walk requirements, estimate, design, deep dive — in order."

## Hands-on: Design a URL Shortener

### Step 1 — Requirements

```text
functional: shorten, redirect, analytics
non-functional: 100M URLs, 99.99% availability
```

### Step 2 — Estimate

```text
QPS: 1000 reads/s, 10 writes/s
storage: 100M * 500 bytes = 50 GB
```

### Step 3 — Components

```text
LB → API → KV store
analytics → Kafka → DW
```

### Step 4 — Deep Dive

```text
- collision: base62 + counter
- cache: redis (LRU)
- DR: multi-AZ
```

### Step 5 — Trade-offs

```text
SQL vs KV: consistency vs performance
```

## Questions that make a design answer feel senior

| Phase | Question to ask yourself | What must stay in the answer |
| --- | --- | --- |
| Requirements | Which user path matters most right now? | Functional vs non-functional split |
| Estimate | How do read/write ratios change the storage choice? | QPS, storage, growth assumptions |
| High-level design | Where does the first serious bottleneck appear? | Main flow and storage boundaries |
| Deep dive | Which design choice creates the largest cost? | Caching, consistency, and recovery trade-offs |

## Questions that make a design answer feel senior

| Phase | Question to ask yourself | What must stay in the answer |
| --- | --- | --- |
| Requirements | Which user path matters most right now? | Functional vs non-functional split |
| Estimate | How do read/write ratios change the storage choice? | QPS, storage, growth assumptions |
| High-level design | Where does the first serious bottleneck appear? | Main flow and storage boundaries |
| Deep dive | Which design choice creates the largest cost? | Caching, consistency, and recovery trade-offs |

## Questions that make a design answer feel senior

| Phase | Question to ask yourself | What must stay in the answer |
| --- | --- | --- |
| Requirements | Which user path matters most right now? | Functional vs non-functional split |
| Estimate | How do read/write ratios change the storage choice? | QPS, storage, growth assumptions |
| High-level design | Where does the first serious bottleneck appear? | Main flow and storage boundaries |
| Deep dive | Which design choice creates the largest cost? | Caching, consistency, and recovery trade-offs |

## What to Notice in This Code

- Requirements come first.
- Estimates ground the design.
- Deep dive shows seniority.

## Five Common Mistakes

1. **Skipping requirements.**
2. **No estimates.**
3. **Not stating trade-offs.**
4. **Not knowing the bottleneck.**
5. **Bad time management.**

## How This Shows Up in Production

Companies use the same frame when writing internal RFCs.

## How a Senior Engineer Thinks

- Design is a conversation.
- Estimation is muscle.
- Trade-offs are a language.
- Deep dive is depth.
- Time management is training.

## Checklist

- [ ] Functional and non-functional split.
- [ ] Estimates explicit.
- [ ] Trade-offs stated.
- [ ] One bottleneck deep dive.

## Practice Problems

1. One line: define QPS.
2. One line: example of a non-functional requirement.
3. One line: example of a bottleneck.

## Wrap-up and Next Steps

Next post covers *Settling into the First Job*.

## Answering the Opening Questions

- **What are interviewers truly evaluating in a system design round?**
  - The article treats System Design Interviews as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **In what order should you move through requirements, estimates, high-level design, and deep dives?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why do trade-offs and bottlenecks separate shallow answers from senior ones?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Developer Career 101 (1/10): What Is a Developer Career](./01-what-is-developer-career.md)
- [Developer Career 101 (2/10): Understanding Roles](./02-understanding-roles.md)
- [Developer Career 101 (3/10): Building a Learning Plan](./03-learning-plan.md)
- [Developer Career 101 (4/10): Resume and Portfolio](./04-resume-and-portfolio.md)
- [Developer Career 101 (5/10): Preparing for Coding Interviews](./05-coding-interview.md)
- **System Design Interviews (current)**
- Settling into the First Job (upcoming)
- Side Projects and Learning (upcoming)
- Mentoring and Networking (upcoming)
- The Path to Senior (upcoming)

<!-- toc:end -->

## References

- [Designing Data-Intensive Applications](https://dataintensive.net/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [High Scalability](http://highscalability.com/)
- [Google SRE Book](https://sre.google/books/)

Tags: Career, Interview, SystemDesign, Architecture, Beginner
