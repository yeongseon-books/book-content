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

When communication breaks down, recovery work suffers too. Responders lose focus answering the same questions repeatedly, customers interpret silence as a larger problem, and executives open separate channels because they cannot gauge current status. Good teams do not improvise messages — they pre-define audiences and formats.

## Diagram at a glance

The important idea is audience branching. One incident can require three communication streams, each with its own channel, level of detail, and timing expectation.

## Key Terms

- **internal**: shared inside the response team.
- **external**: addressed to customers.
- **exec**: executive summary.
- **cadence**: the update interval.
- **statuspage**: the official status page.

Confusing these streams causes problems. Sending an internal message directly to customers is overly technical; copying an exec message into the response channel lacks information density. The premise is that the same event requires different information for each audience.

## Before/After

**Before**: everything mixed into one channel. The same sentence goes to everyone.

**After**: separate channels and templates per audience. Same facts, different language.

The benefit of the "after" state is clear: responders can continue technical discussion uninterrupted, customers receive only actionable information quickly, and executives get the summary they need. This is far more stable than trying to satisfy all requirements in a single message.

## Hands-on: Build Per-Audience Messages

### Step 1 — Define audiences

Fix who you are speaking to before composing anything. A pre-defined audience list prevents reinventing the recipient list under pressure every time.

```python
AUDIENCES = ("internal", "external", "exec")
```

### Step 2 — Template function

Structuring messages as data (audience, severity, summary) makes reuse and automation straightforward. The template is the reason you can send a first update in under two minutes.

```python
def message(audience, sev, summary):
    return {"to": audience, "sev": sev, "text": summary}
```

### Step 3 — Cadence calculation

SEV1 means more frequent updates; SEV3 can breathe longer. Pre-setting cadence keeps communication consistent instead of erratic during the stress of an active incident.

```python
def cadence(sev):
    return {"SEV1": 15, "SEV2": 30, "SEV3": 60}.get(sev, 120)
```

### Step 4 — Statuspage draft

Customer-facing notices should be brief and clear: state and impact, not internal debug details. A short accurate draft ships faster than a perfect long one.

```python
def statuspage(component, state):
    return f"{component} is {state}"
```

### Step 5 — Send queue

When multiple messages queue up, sorting by severity ensures the most critical updates go out first. Priority ordering is a small detail that prevents confusion at scale.

```python
def queue(messages):
    return sorted(messages, key=lambda m: m["sev"])
```

## What to Notice in This Code

- Audience is the key in the data structure.
- Cadence is tied to SEV.
- Templates are functions — reusable.

The first update does not need to be perfect. A short, accurate first notice beats a late, verbose one. "We are aware of the issue, investigating, and will update in 15 minutes" is one sentence that preserves trust.

## Five Common Mistakes

1. **Sending the same message to everyone.**
2. **Believing the first update must be perfect.**
3. **Updating irregularly without a cadence.**
4. **Sending raw technical jargon to executives.**
5. **Forgetting the resolution announcement.**

The last mistake repeats frequently. If recovery is complete, the fact that the incident is over must also be communicated explicitly. Only then can both customers and internal teams close out the situation.

## How This Shows Up in Production

In production, teams wire together a status page, Slack, and an email broadcaster so one input fans out to three channels. The message bodies are still different: internal is detailed, customer notices are concise, and executive messages are compressed around impact and timeline.

A senior engineer views silence as the worst option in communication. They know that short and frequent updates beat long and rare ones, and that the next action matters more than a technical explanation.

## How a Senior Engineer Thinks

- Silence is the worst option.
- Short and frequent beats long and rare.
- Executives hear impact, not internals.
- Customers hear what to do.
- Send one more note after resolution.

## Deep Dive: Template Systems and Cadence Tables

Incident communication is a structural problem, not a writing-skill problem. Fix who receives what, at what depth, and at what interval — and the response team keeps its focus. Without structure, responders lose recovery speed answering repeated questions.

### Per-Audience Message Principles

| Audience | Core Question | Message Focus | Length |
| --- | --- | --- | --- |
| Internal responders | What do we do now? | Facts, hypotheses, next action | Detailed |
| Customers | How am I affected? | Impact, workaround, next update time | Concise |
| Executives | What is the business impact level? | Impact scale, risk, expected recovery path | Summary |

