---
series: incident-response-101
episode: 10
title: Building an Incident Runbook
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
  - Runbook
  - OnCall
  - Capstone
  - Operations
seo_description: Learn how to assemble SEV policy, on-call ownership, templates, and drills into a practical runbook-as-code workflow.
last_reviewed: '2026-05-15'
---

# Building an Incident Runbook

During a real incident, scattered documentation is almost as dangerous as missing documentation. If the SEV matrix lives in one wiki, the on-call schedule in another tool, and the customer-update template in a personal note, the team loses time before it even starts acting.

A runbook is valuable because it turns those fragments into one executable operating surface. It tells the responder where to begin, what to check next, and how the incident should flow into postmortem and prevention work.

This is the final post in the Incident Response 101 series. This capstone post shows how to assemble a runbook as code so response logic, templates, ownership, and drill practice evolve together.

## Questions this chapter answers

A runbook fails when it is only a reading document. During a live incident, responders need one place that links severity policy, current ownership, communication templates, next-step logic, and postmortem follow-through.

> A good runbook is an operating interface, not a pile of notes. It should let a responder move from page acknowledgement to postmortem creation without hunting through five systems.

- Why does runbook quality show up most clearly at 3 a.m.?
- How should severity policy connect to on-call ownership and templates?
- Why is runbooks-as-code better than keeping everything in a wiki?
- What should be exercised in drills before the runbook is trusted?
- How do you keep the runbook current after real incidents?

## Why this topic matters

The first cost of scattered operations knowledge is search time. The second cost is inconsistency: people start from different assumptions and follow different links even though they are handling the same outage.

A runbook repository reduces both costs. It makes the response path reviewable, versioned, and easy to improve after drills or real incidents.

## Diagram at a glance

![Diagram at a glance](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/10/10-01-diagram-at-a-glance.en.png)

*Diagram at a glance*
Think of the runbook as a graph, not a page. Severity, on-call, templates, response steps, and postmortem linkage have to connect cleanly for the system to be usable under stress.

## Key Terms

- **runbook**: a collection of response procedures.
- **on-call**: the paging schedule.
- **sev map**: a mapping from SEV to response.
- **template**: a reusable form.
- **drill**: a practice exercise.

## Before/After

**Before**: scattered across Wikis, Slack pins, and personal notes.

**After**: unified as code in a Git repository.

## Hands-on: Runbook Capstone

### Step 1 — SEV map

```python
SEV = {
    "SEV1": {"page": True, "comms": 15},
    "SEV2": {"page": True, "comms": 30},
    "SEV3": {"page": False, "comms": 60},
}
```

### Step 2 — On-call lookup

```python
def on_call(schedule, now):
    return next(p for p in schedule if p["from"] <= now <= p["to"])
```

### Step 3 — Communication templates

```python
def comms(audience, sev, summary):
    return {"to": audience, "sev": sev, "text": summary}
```

### Step 4 — Response steps

```python
STEPS = ("ack", "stabilize", "communicate", "investigate", "resolve")

def next_step(current):
    i = STEPS.index(current)
    return STEPS[i + 1] if i + 1 < len(STEPS) else "done"
```

### Step 5 — Postmortem template link

```python
def link_postmortem(incident_id):
    return f"runbook/postmortems/{incident_id}.md"
```

### Step 6 — Integrated execution

```python
def run_incident(sev, schedule, now, summary):
    person = on_call(schedule, now)
    msg = comms("internal", sev, summary)
    return {
        "sev": SEV[sev],
        "ic": person["name"],
        "first_msg": msg,
        "step": "ack",
        "postmortem": link_postmortem("INC-001"),
    }
```

## What to Notice in This Code

- Every stage is a data structure.
- State transitions are tuple indices.
- Postmortem is a file link.

## Five Common Mistakes

1. **Keeping the runbook only in a Wiki.**
2. **Using the same procedure for every SEV.**
3. **On-call info living in an external tool only.**
4. **Templates that are not current.**
5. **Going live without a drill.**

## How This Shows Up in Production

A runbook/ directory holds Markdown plus Python scripts; PR review tracks changes. Quarterly drills keep it up to date.

## How a Senior Engineer Thinks

- A runbook is code.
- Without practice, it is useless.
- Quarterly drills are culture.
- Changes go through PRs.
- One procedure for all SEVs is dangerous.

## Example runbook repository layout

A runbook works better when the directory structure itself makes the response path obvious.

```text
runbook/
  sev-matrix.md
  oncall.md
  comms/
    internal.md
    external.md
    exec.md
  procedures/
    rollback.md
    scale-out.md
    statuspage.md
  postmortems/
    template.md
```

The goal is not to flatten every document into one giant file. The goal is to make the start point and the next links obvious enough that a responder can move quickly under stress.

## Checklist

- [ ] SEV map.
- [ ] On-call schedule.
- [ ] Communication templates.
- [ ] Postmortem template.
- [ ] Quarterly drill.

## Practice Problems

1. Define runbook in one line.
2. Define drill in one line.
3. Define sev map in one line.

## Wrap-up and Next Steps

This series wraps up here. Next, read the SRE 101 and Information Security 101 series to grow reliability and security together.

<!-- toc:begin -->
- [What is an Incident?](./01-what-is-incident.md)
- [Severity Classification](./02-severity.md)
- [Initial Response](./03-initial-response.md)
- [Communication](./04-communication.md)
- [Writing the Timeline](./05-timeline.md)
- [Root Cause Analysis](./06-root-cause-analysis.md)
- [Mitigation and Resolution](./07-mitigation-and-resolution.md)
- [Postmortem](./08-postmortem.md)
- [Prevention](./09-prevention.md)
- **Building an Incident Runbook (current)**
<!-- toc:end -->

## References

### Official Docs
- [Runbooks - PagerDuty](https://response.pagerduty.com/oncall/runbooks/)
- [Managing Load - Google SRE Workbook](https://sre.google/workbook/managing-load/)
- [On-call management - Atlassian](https://www.atlassian.com/incident-management/on-call)
- [Game days - Azure Architecture Center](https://learn.microsoft.com/azure/architecture/framework/resiliency/testing)

### Example source
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, Runbook, OnCall, Capstone, Operations
