---
series: developer-career-101
episode: 8
title: "Developer Career 101 (8/10): Side Projects and Learning"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
- Career
- SideProject
- Learning
- Portfolio
- Beginner
seo_description: A beginner-friendly tour of running a side project alongside a full-time
  job.
last_reviewed: '2026-05-14'
---

# Developer Career 101 (8/10): Side Projects and Learning

The hardest part of side projects is usually not finding ideas. It is choosing a scope that can survive real life. A project that competes with your day job, drifts without a finish line, or ignores IP boundaries often becomes a source of fatigue instead of a source of growth.

This is the 8th post in the Developer Career 101 series.


![developer career 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/developer-career-101/08/08-01-concept-at-a-glance.en.png)
*developer career 101 chapter 8 flow overview*
> Side projects are valuable not for the technology stack, but for owning the full responsibility: from gathering requirements to running production.

## Questions to Keep in Mind

- What makes a side project compatible with a full-time job?
- Why does a small MVP beat a grand vision for long-term learning?
- How do time boxes, public releases, and feedback loops keep the work sustainable?

## What You Will Learn

- Picking the *project*
- *Time boxing*
- *Releasing* and gathering *feedback*
- *Separation* from work
- A *sustainability* strategy

## Why It Matters

A good side project leaves both learning and evidence behind. Conversely, projects with unclear scope and boundaries pile up fatigue without producing results.

> The core of a side project is not a grand idea but a structure for finishing small and leaving learning behind.

## The Big Picture

A side project is not a marathon of endurance. It needs a structure: pick an idea, limit time, ship small, collect feedback, and move to the next cycle. Without that structure, burnout arrives before results do.

## Key Terms

- **side project**: Hobbyist or supplemental project.
- **time-box**: Bounded time slot.
- **MVP**: Minimum viable product.
- **moonlighting**: Undisclosed second job.
- **conflict of interest**: Conflicting obligations.

## Before/After

**Before**: "Lots of ideas, none finished."

**After**: "One small MVP shipped each quarter."

## Hands-on: Run the Side Project

### Step 1 — Pick the Idea

```text
criteria:
- interest
- learning value
- no conflict with day job
```

A good idea is not a flashy idea. It needs to be interesting, have clear learning value, and not conflict with your day job—that is what makes it sustainable.

### Step 2 — Time Box

```text
4 hours/week (Sat 09-13)
```

A side project should happen in pre-reserved time, not "whenever there is spare time." Once you start spending unlimited time, both health and your day job suffer.

### Step 3 — Define MVP

```markdown
- 1 core feature
- 1 command
- 1 README
```

The MVP is the device that creates a finish line. One core feature and minimal documentation is enough for a first public release.

### Step 4 — Publish

```bash
gh repo create --public
# README + LICENSE + first release
```

Without publishing, feedback is delayed and motivation weakens. Even a small repo gains asset status once it has a README, LICENSE, and first release.

### Step 5 — Separation Policy

```text
- no company assets
- IP review with employer
```

Separation from your day job is a safety measure. Never mix company assets, and confirm intellectual property terms to avoid unnecessary problems later.

## Scorecard for Choosing Side Projects

| Criterion | High score looks like | Warning sign |
| --- | --- | --- |
| Learning value | Closes a real career gap | Repeats only what you already know |
| Finishability | MVP fits in four to six weeks | Core scope already has three major features |
| Publishability | Easy to explain with README and demo | Output stays invisible |
| Boundary safety | Clean separation from employer assets and IP | Contract language is unclear |

## Side Project Planning Template

The biggest reason side projects end in abandonment is the absence of scope and time boundaries. Fixing a minimal template at the planning stage dramatically raises completion rates.

| Item | Writing standard | Example |
| --- | --- | --- |
| Problem definition | One sentence | "Auto-categorize personal expenses" |
| User | Exactly one segment | Yourself + 1 test user |
| MVP scope | 1 core feature | Receipt entry/classification only |
| Timeline | 4–6 week limit | Saturday 4 hours × 5 weeks |
| Publication format | Verifiable form | GitHub README + demo video |

