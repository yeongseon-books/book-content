---
series: sre-101
episode: 7
title: "SRE 101 (7/10): Postmortem"
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
  - Postmortem
  - BlamelessCulture
  - Learning
  - Operations
seo_description: A beginner-friendly guide to postmortems covering definitions, blameless culture, writing templates, action tracking, and organizational learning
last_reviewed: '2026-05-14'
---

# SRE 101 (7/10): Postmortem

Once an incident is mitigated, teams feel relief first. That is natural, but it also creates the risk that recovery becomes the end of the story even when the same weakness is still sitting in the system.

Postmortems matter because they capture what was visible, what was missing, why decisions made sense at the time, and what has to change so the next incident is smaller or easier to resolve.

This is the 7th post in the SRE 101 series. Here we treat postmortems as a learning system built from blameless analysis, reusable structure, tracked follow-up work, and organizational sharing.


![sre 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/07/07-01-concept-at-a-glance.en.png)
*sre 101 chapter 7 flow overview*

## Questions to Keep in Mind

- Why is a postmortem closer to an organizational learning tool than to a simple report?
- Why does blame suppress the very context a team needs to improve?
- What sections should a useful postmortem always contain?

## Why this topic matters

Repeated outages are often the result of missing learning, not missing effort. If the team cannot preserve the timeline, causes, and follow-up changes, the next incident starts from the same weak foundation.

Good postmortems turn one painful event into shared operating knowledge. That is how incident response becomes better over time instead of merely familiar.

Postmortems are also invisible organizational memory. Even when the on-call engineer who handled the incident leaves the company, a well-written postmortem keeps the lessons alive for the next team.

## Key Terms

| Term | Meaning | Role in practice |
| --- | --- | --- |
| postmortem | A structured post-incident analysis document | Organizes facts and learning into a reusable form |
| blameless | Principle of focusing on system gaps rather than individual fault | Encourages honest disclosure of hidden context |
| timeline | Chronological sequence of events during the incident | Separates fact from interpretation |
| root cause | The structural cause beneath visible symptoms | Points the fix at prevention, not just recovery |
| action item | A follow-up task with owner, due date, and priority | Converts learning into tracked system changes |

## Why blameless culture comes first

In teams where blame is strong, people speak defensively. Information gaps, missing warning signals, procedural holes, and tooling limitations—the real causes—stay hidden because no one wants to be the person who "caused" the outage.

Blameless does not mean no accountability. It means asking "what was missing from the system?" before asking "who made a mistake?" When the real explanation surfaces, the follow-up actions actually prevent recurrence.

### Blameful vs blameless questions

| Blameful question | Blameless alternative |
| --- | --- |
| Why didn't you check the backup? | Was the backup-verification procedure documented? |
| Why did you miss the alert? | Was alert fatigue already a problem on this channel? |
| Why didn't you roll back sooner? | Was the rollback button in a discoverable location? |
| Why didn't you predict the failure? | What signals existed before the failure, and were they surfaced? |

The same facts are uncovered, but the blameless framing produces answers about systems and processes rather than defensive justifications.

## Why templates matter

Free-form postmortems drift in quality. Some have detailed timelines but no actions; others have vague root causes and no impact numbers. A shared template replaces memory with structure.

Strong teams do not compete on writing skill. They invest in a skeleton that guarantees every postmortem covers facts, impact, cause, and follow-up—regardless of who writes it.

## Postmortem template sections

| Section | Question it answers | Writing guidance |
| --- | --- | --- |
| Summary | What happened in one sentence? | Include date, symptom, and blast radius. Keep under 3 sentences. |
| Timeline | How did events unfold? | Timestamps (HH:MM), events, actions, outcomes in chronological order. Copy Slack messages verbatim when useful. |
| Root cause | What structural flaw caused the symptoms? | Replace "DB was slow" with "missing query timeout." Use 5-whys if needed. |
| Action items | What must change to prevent recurrence? | Each item gets owner, due date, priority (P0/P1/P2). Replace vague "review improvements" with "add memory-usage alert at 80%." |
| Lessons learned | What insights did the team gain? | 2–3 points about system design, monitoring, procedure, or tooling. Write so other teams can learn too. |

## Good postmortem vs bad postmortem

### Bad example

```
Title: DB outage

Summary: DB was slow.

Cause: Something wrong with the DB server.

Resolution: Restarted the DB.

Follow-up: Improve DB monitoring.
```

Problems: no timeline, vague root cause ("something wrong" is a symptom), no owner or due date on the action, no impact quantification.

### Good example

