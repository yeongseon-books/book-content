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

> Trigger design is not about choosing when to run — it is about choosing when NOT to run. The combination of push/pull_request/schedule/workflow_dispatch with paths and concurrency filters is what separates "always-running noise" from "fires only when it matters."

## Questions to Keep in Mind

- What boundary separates the responsibilities of push versus pull_request?
- Why must schedule be understood in UTC rather than local time?
- When is workflow_dispatch useful and what should be documented about it?

## Why It Matters

Trigger design dictates both execution timing and team cost policy. If every commit fires the full test suite, the full build, and the full deployment validation simultaneously, it feels reassuring at first but quickly leads to exploding runner usage and growing queue times. Developers start merging without waiting for checks because the wait is too long.

The opposite approach works better: PR triggers run fast checks only, main push triggers run the heavier build and deployment stages, and nightly cron handles the slow e2e suite. Same repository, far healthier operations. Triggers are not syntax — they are execution policy.

## Key Terms

| Term | Meaning | Practical Point |
| --- | --- | --- |
| `push` | Fires when commits land on a branch | Commonly used for post-merge verification on main |
| `pull_request` | Fires when a PR is opened or updated | Suited for pre-review fast feedback |
| `schedule` | Cron-based periodic execution | UTC-only — time conversion matters |
| `workflow_dispatch` | Manual run button | Useful for deploy, rollback, and operational tasks |
| `paths` / `branches` | Filter by file path or branch name | Simplest way to eliminate unnecessary runs |
| `concurrency` | Controls simultaneous execution | Reduces duplicate runs and queue waste |

When designing triggers, think "when should this NOT run?" before "when should it run?" Cost savings almost always start there.

## Before/After

A repository where docs-only edits still trigger the full build and test suite is common. Maintainers think "it's safe anyway," but developers face long wait times on every change. Notifications pile up, and real failures get buried.

With a `paths` filter limiting triggers to `src/**`, `tests/**`, and `pyproject.toml`, docs edits and code changes carry different cost structures. Trigger design alone can make the same workflow far more practical.

## Hands-on: Triggers in 5 Steps

### Step 1 — Separate push and PR

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

PR and main push serve different roles even when they run the same checks. PR is for surfacing risk fast before merge; main push is for validating what actually landed on the reference branch.

### Step 2 — Cut cost with paths filters

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

`paths` is often more readable than `paths-ignore` because it makes explicit what file changes cause execution.

### Step 3 — Schedule (cron) for nightlies

```yaml
on:
  schedule:
    - cron: "0 17 * * 0-4"  # UTC 17:00 = KST 02:00, Sun-Thu
```

The key point: cron is always UTC. If you want 2 AM Korean time, you must convert to UTC — do not enter `2` directly.

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

Manual triggers are not simply "add a button." They expose in code what values an operator can provide and what environments are allowed.

### Step 5 — concurrency to prevent duplicates

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

When multiple pushes hit the same PR in quick succession, earlier runs are often meaningless. `cancel-in-progress: true` eliminates that waste.

## What to Notice in This Code

- `paths` makes clear what triggers execution rather than what skips it.
- cron is UTC — mistaking it for local time is the most common schedule bug.
- `cancel-in-progress` has the most impact on teams with frequent PR pushes.

I often use the phrase "the right moment" when talking about triggers. Reducing unnecessary execution matters as much as enabling fast execution.

## Five Common Mistakes

1. Running the same heavy workflow on every trigger type.
2. Writing `schedule` in local time instead of UTC.
3. Using `pull_request_target` casually, creating secret exposure risk.
4. Omitting `concurrency`, letting duplicate builds fill the queue.
5. Creating `workflow_dispatch` without documenting who runs it, when, and how.

The third one is a direct security concern — choosing `pull_request_target` just because "we need secrets on PRs" is dangerous without careful isolation.

## How This Shows Up in Production

Mature teams split triggers by role: PR = quick checks, main push = full test + build, nightly cron = slow e2e, workflow_dispatch = production deploy and rollback. The number of workflow files grows, but the system becomes easier to read because each file has one clear purpose.

Time-zone awareness also matters. For global teams or multi-region work, thinking in UTC from the start avoids the fragile mental-conversion approach that breaks when people change locations.

## Checklist

- [ ] Path filters eliminate unnecessary runs.
- [ ] Cron is written in UTC.
- [ ] `concurrency` is configured.
- [ ] `workflow_dispatch` inputs and usage are documented.

