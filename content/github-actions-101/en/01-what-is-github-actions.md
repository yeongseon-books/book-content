---
series: github-actions-101
episode: 1
title: "GitHub Actions 101 (1/10): What Is GitHub Actions?"
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
  - CICD
  - Automation
  - DevOps
  - Workflow
seo_description: Core concepts of GitHub Actions and your first workflow. The starting line for replacing manual steps with automation.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (1/10): What Is GitHub Actions?

At first glance, GitHub Actions looks like "CI built into GitHub." That is a fair starting point, but it does not explain why some teams move faster with better release discipline while others just accumulate more YAML and still rely on manual steps.

The more useful way to think about GitHub Actions is as an execution platform that lives next to your repository. Once a push, pull request, or tag becomes the trigger for test, lint, build, and deploy, the team stops depending on memory and starts depending on repeatable code.

This is the first post in the GitHub Actions 101 series. In this post, we will frame GitHub Actions as an execution platform for repository events rather than a convenient automation button.


![github actions 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/01/01-01-concept-at-a-glance.en.png)
*Event wakes workflow, job runs steps sequentially on a runner*

> GitHub Actions is not "CI inside GitHub" — it is an execution platform next to the repository that reacts to events. Build, test, labeling, releases, and docs deployment all collapse into the same model. That integration density is the decisive difference from standalone CI services.

## Questions to Keep in Mind

- What exactly is GitHub Actions and where does it fit in CI/CD?
- What hierarchy should you understand for Workflow, Job, and Step?
- What minimal configuration should a first workflow start with?

## What You Will Learn

- The definition and place of *GitHub Actions*
- The relationship between *Workflow / Job / Step*
- How to author your first workflow
- *Why GitHub Actions* (vs. Jenkins/CircleCI)
- Runner mechanics and cost awareness
- Security fundamentals from day one

## Why It Matters

CI/CD determines not just team speed but the trust baseline. Teams that only run tests locally depend on "it passed on my machine." Teams whose repository runs the same verification on every commit share a common standard: "this commit passed the same procedure."

GitHub Actions is strong because you can create that standard without operating a separate server. The moment you add a `.github/workflows/*.yml` file, automation becomes part of the code. No server to babysit, and the execution history lives right next to PRs and commits.

## The Execution Flow at a Glance

The intuition to grab first is simple: an event wakes a workflow, jobs run inside the workflow, and steps execute sequentially within each job. When you later ask "where do I fix this?", you trace this hierarchy every time.

## Key Terms

| Term | Meaning | Why It Matters Operationally |
| --- | --- | --- |
| Workflow | An automation unit in `.github/workflows/*.yml` | Defines the entry point and scope of automation |
| Event | What starts a workflow (push, PR, schedule, etc.) | Determines when execution happens |
| Job | A unit of execution within a workflow | Runs in parallel by default — drives speed and structure |
| Step | A single command or Action call inside a Job | Where install, test, and build actually happen |
| Runner | The machine that runs a Job | Selects execution environment (ubuntu-latest, etc.) |
| Action | A reusable Step (e.g., `actions/checkout`) | Standardizes repeated operations |

The most common confusion for newcomers is treating Workflow and Job as the same thing. A Workflow is the outer container; Jobs are work units running inside it. Get this distinction early and parallelism and dependency settings later will make immediate sense.

## Before and After

Without automation, every PR requires a developer to run tests locally, share results verbally, and someone to judge deploy-readiness manually. This structure barely survives in small repos but collapses as teams grow — one person runs tests, another skips them, another uses a stale virtualenv.

With automation, opening a PR triggers the repository to run tests in an identical environment and the result persists as a check. The procedure humans used to perform from memory becomes the repository's default behavior. This transition is where GitHub Actions delivers its value.

## Hands-on: Your First Workflow in 5 Steps

### Step 1 — Create the directory

```bash
mkdir -p .github/workflows
```

GitHub Actions only recognizes workflow files in this exact location. Simple as this step looks, it teaches that automation files live within repository conventions.

### Step 2 — Write the workflow file

```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest -q
```