```
Title: 2026-05-19 DB connection-pool exhaustion causing API latency spike

Summary: 18:45–19:20 API latency rose from 3 s to 15 s.
         12,000 users affected. Duration: 35 min.

Timeline:
- 18:45 — Latency alert fires (p99 > 15 s)
- 18:47 — IC assigned, #inc-0519-db-pool channel created
- 18:52 — DB connections at max (100) confirmed
- 18:58 — Temporary fix: pool size raised 100 → 200
- 19:10 — Latency below 3 s confirmed
- 19:20 — Incident closed

Root cause: Batch job held connections without releasing them.
            Connection timeout was not configured.

Action items:
1. [P0] Add 10-min connection timeout to batch job (@backend, 2026-05-22)
2. [P1] Alert on pool utilization > 80% (@sre, 2026-05-25)
3. [P2] Analyze batch connection patterns (@backend, 2026-05-30)

Lessons:
- Connection pools are not infinite; timeouts are mandatory.
- Pool monitoring must track wait time, not just connection count.
- Batch workloads should not share the API connection pool.
```

Why this is good: reconstructable timeline, structural root cause, quantified impact, actionable items with owners and deadlines, and transferable lessons.

## Hands-on: Writing a Postmortem

### Step 1 — Define the template

```python
template = {
    "title": "",
    "summary": "",
    "impact": "",
    "timeline": [],
    "root_cause": "",
    "actions": [],
    "lessons": [],
}
```

A shared template means every incident gets the same analytical frame. Consistency accelerates organizational learning.

### Step 2 — Summarize impact

```python
def impact_line(users, minutes):
    return f"{users} users affected for {minutes} min"
```

Impact summaries anchor the severity. User count, duration, and affected features make follow-up prioritization obvious.

### Step 3 — Timeline

```python
def event(t, msg):
    return {"time": t, "event": msg}
```

Timelines reduce memory confusion. Who saw what, when, and what action followed—these facts reveal the gap between symptom and response.

### Step 4 — Action items

```python
def action(desc, owner, due):
    return {"desc": desc, "owner": owner, "due": due}
```

Good action items have an owner and a deadline. Vague resolutions disappear; tracked tasks with assignees get done.

### Step 5 — Track open actions

```python
def open_actions(items):
    return [a for a in items if not a.get("done")]
```

Postmortem quality is measured by action completion rate, not document length. Without ongoing tracking, documents drift into an archive nobody reads.

## Postmortem example — cache cluster failure

```python
postmortem = {
    "title": "2026-05-19 Redis cluster OOM causing home-feed latency spike",
    "severity": "SEV2",
    "impact": {"affected_users": 8500, "duration_min": 25, "service": "Home Feed API"},
    "timeline": [
        "14:12 - Redis primary node OOM-killed",
        "14:13 - Feed latency alert (p99 > 5 s)",
        "14:15 - IC assigned, #inc-0519-redis channel created",
        "14:20 - Failover: replica promoted, cluster stabilized",
        "14:25 - DB fallback path serving partial requests",
        "14:30 - Feed p99 latency below 800 ms",
        "14:37 - Incident closed",
    ],
    "root_cause": "maxmemory-policy set to noeviction instead of allkeys-lru; "
                  "new key writes failed, errors accumulated, OOM triggered",
    "actions": [
        {"desc": "Change maxmemory-policy to allkeys-lru", "owner": "infra", "due": "2026-05-20", "priority": "P0"},
        {"desc": "Alert on cache memory > 80%", "owner": "sre", "due": "2026-05-22", "priority": "P1"},
        {"desc": "Analyze DB fallback cache-miss ratio", "owner": "backend", "due": "2026-05-25", "priority": "P2"},
    ],
    "lessons": [
        "Never rely on default cache config—verify explicitly.",
        "DB fallback prevented total outage but still impacted latency.",
        "Memory utilization monitoring is a core stability metric for cache clusters.",
    ],
}
```

This example shows structured timeline, explicit root cause, prioritized actions with owners, and transferable lessons.

## Writing timing

| Timing | Suitability | Reason |
| --- | --- | --- |
| Within 24 hours of recovery | Best | Memory is fresh, chat logs are still active |
| Within 1 week | Good | Main timeline recoverable, some detail may be lost |
| After 1 month | Poor | Most context forgotten, relying solely on logs |

Treat the postmortem as a mandatory step in the incident lifecycle, not an optional add-on.

## Action item tracking

The value of a postmortem does not end at writing—it emerges when follow-up work is actually completed. Create tickets in GitHub Issues, Jira, or Linear, and review progress weekly.

Every action item needs:

- **Clear description** — what must be done, concretely
- **Owner** — who is responsible
- **Due date** — when it must be completed
- **Priority** — P0 (immediate), P1 (this week), P2 (this month)
- **Linked postmortem** — which incident produced this action

Review open actions in the weekly SRE meeting. Record reasons for delays. Verify completed items actually had the intended effect.

## Postmortem health metrics

