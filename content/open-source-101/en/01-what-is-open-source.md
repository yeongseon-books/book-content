---
series: open-source-101
episode: 1
title: "Open Source 101 (1/10): What Is Open Source"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - OpenSource
  - GitHub
  - Community
  - Contribution
  - Beginner
seo_description: Define open source beyond free code and learn how licenses, contribution flow, and community practices shape real projects.
last_reviewed: '2026-05-15'
---

# Open Source 101 (1/10): What Is Open Source

When people first hear *open source*, they often reduce it to price. Code that you can download for free is part of the story, but it does not explain why licenses matter, why issues and pull requests matter, or why a project's maintainers and community culture directly affect software quality.

This is the first post in the Open Source 101 series.

Here, we will define open source not as code that happens to be public, but as a system of rights, responsibilities, and collaboration patterns that let people read, change, and redistribute software together.

## Questions to Keep in Mind

- Why does the “free code” definition keep creating misunderstandings?
- How should you distinguish terms such as *free software*, *upstream*, *fork*, and *contributor*?
- Why do docs, translations, and reproducible bug reports count as real contribution?

## Big Picture

![open source 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/01/01-01-a-concept-map-you-can-keep-in-your-head.en.png)

*open source 101 chapter 1 flow overview*

This picture places What Is Open Source inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What Is Open Source is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

Modern software stacks sit on top of open source. Web frameworks, data tools, infrastructure automation, test libraries, and developer tooling all rely on projects maintained by people outside your company. So understanding open source means more than knowing how to download a dependency. It means understanding how today's software is built, reviewed, shipped, and sustained.

This matters immediately in production work. When teams evaluate a library, they do not look only at features. They also look at the license, release cadence, issue responsiveness, contributor documentation, and whether maintenance depends on one exhausted person. Reading open source well means reading both the code and the community around it.

## A Concept Map You Can Keep in Your Head

If you read that diagram as a strict hierarchy, you only understand half of it. In practice it is a loop. A user can report a bug and become a contributor through one issue or one typo fix. A contributor can start reviewing other people's work and gradually grow into a maintainer role. The point is not that everyone has the same responsibilities. The point is that the participation path is open.

That is why open source cannot be defined by code visibility alone. People must be able to read the code, modify it, and redistribute it under a license that permits those actions. Then the project still needs a working collaboration culture before it becomes a living project rather than a code dump.

## Key Terms You Should Get Right Early

When you first start reading open source projects, memorizing many terms is less useful than getting a small set of terms exactly right.

Open source is not merely software whose source is visible. It also implies a license that allows modification and redistribution. *Free software* emphasizes freedom more than price. It is about user rights, not about whether the cost is zero. *Upstream* means the original repository, not your personal fork. A *fork* is your copy under your account, usually used as a safe workspace for experiments and contributions. A *contributor* is not only someone who writes code. Docs, translations, design improvements, issue triage, and reproduction steps all count.

If these terms are clear, README, LICENSE, Issues, and Pull Requests stop looking like disconnected tabs. You begin to see them as one workflow.

## How Your Mental Model Should Change

At first, open source often looks like free code you can grab and use. A better definition is broader: it is a system of rights that let people read, modify, and share software, plus an operating model that turns those rights into real collaboration.

Once that shift clicks, the rest of the series lines up naturally. The license records the rights. Issues define problems together. Pull requests formalize shared review. Maintainers keep the whole flow sustainable over time.

## Hands-on: Read One Repository Like an Open Source Participant

### Step 1 — Find a repository

Do not start with a random project. Pick one where the language and topic are obvious so the later license and contribution cues are easier to interpret.

```bash
gh search repos --language python --topic open-source
```

### Step 2 — Check the license

Before you read the feature list, read the license. This is where the habit begins.

```bash
gh repo view fastapi/fastapi --json licenseInfo
```

### Step 3 — Look at contributor flow

