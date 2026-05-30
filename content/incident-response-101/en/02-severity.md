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

A strong severity system removes those debates from the live path. When someone says "SEV2," the room should already know the expected fan-out, communication cadence, and decision urgency.

## Diagram at a glance

The point of the flow is the mapping step. Severity is not the impact itself; it is the operating language that turns impact into a response pattern.

## Key Terms

- **SEV1**: company-wide impact.
- **SEV2**: major feature degradation.
- **SEV3**: partial degradation.
- **scope**: the range of impact.
- **duration**: how long it lasts.

When defining these terms, examples beat abstractions. "Serious" means different things to different people. "Payment failure is SEV1; search ranking bug is SEV3" leaves no room for interpretation.

## Before/After

**Before**: vague phrases like "this is serious".

**After**: an agreed level like "SEV2" that immediately implies paging scope and update cadence.

The difference is not just vocabulary. In the "before" state, paging scope and priority vary by person. In the "after" state, one word triggers the entire behavior chain.

## Hands-on: Severity Mapping

### Step 1 — Impact axes

Looking at a single number misses context. Breaking an event into user count, geographic scope, and financial loss makes boundaries sharper.

```python
def axes(users, region, money_loss):
    return {"users": users, "region": region, "money": money_loss}
```

### Step 2 — Mapping

Once the axes exist, set thresholds. Here we use user count and monetary loss to gate SEV1, then split the remainder into SEV2 and SEV3.

```python
def severity(a):
    if a["users"] > 100000 or a["money"] > 100000:
        return "SEV1"
    if a["users"] > 1000:
        return "SEV2"
    return "SEV3"
```

### Step 3 — Page policy

Severity that stops at a label is incomplete. Each level must specify who gets woken up and when.

```python
def page_policy(sev):
    return {"SEV1": "all", "SEV2": "primary", "SEV3": "next-day"}[sev]
```

### Step 4 — Report cadence

Update frequency must track severity. Higher severity means shorter intervals; lower severity affords longer gaps.

```python
def report_every_min(sev):
    return {"SEV1": 15, "SEV2": 30, "SEV3": 60}[sev]
```

### Step 5 — Auto routing

Combine severity, page policy, and cadence into a single decision object. Removing manual steps here reduces classification error under pressure.

```python
def route(a):
    sev = severity(a)
    return {"sev": sev, "page": page_policy(sev), "every": report_every_min(sev)}
```

## What to Notice in This Code

- Axes split the impact into measurable dimensions so boundaries stay clear.
- Every level maps to behavior — not just a description.
- Auto routing reduces person-to-person variation in classification.

The key insight: severity is both a technical rule and an organizational rule. The numbers live in code, but the thresholds come from service characteristics and business context. SEV1 for a payment service and SEV1 for an internal tool need not be the same.

## Five Common Mistakes

1. **Vague level definitions** — everyone interprets them differently.
2. **Forgetting monetary impact** — looking only at user count.
3. **Fuzzy line between SEV2 and SEV3** — no examples at the boundary.
4. **Manual classification with no automation** — no routing rules.
5. **Centering internal impact over customer impact** — inflating severity for internal discomfort.

The most frequent real-world problem is the boundary case. That is why documenting representative examples at each boundary matters more than perfecting abstract definitions.

## How This Shows Up in Production

In live services, payment failure defaults to SEV1, and search result ordering bugs default to SEV3. The point is not to debate after the event — it is to have the table and examples ready before the event happens.

A senior engineer treats severity as a "behavior shorthand," not an "importance description." The moment someone says SEV2, paging scope, update cadence, and channel assignment should all come to mind simultaneously.

## Extended severity table: Locking the SEV grid to behavioral rules

Even when severity definitions exist, teams still stumble in practice because the label exists without the behavioral contract. A proper grid binds service state, customer impact, paging policy, internal cadence, and external notice into one row.

| Level | Service state | Customer impact | Paging policy | Internal update | External notice |
| --- | --- | --- | --- | --- | --- |
| SEV1 | Core function down | Broad / direct revenue loss | IC + full core team immediately | 15 min | Start immediately |
| SEV2 | Core function severely degraded | Multiple customer segments failing | Primary + owning team | 30 min | As needed, early |
| SEV3 | Partial function abnormal | Limited customer impact | Primary on-call only | 60 min | Usually skipped |

When building this table, define rows around **customer journeys**, not raw events. The same API error rate means completely different things for a checkout step vs. a recommendation widget. Tag each row with the critical journey it protects.

## Boundary case rules

The boundary between SEV1 and SEV2 consumes the most debate time. These standing rules cut that time:

1. Payment, login, or authentication failures get escalation review regardless of user count.
2. If the blast radius is trending upward, escalate one level proactively.
3. External regulatory or legal risk warrants conservative escalation.
4. Any suspicion of data integrity loss triggers immediate high-severity treatment.

These rules exist for consistency, not correctness. The highest cost is reaching different conclusions for identical situations.

## Severity-based reporting cadence

Reporting cadence balances team focus against customer trust. Too frequent and responders burn out writing updates; too infrequent and trust erodes.

```yaml
severity_cadence:
  SEV1:
    internal_minutes: 15
    exec_minutes: 30
    external_minutes: 30
  SEV2:
    internal_minutes: 30
    exec_minutes: 60
    external_minutes: 60
  SEV3:
    internal_minutes: 60
    exec_minutes: 180
    external_minutes: null
```

