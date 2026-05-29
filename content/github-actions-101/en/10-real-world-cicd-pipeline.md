---
series: github-actions-101
episode: 10
title: "GitHub Actions 101 (10/10): A Real-World CI/CD Pipeline"
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
  - Pipeline
  - CICD
  - Capstone
  - ReusableWorkflow
seo_description: A capstone that ties episodes 1-9 into one pipeline split by PR, main, and tag, standardized with reusable workflows for the whole team.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (10/10): A Real-World CI/CD Pipeline

The pieces we covered one by one are all useful, but real systems do not run them in isolation. Triggers, tests, lint, artifacts, Docker, deployment, and secret handling eventually meet in one delivery path, and the quality of that composition determines whether the pipeline scales or collapses under its own weight.

The practical question is not "how many checks can we add?" It is "how clearly can we separate responsibility?" Pull requests need fast feedback. Main needs integration and staging confidence. Tags need traceable release and production promotion. Once those roles are clear, the YAML gets simpler instead of larger.

This is the final post in the GitHub Actions 101 series. In this post, we will combine the earlier topics into a reusable CI/CD shape that separates PR, `main`, and tag responsibilities without losing traceability.


![github actions 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/10/10-01-concept-at-a-glance.en.png)
*github actions 101 chapter 10 flow overview*

## Questions to Keep in Mind

- Why should PR, main, and tag be separated into different responsibilities?
- What duplication do reusable workflows eliminate?
- How far should a composite action bundle?

## Why It Matters

Even if you have test automation, lint, Docker builds, deployment automation, and secret management individually, poor composition means team velocity does not rise as expected. If every PR runs overly heavy validation slowing feedback, if main pushes trigger production-level deployment, if similar-but-different YAML is scattered across repositories — maintenance cost keeps climbing.

I see the purpose of a real-world CI/CD pipeline as "reusing a well-designed structure across many repositories for a long time." Rather than stacking many components, clearly separating responsibilities and making common parts reusable produces far greater effect.

## Key Terms

| Term | Meaning | Practical Point |
| --- | --- | --- |
| Reusable workflow | A shared workflow invoked via `workflow_call` | Significantly reduces cross-repo duplication |
| Composite action | Multiple steps wrapped as one reusable unit | Good for organizing repetitive setup work |
| Template repo | A repository teams use as a starting point | Convenient for distributing standard CI/CD skeletons |
| DORA metrics | Four key delivery performance metrics | Directly connected to pipeline design quality |
| Promotion | Moving from staging to production | The sense of moving the same artifact to the next environment matters |

## Before/After

When each repository has similar-but-slightly-different workflows, the cost of propagating improvements from one place to others is high. One repo has different lint rules, another is missing Docker build cache, another lacks a production deploy gate. This state creates drift over time.

When you create a shared reusable workflow and each repository keeps only a thin caller, the structure simplifies. Common rules are managed in one place, and only per-repository differences remain as input values. The reason platform teams favor this pattern is clear.

## A Real Pipeline in 5 Steps

### Step 1 — Define a reusable workflow

```yaml
# .github/workflows/_ci.yml in org/template-repo
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.12"
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ inputs.python-version }}
      - run: pip install -e ".[dev]"
      - run: ruff check . && mypy . && pytest -q
```

If common rules keep repeating, calling is better than copying. Reusable workflows are the most direct tool for this duplication removal.

### Step 2 — PR stage focuses on fast feedback

```yaml
# .github/workflows/pr.yml
on:
  pull_request:
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
    with:
      python-version: "3.12"
```

In PRs, fast-feedback validation like lint, test, and typecheck is the core. Attaching deployment here makes the review rhythm heavy.

### Step 3 — Main stage flows into integration and staging

```yaml
on:
  push:
    branches: [main]
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
  docker:
    needs: ci
    uses: org/template-repo/.github/workflows/_docker.yml@v1
  deploy-staging:
    needs: docker
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/staging/
```

Main push is based on already-merged code, so build, Docker image creation, and staging deploy can naturally follow from here.

### Step 4 — Tag stage ties to official release and production

```yaml
on:
  push:
    tags: ["v*"]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: softprops/action-gh-release@v2
  deploy-prod:
    needs: release
    environment: production  # required reviewers ON
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/production/
```

Using tags as the basis for production promotion makes tracing which version shipped easy. Production should be connected to a tag or clear version whenever possible.