This is a fast way to see whether the project is maintained by one person or by a healthier group of people. Raw contributor count matters less than whether work is distributed.

```bash
gh api repos/fastapi/fastapi/contributors --jq '.[].login' | head
```

### Step 4 — Check whether the entrance is open

For a beginner, the best starting point is often a small, well-scoped issue. The `good first issue` label is also a signal that the project has thought about onboarding new contributors.

```bash
gh issue list --repo fastapi/fastapi --label "good first issue"
```

### Step 5 — Star the repo

A star is not a dramatic contribution, but it is still a signal of interest and usage for the project.

```bash
gh repo star fastapi/fastapi
```

## What to Notice in This Walkthrough

The goal here is not to memorize commands. It is to learn a reading order. The license should often be read before the feature list. The contributor list tells you whether the project looks sustainable. A `good first issue` label is not just metadata. It is an onboarding path.

Once you start opening repositories with these questions in mind, you stop asking only “Is this useful code?” and start asking “Is this a project I can trust and possibly work with?” That is the more useful question.

## Five Common Mistakes

1. Reading only the repository description and skipping the license.
2. Treating your fork and the upstream repository as if they were the same thing.
3. Using issues as a generic support desk.
4. Assuming only code contribution counts.
5. Trying to make your first contribution a large feature.

## How This Shows Up in Production

Senior engineers do not read open source as a feature catalog alone. They also inspect release frequency, issue response time, documentation quality, license compatibility, and how many maintainers actually carry the project. The reason is simple: production systems sit on top of the health of those projects.

Even one small contribution matters more than it first appears. Fixing a typo or improving a reproduction guide still forces you to read the repository structure, follow contribution rules, go through review, and leave a change history behind. After you do that once, the next contribution becomes far easier.

## How a Senior Engineer Thinks

- Open source is a rights model, not a pricing model.
- Contribution is broader than code.
- The entry path matters as much as the code quality.
- A healthy community is a real engineering asset.
- Small contributions often create the fastest learning loop.

## Checklist

- [ ] I found one repository I care about.
- [ ] I checked the `LICENSE` or `licenseInfo` field.
- [ ] I found one issue labeled `good first issue`.
- [ ] I read the README or CONTRIBUTING guide for the contribution flow.

## Practice Problems

1. Define open source in one sentence.
2. Explain the difference between *upstream* and *fork* in one sentence.
3. Give three examples of contribution that are not feature code.

## Wrap-up and Next Steps

In this post, we established the basic view that open source is not just free code. It is an ecosystem of rights and collaboration. That view matters because the rest of the series only becomes coherent once licenses, issues, pull requests, maintainers, and community norms are all seen as parts of one flow.

Next, we will move into licenses. The moment you use open source, you are not making a technical choice alone. You are also accepting legal terms.

## Answering the Opening Questions

- **Why does the “free code” definition keep creating misunderstandings?**
  - The article treats What Is Open Source as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How should you distinguish terms such as *free software*, *upstream*, *fork*, and *contributor*?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why do docs, translations, and reproducible bug reports count as real contribution?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is Open Source (current)**
- Understanding Licenses (upcoming)
- Reading Issues (upcoming)
- Creating Pull Requests (upcoming)
- A Good README (upcoming)
- Release and Versioning (upcoming)
- Community Management (upcoming)
- The Maintainer Role (upcoming)
- An Open Source Portfolio (upcoming)
- My First Open Source Project (upcoming)

<!-- toc:end -->

## References

- [Open Source Initiative](https://opensource.org/osd)
- [Free Software Foundation - GNU Project](https://www.gnu.org/philosophy/free-sw.html)
- [Open Source Guides - GitHub](https://opensource.guide/)
- [opensource.guide repository](https://github.com/github/opensource.guide)
- [The Cathedral and the Bazaar - Eric Raymond](http://www.catb.org/~esr/writings/cathedral-bazaar/)

Tags: OpenSource, GitHub, Community, Contribution, Beginner
