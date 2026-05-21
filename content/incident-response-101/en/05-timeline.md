---
series: incident-response-101
episode: 5
title: "Incident Response 101 (5/10): Writing the Timeline"
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
  - Timeline
  - Postmortem
  - Logging
  - Operations
seo_description: Learn how to build an incident timeline from live notes, channel exports, and anchor timestamps without mixing facts and theory.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (5/10): Writing the Timeline

One of the most expensive mistakes after an incident is trusting memory more than recorded evidence. Everyone thinks they saw the same thing, but a few days later the sequence of events, the basis for decisions, and even the time of mitigation start to blur.

A useful timeline is not a polished story reconstructed after the fact. It is a fact log captured during the response and cleaned up later without mixing observation and interpretation.

This is post 5 in the Incident Response 101 series. This post explains how to record incident events in real time, merge multiple channels into one chronology, and anchor the moments that matter for later RCA and postmortem work.


![incident response 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/05/05-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 5 flow overview*
> The timeline is for the postmortem investigator, not the responder. Record facts and timestamps, not feelings.

## Questions to Keep in Mind

- Why should timeline work begin during the incident instead of after it?
- Which channels need to be collected besides the main response chat?
- How do you separate recorded facts from later theories?

## Why this topic matters

Memory drifts fast, especially after a stressful outage. People remember the final explanation and unconsciously pull it backward into earlier moments where it did not yet exist.

A clear timeline protects the team from that distortion. It creates a fact base that later RCA and postmortem work can trust without rewriting history.

## Diagram at a glance

The shape matters: collect from more than one source, normalize the timestamps, then sort into one document that preserves the real order of events.

## Key Terms

- **timestamp**: a UTC time stamp.
- **scrape**: gathering events from multiple channels.
- **fact**: a recorded observation.
- **interpretation**: guesses and opinions.
- **anchor**: reference moments like Detection or Mitigation.

## Before/After

**Before**: reconstruct from memory.

**After**: reconstruct from contemporaneous logs and channel scrapes.

## Hands-on: A Tiny Timeline Builder

### Step 1 — Event model

```python
def event(ts, source, text):
    return {"ts": ts, "src": source, "text": text}
```

### Step 2 — Scrape a channel

```python
def scrape(channel):
    return [event(m["ts"], channel, m["text"]) for m in channel.get("messages", [])]
```

### Step 3 — Order events

```python
def order(events):
    return sorted(events, key=lambda e: e["ts"])
```

### Step 4 — Split fact and interpretation

```python
def split(events):
    facts = [e for e in events if not e["text"].startswith("?")]
    notes = [e for e in events if e["text"].startswith("?")]
    return facts, notes
```

### Step 5 — Mark anchors

```python
ANCHORS = ("detected", "acknowledged", "mitigated", "resolved")

def mark(event):
    return event["text"].lower() in ANCHORS
```

## What to Notice in This Code

- Every event has three fields.
- Interpretation is split off by a prefix.
- Anchors are the dashboard reference points.

## Five Common Mistakes

1. **Writing the timeline after the incident ends.**
2. **Treating interpretation as fact.**
3. **Mixing time zones (KST/UTC).**
4. **Scraping only one channel.**
5. **Pasting sensitive data directly.**

## How This Shows Up in Production

A Slack bot collects events with `!ts <text>` and exports them into a postmortem doc.

## How a Senior Engineer Thinks

- Contemporaneous logging is the rule.
- Standardize on UTC.
- Short, frequent lines.
- Speculation goes elsewhere.
- If the anchors are right, you can recover the rest.

## Example timeline entries

A timeline becomes much more useful when facts and interpretation are visibly separated.

```text
2026-05-15T00:03Z fact: error rate exceeded 12%
2026-05-15T00:05Z fact: primary on-call acknowledged page
2026-05-15T00:08Z note: ?possible DB connection pool exhaustion
2026-05-15T00:11Z fact: rollback initiated
2026-05-15T00:19Z fact: error rate returned below 1%
```

The `fact` lines preserve what the team knew at the time. The `note` line preserves a hypothesis without rewriting it into truth.

## Checklist

- [ ] Recording owner.
- [ ] Bot command.
- [ ] UTC enforcement.
- [ ] Anchor definitions.

## Practice Problems

1. Define anchor in one line.
2. Distinguish fact and interpretation in one line.
3. Explain why UTC matters in one line.

## Wrap-up and Next Steps

Next, we cover root cause analysis.

## Answering the Opening Questions

- **Why should timeline work begin during the incident instead of after it?**
  - The article treats Writing the Timeline as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which channels need to be collected besides the main response chat?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How do you separate recorded facts from later theories?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity Classification](./02-severity.md)
- [Incident Response 101 (3/10): Initial Response](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- **Writing the Timeline (current)**
- Root Cause Analysis (upcoming)
- Mitigation and Resolution (upcoming)
- Postmortem (upcoming)
- Prevention (upcoming)
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem Process - PagerDuty](https://response.pagerduty.com/after/post_mortem_process/)
- [Postmortem guide - Atlassian](https://www.atlassian.com/incident-management/postmortem)
- [OpenTelemetry Semantic Conventions](https://github.com/open-telemetry/semantic-conventions)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Timeline, Postmortem, Logging, Operations
