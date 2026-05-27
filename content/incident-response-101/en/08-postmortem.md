---
series: incident-response-101
episode: 8
title: "Incident Response 101 (8/10): Postmortem"
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
  - Postmortem
  - Blameless
  - Learning
  - Operations
seo_description: Learn how to write a blameless postmortem with quantified impact, owned action items, and a review loop that sticks.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (8/10): Postmortem

Once an incident is over, the emotional temptation is to move on quickly. The channel quiets down, customer impact is gone, and everyone wants to get back to roadmap work.

That is exactly when the most valuable learning can be lost. A good postmortem converts a stressful event into an organizational asset instead of a fading memory or a blame ritual.

This is the 8th post in the Incident Response 101 series. This post covers blameless postmortem structure, quantified impact, actionable follow-up items, and the review loop that keeps the document from becoming shelfware.


![incident response 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/08/08-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 8 flow overview*
> Postmortems are not optional. They are how the team learns and the codebase improves from each incident.

## Questions to Keep in Mind

- Why is a postmortem still necessary after the incident is already over?
- What does blameless analysis mean in practical terms?
- Why should the template stay stable across incidents?

## Why this topic matters

If the team cannot convert the incident into reusable learning, the same outage pattern comes back under a new name. Recovery restores service, but postmortem work is what restores organizational memory.

A strong postmortem also protects accuracy. It captures facts before memory fades and links them to work that can be prioritized, assigned, and revisited later.

## Diagram at a glance

Publishing the document is only the midpoint. The real payoff comes when the review leads to tracked action items that are still checked later.

## Key Terms

- **blameless**: no personal blame.
- **summary**: a three-sentence recap.
- **impact**: what the customer experienced.
- **action item**: a verifiable follow-up.
- **owner**: the action's responsible person.

## Before/After

**Before**: an internal document of blame.

**After**: an organization-wide, blameless document.

## Hands-on: A Mini Postmortem Builder

### Step 1 — Template

```python
TEMPLATE = ("summary", "impact", "timeline", "rca", "actions")

def new_doc():
    return {k: "" for k in TEMPLATE}
```

### Step 2 — Summary check

```python
def is_short(text):
    return text.count(".") <= 3
```

### Step 3 — Quantify impact

```python
def impact(users, minutes):
    return {"users": users, "minutes": minutes}
```

### Step 4 — Register an action

```python
def action(text, owner, due):
    return {"text": text, "owner": owner, "due": due}
```

### Step 5 — Track

```python
def overdue(actions, today):
    return [a for a in actions if a["due"] < today]
```

## What to Notice in This Code

- The template is fixed as a tuple.
- Impact is numeric.
- Tracking is one deadline comparison.

## Five Common Mistakes

1. **Naming an individual as the cause.**
2. **Actions with no owner.**
3. **Actions with no deadline.**
4. **Sharing only internally.**
5. **Reinventing the template every time.**

## How This Shows Up in Production

Teams keep a Notion/Confluence postmortem template and link action items to Jira. A quarterly review tracks them.

## How a Senior Engineer Thinks

- Blameless is culture.
- No actions, no document.
- Impact is in numbers.
- Sharing is company-wide.
- The quarterly review closes the loop.

## Good and bad postmortem action items

Small wording differences determine whether a postmortem item will ever change production.

- Bad: `Improve monitoring.`
- Good: `Add an Alertmanager rule that opens a PagerDuty SEV2 incident when checkout API 5xx stays above 2% for three consecutive minutes. Owner: platform-oncall. Due: 2026-06-01.`

A strong action item starts with a verb, names an owner, includes a due date, and leaves behind something that can be checked later.

## Checklist

- [ ] Template.
- [ ] Action register.
- [ ] Tracking tool.
- [ ] Quarterly review on the calendar.

## Practice Problems

1. Define blameless in one line.
2. Define action item in one line.
3. Define owner in one line.

## Wrap-up and Next Steps

Next, we cover prevention.

## Answering the Opening Questions

- **Why is a postmortem still necessary after the incident is already over?**
  - The article treats Postmortem as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What does blameless analysis mean in practical terms?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why should the template stay stable across incidents?**
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
- **Postmortem (current)**
- Prevention (upcoming)
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem Process - PagerDuty](https://response.pagerduty.com/after/post_mortem_process/)
- [Postmortem templates - Atlassian](https://www.atlassian.com/incident-management/postmortem/templates)
- [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/)

Tags: Incident, Postmortem, Blameless, Learning, Operations