### Step 5 — Wrap repetitive setup with a composite action

```yaml
# .github/actions/setup-app/action.yml
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v6
      with: { python-version: "3.12" }
    - run: pip install -e ".[dev]"
      shell: bash
```

If reusable workflows are job-level reuse, composite actions are step-level reuse. Distinguishing their roles keeps the structure cleaner.

## What Success Looks Like at This Point

| Trigger | Expected Run Shape | Merge/Deploy Decision Criteria |
| --- | --- | --- |
| PR | lint, test, typecheck | Fast feedback returns within 5 minutes |
| main push | build, docker, staging | Verified artifact reaches staging unchanged |
| tag push | release, production | Same version promotes to production after approval |

If this table matches your actual execution logs, the pipeline responsibility split is working well. Conversely, if PRs run all the way through pre-production verification, that is a signal to split the structure further.

## When the Pipeline Misbehaves, Narrow It in This Order

1. **PR feedback is too slow**: check whether only necessary checks remain in the reusable workflow and whether the matrix is excessive.
2. **Main is unstable**: verify that build output and Docker image tag are delivered identically to staging.
3. **Production is risky**: confirm tag-based promotion, required reviewers, and rollback workflow are actually live — not just documented.

## Branch Protection and Promotion Policy Are Half the Design

In practice, the YAML itself is only half the story. Branch protection rules should require status checks before merge. Main should not accept casual direct pushes. Production environments should keep reviewers and environment-scoped secrets separate from staging. If those repository-level policies are missing, even a clean YAML design will drift into unsafe operations.

---

## Full Pipeline Architecture

The complete pipeline structure applying everything covered so far to one project:

```text
.github/workflows/
├── ci.yml              # PR checks (lint + typecheck + test)
├── build.yml           # main push: build + Docker + artifact
├── deploy-staging.yml  # main push → staging auto-deploy
├── deploy-prod.yml     # tag push → production approval deploy
├── nightly.yml         # nightly full matrix + security scan
└── reusable/
    ├── test.yml        # reusable test workflow
    └── docker.yml      # reusable Docker build
```

Each file's responsibility should be describable in one sentence. Putting multiple responsibilities in one file makes "when should I modify this file?" hard to answer.

### PR Validation Workflow (ci.yml)

```yaml
name: ci
on:
  pull_request:
    paths: ["src/**", "tests/**", "pyproject.toml", "Dockerfile"]

concurrency:
  group: ci-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  lint:
    uses: ./.github/workflows/reusable/test.yml
    with:
      command: "ruff check --output-format github && ruff format --check"

  typecheck:
    uses: ./.github/workflows/reusable/test.yml
    with:
      command: "mypy src"

  test:
    uses: ./.github/workflows/reusable/test.yml
    with:
      command: "pytest -q -n auto --cov=src"
      python-versions: '["3.11", "3.12"]'

  docker-check:
    uses: ./.github/workflows/reusable/docker.yml
    with:
      push: false
```

All checks run in parallel, so the slowest job determines overall time.

### Build + Deploy Workflow (build.yml + deploy-staging.yml)

```yaml
# build.yml
name: build
on:
  push:
    branches: [main]
    paths: ["src/**", "Dockerfile", "pyproject.toml"]

jobs:
  build:
    uses: ./.github/workflows/reusable/docker.yml
    with:
      push: true
      tags: |
        ghcr.io/${{ github.repository }}:main
        ghcr.io/${{ github.repository }}:${{ github.sha }}
    permissions:
      packages: write

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}
      - run: ./scripts/deploy.sh staging ${{ github.sha }}
```

---

## Reusable Workflow Design Patterns

Reusable workflows are a tool for turning "organization standards" into code.

```yaml
# .github/workflows/reusable/test.yml
name: reusable-test
on:
  workflow_call:
    inputs:
      command:
        required: true
        type: string
      python-versions:
        required: false
        type: string
        default: '["3.12"]'
      working-directory:
        required: false
        type: string
        default: "."

jobs:
  run:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ${{ fromJSON(inputs.python-versions) }}
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: ${{ inputs.command }}
```

The calling side only passes the command to execute. Python installation, cache, and dependency installation are managed in one place, so updates automatically propagate to all callers.

### Reusable Workflow Constraints and Alternatives

