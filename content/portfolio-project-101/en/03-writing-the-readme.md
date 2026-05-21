---
series: portfolio-project-101
episode: 3
title: "Portfolio Project 101 (3/10): Writing the README"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Portfolio
  - README
  - Documentation
  - Onboarding
  - Beginner
seo_description: How to write a README that helps a hiring reviewer understand your project quickly and decide what to inspect next.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (3/10): Writing the README

A good project can still lose power at the entrance if the README is weak. Most visitors read the README before they read any code. In that short window, they need to understand what problem the project solves, whether there is a demo worth opening, and how they could run it themselves.

If those answers are buried or missing, the reviewer often leaves before your implementation quality gets a chance to matter.

This is post 3 in the Portfolio Project 101 series. Here we will treat the README as the project's first demo and look at how to arrange it so a reviewer can understand the value in about a minute.

---

> A strong README is not just a repository description. It is an entry document that helps a first-time visitor decide what to do next.


![portfolio project 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/03/03-01-concept-at-a-glance.en.png)
*portfolio project 101 chapter 3 flow overview*
> A README is the face of a repository. If you can explain the problem and solution within a minute, the visitor gains momentum to read code.

## Questions to Keep in Mind

- What information should a portfolio README show first?
- Why does the order pitch → demo → stack → run → next feel easy to scan?
- Why can a README still feel weak even when it contains many screenshots?

## Why It Matters

A README shapes the first impression of the project. The exact same codebase can feel much stronger when the README is tight, structured, and honest about the current state. Reviewers often read communication quality, onboarding care, and scope discipline from the README itself.

In portfolio work, that matters a lot because the reviewer is not a teammate who already knows the context. The README has to do the work of orientation on its own.

## Mental Model

The simplest way to design a README is to follow the visitor’s question order.

Most first-time readers think in roughly this order: what is this, does it work, what is it built with, can I run it, and what is still left. A README works best when it follows that flow instead of following the author's implementation history.

## Key Terms

- **Pitch**: a one-line summary of the problem and project shape.
- **Demo**: a live link or screenshot that proves the product experience exists.
- **Stack**: the short list of technologies that matter for orientation.
- **Run path**: copy-paste steps for trying the project locally.
- **Next**: the unfinished work or improvement list that sets expectations honestly.

## Before and After

**Before**: the README shows a title and maybe an install command, but the actual value of the project is hard to infer.

**After**: a visitor can understand the project, open the demo, and decide whether to inspect the implementation in well under a minute.

The difference is not length. It is whether the document is written for a first-time reader.

## Step by Step

### Step 1 — Start with a one-line pitch

Lead with the problem the project solves, not the framework name.

```markdown
> A mini SaaS that fixes lost team schedules
```

A strong pitch does not repeat the title. It compresses the reason the project exists.

### Step 2 — Surface the demo early

A reviewer should not have to hunt for the proof.

```markdown
[Live Demo](https://demo.example.com)
```

A visible demo link creates trust faster than a long explanation paragraph.

### Step 3 — Keep the stack short

The stack section is for orientation, not for showing off every library.

```markdown
- FastAPI, PostgreSQL, Docker
```

The goal is to make the system shape legible. The reasoning behind those choices can live elsewhere.

### Step 4 — Make the run path copy-paste friendly

The first local run should feel simple.

```bash
docker compose up
```

The more setup assumptions you require, the weaker the README becomes as an onboarding path.

### Step 5 — Leave the next tasks visible

Unfinished work is easier to trust when it is named clearly.

```markdown
- [ ] add notifications
```

A next-tasks section is not a weakness. It shows scope control and gives the reviewer an honest sense of what is done versus what is still planned.

## What to Notice in the Code

- The pitch should describe the problem, not restate the title.
- The demo should arrive before deep detail.
- The run path should be short enough that a reviewer can try it without guesswork.

## Common Mistakes

1. Starting with a long preface that pushes the real value too far down.
2. Showing only screenshots without a live link or clear run path.
3. Making the setup instructions too complex for a quick first pass.
4. Naming the stack without explaining what the project is trying to do.
5. Hiding unfinished work so the current state becomes harder to judge.

A README does not win by saying everything. It wins by making the next step obvious.

## How This Reads in Practice

Well-maintained open source projects usually repeat the same pattern: short intro, quick start, visible example or demo, and a clear path to the deeper docs. They do that because first-time visitors always need roughly the same things.

Portfolio projects benefit from the same discipline. A small repository can feel polished when the entry path is easy to follow.

## Checklist

- [ ] The README opens with a problem-first pitch.
- [ ] The demo link or screenshot is visible immediately.
- [ ] The local run path is easy to copy and follow.
- [ ] The core stack is listed without unnecessary noise.
- [ ] The next tasks are written down honestly.

## Practice Problems

1. Rewrite your project pitch without using technology names.
2. List the three things a reviewer should learn within 30 seconds.
3. Find the least friendly part of your current run section and rewrite it.

## Wrap-up and Next Steps

A README is not just a summary page. It is the first user experience of the project. When it leads with the problem, proves the demo, makes the run path simple, and shows unfinished work honestly, even a small project becomes much easier to trust.

Next, we will move from the repository to the product surface itself and look at how to build a demo that reveals value quickly.

## Answering the Opening Questions

- **What information should a portfolio README show first?**
  - The article treats Writing the README as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why does the order pitch → demo → stack → run → next feel easy to scan?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why can a README still feel weak even when it contains many screenshots?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Portfolio Project 101 (1/10): What is a Portfolio Project](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): Traits of a Good Project](./02-traits-of-a-good-project.md)
- **Writing the README (current)**
- Building the Demo (upcoming)
- Deploying the Project (upcoming)
- Tests and Documentation (upcoming)
- Recording Tech Decisions (upcoming)
- Summarizing as Blog Posts (upcoming)
- Explaining in Interviews (upcoming)
- Portfolio Improvement Checklist (upcoming)

<!-- toc:end -->

## References

- [About READMEs (GitHub Docs)](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Make a README](https://www.makeareadme.com/)
- [Standard Readme](https://github.com/RichardLitt/standard-readme)
- [Awesome README](https://github.com/matiassingers/awesome-readme)

Tags: Portfolio, README, Documentation, Onboarding, Beginner
