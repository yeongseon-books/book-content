---
series: github-actions-101
episode: 2
title: "GitHub Actions 101 (2/10): Workflows and Jobs"
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
  - Workflow
  - Job
  - Matrix
  - CICD
seo_description: Workflow, Job, and Step structure with dependencies. Master parallelism and ordering in your CI graph.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (2/10): Workflows and Jobs

Once you start using GitHub Actions, the next question is rarely about YAML syntax. It is about structure. Should lint and test live in one job? Should deploy wait for build only, or for every earlier check? When does a single workflow become harder to reason about than several smaller ones?

Those questions are really about pipeline design. A workflow file is only the container. The actual pipeline is the graph of jobs inside it, and the quality of that graph determines both feedback speed and operational safety.

This is the 2nd post in the GitHub Actions 101 series. In this post, we will map the relationship between workflows, jobs, and steps, then use `needs`, `matrix`, and `outputs` to design a graph that is fast without becoming fragile.


![github actions 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/02/02-01-concept-at-a-glance.en.png)
*Job graph showing parallel lint/test with sequential build and deploy*

> Workflow, Job, and Step are not just a YAML hierarchy — they are units of parallelism and dependency. Group things that must finish together as Steps in one Job; split things that can fail independently into separate Jobs. This is how you make both execution time and failure location clear simultaneously.

## Questions to Keep in Mind

- What does each of Workflow, Job, and Step handle?
- Why is `needs` not just a simple option but a pipeline design tool?
- When is `matrix` useful and when does it become a cost bomb?

## What You Will Learn

- The exact relationship between Workflow / Job / Step
- Expressing dependencies with `jobs.<id>.needs`
- Running many environments with `matrix`
- Passing values between jobs with `outputs`
- Job decomposition criteria for real-world pipelines
- Cost control strategies for matrix builds

## Why It Matters

Putting all work in one job looks simpler but slows feedback. Splitting without criteria scatters dependencies and makes the execution order unreadable. Good CI is "parallel where possible, sequential only where necessary."

In practice, this design directly shapes developer experience. If lint results arrive in 30 seconds, tests in 2 minutes, and deploy only starts after both pass, the team's rhythm changes. The ability to draw a good job graph is what separates competent from excellent GitHub Actions usage.

## Key Terms

| Term | Meaning | Design Point |
| --- | --- | --- |
| Workflow | An automation unit in one YAML file | Defines what event starts what pipeline |
| Job | Execution unit within a workflow | Defaults to parallel — this is critical |
| Step | A command or Action call inside a Job | Runs sequentially within the same Job |
| `needs` | Dependency declaration between Jobs | Creates directed graph, enforces ordering |
| `matrix` | Replicates a Job across variable combinations | Widens coverage but must be cost-controlled |
| `outputs` | Values a Job passes to the next Job | Best kept as simple strings |

The key intuition: Steps run serially within a Job, Jobs run in parallel by default. Therefore "can these run simultaneously?" is a Job boundary question, and "must this run after that?" is a `needs` question.

## Before and After

A pipeline with everything in one job is easy to start. Fewer files, one flow at a glance. But a single lint violation forces you to wait for tests and build to finish, and locating the failure point in logs becomes tedious.

Split lint, test, and build into separate jobs with `needs: [lint, test]` on build, and feedback time changes fundamentally. Failures surface faster, and only successes advance to the next stage. Job decomposition is not YAML decoration — it is feedback time engineering.

## Hands-on: Job Graph in 5 Steps

### Step 1 — Split into jobs

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest -q
```

Start by separating work that can run independently. Lint and test rarely share results, making them ideal parallel candidates.

### Step 2 — Order with needs

```yaml
  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

`needs` reveals "what success does this job assume before starting?" The syntax is short, but it functions as the pipeline's safety gate.

### Step 3 — Multiple environments via matrix

```yaml
  test:
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12"]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest -q
```