```python
def postmortem_health(postmortems):
    """Track process health over time."""
    total = len(postmortems)
    if total == 0:
        return {}

    avg_write_hours = sum(p["write_time_hours"] for p in postmortems) / total

    total_actions = sum(len(p["actions"]) for p in postmortems)
    done_actions = sum(
        sum(1 for a in p["actions"] if a.get("done"))
        for p in postmortems
    )
    completion_rate = done_actions / total_actions if total_actions else 0

    causes = [p["root_cause"] for p in postmortems]
    repeat_rate = 1 - len(set(causes)) / total

    return {
        "avg_write_hours": f"{avg_write_hours:.1f}h",
        "action_completion": f"{completion_rate*100:.0f}%",
        "repeat_incident_rate": f"{repeat_rate*100:.0f}%",
    }
```

| Metric | Target | Meaning |
| --- | --- | --- |
| Write time | Under 24 h | Faster writing = more accurate memory |
| Action completion rate | Above 90% | Learning converts to real changes |
| Repeat incident rate | Below 10% | Postmortems actually prevent recurrence |
| Sharing coverage | 100% of related teams | Others avoid the same mistake |

Review quarterly. Low action-completion signals ownership or prioritization problems.

## Sharing strategy

Postmortems are too valuable to stay inside the authoring team.

**Internal sharing:**
- Publish full postmortem on internal wiki or Confluence
- Review major incidents in weekly engineering meetings
- Link postmortems to shared-infrastructure teams

**Limited external sharing:**
- Provide customers a non-technical summary
- Post a brief timeline and blast radius on the status page
- If security vulnerabilities are involved, share only after patching

**Full public sharing:**
- Blog-format postmortem (e.g., Cloudflare, GitHub, GitLab)
- Builds community trust and helps competitors avoid the same failure

In all cases, sharing beats hiding. Long-term trust and learning speed both improve.

## What to Notice in This Code

- The template reduces variance in documentation quality.
- Impact, timeline, cause, and actions together form a complete learning loop.
- Owner and due date are the minimum tracking axes for action items.
- Postmortem value shows up in follow-up management, not at writing time.

## Five Common Mistakes

1. **Treating symptoms as root cause.** "Database overload" is a result; the cause might be missing query rate-limiting. Dig deeper.
2. **Stopping at the document.** Without tracked action items, learning never enters the organization's priority system.
3. **Not sharing the result.** Similar problems repeat in other teams using the same infrastructure.
4. **Personal blame leading to silence.** People withhold critical context when they fear punishment.
5. **Filling in the template without genuine analysis.** A complete form is not the same as actual learning.

## How a Senior Engineer Thinks

A senior engineer treats the postmortem not as paperwork but as an input device for system change. It is the most practical tool for ensuring the same failure does not recur.

They also keep postmortems connected to the tracking system (Jira, Linear, GitHub Issues). When document actions become real work tickets, learning enters the team's sprint and priority queue rather than sitting in a wiki.

## Checklist

- [ ] Shared postmortem template agreed upon.
- [ ] Blameless principle practiced in postmortem meetings.
- [ ] Action items tracked with owner, due date, and priority.
- [ ] Open actions reviewed weekly.
- [ ] Postmortem results shared with related teams.

## Practice Problems

1. Rewrite this blameful question as a blameless one: "Why didn't you notice the alert?"
2. A postmortem has 8 action items; 3 are still open after a month. What process failure does this suggest?
3. Your team's repeat-incident rate is 25%. Name two changes to the postmortem process that could lower it.

## Wrap-up and Next Steps

A postmortem is a learning system that turns incidents into organizational memory. When teams focus on system structure over blame, and on action completion over document polish, repeat outages decrease.

Next, we cover *reducing toil*—how to measure repetitive manual work and decide what to automate first.

## Answering the Opening Questions

- **Why is a postmortem closer to a learning device than a report?**
  A postmortem divides the incident into timeline and action items, reframing individual technical failures as systemic design flaws—it's a process for understanding, not documenting.
- **Why does critical information get omitted without blameless principles?**
  In a blameless culture, people don't speak defensively. Information gaps, missing warning signals, and procedural holes—the real causes—surface naturally when no one fears punishment.
- **What items must a good postmortem document always contain?**
  A common template ensures everyone records facts, impact, causes, and follow-up actions in the same skeleton—relying on structure rather than writing skill.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- **Postmortem (current)**
- [SRE 101 (8/10): Reducing Toil](./08-reducing-toil.md)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Etsy Debriefing Guide](https://extfiles.etsy.com/DebriefingFacilitationGuide.pdf)
- [Blameless Postmortems - Atlassian](https://www.atlassian.com/incident-management/postmortem/blameless)
- [PagerDuty Postmortem Guide](https://postmortems.pagerduty.com/)

Tags: SRE, Postmortem, BlamelessCulture, Learning, Operations
