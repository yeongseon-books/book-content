---
series: testing-101
episode: 9
title: "Testing 101 (9/10): Running Tests in CI"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Testing
  - CI
  - GitHub Actions
  - Automation
  - Quality
seo_description: Automate tests with GitHub Actions and speed them up using matrix builds, dependency caching, and parallel execution.
last_reviewed: '2026-05-04'
---

# Testing 101 (9/10): Running Tests in CI

A local green run is useful, but it is still only one machine, one dependency cache, and one engineer’s environment. Teams get into trouble when they treat that as sufficient evidence for everyone else, especially once multiple Python versions, operating systems, or contributors are involved.

Continuous Integration exists to turn “works on my laptop” into a shared standard. The point is not just automation—it is consistent automation under conditions the whole team can trust.

This is the 9th post in the Testing 101 series. Here we use GitHub Actions to build a practical CI path, then look at the operational details that keep the pipeline fast enough to enforce and informative enough to debug.

> CI is where personal confidence becomes organizational evidence.


![testing 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/09/09-01-concept-at-a-glance.en.png)
*testing 101 chapter 9 flow overview*
> CI transforms "works on my machine" from an anecdote into a requirement.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Running Tests in CI?
- Which signal should the example or diagram make visible for Running Tests in CI?
- What failure should be prevented first when Running Tests in CI reaches a real system?

## What You Will Learn

- The definition and purpose of *CI (Continuous Integration)*
- The basic structure of a *GitHub Actions* workflow
- Speeding things up with *matrix* builds and *caching*
- Test *parallelization* and *result artifacts*
- Five common pitfalls

## Why It Matters

Local environments *differ from person to person*. *CI* validates *every PR* in an *identical container*. It is the *last gate* that keeps broken code out of main.

> Tests without CI are tests that *passed by accident*.

## Concept at a Glance
Continuous Integration runs tests automatically on every commit and PR in a controlled environment, catching environment-specific failures, dependency version mismatches, and test order dependencies that local runs would miss, turning test results into organizational evidence rather than individual confidence.
## Key Terms

- **CI**: *Continuous Integration*. *Auto-validate* every commit.
- **Workflow**: A GitHub Actions *YAML definition*.
- **Matrix**: A configuration that runs multiple *Python versions and OSes* *in parallel*.
- **Cache**: *Reusing* dependency installations to gain speed.
- **Artifact**: A *file produced* by a CI run (logs, reports).

## Before/After

**Before (manual testing)**

```text
- Developers run pytest *only on their laptops*
- One forgotten run later, *failures get merged*
```

**After (CI automation)**

```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - run: pytest -v
```

## Hands-on: Five Steps to Set Up CI

### Step 1 - Create the workflow file

```bash
mkdir -p .github/workflows
touch .github/workflows/test.yml
```

### Step 2 - Test multiple versions with a matrix

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
steps:
  - uses: actions/setup-python@v5
    with: { python-version: ${{ matrix.python-version }} }
```

### Step 3 - Cache dependencies

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: 'pip'           # auto-detects requirements.txt
- run: pip install -r requirements.txt
```

### Step 4 - Speed it up with parallel execution

```bash
pip install pytest-xdist
pytest -n auto             # parallel across CPU cores
```

### Step 5 - Upload coverage as an artifact

```yaml
- run: pytest --cov=src --cov-report=html
- uses: actions/upload-artifact@v4
  with:
    name: coverage-html
    path: htmlcov/
```

## What to Notice in This Code

- The *trigger* usually includes *both* `push` and `pull_request`.
- The cache key is *managed by the requirements hash* automatically.
- Be careful with matrix *combinatorial explosion*. *Two or three versions* are usually enough.

## Five Common Mistakes

1. **Tests that are *flaky only on CI*.** Usually an *order dependency* or an *external resource* problem.
2. **Running the *full E2E suite* on every PR.** Split into *unit -> integration -> E2E* tiers.
3. **Cache *without a key* lets *stale dependencies* pass.** Always use a *hash-based key*.
4. **Printing *secrets to the log*.** Never do `echo $SECRET`.
5. **Build time exceeds *10 minutes* and you ignore it.** Aim for *under 5 minutes* with parallelism and caching.

## Verification Points

1. Compare the local command you trust with the command CI runs. If they differ, the meaning of a green build is already diluted.
2. Measure runtime with and without dependency caching so you know whether the optimization is actually worth the complexity.
3. Compare a single all-in-one job with split unit/integration/E2E jobs and inspect the feedback time difference.

**Expected output:** the default PR path should finish within a few minutes, and the logs should tell you exactly which stage failed without additional guesswork.

## Failure Signals and First Checks

- CI-only flakes usually point to order dependence, timing assumptions, or real external resources.
- A stale cache can keep broken dependency changes hidden until much later.
- Secrets in logs turn a test pipeline problem into a security incident.

## How This Shows Up in Production

Large teams *split* their suites into a *unit job* (1-2 minutes), an *integration job* (5 minutes), and an *E2E job* (15 minutes, nightly). PRs only require *unit and integration*; *E2E* runs after merge during the night.

## How a Senior Engineer Thinks

- A *red PR getting merged* is a *system failure*.
- CI duration is *developer velocity*. Defend the *5-minute rule*.
- *Flaky tests* are *quarantined immediately* and repaired.
- *Secrets* are *separated per environment*.
- The *badge* is the *first signal in the README*.

## Checklist

- [ ] `.github/workflows/test.yml` *exists*.
- [ ] The *matrix* runs at least *two Python versions*.
- [ ] *Dependency caching* is enabled.
- [ ] *Red PRs* never get merged.

## Practice Problems

1. Add a *test.yml* workflow to your project and produce its first *green build*.
2. Add *Python 3.11 and 3.12* to the matrix.
3. Adopt *pytest-xdist* and *measure and compare* the runtime.

## Wrap-up and Next Steps

CI is *the safety net for the whole team*. In the next post we tie everything together into a *test strategy*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Running Tests in CI?**
  - The article treats Running Tests in CI as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Running Tests in CI?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Running Tests in CI reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Testing 101 (1/10): What Is Testing?](./01-what-is-testing.md)
- [Testing 101 (2/10): Unit Test](./02-unit-test.md)
- [Testing 101 (3/10): Integration Test](./03-integration-test.md)
- [Testing 101 (4/10): E2E Test](./04-e2e-test.md)
- [Testing 101 (5/10): Test Double](./05-test-double.md)
- [Testing 101 (6/10): Mock and Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): Test Coverage](./07-test-coverage.md)
- [Testing 101 (8/10): Regression Test](./08-regression-test.md)
- **Running Tests in CI (current)**
- Building a Test Strategy (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [actions/setup-python](https://github.com/actions/setup-python)
- [Caching dependencies to speed up workflows](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

### Practical Reading
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)

Tags: Testing, CI, GitHub Actions, Automation, Quality
