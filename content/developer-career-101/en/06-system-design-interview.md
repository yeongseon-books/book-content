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

This is the 6th post in the Developer Career 101 series.


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

System design is the senior-level filter. Interviewers care less about a perfect diagram and more about how you prioritize under constraints and explain your judgment.

> A system design interview is not a test of drawing nice boxes — it is a test of explaining decisions under constraints.

## Key Terms

- **functional requirement**: What the system must do (shorten URL, redirect, analytics).
- **non-functional requirement**: Performance and availability constraints (99.99% uptime, sub-100ms p95).
- **estimate**: A rough calculation that grounds the design in reality.
- **trade-off**: The cost attached to every design choice.
- **bottleneck**: The component that limits the entire system's throughput.

## Before/After

**Before**: "I just sketch boxes and hope it looks reasonable."

**After**: "I walk requirements, estimate, design, deep dive — in order — and articulate tradeoffs at every decision point."

## Hands-on: Design a URL Shortener

### Step 1 — Requirements

```text
functional: shorten, redirect, analytics
non-functional: 100M URLs, 99.99% availability
```

Splitting functional from non-functional requirements first sets the scope. Without this, you risk over-designing or heading in the wrong direction.

### Step 2 — Estimate

```text
QPS: 1000 reads/s, 10 writes/s
storage: 100M * 500 bytes = 50 GB
```

Estimation is not about getting the exact number — it is about grounding the design. Read/write ratio and storage volume immediately inform cache and storage technology choices.

### Step 3 — Components

```text
LB → API → KV store
analytics → Kafka → DW
```

At the high-level design stage, showing the main request path clearly is enough. Where requests enter, where they are stored, and where analytics data exits should be immediately visible.

### Step 4 — Deep Dive

```text
- collision: base62 + counter
- cache: redis (LRU)
- DR: multi-AZ
```

The deep dive picks one bottleneck or critical design decision and explores it thoroughly. Collision handling, cache strategy, and disaster recovery are where senior-level depth emerges.

### Step 5 — Trade-offs

```text
SQL vs KV: consistency vs performance
```

Without stating trade-offs, the design looks flat. Explaining what cost each choice carries reveals the quality of your judgment.

## Questions That Make a Design Answer Feel Senior

| Phase | Question to ask yourself | What must stay in the answer |
| --- | --- | --- |
| Requirements | Which user path matters most right now? | Functional vs non-functional split |
| Estimate | How do read/write ratios change the storage choice? | QPS, storage, growth assumptions |
| High-level design | Where does the first serious bottleneck appear? | Main flow and storage boundaries |
| Deep dive | Which design choice creates the largest cost? | Caching, consistency, and recovery trade-offs |

## Senior Capability Checklist

System design interviews are not architecture trivia tests. They validate senior capabilities: problem structuring, priority judgment, and trade-off explanation.

| Capability axis | Self-check question | Preparation artifact |
| --- | --- | --- |
| Requirements refinement | Can I clearly split functional vs non-functional? | Requirements template |
| Estimation sense | Can I quickly calculate QPS, storage, growth? | Back-of-envelope notes |
| Structuring ability | Can I explain components step by step? | 3 block diagrams |
| Trade-off articulation | Can I name the cost of each choice? | Alternatives comparison table |
| Operational perspective | Do I include failures, monitoring, recovery? | SLO / runbook draft |

## IC vs Manager Perspective

At senior levels, both individual contributor (IC) and manager perspectives are expected. Showing both in your design answer improves evaluation.

| Perspective | What to show in the answer |
| --- | --- |
| IC | Data structure, storage, cache, consistency choice rationale |
| Manager | Risk prioritization, timeline realism, operational ownership split |

For example, when explaining cache introduction, do not stop at "reduces response time." Continue to "if cache invalidation fails, what incident occurs and who owns the response?" — this is where depth separates.

## Mini-Framework for Higher Quality Answers

1. Redefine the problem in one sentence.
2. Pick the two most important non-functional requirements.
3. Present one simple baseline design first.
4. Deep-dive one bottleneck and compare alternatives.
5. Attach operational risk and monitoring metrics.

Following these five steps alone converts a scattered answer into a structured one.

## 6-Week System Design Preparation Schedule

System design prep is about repeating answer structure, not memorizing concepts.

| Week | Core topic | Practice | Retro point |
| --- | --- | --- | --- |
| Week 1 | Requirements framing | Chat system requirements 2x | Number of missed questions |
| Week 2 | Capacity estimation | URL shortener QPS/storage calc 3x | Unit conversion mistakes |
| Week 3 | Data modeling | Feed service schema design 2x | Normalization/denormalization rationale |
| Week 4 | Bottleneck / scaling strategy | Cache layer design 2x | Failure point identification |
| Week 5 | Consistency / availability | Order system transaction design | Compensation transaction explanation |
| Week 6 | Mock interviews | 60-min full simulation 2x | Time allocation stability |

The most important habit in this schedule is keeping a "failure log" each week. If you missed 3 of 8 requirement questions, re-run the same question set before moving to the next topic. The threshold for advancing is reproducibility, not a feeling of understanding.