## Time Management Table

When running alongside a day job, time budgets—not willpower—are the standard.

| Week | Dev time | Doc time | Retro time | Goal |
| --- | --- | --- | --- | --- |
| Week 1 | 3 hrs | 1 hr | 30 min | Lock requirements/MVP |
| Week 2 | 4 hrs | 1 hr | 30 min | Implement core feature |
| Week 3 | 4 hrs | 1 hr | 30 min | Test/bug fix |
| Week 4 | 3 hrs | 2 hrs | 30 min | Deploy/finish README |
| Week 5 | 2 hrs | 2 hrs | 1 hr | Retro/next plan |

The table shows that documentation and retro time matter as much as coding time. In practice, what raises portfolio value is often the decision record and publication quality rather than the implementation itself.

## Strategy for Repeating Small Completions

- Instead of "one big push," repeat "4–6 week completions."
- Ship the minimum deployable version first; add features in release increments.
- After publishing, collect 3 pieces of feedback and feed them into the next cycle's requirements.
- During high-fatigue weeks from your main job, switch to maintenance and documentation.

Sustainable side projects come from rhythm management, not high-intensity sprints.

## 10-Week Roadmap

The most common reason side projects stall is that goals are too large. The roadmap below focuses on producing a deployable result within ten weeks.

| Week | Goal | Deliverable | Completion criteria |
| --- | --- | --- | --- |
| Weeks 1–2 | Problem definition/scope lock | 1-page PRD, core user scenario | Exclusion list is clear |
| Weeks 3–4 | MVP implementation | 1 core feature working | 3-min demo video possible |
| Weeks 5–6 | Data/logging | DB schema, structured logs | Error reproduction path traceable |
| Weeks 7–8 | Test/deploy | 20 tests, CI pipeline | Redeployment possible within 30 min |
| Weeks 9–10 | Documentation/sharing | README, retro, presentation materials | Someone else can run it within 1 hour |

To raise completion probability, decide on one feature to delete every week. Knowing what to remove is more important than knowing what to add. Especially when investing 7–8 hours or fewer per week, operational quality matters more to resume credibility than feature count.

## Time Budget Table: Working Alongside a Day Job

Without a realistic time allocation, side projects become guilt routines. Below is an 8-hour-per-week budget model.

| Activity | Hours | Notes |
| --- | ---: | --- |
| Implementation | 4 hrs | Schedule during your highest-energy time slot |
| Testing/debugging | 2 hrs | Fixed Saturday morning |
| Documentation/retro | 1 hr | Sunday evening 30 min × 2 |
| Learning/research | 1 hr | Only topics directly needed for implementation |

The key is not expanding learning time infinitely. Distinguish "learning for the project" from "learning for learning's sake." If a deliverable is the goal, research should not exceed 20 % of total time.

## Portfolio Connection Result Template

After finishing a project, organize it in this format.

| Question | Example answer |
| --- | --- |
| What problem did it solve? | "Schedule-sharing delays in small teams" |
| Why this architecture? | "Minimized ops complexity with a single service initially" |
| What was improved? | "Notification failure rate 9 % → 2 %" |
| What is the next step? | "Introduce async queue, add notification retry policy" |

Sentences organized with this template can be reused directly as resume bullets, portfolio body text, and interview answers.

## Learning Roadmap + Side Project Connection Table

When learning and projects are disconnected, both stall. Attach each learning topic to an immediate project task as shown below.

| Learning topic | Project task | Completion signal |
| --- | --- | --- |
| Auth/authz | Implement login/permission separation | Permission tests pass |
| Data modeling | Redesign core entity schema | Query response time improved |
| Observability | Add error logging/alerts | Root cause identifiable within 10 min |
| Deploy automation | Build CI pipeline | Tag-based deploy succeeds |

This approach reduces the disconnect of "studied but never implemented."

## Pre-Release Checklist

Before publishing a project, check trust factors over features.