This example is small but shows the complete skeleton: `on:` defines when, `jobs:` defines what, `runs-on:` defines where, and `steps:` defines in what order.

### Step 3 — Trigger via push

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add first workflow"
git push
```

Automation is not a write-and-forget feature. It only comes alive when reflected in the repository and a real event fires. Always push and read the execution log on your first workflow.

### Step 4 — Check results in the Actions tab

```text
Repo > Actions tab
- The workflow run log appears.
- Each step prints its output and time.
```

The key here is not just "did it pass?" but "can I read what ran in what order?" When CI breaks later, you will find the cause in these execution logs nearly every time.

### Step 5 — Use it as a PR check

```text
In branch protection, enable "Require status checks to pass."
A failed test now blocks merge.
```

Only at this step does GitHub Actions become more than an execution tool — it becomes part of team rules. Once a failed test blocks merge, automation becomes a quality gate, not a suggestion.

## What to Notice in This Code

- A single YAML file defines the entire automation.
- `actions/checkout` is the first step in almost every workflow.
- `runs-on` selects the execution environment and connects to speed, compatibility, and cost.

Forgetting `checkout` is extremely common. The runner has no repository code by default, so without fetching it first, every subsequent install or test step fails.

## Where GitHub Actions Sits in the CI/CD Ecosystem

When first encountering GitHub Actions, the natural comparison is Jenkins, GitLab CI, and CircleCI. Key differences:

| Criterion | Jenkins | GitLab CI | GitHub Actions |
| --- | --- | --- | --- |
| Execution infra | Self-managed servers | GitLab Runner install | GitHub-hosted runners by default |
| Config location | Jenkins UI + Jenkinsfile | `.gitlab-ci.yml` | `.github/workflows/*.yml` |
| Marketplace | Plugin-centric | Limited | 20,000+ public Actions |
| Repo integration | External connection | Built into GitLab | Built into GitHub |
| Billing unit | Server cost | Per-minute (SaaS) | Per-minute (public repos free) |

The core difference is integration density. GitHub Actions connects PR checks, issue automation, package publishing, releases, and dependency updates on a single platform. You trade fewer external integrations for tighter coupling to the GitHub ecosystem.

This understanding makes "when does GitHub Actions fit, and when doesn't it?" easier to answer. If you require mandatory self-hosting, multi-VCS support, or extremely complex shared build caches, other tools may still be stronger. But for most teams already on GitHub, Actions has the lowest entry cost.

## Understanding Runner Mechanics for Cost Awareness

GitHub-hosted runners allocate a clean virtual machine when a job starts; the VM disappears when the job ends. This architecture is strong for isolation and reproducibility but demands operational awareness.

First, runners have no persistent state. Packages installed, files created, and caches from previous runs do not survive by default. Dependency install time recurs every run, so you must consciously configure `actions/cache` or `setup-python`'s cache option.

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.11"
    cache: "pip"
```

Second, runner selection directly affects cost. `ubuntu-latest` is typically fastest and cheapest; `macos-latest` costs 10x per minute. Think twice before adding macOS to a matrix unless you genuinely need it.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest]
    # macos-latest only when targeting iOS/macOS
```

Third, self-hosted runners exist as an option. When security policies are strict, GPU is required, or builds are extremely heavy, you can register your own machines as runners. But runner maintenance burden comes with it.

## A More Realistic Workflow Structure

Having seen the minimal example, here is a structure closer to what production codebases use:

```yaml
name: ci

on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: pytest -q --junitxml=report.xml

      - name: Upload test report
        uses: actions/upload-artifact@v7
        if: always()
        with:
          name: test-report-${{ matrix.python-version }}
          path: report.xml
          retention-days: 7
```

Each addition solves a real problem:

**`paths` filter**: When only docs or config changed, skip tests entirely. Saves runner cost and wait time.

**`concurrency`**: When consecutive pushes hit the same PR, cancel the earlier run. Prevents stale executions piling up in the queue.

**`matrix`**: Test on Python 3.11 and 3.12 simultaneously. Parallel execution means total time barely increases while compatibility coverage doubles.

**Artifact upload**: Persisting test results as XML makes failure investigation far easier later. Without `if: always()`, the report never uploads on failed runs — exactly when you need it most.

## Action Versioning and Pinning

When you call `uses: actions/checkout@v6`, the `@v6` is a version pin. Why this matters becomes obvious quickly in production.

```yaml
# Recommended: major version pin
- uses: actions/setup-python@v6

# Safer: commit SHA pin
- uses: actions/setup-python@8d9ed867ee42ba1c3be538356b8e3e90c3aef03a  # v6.0.0

# Risky: branch reference
- uses: actions/setup-python@main
```

Major version pins (`@v6`) automatically follow backward-compatible updates and suit most cases. For security-sensitive environments, pin to a commit SHA and let Dependabot submit update PRs — the most stable combination.

Action source is ultimately a GitHub repository. Visit `actions/checkout` and you will find `action.yml` — a metadata file defining inputs, outputs, and execution method. When you later write your own Actions, you follow the same structure.

## Reading Execution Logs

The first skill after writing a workflow is reading execution logs. In the Actions tab, each run shows job-level and step-level collapsible logs.

```text
Run pytest -q --junitxml=report.xml
...
FAILED tests/test_auth.py::test_login_expired_token
  assert response.status_code == 401
  AssertionError: assert 500 == 401
...
1 failed, 42 passed in 3.21s
Error: Process completed with exit code 1.
```

The reading order is clear:

1. Which step failed — find the red indicator among collapsed step names.
2. Which command failed — check what follows `Run`.
3. What is the exit code — `exit code 1` means general failure; `exit code 137` often means out-of-memory.

Execution time also carries information. If dependency install exceeds 2 minutes, check your cache. If tests exceed 5 minutes, consider parallelization or test splitting. This intuition only builds by reading logs regularly.

## Basic Workflow Debugging Techniques

When a workflow does not behave as expected, these techniques help:

```yaml
# Print context values to verify
- name: Debug context output
  run: |
    echo "event_name: ${{ github.event_name }}"
    echo "ref: ${{ github.ref }}"
    echo "sha: ${{ github.sha }}"
    echo "actor: ${{ github.actor }}"
```

The `github` context holds event type, branch, commit SHA, and actor info. When `if:` conditions behave unexpectedly, printing these values first is usually the fastest path.

```yaml
# Check runner environment
- name: Runner info
  run: |
    uname -a
    python --version
    pip --version
    df -h
    free -m
```

Checking OS version, disk space, and memory on the runner often answers "why does it work locally but not on CI?"

Another useful tool is `act` — a local runner simulator based on Docker. It lets you test YAML syntax and basic flow before pushing. However, GitHub context and secrets are not fully replicated, so treat it as a supplement rather than a replacement.

## Cost and Limits to Know Upfront

GitHub Actions is free for public repositories; private repos get plan-dependent free minutes. Key limits:

| Item | Limit |
| --- | --- |
| Job execution time | Max 6 hours per job |
| Concurrent jobs (Free) | 20 |
| Concurrent jobs (Team/Enterprise) | 60–180 |
| Artifact retention | Default 90 days, configurable |
| Log retention | 400 days |

The most reliable way to reduce cost is reducing unnecessary runs: `paths` filters, `concurrency`, and limiting matrix scope. For monitoring, check Settings > Billing for Actions usage periodically.

## Security Fundamentals From Day One

Workflows can access repository code, so misconfiguration can lead to secret exposure or privilege abuse. Principles to internalize from the start:

First, follow least-privilege for workflow permissions. GitHub grants broad default `GITHUB_TOKEN` permissions, but lowering the repository default to `read` and explicitly raising permissions per-job is safer.

```yaml
permissions:
  contents: read
  pull-requests: write

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v5
```

Second, treat PRs from forks with extra caution. By default, secrets are not injected and `GITHUB_TOKEN` permissions are restricted for external contributors' PRs. This is an intentional safeguard — circumventing it requires careful judgment.

Third, verify the source of third-party Actions. Actions outside the `actions/` official namespace should be code-reviewed or at minimum pinned by commit SHA to prevent unexpected changes.

```yaml
# Pin third-party actions by SHA
- uses: slackapi/slack-github-action@485a9d42d3a73031f12ec201c457e2162c45d02d  # v2.0.0
```

Fourth, use `pull_request_target` with extreme caution. This event runs the base branch's workflow while accessing the PR's code, which can let malicious PRs steal secrets if misused. Prefer `pull_request` unless you have a specific reason.

Finally, workflow file changes themselves should be reviewed. Register `.github/workflows/` in CODEOWNERS so workflow modifications always require designated reviewer approval — preventing accidental permission escalation at the team level.

## Five Common Mistakes

1. **Wrong workflow location.** It must be exactly `.github/workflows/`.
2. **Missing `on:`.** A workflow with no trigger never runs.
3. **Skipping `actions/checkout`.** Without code, every later step fails.
4. **Running heavy steps on every PR.** Wastes time and money.
5. **Hardcoding secrets in YAML.** Use `${{ secrets.* }}` only.

At the beginner stage, it is tempting to cram everything into one file because "it's a small project." But once you start treating test automation and deploy automation with equal weight in the same file, splitting them later becomes painful.

## How a Senior Engineer Thinks

- No CI, no new feature.
- YAML is code — review it.
- Run time equals cost plus feedback latency.
- Secrets never mix with code.
- Workflows are decomposed, just like services.

Mature teams split test, lint, typecheck, build, and deploy into different responsibilities. They review workflow files exactly like application code. YAML ultimately changes operational behavior — it deserves the same rigor.

## Checklist

- [ ] A `.github/workflows/` directory exists.
- [ ] Triggers fire on both push and PR.
- [ ] Results appear as PR checks.
- [ ] Secrets use only `secrets.*`.
- [ ] Cache is configured to reduce dependency install time.
- [ ] `concurrency` limits duplicate runs.

## Practice Problems

1. Create a workflow that prints only Hello World.
2. Add a matrix that runs on both Ubuntu and macOS.
3. Intentionally break a test and observe how the PR check fails.
4. Add `concurrency` and verify that consecutive pushes cancel the earlier run.

## Wrap-up and Next Steps

GitHub Actions is an automation executor living next to your code. It wakes on repository events, and the jobs and steps inside perform verification and deployment procedures. Understanding this structure once means every subsequent topic reduces to more sophisticated workflow design.

The next post dives deeper into the internal structure of workflows — how to split jobs, what to parallelize, and where to enforce ordering.

## Answering the Opening Questions

- **What exactly is GitHub Actions and where does it fit in CI/CD?**
  - GitHub Actions is a platform that runs workflows in response to repository events. Unlike Jenkins, there's no separate server to maintain — YAML files in `.github/workflows/` become your CI/CD pipeline. The core differentiator is integration density with the GitHub ecosystem, connecting PR checks, releases, and package deployments on a single platform.
- **What hierarchy should you understand for Workflow, Job, and Step?**
  - A Workflow is the outer frame of automation, a Job is the unit of parallel execution, and a Step is a command executed sequentially within a Job. Following these three layers narrows down "where did it fail." Jobs can be sequenced with `needs`, and Steps can be controlled with `if` conditions.
- **What minimal configuration should a first workflow start with?**
  - Open triggers with `on: [push, pull_request]`, use a single job with three steps: checkout, setup, test. Then add `cache`, `paths` filters, and `concurrency` one by one to naturally evolve toward production quality. Starting small and growing incrementally is more learning-efficient than building the perfect pipeline from scratch.
<!-- toc:begin -->
## In this series

- **What Is GitHub Actions? (current)**
- Workflows and Jobs (upcoming)
- Understanding Triggers (upcoming)
- Python Test Automation (upcoming)
- Lint and Type Check (upcoming)
- Build Artifacts (upcoming)
- Docker Build (upcoming)
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Workflow syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Awesome Actions](https://github.com/sdras/awesome-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)

Tags: GitHubActions, CICD, Automation, DevOps, Workflow