| Constraint | Description | Alternative |
| --- | --- | --- |
| No nested calls | Reusable cannot call another reusable | Composite action combinations |
| Secrets need passing | `secrets: inherit` or explicit passing | Use `secrets: inherit` |
| Job-level only | Step-level reuse not possible | Use composite actions |
| Same repo or public only | Private cross-repo not possible | Organization internal visibility |

---

## Composite Action Design

When step-level reuse is needed, use composite actions.

```yaml
# .github/actions/setup-project/action.yml
name: "Setup Project"
description: "Python project common setup"

inputs:
  python-version:
    description: "Python version"
    required: false
    default: "3.12"

runs:
  using: "composite"
  steps:
    - uses: actions/setup-python@v6
      with:
        python-version: ${{ inputs.python-version }}
        cache: "pip"

    - name: Install dependencies
      shell: bash
      run: pip install -e ".[dev]"

    - name: Verify environment
      shell: bash
      run: |
        python --version
        pip --version
```

The calling side completes project setup in one line:

```yaml
steps:
  - uses: actions/checkout@v6
  - uses: ./.github/actions/setup-project
    with:
      python-version: "3.11"
  - run: pytest -q
```

---

## Pipeline Performance Monitoring

When the pipeline slows down, developers start ignoring CI. Here is how to periodically check execution times.

```yaml
name: ci-metrics
on:
  schedule:
    - cron: "0 9 * * 1"  # Every Monday

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - name: Collect recent run times
        run: |
          gh api repos/${{ github.repository }}/actions/runs \
            --jq '.workflow_runs[:20] | .[] | [.name, .updated_at, .run_started_at] | @tsv' \
            > metrics.txt
          
          echo "## CI Performance Report" > report.md
          echo "Last 20 runs:" >> report.md
          cat metrics.txt >> report.md

      - uses: actions/upload-artifact@v7
        with:
          name: ci-metrics
          path: report.md
          retention-days: 90
```

Evaluating the pipeline from a DORA metrics perspective (deploy frequency, change lead time, failure rate, recovery time) clarifies improvement direction.

| DORA Metric | Measurement Target | Goal |
| --- | --- | --- |
| Deploy frequency | main → production deploy count | 1+ per day |
| Change lead time | Commit → production deploy time | Under 1 hour |
| Change failure rate | Rollback/hotfix ratio after deploy | Under 5% |
| Recovery time | Incident → recovery time | Under 1 hour |

---

## Organization-Level Standardization

When multiple repositories use the same CI/CD patterns, consider standardizing at the organization level.

### Template Repository

```text
org/ci-template/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── deploy.yml
│   │   └── reusable/
│   │       └── test.yml
│   └── actions/
│       └── setup-project/
│           └── action.yml
├── pyproject.toml (template)
├── Dockerfile (template)
└── scripts/
    └── deploy.sh
```

When creating a new repository from this template, CI/CD works immediately.

### Centralized Reusable Workflows

```yaml
# Calling the org's shared workflow from another repository
jobs:
  test:
    uses: org/ci-workflows/.github/workflows/python-test.yml@v1
    with:
      python-version: "3.12"
    secrets: inherit
```

Placing reusable workflows in the organization's shared repository lets all repos call them via `@v1` tag. Workflow updates mean bumping the tag, and each repo upgrades when ready.

### Managing Organization Policy as Code

Controlling Actions permissions in GitHub Organization settings prevents security incidents proactively.

```yaml
# org-level .github/workflows/policy-check.yml
name: Policy Compliance
on:
  workflow_run:
    workflows: ["*"]
    types: [completed]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Verify approved actions only
        run: |
          # Approved action list
          ALLOWED="actions/checkout actions/setup-python actions/upload-artifact"
          ALLOWED="$ALLOWED docker/build-push-action aws-actions/configure-aws-credentials"

          # Extract uses: statements from workflow files
          for wf in .github/workflows/*.yml; do
            grep -oP 'uses:\s*\K[^@]+' "$wf" | while read action; do
              if ! echo "$ALLOWED" | grep -q "$action"; then
                echo "::error::Unapproved action: $action in $wf"
                exit 1
              fi
            done
          done

      - name: Check secret naming convention
        run: |
          # Verify secret names follow ENV_SERVICE_KEY pattern
          gh secret list --json name -q '.[].name' | while read name; do
            if ! echo "$name" | grep -qP '^(PROD|STG|DEV)_[A-Z_]+$'; then
              echo "::warning::Non-standard secret name: $name"
            fi
          done
        env:
          GH_TOKEN: ${{ secrets.ORG_ADMIN_TOKEN }}
```

