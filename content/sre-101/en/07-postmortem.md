---
series: sre-101
episode: 7
title: "SRE 101 (7/10): Postmortem"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SRE
  - Postmortem
  - BlamelessCulture
  - Learning
  - Operations
seo_description: A beginner-friendly guide to postmortems covering definitions, blameless culture, writing templates, action tracking, and organizational learning
last_reviewed: '2026-05-14'
---

# SRE 101 (7/10): Postmortem

Once an incident is mitigated, teams feel relief first. That is natural, but it also creates the risk that recovery becomes the end of the story even when the same weakness is still sitting in the system.

Postmortems matter because they capture what was visible, what was missing, why decisions made sense at the time, and what has to change so the next incident is smaller or easier to resolve.

This is post 7 in the SRE 101 series. Here we treat postmortems as a learning system built from blameless analysis, reusable structure, and tracked follow-up work.

## Questions to Keep in Mind

- Why is a postmortem closer to an organizational learning tool than to a simple report?
- Why does blame suppress the very context a team needs to improve?
- What sections should a useful postmortem always contain?

## Big Picture

![sre 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/07/07-01-concept-at-a-glance.en.png)

*sre 101 chapter 7 flow overview*

This picture places Postmortem inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why this topic matters

Repeated outages are often the result of missing learning, not missing effort. If the team cannot preserve the timeline, causes, and follow-up changes, the next incident starts from the same weak foundation.

Good postmortems turn one painful event into shared operating knowledge. That is how incident response becomes better over time instead of merely familiar.

> A postmortem is a learning system, not a document.

## Concept at a glance

## Key Terms

- **postmortem**: a *post-incident analysis* document.
- **blameless**: a *no-blame* principle.
- **timeline**: the *event flow*.
- **root cause**: the *underlying* cause.
- **action item**: a *follow-up action*.

## Before/After

**Before**: hunt down the *responsible person*.

**After**: analyze the *system weaknesses*.

## Hands-on: Writing a Postmortem

### Step 1 — Define the template

```python
template = {
    "title": "",
    "summary": "",
    "impact": "",
    "timeline": [],
    "root_cause": "",
    "actions": [],
    "lessons": [],
}
```

### Step 2 — Summarize impact

```python
def impact_line(users, minutes):
    return f"{users} users affected for {minutes} min"
```

### Step 3 — Timeline

```python
def event(t, msg):
    return {"time": t, "event": msg}
```

### Step 4 — Action items

```python
def action(desc, owner, due):
    return {"desc": desc, "owner": owner, "due": due}
```

### Step 5 — Track them

```python
def open_actions(items):
    return [a for a in items if not a.get("done")]
```

## What to Notice in This Code

- The *template* substitutes for *memory*.
- *Owner* and *due date* are the *tracking axes*.
- *Lessons* become *reusable* assets.

## Five Common Mistakes

1. **Personal *blame* leading to *silence*.**
2. ***No tracking* of *action items*.**
3. **Mistaking *symptoms* for *root cause*.**
4. **Failing to *share* the result.**
5. **Filling in the *template* without any real *learning*.**

## How This Shows Up in Production

*Jira* or *Linear* tickets track each action; a *weekly review* checks progress.

## How a Senior Engineer Thinks

- *Blameless* invites the *truth*.
- The *cause* lives in the *system*.
- A document *without actions* is *waste*.
- *Recurrence prevention* is *proven by changes*.
- *Learning* spreads through *openness*.

## Checklist

- [ ] *Template* agreed.
- [ ] *Blameless* principle.
- [ ] *Action tracking*.
- [ ] *Shared* channel.

## Practice Problems

1. Define *blameless* in one line.
2. Define *root cause* in one line.
3. Define *action item* in one line.

## Wrap-up and Next Steps

Next, we cover *reducing toil*.

## Answering the Opening Questions

- **Why is a postmortem closer to an organizational learning tool than to a simple report?**
  - The article treats Postmortem as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why does blame suppress the very context a team needs to improve?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What sections should a useful postmortem always contain?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- **Postmortem (current)**
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Etsy Debriefing Guide](https://extfiles.etsy.com/DebriefingFacilitationGuide.pdf)
- [Blameless Postmortems - Atlassian](https://www.atlassian.com/incident-management/postmortem/blameless)
- [PagerDuty Postmortem Guide](https://postmortems.pagerduty.com/)

Tags: SRE, Postmortem, BlamelessCulture, Learning, Operations
