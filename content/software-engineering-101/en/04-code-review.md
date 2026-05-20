---
series: software-engineering-101
episode: 4
title: "Software Engineering 101 (4/10): Code Review"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - SoftwareEngineering
  - CodeReview
  - PullRequest
  - Collaboration
  - Quality
seo_description: The real purpose of code review, how to write a reviewable PR, what reviewers actually look at, and the most common mistakes.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (4/10): Code Review

Code review is one of the most common collaboration rituals in software teams, and one of the easiest to hollow out. The author wants to merge, the reviewer is busy, CI is already green, and the diff is hundreds of lines long. In that situation, review can quietly degrade into a formality that catches neither defects nor knowledge gaps.

A strong review is not just a search for bugs. It is a checkpoint for intent, system impact, and team understanding. The practical question is not whether review is valuable. It is whether the pull request, the automation, and the comment culture make human judgment possible in the first place.

This is post 4 in the Software Engineering 101 series. In this chapter, we look at how to make a PR reviewable, what humans should still review after automation, and how teams keep review focused on decisions instead of noise.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Code Review?
- Which signal should the example or diagram make visible for Code Review?
- What failure should be prevented first when Code Review reaches a real system?

## Big Picture

![software engineering 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/04/04-01-concept-at-a-glance.en.png)

*software engineering 101 chapter 4 flow overview*

This picture places Code Review inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Code Review is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- The real purpose of code review
- How to write a Pull Request that is easy to review
- What reviewers actually look at
- Comment tone and decision signals
- What automation can take off the reviewer's plate

## Why It Matters

Code review shapes both code quality and the distribution of knowledge in a team. The moment one person is the only one who understands a module, the organization is one resignation away from a freeze.

> A review is a consensus, not a verdict.

## Concept at a Glance

Automation first, humans focus on judgment.

## Key Terms

- **PR (Pull Request)**: The unit of change and the discussion space.
- **Reviewer**: A peer who shares responsibility for the code.
- **Nit**: A small suggestion, not a blocker.
- **Blocking comment**: Must be resolved before merging.
- **Approve with comments**: Trust-based approval.

## Before/After

**Before — one PR, 800 lines, "small fix included"**

```text
PR title: Refactor user module + bug fix + log cleanup
-> impossible to review, intent is mixed
```

**After — split PRs, each under 200 lines**

```text
1) fix: null user crash
2) refactor: extract notification port
3) chore: prune verbose logs
```

Small PRs merge fast and cause fewer incidents.

## Hands-on: Make a PR Reviewable

### Step 1 — One-line intent

```text
# 1_pr_title.txt
fix(auth): handle expired refresh token without 500
```

The title states the essence of the change.

### Step 2 — Body template

```text
# 2_pr_body.md
## What
Return 401 for expired refresh tokens.

## Why
Today this throws 500 and floods our alerting.

## How
Map ExpiredTokenError to 401 in AuthService.refresh().

## Test
unit + manual cURL.
```

Reviewers enter through What/Why/How/Test fast.

### Step 3 — Lift load with automation

```yaml
# 3_ci.yml
jobs:
  check:
    steps:
      - run: ruff check .
      - run: mypy app
      - run: pytest -q
```

Format, types, and tests are not human work.

### Step 4 — Split into small units

```text
# 4_split.md
- PR 1: data model change
- PR 2: service logic
- PR 3: handlers and routing
```

The smallest mergeable unit is the right unit.

### Step 5 — Comment tone guide

```text
# 5_tone.md
[nit] Naming user_id consistently would be nicer.
[question] Could this branch trigger an N+1 query?
[blocking] A secret key ends up in the log. Must fix before merge.
```

Tags accelerate decision making.

## A two-minute reviewability check

The fastest way to improve code review is not to ask reviewers for more time. It is to make the first two minutes enough for them to understand the intent, the risk, and the verification path.

### Verification steps

1. Read the PR title alone and try to describe the change in one sentence.
2. Check whether the body covers What, Why, How, and Test without opening the diff.
3. Count how many review comments could have been replaced by automation.

**Expected output:**

- A good PR exposes the review order before the reviewer scrolls through the code.
- Missing automation shows up as human comments about formatting and static checks.
- Oversized PRs reveal how quickly structure and risk questions get replaced by surface-level comments.

### Failure modes to watch

- The title says "misc fixes" or bundles unrelated concerns.
- The test path is unclear, so the reviewer must guess how to validate behavior.
- The comment tone evaluates the author instead of the code.

## What to Notice in This Code

- Automation clears the human's field of view.
- A PR body template accelerates decisions.
- Comment tags make the merge bar explicit.
- Split PRs become recoverable decisions.

## Five Common Mistakes

1. **Giant PRs.** Review quality drops to zero.
2. **Humans pointing out formatting.** Move it to automation.
3. **Aggressive comment tone.** Talk about the code, not the person.
4. **Rubber-stamp approvals.** Responsibility is shared.
5. **Merging without tests.** Review is not a substitute for tests.

## How This Shows Up in Production

GitHub-based teams rely on CODEOWNERS for auto-assignment, 1~2 required reviews, protected branches, and a green CI gate. Larger changes go through an RFC step first.

## How a Senior Engineer Thinks

- A PR is a compression of intent.
- Asking humans to do work a machine can do is disrespectful.
- Comments are about code, not people.
- Every approval is shared responsibility.
- The skill of cutting work small is the mark of seniority.

## Checklist

- [ ] Does the PR title state intent in one line?
- [ ] Does the PR body include What/Why/How/Test?
- [ ] Does CI cover format, types, and tests?
- [ ] Is the PR under 200~400 lines of change?
- [ ] Are comments about the code, not the author?

## Practice Problems

1. Pick a recent PR and rewrite it using the template above.
2. Find one CI item still being checked by humans and propose how to automate it.
3. Draft a one-page comment guide with three tags for your team.

## Wrap-up and Next Steps

Code review does defect detection and knowledge distribution at the same time. Next, we move defect detection to where it belongs — testing strategy.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Code Review?**
  - The article treats Code Review as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Code Review?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Code Review reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Software Engineering 101 (1/10): What Is Software Engineering?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): Understanding Requirements](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): Design vs Implementation](./03-design-vs-implementation.md)
- **Code Review (current)**
- Testing Strategy (upcoming)
- Version Control and Release (upcoming)
- Documentation (upcoming)
- Collaboration Process (upcoming)
- Maintenance and Tech Debt (upcoming)
- What Makes Good Software (upcoming)

<!-- toc:end -->

## References

- [Google Engineering Practices — Code Review Developer Guide](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [GitHub Docs — About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Best Kept Secrets of Peer Code Review — Smart Bear](https://smartbear.com/resources/ebooks/best-kept-secrets-of-peer-code-review/)

Tags: Computer Science, SoftwareEngineering, CodeReview, PullRequest, Collaboration, Quality
