---
series: incident-response-101
episode: 3
title: "Incident Response 101 (3/10): Initial Response"
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

# Incident Response 101 (3/10): Initial Response

The first few minutes after an alert feel both compressed and chaotic. Data is incomplete, pressure is high, and different people start pulling toward diagnosis, rollback, communication, and ownership at the same time.

Teams that survive this window well do not start with perfect answers. They start with structure: acknowledge the page, estimate impact, open one channel, assign roles, and buy time with stabilization.

This is the 3rd post in the Incident Response 101 series. This post breaks down that first-response sequence so the team can stop the bleeding before it tries to explain every detail.


![incident response 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/03/03-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 3 flow overview*
> Initial response prioritizes stabilization over diagnosis. The cost of delay is real; the cost of a wrong direction is usually recoverable.

## Questions to Keep in Mind

- What should happen first after a page is acknowledged?
- Why is stabilization usually more urgent than diagnosis?
- How much impact estimation is enough for the first update?

## Why this topic matters

The most expensive minutes in an incident are often the earliest ones. If everyone starts investigating independently, the team loses both speed and a shared picture of the problem.

A strong first-response routine creates enough order to keep the incident legible. Once ownership, communication, and stabilization are in place, deeper diagnosis becomes much more effective.

## Diagram at a glance

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

Acknowledging is not just pressing a button—it is a declaration of ownership. From this moment, someone is responsible, and the timestamp becomes the official start of the response.

### Step 2 — Estimate impact

```python
def estimate_impact(metrics):
    return metrics.get("err_ratio", 0) * 100
```

In the first minutes, you do not need exact numbers. But expressing impact as a numeric estimate rather than a gut feeling gives the team a common reference point for severity calls.

### Step 3 — Open the channel

```python
def open_channel(name):
    return f"#inc-{name}"
```

Before discussion scatters across DMs and threads, open a dedicated incident channel. It is the cheapest device for holding collaboration structure together.

### Step 4 — Assign roles

```python
def assign(team):
    return {"IC": team[0], "ops": team[1], "comms": team[2]}
```

Separating incident commander, operations lead, and communications lead stabilizes the response. When the IC starts doing hands-on work directly, coordination breaks down fast.

### Step 5 — Stabilize

```python
def stabilize(actions):
    return [a for a in actions if a in ("rollback", "scale", "throttle")]
```

In the opening minutes, full resolution is not the goal—fast mitigation is. Rollback, scale-out, and throttle are the standard first moves to stop the bleeding while investigation continues.

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

This kind of log is short, but it preserves the difference between "we were investigating" and "we had actually established command."

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

## First 10 Minutes — Time-Based Checklist

Initial response quality hinges on how quickly you establish structure, not how accurately you diagnose. When information is scarce, fixing execution order matters more than competing hypotheses.

| Time Window | Goal | Required Action | Output |
| --- | --- | --- | --- |
| 0–2 min | Establish ownership | Ack, open incident channel | Incident ID, channel link |
| 2–5 min | Make impact visible | Check error rate / latency / affected path | First impact numbers |
| 5–7 min | Assign roles | Designate IC, Ops, Comms | Responsibility assignment |
| 7–10 min | Begin stabilization | Execute rollback / scale / throttle candidate | First mitigation status |

The key insight: the 5–7 minute role assignment window determines how smoothly the next hour goes. When role separation is late, the technical responder and the comms lead waste time answering the same questions independently.

## Role Assignment Table

| Role | Responsibility | Forbidden Action |
| --- | --- | --- |
| Incident Commander | Priority decisions, stage transition approval | Diving into hands-on work |
| Ops Lead | Execute mitigation, verify recovery | Writing external notices alone |
| Comms Lead | Publish internal/external updates | Asserting unconfirmed root cause |
| Scribe | Maintain timeline, log decisions | Making decisions on behalf of IC |

Roles are momentary responsibilities, not job titles. Small teams can combine roles, but separating IC and Scribe noticeably improves retrospective quality.

## First Notification Template

The initial notice only needs three things: "we are aware," "scope of impact," and "next update time." Avoid speculating on root cause until confirmed.

```text
[initial-notice-template]
- We are seeing elevated failure rates on the checkout path.
- Some customers may experience payment failures.
- The response team is executing mitigation. Next update in 30 minutes.
```

Short is fine. A timely three-line factual notice preserves trust far better than silence.

## Response Automation Example

```python
def initial_response(alert_id: str, team: list[str]) -> dict:
    return {
        "ack": {"alert": alert_id, "status": "acknowledged"},
        "roles": {
            "IC": team[0],
            "Ops": team[1],
            "Comms": team[2],
            "Scribe": team[3] if len(team) > 3 else team[0],
        },
        "next_update_minutes": 30,
    }
```

Automation does not replace people — it standardizes the repeatable startup procedure. Consistent structure reduces quality variance during 3 AM incidents.

## Operational Rules for Reducing Failure

- If no stabilization candidate exists within 10 minutes, escalate immediately.
- Label impact numbers as "estimated" and refresh periodically.
- Log decisions in both the channel and the timeline.
- Define the exit condition for initial response as "mitigation started."

Following these rules reduces early-stage chaos and creates smooth transitions into the next phases (communication, timeline, RCA).

## Handoff Message Template

When initial response extends long enough to require shift handoff, standardize the handoff message:

```text
[handoff]
- Current state: error rate 1.2% after mitigation, monitoring
- Recent action: rollback complete, throttle at 20%
- Open items: specific payment method failure root cause pending
- Next action: re-check metrics in 15 min, decide on throttle removal
```

A standardized short handoff message reduces information loss at shift boundaries.

## Internal/External First Update Templates

```text
[internal-first-update]
- incident_id:
- current_severity:
- observed_impact:
- mitigation_in_progress:
- next_update_at:

[external-first-update]
- We are currently experiencing service errors affecting some users.
- The response team is analyzing and mitigating the issue.
- Next update at <UTC time>.
```

Even if the initial notice is brief, arriving on time matters more than arriving complete.

## First 10 Minutes — Common Failure Patterns

1. Channel not opened — conversations scatter across DMs.
2. IC dives into command execution, creating a decision vacuum.
3. First notice delayed — customer trust drops.
4. Roles assigned without defining expected outputs — confusion persists.
5. Mitigation attempted without defining verification metrics — risk of re-escalation.

Reviewing these patterns in team rehearsals measurably improves first-10-minute quality during real incidents.

## Answering the Opening Questions

- **What should you do first in the five minutes after an alert fires?**
  - Stabilize immediately. Customer impact is growing every second you wait.
- **Why does stabilization come before diagnosis?**
  - Confirm the blast radius first, then hunt for the cause. Reversing this order makes resolution take longer.
- **What numbers should you use to express impact?**
  - Affected customer count, customer-impact duration, and service recovery time—objective metrics, not feelings.
<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity Classification](./02-severity.md)
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
