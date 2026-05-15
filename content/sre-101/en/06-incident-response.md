---
series: sre-101
episode: 6
title: Incident Response
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
  - Incident
  - Response
  - OnCall
  - Operations
seo_description: A beginner-friendly guide to incident response covering definitions, severity levels, roles, communications, and closure procedures
last_reviewed: '2026-05-14'
---

# Incident Response

When an outage starts, the technical problem is only half the problem. The other half is human coordination: who decides priorities, who works the fix, who updates customers, and who keeps the timeline coherent enough for later learning.

Teams that decide those things during the outage usually lose time in confusion. Teams that decide them beforehand recover faster because the response structure is already available when stress is highest.

This is post 6 in the SRE 101 series. Here we treat incident response as a team system with roles, severity levels, communication rules, and explicit closure criteria.

## Questions this chapter answers

- Why does incident response depend so heavily on team structure instead of only on technical skill?
- Why should severity be defined by impact rather than intuition?
- What should an Incident Commander do directly, and what should they deliberately avoid doing?
- Why do recovery work and stakeholder communication have to move in parallel?
- What goes wrong when closure and handover rules stay vague?

## Why this topic matters

Chaos magnifies impact. A technically recoverable issue can become a prolonged incident when decisions stall and communication lags behind the actual state of the system.

The response process also shapes trust. Customers, leadership, and the team itself all experience the incident through the quality of updates, coordination, and follow-through.

> Incident response is a team activity with fixed roles and a fixed order.

## Concept at a glance

![Concept at a glance](../../../assets/sre-101/06/06-01-concept-at-a-glance.en.png)

*A healthy incident process moves from detection to triage, mitigation, resolution, and learning in order.*
## Key Terms

- **incident**: an *abnormal* condition with *impact*.
- **severity**: the level of *impact*.
- **IC**: the *Incident Commander*.
- **ops lead**: the operational lead.
- **comms lead**: the communications lead.

## Before/After

**Before**: at *start*, everyone *responds at once*.

**After**: *roles* and *channels* are *fixed* up front.

## Hands-on: Defining the Process

### Step 1 — Severity mapping

```python
def severity(impact_users, duration_min):
    if impact_users > 10000 or duration_min > 60:
        return "SEV1"
    if impact_users > 1000:
        return "SEV2"
    return "SEV3"
```

### Step 2 — Assign IC

```python
def assign_ic(on_call):
    return on_call[0]
```

### Step 3 — Create the channel

```python
def channel(name):
    return f"#inc-{name}"
```

### Step 4 — Status updates

```python
def update(channel, msg, every_min=15):
    return {"channel": channel, "msg": msg, "every": every_min}
```

### Step 5 — Closure check

```python
def can_close(mitigated, customer_impact_zero):
    return mitigated and customer_impact_zero
```

## What to Notice in This Code

- *Severity* is defined by *impact*, not feel.
- The *IC* is the *single* decision-maker.
- A separate *channel* preserves the *record*.

## Five Common Mistakes

1. **Delaying decisions by *consensus* instead of using an *IC*.**
2. **Estimating *impact* *subjectively*.**
3. **Skipping *customer communication*.**
4. **Vague *closure* criteria.**
5. **Returning to work without a *record*.**

## How This Shows Up in Production

*PagerDuty*, *Statuspage*, and *Slack* integrations *automate* roles and customer comms.

## How a Senior Engineer Thinks

- *Response* gets *faster* with *training*.
- The *IC* decides; *experts* do the work.
- *Communication* is the *axis of trust*.
- *Closure* is done *carefully*.
- *Training* happens *before* the call.

## Checklist

- [ ] *Severity* defined.
- [ ] *IC* rotation.
- [ ] *Communication* templates.
- [ ] *Closure* criteria.

## Practice Problems

1. Define the *IC* role in one line.
2. Define *severity* in one line.
3. Define the role of a *Statuspage* in one line.

## Wrap-up and Next Steps

Next, we cover *postmortems*.

<!-- toc:begin -->
- [What is SRE?](./01-what-is-sre.md)
- [Reliability](./02-reliability.md)
- [SLI, SLO, SLA](./03-sli-slo-sla.md)
- [Error Budget](./04-error-budget.md)
- [Monitoring](./05-monitoring.md)
- **Incident Response (current)**
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)
<!-- toc:end -->

## References

- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)
- [Incident Response - PagerDuty](https://response.pagerduty.com/)
- [Incident Command System](https://en.wikipedia.org/wiki/Incident_Command_System)
- [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook)

Tags: SRE, Incident, Response, OnCall, Operations