With this policy workflow in place, when a team member adds an unapproved third-party action or uses a non-standard secret name, an immediate warning fires.

### Cost Optimization

GitHub Actions bills per minute beyond the free allocation (public repos: unlimited, private repos: 2,000 min/month). Practical patterns for reducing costs:

| Technique | Savings Effect | How to Apply |
| --- | --- | --- |
| Path filter | Eliminate unnecessary runs | `paths:` + `paths-ignore:` |
| Concurrency cancel | Remove duplicate runs | `concurrency.cancel-in-progress: true` |
| Dependency cache | Reduce install time | `actions/cache` or `setup-*` cache options |
| Self-hosted runner | Avoid per-minute billing | EC2 spot instance + runner registration |
| Matrix optimization | Reduce combinations | `include`/`exclude` for essential combos only |

```yaml
# Cost-optimized workflow header
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
```

With this configuration, CI does not run on documentation-only commits, and rapid consecutive pushes to the same branch cancel previous runs.

## Five Common Mistakes

1. **Running full e2e and pre-deploy validation on every PR.** Feedback now takes 30 minutes.
2. **Deploying straight to production from main.** Skipping canary and staging.
3. **Calling reusable workflows with `@main`.** One day it breaks silently.
4. **Deploying to production without a tag.** No way to trace what shipped.
5. **Composite actions with no input validation.** Bad values pass through quietly.

The third mistake is particularly insidious. Changes in the upstream repository can shake all downstream repositories without any notice.

## Checklist

- [ ] PR, main, and tag stages are separated.
- [ ] Common steps are extracted into reusable workflows.
- [ ] Production has required reviewers.
- [ ] Reusable workflows are called with a pinned version.

## Practice Problems

1. Write a PR-stage workflow that runs only lint, test, and typecheck.
2. Create a reusable workflow and call it from two repos with the same CI.
3. Build a workflow where a tag push triggers production deploy behind an approval gate.

## Wrap-up and Next Steps

A real-world CI/CD pipeline is not about stacking many components — it is about combining small flows with clearly separated responsibilities. Viewing PR, main, and tag as different stages, and bundling common parts with reusable workflows and composite actions, makes the pipeline simpler and organization-wide standardization easier.

If you followed this series to the end, you have the foundation to read and design most real-world GitHub Actions structures. Next steps: broaden your view into runtime and post-deployment with Docker, Kubernetes, and operational automation.

## Answering the Opening Questions

- **Why should PR, main, and tag be separated into different responsibilities?**
  - PR validates "is this code safe," main push "builds verified code and deploys to staging," and tag push means "production release." Each stage needs different permissions, secrets, and execution scope, so separating workflow files clarifies responsibilities and strengthens security.
- **What duplication do reusable workflows eliminate?**
  - Common steps like Python setup, cache configuration, dependency installation, and Docker builds are defined once and called from multiple workflows. Updates propagate from a single source, preventing the drift of "why is this repo's setup different from that repo's." At org level, multiple repos' CI standards can be unified into one shared workflow.
- **How far should a composite action bundle?**
  - If a step combination always runs together and repeats across multiple jobs/workflows, it is a composite action candidate. Project setup (checkout + setup + install), notification sending, and cache restore + build are typical patterns. Bundling too many features makes inputs complex, so "describable in one sentence" is a good sizing criterion.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint and Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): Build Artifacts](./06-build-artifact.md)
- [GitHub Actions 101 (7/10): Docker Build](./07-docker-build.md)
- [GitHub Actions 101 (8/10): Deployment Automation](./08-deploy-automation.md)
- [GitHub Actions 101 (9/10): Secret Management](./09-secret-management.md)
- **A Real-World CI/CD Pipeline (current)**

<!-- toc:end -->

## References

- [Reusing workflows](https://docs.github.com/actions/using-workflows/reusing-workflows)
- [Creating a composite action](https://docs.github.com/actions/creating-actions/creating-a-composite-action)
- [DORA - Accelerate State of DevOps](https://dora.dev/)
- [Creating a template repository](https://docs.github.com/repositories/creating-and-managing-repositories/creating-a-template-repository)

Tags: GitHubActions, Pipeline, CICD, Capstone, ReusableWorkflow
