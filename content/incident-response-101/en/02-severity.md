---
series: incident-response-101
episode: 2
title: "Incident Response 101 (2/10): Severity Classification"
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
  - Severity
  - Triage
  - Response
  - Operations
seo_description: Learn how to map incident impact to SEV levels, paging scope, and update cadence without leaving boundary cases ambiguous.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (2/10): Severity Classification

Once a team agrees on what counts as an incident, the next question is how serious that incident is. Not every incident deserves the same paging fan-out, the same update cadence, or the same leadership attention.

That is why severity is more than a label. It is the shorthand that turns impact into response behavior, escalation paths, and communication timing.

This is the 2nd post in the Incident Response 101 series. This post shows how to define SEV levels, how to map them to concrete actions, and how to keep boundary cases from turning into live arguments during an outage.


![incident response 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/02/02-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 2 flow overview*
> Severity is your team's shorthand for action. When someone says SEV1, everyone knows the scope, who pages, and how often to communicate.

## Questions to Keep in Mind

- What separates SEV1, SEV2, and SEV3 in practice?
- Which axes matter most: users, scope, revenue, legal exposure, or duration?
- How should severity affect paging and update cadence?

## Why this topic matters

Without severity, every incident starts with improvised negotiation. People debate the label, the audience, and the pacing at the exact moment when they should already be acting.

A strong severity system removes those debates from the live path. When someone says “SEV2,” the room should already know the expected fan-out, communication cadence, and decision urgency.

## Diagram at a glance

The point of the flow is the mapping step. Severity is not the impact itself; it is the operating language that turns impact into a response pattern.

## Key Terms

- **SEV1**: company-wide impact.
- **SEV2**: major feature degradation.
- **SEV3**: partial degradation.
- **scope**: the range of impact.
- **duration**: how long it lasts.

## Before/After

**Before**: vague phrases like "this is serious".

**After**: an agreed level like "SEV2".

## Hands-on: Severity Mapping

### Step 1 — Impact axes

```python
def axes(users, region, money_loss):
    return {"users": users, "region": region, "money": money_loss}
```

### Step 2 — Mapping

```python
def severity(a):
    if a["users"] > 100000 or a["money"] > 100000:
        return "SEV1"
    if a["users"] > 1000:
        return "SEV2"
    return "SEV3"
```

### Step 3 — Page policy

```python
def page_policy(sev):
    return {"SEV1": "all", "SEV2": "primary", "SEV3": "next-day"}[sev]
```

### Step 4 — Report cadence

```python
def report_every_min(sev):
    return {"SEV1": 15, "SEV2": 30, "SEV3": 60}[sev]
```

### Step 5 — Auto routing

```python
def route(a):
    sev = severity(a)
    return {"sev": sev, "page": page_policy(sev), "every": report_every_min(sev)}
```

## What to Notice in This Code

- Axes break down the impact.
- Each level maps to behavior.
- Auto routing reduces errors.

## Five Common Mistakes

1. **Vague level definitions.**
2. **Forgetting monetary impact.**
3. **Fuzzy line between SEV2 and SEV3.**
4. **Manual classification with no automation.**
5. **Centering internal impact over customer impact.**

## How This Shows Up in Production

A payment failure defaults to SEV1; a search result ordering bug defaults to SEV3.

## How a Senior Engineer Thinks

- A level is a shorthand for behavior.
- Keep the axes to a minimum.
- Settle the boundaries with examples.
- Automation is the default for decisions.
- Differentiate by product or region.

## Example: turning severity into actions

Severity definitions are most useful when they can be read as an action matrix rather than a glossary.

| Severity | Typical impact | Paging scope | Internal update cadence | Customer update |
| --- | --- | --- | --- | --- |
| SEV1 | Broad outage on a critical path | Full incident core team + leadership | 15 min | Immediate |
| SEV2 | Major degradation in an important function | Primary on-call + owning team | 30 min | As needed, usually early |
| SEV3 | Limited or partial impact | Primary on-call only | 60 min | Often skipped |

If someone says “This is SEV2,” the room should already know which people to bring in and how fast updates have to move.

## Checklist

- [ ] Level definitions.
- [ ] Mapping code.
- [ ] Behavior matrix.
- [ ] Example cases.

## Practice Problems

1. Define SEV1 in one line.
2. Define scope in one line.
3. Define duration in one line.

## Wrap-up and Next Steps

Next, we cover initial response.

## Answering the Opening Questions

- **What separates SEV1, SEV2, and SEV3 in practice?**
  - The article treats Severity Classification as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which axes matter most: users, scope, revenue, legal exposure, or duration?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How should severity affect paging and update cadence?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- **Severity Classification (current)**
- Initial Response (upcoming)
- Communication (upcoming)
- Writing the Timeline (upcoming)
- Root Cause Analysis (upcoming)
- Mitigation and Resolution (upcoming)
- Postmortem (upcoming)
- Prevention (upcoming)
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Severity Levels - PagerDuty](https://response.pagerduty.com/before/severity_levels/)
- [Severity level examples - Atlassian](https://www.atlassian.com/incident-management/kpis/severity-levels)
- [Incident Response - Google SRE Workbook](https://sre.google/workbook/incident-response/)
- [NIST SP 800-61 Rev. 2 Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Severity, Triage, Response, Operations
