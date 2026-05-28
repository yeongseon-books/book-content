---
series: github-actions-101
episode: 3
title: "GitHub Actions 101 (3/10): Understanding Triggers"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - GitHubActions
  - Trigger
  - Event
  - Schedule
  - CICD
seo_description: From push and PR to schedule and workflow_dispatch. Take precise control of when your workflows run.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (3/10): Understanding Triggers

As automation grows, a new kind of waste appears. Why did a docs-only edit trigger a full build? Why did three quick pushes to the same PR queue three identical runs? Why did the nightly job fire at the wrong local time even though the cron expression looked correct?

Trigger design is where GitHub Actions stops being just syntax and becomes policy. The practical question is not only when a workflow should run, but when it should stay silent so cost, queue time, and alert noise remain under control.

This is the 3rd post in the GitHub Actions 101 series. In this post, we will use `push`, `pull_request`, `schedule`, `workflow_dispatch`, path filters, and `concurrency` to make workflows run at the right moment and only at the right moment.


![github actions 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/03/03-01-concept-at-a-glance.en.png)
*github actions 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Understanding Triggers?
- Which signal should the example or diagram make visible for Understanding Triggers?
- What failure should be prevented first when Understanding Triggers reaches a real system?

## What You Will Learn

- The difference between *push* and *pull_request*
- Scheduling with *schedule (cron)*
- Manual runs with *workflow_dispatch*
- *Cost reduction* with *paths / branches* filters
- Five common pitfalls

## Why It Matters

Trigger design dictates your *cost and noise*. Running *every workflow on every commit* leads to *cost explosion and alert fatigue*.

> A *good workflow* runs *only at the right moment*.

## Key Terms

- **push**: when *commits land* on a branch.
- **pull_request**: when a PR is *opened or updated*.
- **schedule**: a recurring *cron expression*.
- **workflow_dispatch**: a *manual run* button.
- **paths/branches filter**: *limits* triggers by *path/branch*.
- **concurrency**: *serializes* concurrent runs.

## Before/After

**Before**: a docs-only edit triggers *the full build and test*.

**After**: a `paths` filter runs the build only when *code changes*.

## Hands-on: Triggers in 5 Steps

### Step 1 — Separate push and PR

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

### Step 2 — Cut cost with paths filters

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

### Step 3 — Schedule (cron) for nightlies

```yaml
on:
  schedule:
    - cron: "0 17 * * 0-4"  # UTC 17:00 = KST 02:00, Sun-Thu
```

### Step 4 — workflow_dispatch for manual runs

```yaml
on:
  workflow_dispatch:
    inputs:
      env:
        description: "deploy target"
        required: true
        default: staging
        type: choice
        options: [staging, production]
```

### Step 5 — concurrency to prevent duplicates

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

## What to Notice in This Code

- *paths* is more *explicit* than *paths-ignore*.
- *cron* is in *UTC*; convert local times carefully.
- *cancel-in-progress* saves cost on *PR push storms*.

## Five Common Mistakes

1. **Running the *whole workflow* on every trigger.** Cost explodes.
2. **Writing `schedule` in *local time*.** UTC only.
3. **Misusing `pull_request_target`.** Risks *secret exposure*.
4. **Missing `concurrency`.** Duplicate builds clog the queue.
5. **`workflow_dispatch` without docs.** No one knows who clicks it or how.

## How This Shows Up in Production

Mature teams split triggers by *role*: *PR* = quick checks, *main push* = full test + build, *nightly cron* = slow e2e, *workflow_dispatch* = production deploy.

## How a Senior Engineer Thinks

- Trigger design balances *cost and trust*.
- Think in *UTC* for cron.
- Add *concurrency* by default.
- *Validate inputs* even on manual triggers.
- Separate *PR* and *main* workflows.

## Checklist

- [ ] *paths filters* eliminate unnecessary runs.
- [ ] *cron* is written in *UTC*.
- [ ] *concurrency* is configured.
- [ ] *workflow_dispatch* is documented.

## Practice Problems

1. Skip the workflow on *docs/* changes.
2. Write a cron that fires *daily at 03:00 KST*.
3. Add an *environment selection* input to *workflow_dispatch*.

## Wrap-up and Next Steps

Triggers control *when* your workflow runs. Next up: *Python test automation*.

## Answering the Opening Questions

- **What difference dictates how push and pull_request should be used?**
  - `pull_request` is for code validation — runs when PRs open or update, and secrets are blocked from forks for safety. `push` suits post-merge follow-up (deployment, releases). Putting both events in the same workflow can cause duplicate runs at merge time, so separating files or using conditionals is better.
- **Why must schedule be understood in UTC rather than local time?**
  - GitHub Actions cron is fixed to UTC. To run at 2 AM KST, set UTC 17:00. Regions with daylight saving time see time shifts year-round. Since exact timing isn't guaranteed, if minute-level accuracy is needed, calling `workflow_dispatch` from an external scheduler is more stable.
- **When is workflow_dispatch useful and what should be documented?**
  - Useful for emergency deployments, rollbacks, and environment resets requiring human judgment. Document examples and constraints in input `description`, prevent mistakes with `choice` type and `dry-run` defaults, and share with the team that audit logs record who ran what and when.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- **Understanding Triggers (current)**
- Python Test Automation (upcoming)
- Lint and Type Check (upcoming)
- Build Artifacts (upcoming)
- Docker Build (upcoming)
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [Events that trigger workflows](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows)
- [Schedule events](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule)
- [workflow_dispatch](https://docs.github.com/actions/using-workflows/manually-running-a-workflow)
- [Concurrency](https://docs.github.com/actions/using-jobs/using-concurrency)

Tags: GitHubActions, Trigger, Event, Schedule, CICD
