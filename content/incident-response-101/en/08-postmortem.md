---
series: incident-response-101
episode: 8
title: "Incident Response 101 (8/10): Postmortem"
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
  - Postmortem
  - Blameless
  - Learning
  - Operations
seo_description: Learn how to write a blameless postmortem with quantified impact, owned action items, and a review loop that sticks.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (8/10): Postmortem

Once an incident is over, the emotional temptation is to move on quickly. The channel quiets down, customer impact is gone, and everyone wants to get back to roadmap work.

That is exactly when the most valuable learning can be lost. A good postmortem converts a stressful event into an organizational asset instead of a fading memory or a blame ritual.

This is the 8th post in the Incident Response 101 series. This post covers blameless postmortem structure, quantified impact, actionable follow-up items, and the review loop that keeps the document from becoming shelfware.


![incident response 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/08/08-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 8 flow overview*
> Postmortems are not optional. They are how the team learns and the codebase improves from each incident.

## Questions to Keep in Mind

- Why is a postmortem still necessary after the incident is already over?
- What does blameless analysis mean in practical terms?
- Why should the template stay stable across incidents?

## Why this topic matters

If the team cannot convert the incident into reusable learning, the same outage pattern comes back under a new name. Recovery restores service, but postmortem work is what restores organizational memory.

A strong postmortem also protects accuracy. It captures facts before memory fades and links them to work that can be prioritized, assigned, and revisited later. Everyone thinks they remember vividly right after the event, but within days the sequence and decision rationale blur. Without recorded facts, the organization ends up relying on the loudest voice or the most recent memory.

## Diagram at a glance

Publishing the document is only the midpoint. The real payoff comes when the review leads to tracked action items that are still checked later.

## Key Terms

- **blameless**: no personal blame — analyze system conditions and context, not individual fault.
- **summary**: a three-sentence recap.
- **impact**: what the customer experienced.
- **action item**: a verifiable follow-up.
- **owner**: the action's responsible person.

Blameless does not mean "no accountability." It means not ending the analysis at "person X made a mistake." Instead, ask what alerts were missing, what reviews were insufficient, what defaults were dangerous. That is how you prevent recurrence.

## Before/After

**Before**: an internal document of blame and defense. Readers look for who to blame.

**After**: an organization-wide, blameless document with tracked follow-ups. Readers look for what to change next.

In the "after" state, the document's purpose shifts. Structure comes before emotion, and good postmortems lead with facts rather than feelings.

## Hands-on: A Mini Postmortem Builder

### Step 1 — Template

A fixed template guarantees every postmortem covers the same sections. Teams that reinvent the format each time lose consistency and skip critical fields under pressure.

```python
TEMPLATE = ("summary", "impact", "timeline", "rca", "actions")

def new_doc():
    return {k: "" for k in TEMPLATE}
```

### Step 2 — Summary check

A good summary fits in three sentences. Keeping it short forces clarity—if you cannot summarize concisely, you probably have not identified the core issue yet.

```python
def is_short(text):
    return text.count(".") <= 3
```

### Step 3 — Quantify impact

Impact expressed as numbers (affected users, duration in minutes) removes ambiguity. "Many users were affected" is useless; "12,000 users for 23 minutes" drives the right priority.

```python
def impact(users, minutes):
    return {"users": users, "minutes": minutes}
```

### Step 4 — Register an action

Every action needs an owner and a deadline. Without both, follow-through drops to near zero and the same incident recurs.

```python
def action(text, owner, due):
    return {"text": text, "owner": owner, "due": due}
```

### Step 5 — Track

Tracking overdue actions closes the learning loop. If actions slip past their due date without notice, the postmortem was paperwork, not prevention.

```python
def overdue(actions, today):
    return [a for a in actions if a["due"] < today]
```

## What to Notice in This Code

- The template is fixed as a tuple — document structure never drifts.
- Impact is numeric — enabling comparison across incidents.
- Tracking is one deadline comparison — simple enough to automate.

Good postmortems come from the habit of fixing structure, not from writing talent. Consistent format lets readers scan quickly and makes cross-incident comparison straightforward.

## Five Common Mistakes

1. **Naming an individual as the cause** without examining system conditions.
2. **Actions with no owner.**
3. **Actions with no deadline.**
4. **Sharing only internally** — the rest of the organization never learns.
5. **Reinventing the template every time** — losing comparability.

The most dangerous mistake is a postmortem with no action items. The document may look polished, but nothing changes. That is a record, not a learning device.

## How This Shows Up in Production

Teams keep a Notion/Confluence postmortem template and link action items to Jira. A quarterly review tracks overdue items. This quarterly check is what reconnects the document to actual operations.

A senior engineer views blameless as culture. They expand root causes beyond individuals to system and process gaps. At the same time, they know a document without follow-through is meaningless.

## How a Senior Engineer Thinks

- Blameless is culture.
- No actions, no document.
- Impact is in numbers.
- Sharing is company-wide.
- The quarterly review closes the loop.

## Good and Bad Action Items — Detailed Comparison

Small wording differences determine whether a postmortem item will ever change production. Compare abstract items against specific, verifiable ones:

**Bad examples: abstract and unverifiable**

- Improve monitoring
- Improve communication
- Be more careful
- Add more detailed logs

**Good examples: specific and verifiable**

- Add an Alertmanager rule that opens a PagerDuty SEV2 incident when checkout API 5xx stays above 2% for three consecutive minutes. Owner: @platform-oncall. Due: 2026-06-01. Verify: Alertmanager config PR merged + test firing confirmed.
- Add an automatic timeline bot to the incident channel that attaches UTC timestamps to all messages. Owner: @incident-lead. Due: 2026-05-25. Verify: bot deployed + test incident channel confirmed.
- Apply structured logging with request_id to all services. Owner: @backend-team. Due: 2026-06-15. Verify: per-service PR + production log sample check.
- Add weekly automated load tests at production level to staging via CI, running every Tuesday morning. Owner: @qa-platform. Due: 2026-06-10. Verify: CI config PR + first run results.

Every good action item starts with a verb, names an owner, includes a due date, and specifies how to verify completion. This is what makes quarterly tracking possible and completion unambiguous.

## Blameless Postmortem Culture

The core of blameless postmortem is refusing to end analysis at individual mistakes. When the conclusion is "person X was wrong," the same structural conditions repeat in the next incident. Instead, ask: "What system conditions made that mistake possible?"

Example: an engineer ran a bad query against the production database, causing an outage.

Bad analysis:

- Cause: Engineer A modified production DB directly
- Follow-up: Warn Engineer A

Good analysis:

- Cause: Production DB access was granted to developer accounts + no review process before dangerous commands + staging and production connection strings were not clearly distinguished
- Follow-up: Move production DB access behind a bastion with approval workflow + add SQL query review checklist + include environment tags in connection strings

The good analysis finds multiple conditions that enabled the mistake and addresses all of them. In practice, teams tag postmortem documents as "blameless" at the top and request revisions if personal blame appears during review. This culture takes time but, once established, team members share facts honestly even after incidents.

## Postmortem Template Components

| Section | Role | Writing Tips |
| --- | --- | --- |
| Summary | Event overview | 3 sentences max; include severity, service, duration |
| Impact | Customer effect | Quantify users, duration, revenue impact |
| Timeline | Chronological record | UTC timestamps, separate fact from interpretation |
| Root Cause | Cause analysis | Distinguish trigger from root cause; use 5 Whys |
| Action Items | Follow-ups | Start with verb; owner + due date mandatory; include verification |
| Lessons Learned | Learning summary | What was learned; what changes next time |

A fixed template raises document consistency. New team members can scan past postmortems quickly, and quarterly reviews can find similar incident types easily. In practice, teams keep this as a Markdown or Notion template and copy-fill per incident.

## Full Postmortem Template

```markdown
# Postmortem: INC-YYYYMMDD-XXX

## 1) Incident Summary
- Date/Time (UTC):
- Severity:
- Affected Service:
- Incident Commander:
- Current Status: Resolved

## 2) Customer Impact
- Impacted users (estimate):
- Impact duration (minutes):
- Affected journey (checkout/login/search/...):
- Financial/contractual impact (if known):

## 3) Timeline (Fact Only)
- 00:01 detected ...
- 00:03 acknowledged ...
- 00:07 mitigation started ...
- 00:19 impact reduced ...
- 00:41 resolved ...

## 4) Root Cause Analysis
- Trigger:
- Root cause:
- Contributing factors:
  - People:
  - Process:
  - Tooling:
  - System:

## 5) What Went Well
-

## 6) What Could Be Improved
-

## 7) Action Items
| Action | Owner | Due | Priority | Verification |
| --- | --- | --- | --- | --- |

## 8) Follow-up Review Date
- YYYY-MM-DD
```

### Writing Guide

1. Keep summary under 5 sentences.
2. Always express impact in numbers.
3. Separate facts from notes in the timeline.
4. Describe causes at the system boundary, not at the individual.
5. Include verification method in every action item.

Following these five rules alone significantly reduces postmortem quality variance.

## Action Item Quality Criteria

- Does it start with a verb?
- Is an owner assigned?
- Is a due date specified?
- Is there a verification method?
- Is the priority clear?

If any single element is missing, execution rates drop sharply. Verification is especially critical — without it, completion reports become pro-forma.

## Tracking Automation

```python
from dataclasses import dataclass

@dataclass
class ActionItem:
    text: str
    owner: str
    due: str
    priority: str
    verify: str
    status: str = "open"

def is_complete(item: ActionItem) -> bool:
    return item.status == "done" and bool(item.verify)
```

The code is simple, but structuring state lets you quickly identify incomplete items during quarterly reviews.

## Operational Loop

- Draft postmortem within 48 hours of incident close
- Complete review within 5 business days
- Issue action item tickets with owner assignment
- Follow-up check within 30 days

When this loop is fixed, the postmortem stops being "a nice document" and becomes "a device that produces actual change."

## Review Meeting Structure

Postmortem review meetings are most effective when fact verification and improvement design are separated into two phases. The first meeting reviews only timeline and root-cause accuracy; the second meeting sets action item priorities. Combining everything in one session increases emotional drain and blurs conclusions.

| Phase | Goal | Input | Output |
| --- | --- | --- | --- |
| Phase 1 (Fact verification) | Confirm timeline/impact/RCA accuracy | Logs, dashboards | Corrected fact-based document |
| Phase 2 (Improvement design) | Decide action item priorities | Finalized Phase 1 document | Execution list with owner/due/verify |

This structure also supports blameless culture. Phase 1 deals only with facts; Phase 2 designs improvements — reducing the risk of the meeting drifting into personal evaluation.

Meeting results must connect to the ticket system. Comments in the document alone weaken execution tracking. Treat owner assignment and due-date confirmation as meeting exit conditions.

### Action Item Registration Template

```text
[action-item-template]
- description:
- owner:
- due_date:
- priority: (high/medium/low)
- verification:
- linked_ticket:
```

For a postmortem to become an organizational asset, action items must link to the ticket system. Document comments alone cannot sustain execution tracking.

### Postmortem Review Checklist

| Field | Verification Question |
| --- | --- |
| Summary | Does the core event fit in three sentences? |
| Impact | Are users/time/business impact quantified? |
| Timeline | Are facts separated from notes? |
| RCA | Are trigger and root cause distinguished? |
| Actions | Do all items have owner/due/verify? |

### Review Meeting Exit Criteria

1. All factual errors have been corrected.
2. Action item priorities have been agreed upon.
3. Each action item has a confirmed owner.
4. Due dates have been entered.
5. The next review date is on the calendar.

Exit criteria ensure the postmortem moves from the document stage to the execution stage.

## Checklist

- [ ] Template.
- [ ] Action register.
- [ ] Tracking tool.
- [ ] Quarterly review on the calendar.

## Practice Problems

1. Define blameless in one line.
2. Define action item in one line.
3. Define owner in one line.

## Wrap-up and Next Steps

Next, we cover prevention.

## Answering the Opening Questions

- **Why is a postmortem still necessary after the incident is already over?**
  - You have already paid a large cost for one incident. If you do not learn from it, the same cost recurs. A postmortem gathers information scattered across detection, mitigation, and recovery into one document that makes timeline, root cause, and action items explicit — turning experience into an organizational asset. As the operational loop showed, drafting within 48 hours while memory is fresh is essential.
- **What does blameless analysis mean in practical terms?**
  - Blameless means "do not punish individuals," not "no one is responsible." As the production DB example demonstrated, blaming an individual causes information hiding during the next incident. Find causes at the system/process level (missing access controls, unclear connection strings, absent review steps), but assign follow-up actions and owners clearly. That honors both principles simultaneously.
- **Why should the template stay stable across incidents?**
  - When the format varies per incident, mandatory fields like timeline, impact, root cause, and action items are easily omitted, and cross-incident comparison becomes impossible. The template components table shows each section's role — a fixed template reduces the author's cognitive load so more time goes to fact-gathering and analysis, and accumulated postmortems become a pattern-analyzable dataset.
<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity Classification](./02-severity.md)
- [Incident Response 101 (3/10): Initial Response](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Writing the Timeline](./05-timeline.md)
- [Incident Response 101 (6/10): Root Cause Analysis](./06-root-cause-analysis.md)
- [Incident Response 101 (7/10): Mitigation and Resolution](./07-mitigation-and-resolution.md)
- **Postmortem (current)**
- Prevention (upcoming)
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem Process - PagerDuty](https://response.pagerduty.com/after/post_mortem_process/)
- [Postmortem templates - Atlassian](https://www.atlassian.com/incident-management/postmortem/templates)
- [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/)

Tags: Incident, Postmortem, Blameless, Learning, Operations