## Practice Problems

1. Skip the workflow when only `docs/` files change.
2. Write a cron expression that fires daily at 03:00 KST.
3. Add an environment selection input to `workflow_dispatch`.

## Trigger Combination Strategies

In practice, a single workflow often combines multiple triggers. Here is how common combinations map to team needs:

| Scenario | Trigger combination | Rationale |
| --- | --- | --- |
| PR validation | `pull_request` + `paths` | Validate only changed code, cut cost |
| main deploy | `push: branches: [main]` | Only merged code enters deployment |
| Nightly full test | `schedule` | Run broad matrix at low-cost hours |
| Manual rollback/deploy | `workflow_dispatch` | Human judgment controls execution |
| Release publishing | `push: tags: ['v*']` | Tag-based version management |
| Post-workflow chain | `workflow_run` | Start deployment after build succeeds |

### Duplicate execution when push and pull_request overlap

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

When you merge a PR, a `push` event also fires. This means the workflow can run twice at merge time. The general fix is to use PR only for validation and reserve push for main-specific work (deploy, release):

```yaml
# Validation (PR only)
on:
  pull_request:

# Deployment (main push only)
on:
  push:
    branches: [main]
```

Separating into two files eliminates the duplicate without conditional logic.

---

## Paths Filter in Practice

Paths filters are the core cost-reduction tool. If a docs edit triggers the full build, both time and money are wasted.

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
      - "requirements*.txt"
    paths-ignore:
      - "docs/**"
      - "*.md"
      - ".github/ISSUE_TEMPLATE/**"
```

`paths` and `paths-ignore` cannot be used together — pick one. When the set of included paths is clear, use `paths`; when only a few things should be excluded, use `paths-ignore`.

A common mistake with paths filters is forgetting dependency files. If `requirements.txt` changes, test results may differ, so dependency declaration files must be included alongside source code.

### Change-Detection Based Conditional Execution

Paths filters skip the entire workflow, but for finer job-level control, use an action like `dorny/paths-filter`:

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v6
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'src/api/**'
              - 'requirements*.txt'
            frontend:
              - 'src/web/**'
              - 'package.json'

  test-backend:
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest tests/api -q

  test-frontend:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm test
```

This pattern is especially useful in monorepos. If only backend code changed, the frontend test is skipped, and vice versa.

---

## Schedule Trigger Deep Dive

Cron expressions are UTC-only. Korean Standard Time (KST) is UTC+9, so running at 2 AM KST requires setting UTC 17:00 (the previous day).

```yaml
on:
  schedule:
    # KST 02:00 = UTC 17:00 (previous day)
    - cron: "0 17 * * *"
    # Weekdays only (exclude weekends)
    - cron: "0 17 * * 1-5"
```

Key points about schedule triggers:

1. **Exact timing is not guaranteed.** GitHub may delay execution by up to tens of minutes under load. If minute-level accuracy matters, have an external scheduler call `workflow_dispatch` instead.
2. **Runs only on the default branch.** Feature branch schedules are ignored.
3. **Disables after 60 days of no commits.** This is why scheduled workflows stop on dormant repos.
4. **Multiple cron expressions in an array.** You can run nightly tests and weekly dependency scans from the same workflow.

### Schedule usage patterns

```yaml
on:
  schedule:
    - cron: "0 17 * * 1-5"  # Weekdays KST 02:00 - full matrix test
    - cron: "0 9 * * 1"     # Monday KST 18:00 - dependency vulnerability scan

jobs:
  nightly-test:
    if: github.event.schedule == '0 17 * * 1-5'
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest -q

  security-scan:
    if: github.event.schedule == '0 9 * * 1'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pip-audit
```

`github.event.schedule` distinguishes which cron expression triggered the run, allowing different jobs for different schedules.

---

## workflow_dispatch Design Guide

Manual triggers serve "moments that need human judgment" — rollback, emergency deploy, environment reset — not "tasks that can't be automated."

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Deploy target environment"
        required: true
        type: choice
        options:
          - staging
          - production
      version:
        description: "Version tag to deploy (e.g., v1.2.3)"
        required: true
        type: string
      dry-run:
        description: "Verify only without actual deployment"
        required: false
        type: boolean
        default: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ inputs.version }}
      - name: Validate
        run: ./scripts/validate.sh ${{ inputs.environment }}
      - name: Deploy
        if: inputs.dry-run == false
        run: ./scripts/deploy.sh ${{ inputs.environment }} ${{ inputs.version }}
