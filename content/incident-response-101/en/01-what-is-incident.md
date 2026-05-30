---
series: incident-response-101
episode: 1
title: "Incident Response 101 (1/10): What is an Incident?"
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
  - Response
  - SRE
  - Operations
  - OnCall
seo_description: Learn how to distinguish a real incident from a routine bug by using customer impact, duration, and paging thresholds.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (1/10): What is an Incident?

The first hard question in on-call work is rarely technical. When an alert fires, you have to decide whether you are looking at a real incident, a routine bug, or a noisy warning that only needs follow-up during business hours.

Without a shared threshold, teams drift in opposite directions. Some page everyone for minor symptoms and burn out the rotation. Others wait too long while customer impact is already spreading.

This is the first post in the Incident Response 101 series. This post explains how to define an incident around customer impact, duration, and response thresholds so the rest of the incident process has a stable starting point.


![incident response 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/01/01-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 1 flow overview*
> Without clear definitions, incident response becomes reactive and inconsistent. A shared threshold makes the first decision reliable.

## Questions to Keep in Mind

- Which problems should count as an incident instead of a regular bug?
- How is an alert different from an incident?
- What metrics make customer impact concrete enough to page people?

## Why this topic matters

If the definition is too loose, the team pages on noise and the rotation stops trusting alerts. If the definition is too strict, the team waits while customers are already affected. Both failure modes are expensive.

A usable incident definition reduces argument during the first minutes of response. It tells responders which channel to open, which severity system to use, and when leadership communication has to begin.

## Diagram at a glance

The diagram below shows the first decision cut. Events arrive all day, but only the subset with meaningful customer impact should cross into the incident path.

## Key Terms

- **incident**: an abnormal event with customer impact.
- **alert**: an action-required signal.
- **outage**: a service interruption.
- **degradation**: a performance drop.
- **on-call**: a standby duty rotation.

## Before/After

**Before**: every alert is treated like an incident.

**After**: alerts are classified by impact before action.

## Hands-on: Incident Decision

### Step 1 — Capture impact

```python
def impact(users, minutes):
    return {"users": users, "minutes": minutes}
```

First, bundle the minimum information needed to judge an event into one structure. Here we capture affected user count and duration—the two signals that most reliably separate noise from real incidents.

### Step 2 — Threshold

```python
def is_incident(i, user_th=100, min_th=5):
    return i["users"] >= user_th or i["minutes"] >= min_th
```

Next, fix in code where the line is between incident and non-incident. These numbers are not technical laws—they are operational agreements your team makes together. Without them, every on-call engineer judges differently.

### Step 3 — Classify

```python
def classify(i):
    return "incident" if is_incident(i) else "bug"
```

Now the threshold drives a label. Classification is both a technical implementation and an operational policy—it determines which workflow fires next.

### Step 4 — Page or not

```python
def page(i):
    return classify(i) == "incident"
```

If it is an incident, wake someone up; otherwise route to the normal issue queue. On-call fatigue diverges sharply at this branch point.

### Step 5 — Route the channel

```python
def channel(kind):
    return "#inc" if kind == "incident" else "#bugs"
```

Finally, connect the classification to a communication channel. The event name becomes the collaboration path—everyone knows where to look without asking.

## What to Notice in This Code

- The threshold is the result of an agreement.
- The classification picks the path.
- Code removes subjectivity.

## Five Common Mistakes

1. **Confusing alerts with incidents.**
2. **No agreed threshold.**
3. **Estimating impact subjectively.**
4. **Insufficient on-call training material.**
5. **Returning to work without records.**

## How This Shows Up in Production

PagerDuty's severity rules automate the classification.

## How a Senior Engineer Thinks

- Customer impact is the yardstick.
- Alerts are raw material; judgment is human.
- Over-response is also a cost.
- Records are the fuel for learning.
- On-call matures through training.

## First questions to ask before declaring an incident

Before you declare an incident, run through a small set of questions that force evidence over instinct.

- Who is affected right now, and roughly how many users are involved?
- Which metric best expresses the impact: error rate, latency, failed checkouts, or something else?
- Was there a deployment, configuration change, or upstream dependency issue in the last 30 minutes?
- Is there a customer-visible workaround, or is the path fully blocked?
- If the condition lasts five more minutes, who should be paged next?

```bash
# Example: quick declaration checklist
checklist=(error-rate latency saturation deploy-feed statuspage)
for item in "${checklist[@]}"; do
  printf 'check: %s\n' "$item"
done
```

You are not trying to prove the full root cause yet. You are gathering enough evidence to justify whether the incident process should start.

## Incident decision matrix

The hardest boundary in early triage is between "inconvenience" and "outage." Leaving that boundary to human intuition produces different conclusions for identical situations. Lock at least three axes: customer count, critical-path impact, and duration.

| Category | Customers (est.) | Critical path impact | Duration | Default judgment |
| --- | --- | --- | --- | --- |
| A | 1–99 | None | Under 5 min | bug / alert |
| B | 100–999 | Partial | 5–15 min | incident candidate |
| C | 1,000–9,999 | Core feature degraded | 15–30 min | incident |
| D | 10,000+ | Payment / login / primary API down | 30+ min | high-severity incident |

The table is not a perfect classifier. Its purpose is to converge debate quickly. Real-world edge cases always appear — for example, few customers but a spike in checkout failure rate. Pre-documenting a rule like "critical-path impact gets higher weight" reduces judgment variance.

## Response process flow

After the incident/non-incident decision, confusion often persists because "what to do next" is not fixed. The sequence below works reliably across many teams:

1. **Verify signal** — confirm the alert matches actual service state.
2. **Provisional classification** — incident candidate or routine issue.
3. **Claim ownership** — primary on-call acknowledges and opens the channel.
4. **Measure impact** — record customer count, error rate, affected path as numbers.
5. **Route** — incident goes to dedicated workflow; non-incident goes to backlog/bug queue.

Technically simple, organizationally powerful. Skipping steps 3 and 4 means response appears to start, but without ownership and evidence the post-incident review loses reproducibility.

## Triage question cards

The first three minutes of on-call have incomplete information. Reading these questions out loud becomes a useful habit:

- Is the failing function part of a critical user journey?
- Is the failure ratio rising in both absolute value and trend?
- Was there a recent deploy, config change, or upstream dependency shift?
- Can customers work around the issue, or is their workflow blocked?
- If the same state persists 10 more minutes, who else should be paged?

Question cards level-set decision quality regardless of experience. A junior on-call can ask the same questions; a senior can quickly assess the quality of answers.

## Simple decision automation

```python
from dataclasses import dataclass

@dataclass
class IncidentSignal:
    users: int
    minutes: int
    core_path_impacted: bool
    error_ratio: float

def decide(signal: IncidentSignal) -> str:
    if signal.core_path_impacted and signal.error_ratio >= 0.05:
        return "incident"
    if signal.users >= 1000 or signal.minutes >= 15:
        return "incident"
    return "bug"
```

The code is not meant to handle every edge case mechanically. Its value is making the team's agreed criteria explicit so that "why did we classify this as an incident?" always has a traceable answer.

## Operational checkpoints

- Are threshold change histories tracked in version control?
- Does the classification result auto-connect to channel and paging policy?
- When a new boundary case appears, is the definition doc updated immediately?
- Does new on-call training include case-based classification exercises?

When these four items are in place, the incident definition operates as a system, not just a document.

## Incident triage template

Hesitation time before declaring is more expensive than it looks. Teams do better with a fill-in template than a memorized sentence.

```text
[incident-triage-template]
- detected_at_utc:
- affected_journey: (login / payment / search / orders / ...)
- estimated_impacted_users:
- impact_duration_minutes:
- current_error_rate:
- current_latency_p95_ms:
- current_severity_candidate: (SEV1 / SEV2 / SEV3 / bug)
- immediate_action: (declare incident / monitor as bug)
- owner_oncall:
```

Using the template shifts judgment from personal instinct to team criteria. More importantly, it feeds naturally into severity classification, communication, and timeline writing downstream.

## On-call handoff rules

Incidents do not respect shift boundaries. Poor handoffs cause the same event to be triaged twice.

| Item | Minimum standard | Failure signal |
| --- | --- | --- |
| Handoff message | 4-line summary (impact / mitigation / unresolved / next action) | Repeated "where are we?" questions |
| Handoff timing | Draft 10 min before shift end, finalize at transition | 15-min gap after transition |
| Metric check | Incoming on-call re-verifies key metrics twice | Verbal-only briefing, immediate judgment |
| Doc links | Incident channel, dashboard, runbook links included | Missing links, search time increases |

Operational rules exist not to grow documentation but to make anyone who steps in reach the same decision speed. Incident response is a team sport with substitutions, not a solo performance.

## Incident declaration record example

```text
[declare-incident]
incident_id: INC-2026-05-21-001
detected_at_utc: 2026-05-21T01:03:11Z
detected_by: alert.checkout.error_ratio
candidate_severity: SEV2
affected_journey: checkout
estimated_impacted_users: 4300
error_ratio: 0.087
latency_p95_ms: 1840
decision: declare_incident
owner: primary-oncall
next_update_utc: 2026-05-21T01:30:00Z
```

## Team agreement rules

1. A fast hypothesis beats a late correct answer — declare early.
2. De-escalation after declaration is fine; delayed declaration loses time that cannot be recovered.
3. Even incomplete impact numbers should be shared immediately with an "estimated" tag.
4. Separate cause speculation from factual data; facts go to the timeline first.
5. After every incident, review whether the declaration timing was appropriate.

## Post-declaration review questions

- What caused the declaration delay, if any?
- Was role assignment complete within 5 minutes of declaration?
- Did impact numbers appear in the first notification?
- Where did the definition doc and the actual judgment diverge?
- What friction can be reduced before the next incident?

## Checklist

- [ ] Incident threshold documented and agreed.
- [ ] Classification logic reflected in code or automation.
- [ ] Alert routing separates incident and bug channels.
- [ ] Training material with real case examples exists for new on-call members.
- [ ] Triage template linked in incident channel topic.

## Practice Problems

1. Define incident in one line.
2. Define outage in one line.
3. Define degradation in one line.

## Wrap-up and Next Steps

An incident is not "something weird happening." It is an event where customer impact crosses the team's agreed threshold. That threshold enables consistent decisions about who to page, which channel to open, and how often to communicate. On-call maturity starts with sharing judgment criteria.

Next, we cover severity classification — the shared language for expressing how serious an incident is.

## Answering the Opening Questions

- **Which problems should count as an incident instead of a regular bug?**
  - Look at customer impact first. The people you page, the channel you open, and the notification cadence all follow from that single judgment.
- **How is an alert different from an incident?**
  - An alert is an input signal meaning "something happened." An incident is a classification result meaning "response is required."
- **What metrics make customer impact concrete enough to page people?**
  - Define thresholds using affected user count and outage duration. These are operational agreements, not technical laws, so they must be documented.
<!-- toc:begin -->
## In this series

- **What is an Incident? (current)**
- Severity Classification (upcoming)
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
- [PagerDuty Incident Response Documentation](https://response.pagerduty.com/)
- [Managing Incidents - Google SRE Book](https://sre.google/sre-book/managing-incidents/)
- [Incident management overview - Atlassian](https://www.atlassian.com/incident-management)
- [NIST SP 800-61 Rev. 2 Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Response, SRE, Operations, OnCall
