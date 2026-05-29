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

Registering action items as "open" is the first step that turns a postmortem conclusion into trackable work. Without this explicit state transition, follow-up tasks live only in meeting notes and disappear within days.


### Step 2 — Regression test

```python
def test_regression(scenario, run):
    return run(scenario) == "ok"
```

A regression test encodes the exact failure scenario so that CI catches the same defect if it is ever reintroduced. Human memory decays; an automated test does not.


### Step 3 — Guardrail

```python
def guard(payload, limit=1000):
    if payload > limit:
        raise ValueError("blocked")
```

A guardrail blocks the dangerous input outright rather than logging a warning and hoping someone notices. The difference between a warning and a raise is the difference between "we knew it was bad" and "we stopped it from being bad."


### Step 4 — Chaos experiment

```python
def inject(failure):
    return {"injected": failure, "expected": "graceful"}
```

Chaos experiments validate that the regression test and guardrail actually work under realistic failure conditions. Pairing every injection with an expected outcome turns the experiment into a pass/fail assertion rather than an open-ended exploration.


### Step 5 — Learning loop

```python
def closed(action):
    return action["status"] == "done"
```

The learning loop closes when every action item reaches "done." If the loop never completes—items stay open for months—the organization accumulates unresolved risk that compounds with each new incident.


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

- **Why does the same incident recur even after a postmortem?**
  - Even a well-written postmortem document is useless if its action items never enter someone's backlog—or enter but keep losing priority. Analysis only produces "understanding"; "change" comes exclusively from executing follow-up work.
- **What goes wrong when action items aren't tracked?**
  - Without tracking, no one knows who owns what or how far it's progressed. When the same class of incident fires again, the new postmortem can't even find evidence that the item existed before. Untracked learning accumulates into an organization that never improves. Every action item must be reduced to a ticket with an owner and a due date.
- **Why are regression tests the core of recurrence prevention?**
  - Hardening a once-failing scenario into an automated regression test (or monitoring synthetic, or chaos test) means the CI or alerting system blocks the same defect before a human notices it. Human memory and documents decay over time, but automated checks keep the same strength indefinitely.
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