## Leveling Matrix Connected to Promotion Criteria

System design answers map directly to leveling expectations — not just for hiring but for internal promotion.

| Evaluation item | Junior bar | Mid bar | Senior bar |
| --- | --- | --- | --- |
| Problem decomposition | Explains by feature | Includes traffic/failure scenarios | Structures up to business risk |
| Technology choice | Single solution proposed | Alternative comparison presented | Compares cost/ops/org impact |
| Scaling strategy | Mentions scale-out | Scales based on bottleneck analysis | Proposes staged migration plan |
| Operational perspective | Mentions logs/monitoring | Proposes SLI/SLO criteria | Designs on-call/recovery procedures |

Using this table while watching your mock interview recordings lets you assess your answer level far more objectively. It bridges the gap between "I know this" and "I can explain this."

## Architecture Trade-off Explanation Practice

The highest-leverage scoring area in system design interviews is trade-off explanation, not correct-answer presentation. For example, when introducing a cache, you must discuss not just read-performance gains but also invalidation cost and consistency degradation risk.

| Option | Advantage | Risk | When appropriate |
| --- | --- | --- | --- |
| Single DB scale-up | Simple operations | Vertical scaling limit | Early stage, low QPS |
| Read replicas | Easy read scaling | Replication lag | Read-heavy services |
| Sharding | Large scalability | Routing complexity increase | Data explosion phase |

In preparation, build at least three such tables for different service types. This improves both speed and accuracy when explaining trade-offs live.

## Design Answer Template

Below is a common sequence for a 45-60 minute design interview.

1. **Scope the problem**: Confirm users, features, non-functional requirements.
2. **Rough capacity**: QPS, storage volume, read/write ratio.
3. **API and data model**: Core entities and contracts.
4. **High-level architecture**: Request path, cache, async queue placement.
5. **Bottleneck / failure response**: Single point of failure, backpressure, retry policy.
6. **Closing trade-offs**: CAP / cost / operational complexity summary.

Interviewers value consistency in how you approach the problem more than a perfect final answer. Practicing the template aloud repeatedly builds answer stability under pressure.

## Post-Interview Debrief Sheet

After both mock and real interviews, debrief in a fixed format to accelerate improvement.

| Item | Example entry |
| --- | --- |
| What went well | Asked 6 requirement-clarifying questions |
| What was weak | Made 2 unit-conversion errors during estimation |
| Immediate fix | Create estimation flashcards and drill daily |
| Next practice | Re-attempt same problem within 48 hours |

## Whiteboard Explanation Rules

In design interviews, drawing quality reveals thinking quality. Fix component names first, label every arrow with request/response direction, and annotate bottleneck points with numeric justification. These habits dramatically improve explanation clarity.

## What to Notice in This Code

- Requirements come first — without them, design drifts.
- Estimates ground the design — they prevent over-engineering.
- Deep dive shows seniority — surface-level answers stay at mid-level.

## Five Common Mistakes

1. **Skipping requirements** — jumping to boxes without knowing the scope.
2. **No estimates** — design floats without numeric grounding.
3. **Not stating trade-offs** — makes every choice look arbitrary.
4. **Not identifying the bottleneck** — misses the opportunity to show depth.
5. **Bad time management** — spending 30 minutes on requirements leaves no time for depth.

## How This Shows Up in Production

Companies use the same frame when writing internal RFCs and design documents. Requirements, estimation, high-level structure, deep-dive, and trade-offs are not interview-only skills — they are how engineering organizations make decisions daily.

## How a Senior Engineer Thinks

- Design is a conversation, not a presentation.
- Estimation is muscle — it improves only with repetition.
- Trade-offs are the language of architecture.
- Deep dive is where depth becomes visible.
- Time management is trained, not improvised.

## Checklist

- [ ] Functional and non-functional requirements explicitly split.
- [ ] Back-of-envelope estimates stated (QPS, storage, growth).
- [ ] Trade-offs articulated at every major decision point.
- [ ] One bottleneck deep-dived with alternatives compared.

## Practice Problems

1. Define QPS in one sentence.
2. Give one example of a non-functional requirement.
3. Give one example of a system bottleneck.

## Wrap-up and Next Steps

System design interviews are not about producing a correct blueprint — they are about structuring requirements under time pressure and explaining judgment at each decision point. Internalizing the sequence of requirements, estimation, high-level design, and deep dive makes your answers dramatically more stable. The next post covers how to navigate your first 90 days at a new job.

## Answering the Opening Questions

- **What are interviewers truly evaluating in a system design round?**
  - There is no single correct answer. What matters is confirming requirements, stating constraints explicitly, and explaining trade-offs — the process reveals engineering judgment.
- **In what order should you move through requirements, estimates, high-level design, and deep dives?**
  - The order itself is the answer. You must decide what to prioritize among scalability, reliability, and cost, then show how cache-database consistency is maintained.
- **Why do trade-offs and bottlenecks separate shallow answers from senior ones?**
  - Proactively discovering bottlenecks before the interviewer asks, explaining why they exist, and proposing solutions demonstrates the initiative that separates senior from mid-level.
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