Matrix replicates the same job across environments. But the moment you multiply three Python versions by two OSes, you get six runs — cost and wait time grow proportionally.

### Step 4 — Pass values via outputs

```yaml
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.v.outputs.version }}
    steps:
      - id: v
        run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy ${{ needs.build.outputs.version }}"
```

Keep inter-job data transfer small and infrequent. One or two strings are clean; forcing complex objects through outputs makes the pipeline messy fast.

### Step 5 — Failure policy: continue-on-error

```yaml
  flaky:
    continue-on-error: true
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/flaky.py
```

This is not a tool for ignoring failures — it is a policy for deciding which failures are warning-level. Use sparingly, and document the reason when you do.

## What to Notice in This Code

- `needs` creates a directed acyclic graph between jobs.
- `matrix` is powerful but combinatorial explosion lurks behind every extra dimension.
- `outputs` works best for simple string values.

Job design asks "what constitutes an independently runnable unit?" not "how many pieces can I split into?" When this criterion wavers, YAML grows long while readability drops.

## Job Decomposition Criteria

"How should I split jobs?" does not have an intuitive answer. Four criteria prove useful in practice:

**Criterion 1 — Failure isolation**: Lint failures and test failures have different causes. In one job, you hunt through logs; in separate jobs, the failed job name alone narrows the cause.

**Criterion 2 — Execution environment**: Lint only needs Python, but build may need Docker. Different environments naturally suggest separate jobs.

**Criterion 3 — Parallelization potential**: Tasks that share no results can run in parallel. Splitting into jobs lets GitHub Actions parallelize automatically, reducing total time.

**Criterion 4 — Re-run scope**: Jobs can be re-run individually. If tests passed but deploy failed, you can re-run deploy alone. With everything in one job, you start over from the beginning.

| Criterion | Keep in One Job | Split Recommended |
| --- | --- | --- |
| Failure cause | Same type | Different types |
| Execution environment | Identical | Different |
| Parallelism | Order-dependent | Independent |
| Re-run | Always re-run together OK | Partial re-run needed |

## Practical `needs` Graph Patterns

A simple serial chain (`A → B → C`) is easy to understand, but production demands more complex patterns.

### Fan-out / Fan-in

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest tests/unit -q

  test-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest tests/integration -q

  build:
    needs: [lint, test-unit, test-integration]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

Three verification jobs run in parallel (fan-out), and build starts only when all succeed (fan-in). Total time is bound by the longest individual job, so you only need to optimize individual job times.