Note that `external_minutes: null` (no external notice) is still a policy decision that must be explicit. Leaving it unspecified invites ad-hoc interpretation on every incident.

## Auto routing — production version

```python
def route_by_severity(sev: str) -> dict:
    policies = {
        "SEV1": {"page": "all", "war_room": True, "cadence": 15},
        "SEV2": {"page": "primary", "war_room": True, "cadence": 30},
        "SEV3": {"page": "primary", "war_room": False, "cadence": 60},
    }
    return policies[sev]
```

Auto routing speeds up response, but inaccurate thresholds create false confidence. Revisit thresholds quarterly against actual incident data.

## Operational review items

- Is the SEV declaration rationale captured in the timeline?
- Are escalation and de-escalation timestamps recorded?
- Do per-level paging and notice templates exist and stay current?
- Does the quarterly review re-examine misclassification cases?

Severity system quality is measured by post-classification behavioral consistency, not by document length.

## Severity scoring matrix

When an incident opens, responders need a matrix they can read and score immediately — not a paragraph to interpret.

| Decision axis | SEV1 | SEV2 | SEV3 |
| --- | --- | --- | --- |
| User impact | Broad (company-wide / multi-region) | Major customer segment | Limited users |
| Critical path | Payment / login down | Core feature degraded | Auxiliary feature issue |
| Financial / contract | Immediate loss / penalty risk | Partial loss possible | Minor or none |
| Estimated recovery | 60+ min uncertain | 15–60 min | Under 15 min |

A simple scoring rule reduces live debate: two or more SEV1 conditions → immediate escalation. Two SEV2 conditions → hold at SEV2. Complexity of the rule matters less than consistency of its application.

## Escalation and de-escalation template

Severity is not static — it changes as new information arrives. Recording the reason at each change point matters for postmortems.

```text
[severity-escalation-note]
- incident_id:
- from_to: SEV3 -> SEV2
- decided_at_utc:
- evidence:
  - error_rate:
  - impacted_users:
  - affected_journey:
- decision_owner:
- next_update_minutes:
```

When used alongside the timeline, this template lets anyone answer "why was it SEV2 at that moment?" after the fact. Severity quality shows up more in change-history discipline than in the initial declaration.

## Severity scorecard

Teams may disagree on exact numbers, but locking a scoring rubric dramatically cuts boundary-case debate.

| Item | Score 0 | Score 1 | Score 2 |
| --- | --- | --- | --- |
| Affected customers | Under 100 | 100–5000 | Over 5000 |
| Critical path | No impact | Partial failure | Payment / login direct failure |
| Duration | Under 5 min | 5–30 min | Over 30 min |
| Financial impact | None | Estimable | Observed immediate loss |

Total 0–2 → SEV3. Total 3–5 → SEV2. Total 6+ → SEV1.

## Quarterly review metrics

- Is SEV1/2/3 distribution skewed toward a single service?
- What is the ratio of escalations to de-escalations?
- How many minutes after detection does the average escalation happen?
- Are communication delays recurring immediately after escalation?
- Did the last definition revision actually reduce classification variance?

Review findings must feed into next-quarter experiments — otherwise they stay observations. If SEV2 boundary cases keep repeating, add detection signals or expand the triage checklist to raise classification input quality. A severity system is a learning loop, not a lookup table.

## Example: turning severity into actions

Severity definitions are most useful when they can be read as an action matrix rather than a glossary.

| Severity | Typical impact | Paging scope | Internal update cadence | Customer update |
| --- | --- | --- | --- | --- |
| SEV1 | Broad outage on a critical path | Full incident core team + leadership | 15 min | Immediate |
| SEV2 | Major degradation in an important function | Primary on-call + owning team | 30 min | As needed, usually early |
| SEV3 | Limited or partial impact | Primary on-call only | 60 min | Often skipped |

If someone says "This is SEV2," the room should already know which people to bring in and how fast updates have to move.

## Checklist

- [ ] SEV1/2/3 definitions documented with examples.
- [ ] Impact axes (user count, scope, financial loss) agreed upon.
- [ ] Per-level paging policy and reporting cadence recorded.
- [ ] Boundary case examples included in the definition doc.
- [ ] Escalation/de-escalation template linked to timeline.

## Practice Problems

1. Define SEV1 for your team in one sentence.
2. Write down what numeric thresholds you would use for scope and duration.
3. Explain why severity criteria might differ between an internal tool and a customer-facing service.

## Wrap-up and Next Steps

Severity is not a label — it is a shared language that connects impact to behavior. The same word must carry the same meaning for on-call, reporting, and prioritization to align. A good severity system has clear impact axes, boundary-case examples, and every level linked to concrete actions.

Next, we cover initial response — what to do in the first few minutes after an incident fires.

## Answering the Opening Questions

- **What is severity a language for?**
  - SEV1 means company-wide disruption, SEV2 means a major feature is unavailable, SEV3 means partial impact. Each level determines paging and reporting rules.
- **How should you draw the line between SEV1, SEV2, and SEV3?**
  - Classify dynamically using affected user count, blast radius (total vs. partial), and estimated recovery time. Refine thresholds for edge cases by consulting senior responders.
- **Why do you need impact axes like user count, scope, and financial loss?**
  - These numbers replace subjective statements like "it's bad" with objective criteria like "5,000 users affected for 15+ minutes."
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
