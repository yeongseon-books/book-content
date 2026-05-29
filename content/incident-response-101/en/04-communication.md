---
series: incident-response-101
episode: 4
title: "Incident Response 101 (4/10): Communication"
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
  - Communication
  - Statuspage
  - OnCall
  - Operations
seo_description: Learn how to send incident updates to responders, customers, and executives with separate templates and a clear cadence.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (4/10): Communication

Many teams assume incident communication is secondary work that can wait until the technical situation is clearer. In practice, trust often erodes faster from silence than from a slightly slower recovery.

Customers, executives, and responders do not need the same message. They need the same facts translated into different levels of detail and delivered on a predictable cadence.

This is the 4th post in the Incident Response 101 series. This post covers how to separate audiences, when to use Slack versus a status page, and how to keep updates short, honest, and operationally useful.


![incident response 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/04/04-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 4 flow overview*
> Clear channels + fixed cadence + escalation rules = a team that stays coordinated even under pressure.

## Questions to Keep in Mind

- Who needs updates during an incident, and what should each audience hear?
- Why is a fast imperfect first update usually better than a delayed perfect one?
- How should severity shape the update cadence?

## Why this topic matters

Customers do not need raw logs. They need impact, scope, and the next promised update. Executives need business context, decision risk, and timing. Responders need technical detail and precise ownership.

When those streams are mixed together, everyone gets either too little or too much. Separating them early keeps trust higher and lets the technical team keep moving.

## Diagram at a glance

The important idea is audience branching. One incident can require three communication streams, each with its own channel, level of detail, and timing expectation.

## Key Terms

- **internal**: shared inside the response team.
- **external**: addressed to customers.
- **exec**: executive summary.
- **cadence**: the update interval.
- **statuspage**: the official status page.

## Before/After

**Before**: everything mixed into one channel.

**After**: separate channels and templates per audience.

## Hands-on: Build Per-Audience Messages

### Step 1 — Define audiences

```python
AUDIENCES = ("internal", "external", "exec")
```

Fix who you are speaking to before composing anything. A pre-defined audience list prevents reinventing the recipient list under pressure every time.

### Step 2 — Template function

```python
def message(audience, sev, summary):
    return {"to": audience, "sev": sev, "text": summary}
```

Structuring messages as data (audience, severity, summary) makes reuse and automation straightforward. The template is the reason you can send a first update in under two minutes.

### Step 3 — Cadence calculation

```python
def cadence(sev):
    return {"SEV1": 15, "SEV2": 30, "SEV3": 60}.get(sev, 120)
```

SEV1 means more frequent updates; SEV3 can breathe longer. Pre-setting cadence keeps communication consistent instead of erratic during the stress of an active incident.

### Step 4 — Statuspage draft

```python
def statuspage(component, state):
    return f"{component} is {state}"
```

Customer-facing notices should be brief and clear: state and impact, not internal debug details. A short accurate draft ships faster than a perfect long one.

### Step 5 — Send queue

```python
def queue(messages):
    return sorted(messages, key=lambda m: m["sev"])
```

When multiple messages queue up, sorting by severity ensures the most critical updates go out first. Priority ordering is a small detail that prevents confusion at scale.

## What to Notice in This Code

- Audience is the key in the data structure.
- Cadence is tied to SEV.
- Templates are functions — reusable.

## Five Common Mistakes

1. **Sending the same message to everyone.**
2. **Believing the first update must be perfect.**
3. **Updating irregularly without a cadence.**
4. **Sending raw technical jargon to executives.**
5. **Forgetting the resolution announcement.**

## How This Shows Up in Production

Statuspage + Slack + an email broadcaster are wired together so one input fans out to three channels.

## How a Senior Engineer Thinks

- Silence is the worst option.
- Short and frequent beats long and rare.
- Executives hear impact, not internals.
- Customers hear what to do.
- Send one more note after resolution.

## Example message templates

Audience separation works best when the templates already exist before the incident.

```text
[internal]
SEV2 incident on checkout. Error rate increased after the 14:05 deploy. IC: Mina. Next update in 30 minutes.

[external]
We are investigating elevated checkout failures for some customers. Our next update will be shared in 30 minutes.

[exec]
Checkout incident, currently SEV2. Payment conversion is affected. Rollback is in progress; next executive update in 30 minutes.
```

The goal of the first update is not total completeness. It is to establish that the team sees the issue, has started acting, and will update again on a fixed schedule.

## Checklist

- [ ] Audience definition.
- [ ] Template repository.
- [ ] Cadence table.
- [ ] Statuspage permissions.

## Practice Problems

1. Define cadence in one line.
2. Define statuspage in one line.
3. Summarize the core of an exec message in one line.

## Wrap-up and Next Steps

Next, we cover writing the timeline.

## Answering the Opening Questions

- **During an incident, who needs which message and when?**
  - Decide channel → paging scope → reporting cadence first. Clear communication ground rules make collaboration predictable.
- **Why separate internal-team, customer, and executive messages?**
  - Focus on one channel at a time and make each channel's purpose (team/exec/customer) explicit.
- **How polished does the first status update need to be?**
  - Report at fixed intervals—5 min, 15 min, or 30 min—and state the current phase clearly each time.
<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity Classification](./02-severity.md)
- [Incident Response 101 (3/10): Initial Response](./03-initial-response.md)
- **Communication (current)**
- Writing the Timeline (upcoming)
- Root Cause Analysis (upcoming)
- Mitigation and Resolution (upcoming)
- Postmortem (upcoming)
- Prevention (upcoming)
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [External communication during incidents - PagerDuty](https://response.pagerduty.com/during/external_comms/)
- [Incident communication - Atlassian](https://www.atlassian.com/incident-management/incident-communication)
- [Statuspage best practices](https://www.atlassian.com/software/statuspage/best-practices)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)
- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)

Tags: Incident, Communication, Statuspage, OnCall, Operations