```

Design principles for inputs:

- **Use `choice` type to constrain options.** Free-text invites mistakes; prefer a fixed set of allowed values.
- **Default `dry-run` to true.** This prevents accidental production deployments.
- **Include examples in `description`.** The description appears directly in the UI, eliminating the need to look up docs.

---

## Concurrency Patterns

Earlier we touched on `concurrency` briefly, but it deserves deeper treatment since it interacts directly with trigger design.

```yaml
# Pattern 1: Serialize per PR
concurrency:
  group: pr-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

# Pattern 2: Serialize per environment (for deploys)
concurrency:
  group: deploy-${{ inputs.environment || 'staging' }}
  cancel-in-progress: false
```

The choice of `cancel-in-progress` follows a clear rule:

- **Validation workflows**: `true` — a new push makes the old result meaningless.
- **Deployment workflows**: `false` — canceling mid-deploy can leave things in an inconsistent state.

Group key design matters too. Including the PR number means different PRs run independently while only serializing within the same PR. Using `github.ref` alone serializes everything on the same branch.

---

## Security Considerations for Triggers

Trigger selection is directly tied to security, especially when handling PRs from forks.

| Event | Secret access | Risk level | Usage guidance |
| --- | --- | --- | --- |
| `pull_request` | Blocked (forks) | Low | Safe for basic validation |
| `pull_request_target` | Available | High | Never execute untrusted code |
| `push` | Available | Medium | Use with protected branches only |
| `workflow_dispatch` | Available | Low | Only authorized users can trigger |

`pull_request_target` runs the base branch workflow while granting secret access, creating a vector for forks to exfiltrate secrets via malicious code. Use it only for non-code-executing tasks (labeling, commenting), and never checkout or run PR code within it.

---

## Trigger Debugging Checklist

When a workflow does not trigger as expected, check these in order:

1. **Is the workflow file on the default branch?** `schedule` and `workflow_dispatch` only recognize workflows on the default branch. New workflows on feature branches only respond to `pull_request`.

2. **Is the YAML syntax correct?** Incorrect indentation under `on:` silently disables the entire workflow. Check the "Workflow file" tab in GitHub UI for parse errors.

3. **Are paths filters matching correctly?** When paths filters exist and changed files don't match, the workflow shows as "skipped." This is normal behavior, but watch out if using "Require status checks" in branch protection — you need to handle the skipped state.

4. **Did you verify the event payload?** The `github.event` structure differs per event type. If conditionals behave unexpectedly, print the payload:

```yaml
- name: Print full event payload
  run: echo '${{ toJSON(github.event) }}' | jq .
```

5. **Did you check activity types?** `pull_request` fires only on `opened`, `synchronize`, and `reopened` by default. For label additions or review requests, you must specify `types:` explicitly:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, review_requested]
```

---

## Practical Trigger Recipes

### Recipe 1: PR validation + main deploy separation

```yaml
# .github/workflows/ci.yml
on:
  pull_request:
    paths: ["src/**", "tests/**", "pyproject.toml"]

# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
    paths: ["src/**"]
```

### Recipe 2: Tag-based release

```yaml
on:
  push:
    tags: ["v[0-9]+.[0-9]+.[0-9]+"]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
      - uses: softprops/action-gh-release@v2
        with:
          files: dist/*
          generate_release_notes: true
```

### Recipe 3: Dependabot auto-merge

```yaml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  auto-merge-dependabot:
    if: github.actor == 'dependabot[bot]'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v6
      - run: pytest -q
      - uses: fastify/github-action-merge-dependabot@v3
        with:
          target: minor
```

These recipes are ready-to-use starting points. Adapt the paths filters and conditionals to your team's situation.

## Wrap-Up

Triggers control when your workflow runs, but in practice they design cost and trust simultaneously. Knowing when to run matters less than knowing when not to run. Both decisions must be explicit for automation to stay useful.

The next post covers Python test automation. Now that you understand how to wake workflows at the right moment, it is time to decide what tests run inside them and how.

---

## Answering the Opening Questions

- **What boundary separates the responsibilities of push versus pull_request?**
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
- [book-examples example code](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Trigger, Event, Schedule, CICD
