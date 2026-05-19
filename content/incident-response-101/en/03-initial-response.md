---
series: incident-response-101
episode: 3
title: Initial Response
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
  - Triage
  - Response
  - OnCall
  - Operations
seo_description: Learn what a response team should do in the first minutes of an incident, from ack and triage to stabilization and comms.
last_reviewed: '2026-05-15'
---

# Initial Response

The first few minutes after an alert feel both compressed and chaotic. Data is incomplete, pressure is high, and different people start pulling toward diagnosis, rollback, communication, and ownership at the same time.

Teams that survive this window well do not start with perfect answers. They start with structure: acknowledge the page, estimate impact, open one channel, assign roles, and buy time with stabilization.

This is post 3 in the Incident Response 101 series. This post breaks down that first-response sequence so the team can stop the bleeding before it tries to explain every detail.

## Questions this chapter answers

In the first five minutes, teams often chase diagnosis because it feels productive. But when the blast radius is still growing, response structure matters more than a complete explanation.

> Initial response is about stopping the bleeding, creating one command channel, and assigning ownership before the incident fragments into parallel guesses.

- What should happen first after a page is acknowledged?
- Why is stabilization usually more urgent than diagnosis?
- How much impact estimation is enough for the first update?
- Which roles should be assigned immediately?
- What should trigger the first external communication?

## Why this topic matters

The most expensive minutes in an incident are often the earliest ones. If everyone starts investigating independently, the team loses both speed and a shared picture of the problem.

A strong first-response routine creates enough order to keep the incident legible. Once ownership, communication, and stabilization are in place, deeper diagnosis becomes much more effective.

## Diagram at a glance

![Diagram at a glance](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/03/03-01-diagram-at-a-glance.en.png)

*Diagram at a glance*
The response path is intentionally simple. Acknowledge ownership, triage the rough severity, open one channel, and assign roles before the room grows noisy.

## Key Terms

- **ack**: acknowledging a page.
- **triage**: sorting and prioritizing.
- **stabilize**: stop the bleeding.
- **channel**: a dedicated collaboration space.
- **role**: a defined responsibility.

## Before/After

**Before**: start with diagnosis.

**After**: start with stabilization.

## Hands-on: Five-Minute Checklist

### Step 1 — Ack

```python
def ack(alert_id, user):
    return {"alert": alert_id, "by": user, "at": "now"}
```

### Step 2 — Estimate impact

```python
def estimate_impact(metrics):
    return metrics.get("err_ratio", 0) * 100
```

### Step 3 — Open the channel

```python
def open_channel(name):
    return f"#inc-{name}"
```

### Step 4 — Assign roles

```python
def assign(team):
    return {"IC": team[0], "ops": team[1], "comms": team[2]}
```

### Step 5 — Stabilize

```python
def stabilize(actions):
    return [a for a in actions if a in ("rollback", "scale", "throttle")]
```

## What to Notice in This Code

- Ack marks the start of ownership.
- Express impact with numbers.
- The role set has three axes.

## Five Common Mistakes

1. **Starting with diagnosis.**
2. **The IC doing the hands-on work.**
3. **Scattering across channels.**
4. **Skipping customer comms.**
5. **Acting without records.**

## How This Shows Up in Production

PagerDuty ack → auto-created Slack channel → Statuspage draft — all automated.

## How a Senior Engineer Thinks

- Time is the enemy.
- Stabilization is the top priority.
- Roles are fixed.
- Recording happens in parallel.
- Action beats perfection.

## Example: an operator log for the first ten minutes

A compact response log makes it easy to review whether the team established structure before it started chasing detailed diagnosis.

```text
09:01 page acknowledged by primary on-call
09:03 error rate confirmed at 18%, checkout path affected
09:04 #inc-payments channel opened
09:05 IC / ops / comms roles assigned
09:07 rollback started
09:10 status page investigation notice published
```

This kind of log is short, but it preserves the difference between “we were investigating” and “we had actually established command.”

## Checklist

- [ ] Ack policy.
- [ ] Channel automation.
- [ ] Role cards.
- [ ] Stabilization action list.

## Practice Problems

1. Define ack in one line.
2. Define triage in one line.
3. Define stabilize in one line.

## Wrap-up and Next Steps

Next, we cover communication.

<!-- toc:begin -->
- [What is an Incident?](./01-what-is-incident.md)
- [Severity Classification](./02-severity.md)
- **Initial Response (current)**
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
- [Responding During an Incident - PagerDuty](https://response.pagerduty.com/during/during_an_incident/)
- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)
- [Incident response process - Atlassian](https://www.atlassian.com/incident-management/incident-response)
- [Statuspage incident communication guide](https://www.atlassian.com/software/statuspage/incident-communication)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Triage, Response, OnCall, Operations