Copying the same sentence to three channels reduces quality. Internal messages aim for accuracy, customer messages aim for clarity, and executive messages aim for decision-support.

### Update Cadence Table

| Severity | Internal Update | Customer Notice | Executive Report |
| --- | --- | --- | --- |
| SEV1 | 15 min | 30 min | 30 min |
| SEV2 | 30 min | 60 min | 60 min |
| SEV3 | 60 min | As needed | 180 min |

The cadence table provides *predictability* more than "message quality." Even imperfect updates maintain trust when they arrive on schedule.

### Structured Template Set

```text
[internal-update]
- sev:
- impact_metrics:
- mitigation_status:
- unresolved_risk:
- next_update:

[customer-update]
- affected_feature:
- current_status (investigating/mitigating/resolved):
- customer_action (if any):
- next_update_time:

[executive-update]
- business_impact_summary:
- current_severity:
- expected_recovery_scope:
- decisions_needed:
```

Separating templates reduces message rework time and lets the response team focus on recovery. Executive messages in particular should lead with decision-relevant information, not technical logs.

### Message Queue with Cadence

```python
def build_update(audience: str, sev: str, summary: str, next_min: int) -> dict:
    return {
        "audience": audience,
        "severity": sev,
        "summary": summary,
        "next_update_minutes": next_min,
    }

def cadence_minutes(sev: str) -> int:
    return {"SEV1": 15, "SEV2": 30, "SEV3": 60}.get(sev, 120)
```

A queue-based approach makes it easy to track "who sent what when" and objectively review communication quality in the postmortem.

### Operational Rules

- Publish the first notice within 10 minutes; state uncertainty as uncertainty.
- Every notice must include the next update time.
- Resolution notices must distinguish "mitigated" from "resolved."
- Never propagate unconfirmed internal hypotheses directly to external notices.

Following these rules ensures communication accelerates recovery rather than hindering it.

### Resolution Notice Quality Criteria

A resolution notice cannot end with just "it's over." At minimum, include the time impact ended, the verification metric confirming recovery, and the follow-up update plan. This lets customers and internal teams share the same state.

Additionally, providing a summary notice within 24 hours of resolution builds trust. Even without publishing a detailed RCA immediately, stating what category of improvement is underway gives customers the sense that the incident is "closed."

### Communication Approval Flow

| Message Type | Author | Reviewer | Publishing Channel |
| --- | --- | --- | --- |
| Internal update | Comms lead | IC | Incident channel |
| Customer notice | Comms lead | IC + Legal/CS (if needed) | Status page |
| Executive report | IC | Incident lead | Exec channel |

### Customer Notice Writing Guide

- State only confirmed facts.
- Do not assert unconfirmed causes.
- Always include the next update time.
- Separate impact scope from workaround instructions.
- Resolution notices must include the verification metric.

### Resolution Notice Template

```text
[incident-resolved-notice]
- end_time_utc:
- recovery_verification_metric:
- customer_impact_duration:
- current_status: resolved (root cause eliminated)
- follow_up: postmortem summary expected at [time]
```

The resolution notice is the final quality checkpoint of the incident. Stating the recovery evidence explicitly ensures responders and customers share the same understanding.

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

- **Who needs updates during an incident, and what should each audience hear?**
  - Define channel → paging scope → reporting cadence first. The per-audience message table shows that responders need facts and next actions, customers need impact and workarounds, and executives need business impact and decision support. Clear communication ground rules make collaboration predictable.
- **Why is a fast imperfect first update usually better than a delayed perfect one?**
  - The cadence table demonstrates that predictability preserves trust more than perfection. A notice that arrives on schedule — even if incomplete — signals that the team is in control. Silence is interpreted as larger problems.
- **How should severity shape the update cadence?**
  - SEV1 triggers 15-minute internal updates and 30-minute customer/exec notices. SEV3 relaxes to 60-minute internal and as-needed customer updates. The fixed intervals prevent erratic communication under pressure while scaling effort to actual impact.
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
