---
series: capstone-project-101
episode: 4
title: "Capstone Project 101 (4/10): Organizing Requirements"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Capstone
  - Requirements
  - Spec
  - Scope
  - Beginner
seo_description: A beginner-friendly tour of organizing capstone requirements through user stories, non functional needs, and priorities.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (4/10): Organizing Requirements

A feature list alone does not help when the schedule slips. It does not tell the team what can be cut first or what done actually means.

A useful requirements document behaves more like a compact delivery contract. It links user stories, acceptance criteria, non-functional constraints, and priority labels in one place.

This is the 4th post in the Capstone Project 101 series. It turns the problem statement into implementable requirements and explicit verification criteria.


![capstone project 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/04/04-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 4 flow overview*
> Strong requirements emerge from the gap between what users need and what's buildable. Documentation captures that tension so priorities stay visible.

## Questions to Keep in Mind

- Why is a feature list alone not enough?
- How should user stories pair with acceptance criteria?
- Why should non-functional constraints live in a separate table?

## What You Will Learn

- *User stories*
- *Non-functional* needs
- Setting *priority*
- *Acceptance* criteria
- Requirement *traceability*

## Why It Matters

Without acceptance criteria, teams can finish implementation and still disagree about whether the requirement is actually done. Once criteria and priority live together, scope cuts become far less emotional.

Non-functional constraints deserve their own space too. Requirements such as mobile usability, no-sign-up flow, or response-time targets disappear quickly when they are buried inside generic feature bullets.

## Practical artifact: a requirements sheet

Adding IDs like the sheet below makes it much easier to connect implementation tasks and later test checks.

```text
ID: ST-1
User story: as a student, I want to confirm schedule conflicts immediately
Acceptance criteria: input within 5 seconds, results within 1 second, clear error messages
Non-functional needs: mobile-first, usable without sign-up, Korean-first copy
Priority: Must
Linked features: F-1 timetable input, F-2 conflict engine, F-3 results view
```

## What to validate first

- Make acceptance criteria observable rather than subjective.
- Separate non-functional needs from the user story itself.
- Check that not every line has been promoted to Must.
- Ensure the requirement ID can later map to features or tests.

## Key Terms

- **user story**: a request written from the user's perspective describing what they need and why.
- **acceptance criteria**: concrete conditions that must be true for a story to count as done.
- **non-functional**: quality attributes (performance, usability, security) that constrain the solution.
- **MoSCoW**: a priority labeling system — Must, Should, Could, Won't.
- **traceability**: explicit links from requirements to features, tests, and demo scenes.

## Before/After

**Before**: A *list of features*.

**After**: *Stories + criteria + priority*.

## Hands-on: Requirements Table

### Step 1 — User story

Write the story in plain user language: as a student, I want instant conflict detection.

A good story starts with a role ("as a …"), states the desire ("I want …"), and optionally explains the value ("so that …"). Keeping this structure forces you to stay in the user's world rather than the developer's.

### Step 2 — Acceptance criteria

Summarize the acceptance criteria as a short checklist:

- `input 5s` — user can complete input within 5 seconds
- `result 1s` — system returns results within 1 second
- `error clear` — any error message tells the user what to do next

Each criterion must be observable. If you cannot demonstrate it live during the presentation, it is not acceptance criteria — it is a wish.

### Step 3 — Non-functional

Keep the non-functional constraints separate as well:

- `mobile` — layout works at 390 px width
- `no_signup` — core flow usable without account creation
- `korean_first` — all user-facing copy in Korean by default

Non-functional items often get forgotten until the demo rehearsal reveals them. Writing them early prevents last-minute redesigns.

### Step 4 — Priority

Record priority in one consistent format, for example `core=Must`, `share=Should`, and `ai=Could`.

The MoSCoW rule keeps priority to four buckets maximum. More than four and the team starts gaming the labels. Fewer than three and everything becomes "high priority."

### Step 5 — Trace

Write trace links directly, such as `ST-1 -> F-1, F-2`, so requirement IDs connect to implementation items.

Traceability is what turns a requirements sheet into a living document. When a test fails, the trace tells you which user story is at risk. When a feature is cut, the trace shows which stories lose coverage.

## What to Notice in This Code

- *Stories* start with *verbs* — they describe actions, not objects.
- *Criteria* combine *numbers* and *readability* — measurable yet understandable.
- *Trace* uses *IDs* — allowing cross-referencing without ambiguity.

## Five Common Mistakes

1. **The story drifts into feature description.** "Implement a conflict-detection module" is not a user story.
2. **Forgetting non-functional needs.** Response time and mobile layout surprise the team during the demo.
3. **Everything is Must.** When everything is highest priority, nothing is prioritized.
4. **Subjective criteria.** "Works well" cannot be verified.
5. **No traceability.** Disconnected requirements become invisible during testing.

## How This Shows Up in Production

Startup PMs use Must/Should/Could labels every sprint planning. The practice is identical — requirements without priority labels produce infinite scope negotiation. Adding acceptance criteria to each ticket saves hours of back-and-forth between developers and product owners.

## How a Senior Engineer Thinks

- Stories stay short — one sentence, one need.
- Criteria are measurable — "within N seconds" beats "fast."
- Priority is three or four buckets — never ten.
- Non-functional lives separately — it is too easy to forget otherwise.
- Trace is documented — orphan requirements rot silently.

## Checklist

- [ ] Five or more user stories written.
- [ ] Each story has acceptance criteria with numbers.
- [ ] Non-functional constraints in a separate table.
- [ ] Priority labels (MoSCoW) assigned to every item.

## Practice Problems

1. Define *user story* in one line.
2. Define *acceptance criteria* in one line.
3. State the meaning of *MoSCoW* in one line.

## Deep Dive: Role Assignment Table and Collaboration Tool Comparison

Once requirements are organized, the next thing you need is alignment between roles, tools, and decision flow. If you have a requirements document but no clarity on who owns each item's final decision, the document goes stale the moment a change request arrives. Requirements items must connect directly to team roles and collaboration tools.

### Role Assignment Criteria Table

| Area | Primary Owner | Backup | Deliverable | Approval Criterion |
| --- | --- | --- | --- | --- |
| Requirements maintenance | Team lead | QA owner | Requirements sheet, change log | Change reason and impact scope recorded |
| API spec | Backend owner | Frontend owner | OpenAPI draft, sample request/response | Frontend confirms implementability |
| Screen flow | Frontend owner | Team lead | Wireframes, screen state table | Core flow demonstrable in 60 seconds |
| Test criteria | QA owner | Backend owner | Test scenarios, defect list | All Must features pass |
| Schedule sync | Team lead | Everyone | Weekly plan, blocker log | Milestone delay detected early |

The purpose of this table is not role rigidity — it is bottleneck elimination. When work is blocked, being able to immediately find "who decides" prevents requirements changes from cascading into schedule shocks.

### Collaboration Tool Comparison

| Tool | Strength | Weakness | Recommended Use |
| --- | --- | --- | --- |
| Notion | Easy document structuring and sharing | Low version-tracking granularity | Requirements drafts, meeting notes |
| GitHub Issues | Strong change history and code linkage | Entry barrier for non-technical members | Implementation issues, bugs, action items |
| Google Sheets | Fast table editing | Weak contextual linking | Priority tables, schedule tracking |
| Figma | Easy screen flow sharing | Poor for requirements text tracking | UI flows, demo storyboards |
| Slack/Discord | Instant communication | Decisions scattered across threads | Notifications, quick sync |

The tool selection principle is "no single tool solves every problem." Separate your minimum toolset into a document-centric tool, a task-tracking tool, and a communication tool — that keeps operations simple.

### Change Request Protocol

```text
1) Register the change proposal: write what and why in 3 sentences
2) Impact analysis: link requirement ID, feature ID, test ID
3) Role assignment: designate primary owner / backup / reviewer
4) Approve or defer: judge against Must/Should criteria
5) Record preservation: add date and reason to the change log
```

Applying this protocol lets you explain "the idea is good but we are not doing it now" with documented evidence. In team collaboration, conflict arises less from ideas themselves and more from priority misalignment — so a recordable process is essential.

### Mistake Prevention Checklist

- Does every requirement have an assigned owner and reviewer?
- Have verbal agreements been reflected in the document?
- Is duplicate entry across tools excessive?
- Have Slack conversation decisions been promoted to issues or documents?
- Is the change log reviewed at least once a week?

When you design roles and tools alongside requirements, you drastically reduce the "documents exist but execution is slow" problem during MVP implementation.

## Practical Anchor: Requirements Traceability Table and Demo Script Template

The most frequent problem at the requirements stage is "documents exist but they do not connect to the presentation." To prevent this, track requirements, tests, and demo scenes in a single table.

### Requirements Traceability Table

| Requirement ID | User Story | Acceptance Criteria | Test Cases | Demo Scene |
| --- | --- | --- | --- | --- |
| RQ-01 | Enter timetable | Saved without input error | TC-01, TC-02 | Scene 1 |
| RQ-02 | View conflicting courses | 100 % conflict detection | TC-03, TC-04 | Scene 2 |
| RQ-03 | Share results | Share link generated | TC-05 | Scene 3 |

### Presentation Demo Script Template

```text
Scene 1 (30 s): Introduce the problem situation
Scene 2 (60 s): Input and verification flow
Scene 3 (60 s): Result confirmation and value explanation
Scene 4 (30 s): Limitations and next steps
```

Managing the script alongside the requirements document reduces last-minute scene changes before the presentation. It also immediately reveals which requirements are not actually demonstrated, making scope re-alignment easier.

## Wrap-up and Next Steps

Requirement organization is about traceable scope, not prettier feature bullets. Once stories, criteria, non-functional needs, and priority labels live together, design and schedule decisions get much faster. The next post shows how that work should be split across the team.

## Answering the Opening Questions

- **Why is a feature list alone insufficient for requirements?**
  - This article unpacks requirements organization not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **How does a user story differ from a feature description?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **How specific should acceptance criteria be?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- [Capstone Project 101 (3/10): Defining the Problem](./03-defining-the-problem.md)
- **Organizing Requirements (current)**
- Splitting Team Roles (upcoming)
- Designing the MVP (upcoming)
- Choosing the Tech Stack (upcoming)
- Schedule Management (upcoming)
- Building Presentation Materials (upcoming)
- Project Retrospective (upcoming)

<!-- toc:end -->

## References

### Official docs and practical guides

- [Atlassian requirements guide](https://www.atlassian.com/agile/product-management/requirements)
- [User Stories Applied](https://www.mountaingoatsoftware.com/books/user-stories-applied)
- [Specification by Example](https://gojko.net/books/specification-by-example/)
- [INVEST in Good Stories](https://www.agilealliance.org/glossary/invest/)

Tags: Capstone, Requirements, Spec, Scope, Beginner
