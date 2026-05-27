---
series: incident-response-101
episode: 9
title: "Incident Response 101 (9/10): Prevention"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Incident
  - Prevention
  - Reliability
  - Testing
  - Operations
seo_description: Learn how to convert postmortem learning into regression tests, guardrails, chaos drills, and tracked prevention work.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (9/10): Prevention

An incident is not truly closed when the postmortem is published. It is closed when the learning is pushed back into code, tests, automation, and operating constraints that make the same failure harder to repeat.

Teams that stop at documentation keep relearning the same lesson. Teams that attach regression tests, guardrails, and review loops turn each incident into a measurable reliability improvement.

This is the 9th post in the Incident Response 101 series. This post explains how to prioritize prevention work and how to make follow-up items survive beyond the week after the outage.


![incident response 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/09/09-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 9 flow overview*
> Prevention items that are specific + measurable + assigned = items that actually get done.

## Questions to Keep in Mind

- Why do incidents repeat even after strong postmortems?
- Which follow-up items deserve regression tests first?
- How do guardrails differ from warnings or documentation?

## Why this topic matters

Teams get weaker over time when they depend on memory. They get stronger over time when each incident leaves behind a test, a blocking control, or a better operating default.

That is why prevention is best treated as an engineering output. Good intentions do not survive turnover or fatigue; tests and safeguards do.

## Diagram at a glance

The loop matters as much as the individual controls. Action items become tests, tests become guardrails, and experiments verify that the protection still works under failure.

## Key Terms

- **action item**: a postmortem follow-up.
- **regression test**: confirms the same bug does not return.
- **guardrail**: code that blocks dangerous actions.
- **chaos exp**: intentional failure injection.
- **learning loop**: the cycle of learning.

## Before/After

**Before**: only a document remains after the postmortem.

**After**: code and tests remain after the postmortem.

## Hands-on: A Prevention Kit

### Step 1 — Register an action

```python
def register(action):
    return {**action, "status": "open"}
```

### Step 2 — Regression test

```python
def test_regression(scenario, run):
    return run(scenario) == "ok"
```

### Step 3 — Guardrail

```python
def guard(payload, limit=1000):
    if payload > limit:
        raise ValueError("blocked")
```

### Step 4 — Chaos experiment

```python
def inject(failure):
    return {"injected": failure, "expected": "graceful"}
```

### Step 5 — Learning loop

```python
def closed(action):
    return action["status"] == "done"
```

## What to Notice in This Code

- Status has two values: open/done.
- A guardrail is one raise.
- Chaos always pairs with an expected result.

## Five Common Mistakes

1. **Registering actions and then abandoning them.**
2. **Skipping the regression test.**
3. **Leaving the guardrail as a warning only.**
4. **Stating hypotheses without chaos.**
5. **The loop never crosses a quarter.**

## How This Shows Up in Production

Every postmortem action is linked into Jira, converted into regression tests and chaos scenarios, and run weekly in CI.

## How a Senior Engineer Thinks

- Prevention is code.
- The document is the starting point.
- Chaos is your friend.
- The loop is the quarterly review.
- Repetition equals failed learning.

## Prioritizing prevention work

Not every prevention item belongs in the same bucket. A simple priority table helps the team focus on work that most directly reduces repeat risk.

| Item | Repeat-risk reduction | Delivery cost | Priority |
| --- | --- | --- | --- |
| Add a regression test | High | Low | Immediate |
| Add a feature flag or kill switch | High | Medium | High |
| Rework architecture for long-term resilience | High | High | Quarterly planning |
| Expand wiki documentation | Low | Low | Supporting work |

Documentation still matters, but tests and guardrails usually deserve priority because they block the failure path directly.

## Checklist

- [ ] Action tracking.
- [ ] Regression tests.
- [ ] Guardrail policy.
- [ ] Chaos schedule.

## Practice Problems

1. Define guardrail in one line.
2. Define regression test in one line.
3. Define learning loop in one line.

## Wrap-up and Next Steps

Next is the capstone: Building an Incident Runbook.

## Answering the Opening Questions

- **Why do incidents repeat even after strong postmortems?**
  - The article treats Prevention as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which follow-up items deserve regression tests first?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How do guardrails differ from warnings or documentation?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity Classification](./02-severity.md)
- [Incident Response 101 (3/10): Initial Response](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Writing the Timeline](./05-timeline.md)
- [Incident Response 101 (6/10): Root Cause Analysis](./06-root-cause-analysis.md)
- [Incident Response 101 (7/10): Mitigation and Resolution](./07-mitigation-and-resolution.md)
- [Incident Response 101 (8/10): Postmortem](./08-postmortem.md)
- **Prevention (current)**
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Postmortem Action Items - Google SRE Workbook](https://sre.google/workbook/postmortem-culture/)
- [Preventing recurrence - PagerDuty](https://response.pagerduty.com/after/preventing/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)
- [Guardrails, not gates - Thoughtworks](https://www.thoughtworks.com/insights/blog/guardrails-not-gates)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Prevention, Reliability, Testing, Operations