### Conditional Job Pattern

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest -q

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh staging

  deploy-production:
    needs: deploy-staging
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh production
```

`if:` conditions create branches in the job graph. PRs run tests only, main pushes reach staging, and tag pushes reach production. One workflow file handles multiple scenarios.

### Matrix + needs Combination

```yaml
jobs:
  test:
    strategy:
      matrix:
        python: ["3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest -q

  publish:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
      - run: twine upload dist/*
```

`needs: test` means all matrix combinations must succeed before the next job starts. If any of the 4 combinations fails, publish never runs. This lets you use the matrix as a safety gate.

## Deep Dive: `outputs` Between Jobs

Common patterns and pitfalls when passing values between jobs:

```yaml
jobs:
  version:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.get-tag.outputs.tag }}
      should-deploy: ${{ steps.check.outputs.deploy }}
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - id: get-tag
        run: |
          TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
          echo "tag=${TAG}" >> "$GITHUB_OUTPUT"

      - id: check
        run: |
          if [[ "${{ github.ref }}" == refs/tags/v* ]]; then
            echo "deploy=true" >> "$GITHUB_OUTPUT"
          else
            echo "deploy=false" >> "$GITHUB_OUTPUT"
          fi

  build:
    needs: version
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: |
          echo "Building version: ${{ needs.version.outputs.tag }}"
          docker build -t app:${{ needs.version.outputs.tag }} .

  deploy:
    needs: [version, build]
    if: needs.version.outputs.should-deploy == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.version.outputs.tag }}"
```

Three caveats to remember:

1. **Outputs are always strings.** A boolean-looking `'true'` is actually a string — compare with `== 'true'` in `if:` conditions.
2. **A job's outputs are accessible only from jobs connected via `needs`.** Without listing it in `needs`, you cannot read another job's outputs.
3. **Large data goes through artifacts.** Outputs suit short strings; build results and reports need `actions/upload-artifact` and `actions/download-artifact`.

## Matrix Cost Control Strategies

Matrix is powerful but combinations multiply cost rapidly. Production strategies for control:

```yaml
strategy:
  fail-fast: true
  matrix:
    python: ["3.11", "3.12"]
    os: [ubuntu-latest]
    include:
      - python: "3.12"
        os: macos-latest
    exclude:
      - python: "3.10"
        os: macos-latest
```

**`fail-fast: true`**: Cancel remaining runs when one fails. The most direct cost reduction. Though for compatibility matrices where you want all results, `false` may be better.

**`include` and `exclude`**: Add only needed combinations or remove unnecessary ones instead of testing the full Cartesian product.

**PR vs main separation**: Run minimal matrix (latest Python + Ubuntu only) on PRs for fast feedback; run full matrix on main push.

```yaml
strategy:
  matrix:
    python: ${{ github.event_name == 'pull_request' && fromJSON('["3.12"]') || fromJSON('["3.10", "3.11", "3.12"]') }}
```

This expression tests only Python 3.12 on PRs, all three versions on push. Dynamic matrices look complex but capture both cost and feedback speed simultaneously.

## Artifact Passing Between Jobs

If outputs are for strings, file-based results like build artifacts and test reports need artifacts:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
      - uses: actions/upload-artifact@v7
        with:
          name: dist
          path: dist/
          retention-days: 3

  publish:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/
      - run: twine upload dist/*
```

Key points:

- Short `retention-days` (1-3) saves storage cost for CI artifacts.
- Artifacts are shared only within the same workflow run. Cross-workflow access requires `workflow_run` events.
- Artifact names must be unique in matrix builds — use `name: dist-${{ matrix.python }}` to prevent overwrites.

## Preventing Duplicate Runs with `concurrency`

Rapid consecutive pushes to the same PR trigger multiple workflow runs. `concurrency` prevents stale runs from wasting resources:

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

This cancels the previous run when a new one starts on the same branch. For deploy jobs, use `cancel-in-progress: false` to protect in-progress deployments:

```yaml
jobs:
  deploy:
    concurrency:
      group: deploy-production
      cancel-in-progress: false
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh
```

Job-level `concurrency` serializes only that specific job, not the entire workflow. Tests run in parallel while deploys execute one at a time.

## Workflow File Structuring Patterns

As workflow files grow, management becomes painful. Two patterns help:

**Pattern 1 — Separation by responsibility**

```text
.github/workflows/
├── ci.yml          # test, lint, typecheck
├── build.yml       # build, packaging
├── deploy.yml      # deployment
└── maintenance.yml # dependency updates, cleanup
```

**Pattern 2 — Reusable workflows for shared logic**

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ inputs.python-version }}
      - run: pytest -q
```

```yaml
# .github/workflows/ci.yml
jobs:
  test-311:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: "3.11"

  test-312:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: "3.12"
```

Reusable workflows connect directly to job graph design. Common verification logic lives in one place while callers can still add `needs` dependencies. This pattern is covered in more depth in the final post (chapter 10).

## Job Execution Time Optimization

Even with a well-designed graph, long individual job times slow overall feedback. Common optimization techniques:

| Technique | Effect | When to Apply |
| --- | --- | --- |
| Dependency cache | 50-80% install time reduction | Always |
| `fetch-depth: 1` | Faster clone | When git history not needed |
| Matrix minimization | Fewer jobs | PR verification |
| Conditional skip | Prevents unnecessary runs | `paths` filter |
| Parallel tests | Shorter test time | Large test suites |

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 1  # shallow clone

- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
    cache: "pip"

- run: pytest -q -n auto  # pytest-xdist parallel execution
```

`fetch-depth: 1` is the easiest optimization. Most CI jobs only need the latest commit. However, jobs that need `git describe` or changelog generation require `fetch-depth: 0`.

## Five Common Mistakes

1. **All steps in one Job.** Lost parallelism, slow feedback.
2. **Missing `needs`.** Dependencies become implicit and invisible.
3. **A huge matrix.** Build cost explodes multiplicatively.
4. **Complex objects in outputs.** Serialization breaks; use artifacts instead.
5. **No `if:` conditions.** Unnecessary jobs run every time, wasting budget.

The third and fifth connect directly to cost. A poorly drawn job graph is not just slow — runner usage inflates rapidly.

## How a Senior Engineer Thinks

Mature teams run fast lint+test only on PRs and a full matrix + build on main push — a two-tier graph. This goes beyond knowing GitHub Actions syntax to designing feedback and cost as separate concerns.

`needs` expresses not just technical dependencies but business intent. "No deploy before security scan passes" is ultimately a rule that must be encoded in the job graph to persist.

## Checklist

- [ ] lint / test / build are separated into distinct jobs.
- [ ] `needs` makes all dependencies explicit.
- [ ] `matrix` size considers cost impact.
- [ ] `outputs` carry only simple strings.
- [ ] `concurrency` prevents duplicate runs.
- [ ] PR and main branch use different matrix scopes.

## Practice Problems

1. Build a 3-job graph (lint, test, build) with proper `needs`.
2. Add a Python 3.11/3.12 matrix to the test job.
3. Have deploy consume the version output from build.
4. Add `concurrency` and verify that rapid pushes cancel prior runs.

## Wrap-up and Next Steps

The workflow is the outer frame; the job graph is the pipeline's actual skeleton. Deciding what runs in parallel, what requires ordering, and what values pass to the next stage — that is CI design.

The next post covers when this graph should execute: trigger design. A well-structured graph only delivers value when it fires at the right moments.

## Answering the Opening Questions

- **What does each of Workflow, Job, and Step handle?**
  - A Workflow is the outer frame defining "what starts on which event." A Job is the parallel execution unit — the boundary of failure isolation and parallelism. A Step is an individual command executed sequentially within a Job. When designing, draw Job boundaries by "can this work run independently" and Step order by "does this command depend on the previous result."
- **Why is `needs` not just a simple option but a pipeline design tool?**
  - `needs` creates a directed graph between jobs, expressing the business rule "what must succeed before the next starts" as code. Patterns like fan-out/fan-in, conditional deployment, and matrix gates all operate on `needs`. Poor design wastes time with unnecessary serialization; omitting it risks deploying on top of failed validation.
- **When is `matrix` useful and when does it become a cost bomb?**
  - Matrix is useful for compatibility testing (multiple Python versions, multiple OSes). It becomes a cost bomb when combinations multiply unchecked — 3 Python × 3 OS × 2 DB = 18 simultaneous jobs at 18× cost. The practical standard is minimal combinations on PRs, full combinations on main, with `fail-fast` and `include`/`exclude` to control scope.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- **Workflows and Jobs (current)**
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

- [Workflow syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Using jobs in a workflow](https://docs.github.com/actions/using-jobs/using-jobs-in-a-workflow)
- [Using a matrix for jobs](https://docs.github.com/actions/using-jobs/using-a-matrix-for-your-jobs)
- [Defining outputs for jobs](https://docs.github.com/actions/using-jobs/defining-outputs-for-jobs)
- [Reusing workflows](https://docs.github.com/actions/using-workflows/reusing-workflows)

Tags: GitHubActions, Workflow, Job, Matrix, CICD
