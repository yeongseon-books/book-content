---
series: incident-response-101
episode: 6
title: "Incident Response 101 (6/10): Root Cause Analysis"
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
  - RCA
  - Postmortem
  - Analysis
  - Operations
seo_description: Learn how to separate triggers from root causes and turn RCA findings into action items that can be verified later.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (6/10): Root Cause Analysis

When an incident hurts production, the first visible event often gets blamed as the cause. A deployment happened before the outage, so the deployment gets blamed. A human ran a command, so the human gets blamed.

That reaction is understandable, but it is usually shallow. The trigger explains what fired last. The root cause explains why the system was still able to fail that way.

This is the 6th post in the Incident Response 101 series. This post shows how to separate triggers from structural causes, collect contributing factors, and turn an RCA into follow-up work that can actually be verified.


![incident response 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/06/06-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 6 flow overview*
> RCA is not blame. It is a map of how multiple small gaps aligned to create impact.

## Questions to Keep in Mind

- How do you distinguish a trigger from a root cause?
- Why does the Five Whys method still help even in modern systems?
- Which contributing-factor axes are worth tracking explicitly?

## Why this topic matters

If the team only removes the trigger, the incident pattern returns with different packaging. A safer deployment process, stronger defaults, or better checks are often more important than the visible last event.

RCA is valuable when it changes the system. That means tracing beyond the obvious symptom and turning the result into work that can be owned, reviewed, and tested.

## Diagram at a glance

Each “why” step is a reminder not to stop at the first explanation. The useful endpoint is the structural condition that can be changed, not the easiest object to blame.

## Key Terms

- **trigger**: the event that fired directly.
- **root cause**: the condition that made it possible.
- **contributing factor**: a contributing element.
- **5 whys**: ask why five times.
- **systems thinking**: thinking in systems.

## Before/After

**Before**: mistake the trigger for the root cause.

**After**: trace down to the condition with the five whys.

## Hands-on: A Mini RCA Workbook

### Step 1 — Five whys

```python
def five_whys(start):
    chain = [start]
    for _ in range(5):
        chain.append(input(f"why? {chain[-1]} -> "))
    return chain
```

### Step 2 — Collect contributing factors

```python
def factors():
    return {"people": [], "process": [], "tooling": [], "system": []}
```

### Step 3 — Trigger vs root cause

```python
def classify(item, evidence):
    return "root" if evidence >= 3 else "trigger"
```

### Step 4 — Map to actions

```python
def actions(root):
    return [{"root": root, "action": f"fix {root}"}]
```

### Step 5 — Verifiable?

```python
def is_actionable(action):
    return action["action"].startswith(("add ", "fix ", "remove ", "test "))
```

## What to Notice in This Code

- A chain preserves depth.
- Contributing factors sit on four axes.
- Actions start with a verb.

## Five Common Mistakes

1. **Stopping at the first answer.**
2. **Naming a person as the root cause.**
3. **Fixing only the trigger and closing.**
4. **Vague, abstract actions.**
5. **Actions that cannot be verified.**

## How This Shows Up in Production

The postmortem doc embeds a Five Whys section and a Contributing Factors table as part of the template.

## How a Senior Engineer Thinks

- Suspect the system.
- Do not blame people.
- The root cause is usually process.
- Actions are measurable.
- The five whys is a starting point, not the end.

## Example: separating the trigger from the root cause

Imagine a checkout incident that starts right after a deployment.

- Trigger: a deployment introduced the wrong timeout value
- Contributing factor: staging never exercised realistic payment load
- Root cause: the deployment process allowed timeout changes to reach production without a regression gate
- Action item: add a timeout-focused regression test and block deployment when it fails

That framing changes the follow-up work. Instead of blaming the deployment itself, the team fixes the conditions that made the deployment unsafe.

## Checklist

- [ ] Template section.
- [ ] Four-axis factor model.
- [ ] Verb-first action rule.
- [ ] Verification criteria.

## Practice Problems

1. Distinguish trigger and root cause in one line.
2. Define the five whys in one line.
3. Define contributing factor in one line.

## Wrap-up and Next Steps

Next, we cover mitigation and resolution.

## Answering the Opening Questions

- **How do you find the real cause of an incident?**
  - Don't stop at "the component that broke." Ask why that component behaved that way at that moment, stepping back one layer at a time. Usually the answer is not a single line of code but a system-level weakness—an untested assumption, a missing alarm, or an omitted operational procedure. You've reached the real root cause when no new answers emerge.
- **Why is 5 Whys still useful?**
  - The tool is simple enough that anyone can use it immediately. Repeating "why?" naturally shifts blame from people to systems and processes. Five is not a magic number, but stopping at two or three leaves you at the surface, while going too deep makes answers overly abstract—five is an empirically reasonable depth.
- **Where does the line fall between trigger and root cause?**
  - A trigger is the direct stimulus that fired the incident at that moment (a specific deploy, a traffic spike, a particular input). A root cause is the structural weakness that prevented the system from withstanding that trigger. The same trigger might not cause an incident in a different system, so blocking only the trigger leaves you vulnerable to the next variant.
<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity Classification](./02-severity.md)
- [Incident Response 101 (3/10): Initial Response](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Writing the Timeline](./05-timeline.md)
- **Root Cause Analysis (current)**
- Mitigation and Resolution (upcoming)
- Postmortem (upcoming)
- Prevention (upcoming)
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Root cause analysis - PagerDuty](https://response.pagerduty.com/after/root_cause_analysis/)
- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem templates - Atlassian](https://www.atlassian.com/incident-management/postmortem/templates)
- [NIST SP 800-61 Rev. 2 Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, RCA, Postmortem, Analysis, Operations
