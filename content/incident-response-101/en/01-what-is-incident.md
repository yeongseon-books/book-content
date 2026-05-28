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

### Step 2 — Threshold

```python
def is_incident(i, user_th=100, min_th=5):
    return i["users"] >= user_th or i["minutes"] >= min_th
```

### Step 3 — Classify

```python
def classify(i):
    return "incident" if is_incident(i) else "bug"
```

### Step 4 — Page or not

```python
def page(i):
    return classify(i) == "incident"
```

### Step 5 — Route the channel

```python
def channel(kind):
    return "#inc" if kind == "incident" else "#bugs"
```

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

## Checklist

- [ ] Threshold agreed.
- [ ] Classification code.
- [ ] Alert routing.
- [ ] Training material.

## Practice Problems

1. Define incident in one line.
2. Define outage in one line.
3. Define degradation in one line.

## Wrap-up and Next Steps

Next, we cover severity classification.

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