| Item | Verification question |
| --- | --- |
| Execution reproducibility | Can someone else run it within 10 minutes? |
| Error handling | Does the user see actionable guidance on failure? |
| Observability | Are minimal logs and a status page present? |
| Documentation quality | Are problem definition and architecture rationale clear? |

Projects that pass this checklist also hold up structurally when explained in interviews.

## Deletion Rules to Prevent Learning Overload

To keep a side project alive long-term, deletion rules matter more than addition rules. Check three things at your weekly retro:

1. Did the feature I added this week directly improve the core user scenario?
2. Did I boldly remove a high-maintenance-cost feature?
3. Did I limit next week's priorities to three or fewer?

Following this principle keeps direction clear even as the project grows longer.

## Release Notes Template

Even small projects gain higher growth-record quality when you leave release notes. Summarizing what changed in this version, why, and what the user impact is in three lines makes it much easier to explain project execution strength in future interviews.

## Demo Preparation Checkpoint

Right before a demo, stop adding features and focus on stabilization. Running through the start scenario, failure scenario, and recovery scenario once each dramatically reduces unexpected errors during presentation.

## What to Notice in This Code

- A time box is sustainable.
- MVP is the finish line.
- Separation is safety.

## Five Common Mistakes

1. **Mixing in company code.**
2. **Spending unlimited time.**
3. **An MVP too large.**
4. **No license.**
5. **Never shipping.**

## How This Shows Up in Production

Companies spell out open source contribution rules in employment contracts. Side projects are learning tools and simultaneously tests of professional boundary awareness.

## How a Senior Engineer Thinks

- Start small.
- Shipping is motivation.
- Time boxes protect health.
- Separation is job safety.
- Sustainment compounds.

## Checklist

- [ ] Four-hour weekly box.
- [ ] MVP defined.
- [ ] Release procedure.
- [ ] IP review.

## Practice Problems

1. One line: define moonlighting.
2. One line: example of conflict of interest.
3. One line: criteria for an MVP.

## Wrap-up and Next Steps

A good side project is not one that holds a big dream for a long time—it is one that finishes small within boundaries that do not conflict with your main job. Once idea, time, publication, and boundaries are settled, a side project leaves both learning and portfolio evidence behind. The next post covers how to operate mentoring and networking to move beyond the limits of studying alone.

## Answering the Opening Questions

- **What conditions should a good side project have to avoid conflicting with your main job?**
  - A side project's value lies not in technology but in the experience of driving the entire cycle from requirements definition to deployment and maintenance.
- **Why start with a small MVP instead of a too-large idea?**
  - Even small projects that receive user feedback, fix bugs, and add features create practical growth.
- **How do time-boxing, publishing, and feedback make side projects sustainable?**
  - Side projects published on GitHub with thorough READMEs become powerful evidence during job changes or evaluations.
<!-- toc:begin -->
## In this series

- [Developer Career 101 (1/10): What Is a Developer Career](./01-what-is-developer-career.md)
- [Developer Career 101 (2/10): Understanding Roles](./02-understanding-roles.md)
- [Developer Career 101 (3/10): Building a Learning Plan](./03-learning-plan.md)
- [Developer Career 101 (4/10): Resume and Portfolio](./04-resume-and-portfolio.md)
- [Developer Career 101 (5/10): Preparing for Coding Interviews](./05-coding-interview.md)
- [Developer Career 101 (6/10): System Design Interviews](./06-system-design-interview.md)
- [Developer Career 101 (7/10): Settling into the First Job](./07-first-job.md)
- **Side Projects and Learning (current)**
- Mentoring and Networking (upcoming)
- The Path to Senior (upcoming)

<!-- toc:end -->

## References

- [GitHub Docs — Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [Open Source Guides — Legal](https://opensource.guide/legal/)
- [Indie Hackers](https://www.indiehackers.com/)
- [Time blocking method](https://todoist.com/productivity-methods/time-blocking)

Tags: Career, SideProject, Learning, Portfolio, Beginner
