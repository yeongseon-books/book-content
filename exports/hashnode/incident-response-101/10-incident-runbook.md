
# Building an Incident Runbook

> Incident Response 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: How do you bind everything you learned — *severity*, *response*, *communication*, *timeline*, *RCA*, *mitigation*, *postmortem*, *prevention* — into a *single runbook*?

> A *runbook* is *code-shaped documentation* that holds *SEV mapping* through *postmortem templates* in *one repository*.

<!-- a-grade-intro:end -->

## What You Will Learn

- *SEV* mapping
- *On-call* schedule
- *Communication* templates
- *Runbooks as code*
- *Drills* and *maintenance*

## Why It Matters

When *documents* are *scattered*, you do not know *where to start* at *3 a.m.*

## Concept at a Glance

```mermaid
flowchart LR
    Sev["sev map"] --> OnCall["on-call"]
    OnCall --> Comms["comms templates"]
    Comms --> Steps["response steps"]
    Steps --> PM["postmortem template"]
    PM --> Repo["runbook repo"]
```

## Key Terms

- **runbook**: a collection of *response procedures*.
- **on-call**: the *paging* schedule.
- **sev map**: a mapping from *SEV* to *response*.
- **template**: a reusable *form*.
- **drill**: a *practice* exercise.

## Before/After

**Before**: scattered across *Wikis*, *Slack pins*, and *personal notes*.

**After**: unified as *code* in a *Git repository*.

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

- Every *stage* is a *data structure*.
- *State transitions* are *tuple indices*.
- *Postmortem* is a *file link*.

## Five Common Mistakes

1. **Keeping the *runbook* only in a *Wiki*.**
2. **Using the *same procedure* for *every SEV*.**
3. ***On-call* info living in an *external* tool only.**
4. **Templates that are *not current*.**
5. **Going *live* without a *drill*.**

## How This Shows Up in Production

A *runbook/* directory holds *Markdown* plus *Python scripts*; *PR review* tracks *changes*. *Quarterly drills* keep it *up to date*.

## How a Senior Engineer Thinks

- A *runbook* is *code*.
- Without *practice*, it is *useless*.
- *Quarterly drills* are *culture*.
- *Changes* go through *PRs*.
- One procedure for *all SEVs* is *dangerous*.

## Checklist

- [ ] *SEV map*.
- [ ] *On-call schedule*.
- [ ] *Communication templates*.
- [ ] *Postmortem template*.
- [ ] *Quarterly drill*.

## Practice Problems

1. Define *runbook* in one line.
2. Define *drill* in one line.
3. Define *sev map* in one line.

## Wrap-up and Next Steps

This series wraps up here. Next, read the *SRE 101* and *Information Security 101* series to grow *reliability* and *security* together.

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
## References

- [Runbook Template - PagerDuty](https://response.pagerduty.com/oncall/runbooks/)
- [Runbooks as Code - Google SRE Workbook](https://sre.google/workbook/managing-load/)
- [On-Call Rotations - Atlassian](https://www.atlassian.com/incident-management/on-call)
- [Chaos Drills and Game Days - Increment](https://increment.com/reliability/game-days/)

Tags: Incident, Runbook, OnCall, Capstone, Operations

---

© 2026 YeongseonBooks. All rights reserved.
