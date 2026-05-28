---
series: portfolio-project-101
episode: 6
title: "Portfolio Project 101 (6/10): Tests and Documentation"
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
  - Testing
  - Documentation
  - Quality
  - Beginner
seo_description: How to prove a portfolio project is reliable through a minimum testing stack, clear documentation, and CI automation.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (6/10): Tests and Documentation

Saying that a project works is very different from showing that it has been verified. If a reviewer opens the repository and finds no tests and no docs beyond a short README, the whole project starts to look like practice code—even if the app itself is functional.

This is the 6th post in the Portfolio Project 101 series. Here we will look at the level of testing and documentation that makes a small portfolio project feel trustworthy instead of accidental.

---

> Working code is only a claim until another person can verify it through tests, docs, and repeatable checks.


![portfolio project 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/06/06-01-concept-at-a-glance.en.png)
*portfolio project 101 chapter 6 flow overview*
> Tests are your record of every verification you have ever done, run automatically. Documentation is the map that lets the next developer—or you—understand again.

## Questions to Keep in Mind

- What do unit tests, integration tests, and end-to-end checks each prove?
- Why does even a small portfolio project benefit from automated verification?
- What kinds of docs make a repository easier to trust and adopt?

## Why It Matters

Tests and docs are fast signals of professionalism. A reviewer does not need a huge test suite to feel the difference. Even a few well-chosen checks tell them that you expected breakage, created a verification path, and cared about life after the first successful run.

Documentation does the same thing for humans. It lowers the cost of understanding the project, which is exactly what a portfolio should do.

## Mental Model

Verification usually grows from small logic checks to full user flow checks, then out to docs and CI.

That order matters. Unit tests catch fast local mistakes. Integration tests validate boundaries. End-to-end checks confirm the main user path. Documentation and CI make the whole verification story reusable.

## Key Terms

- **Unit test**: a small, fast check for one function or logic unit.
- **Integration test**: a check across boundaries such as API routes or storage.
- **End-to-end test**: a full user scenario from start to finish.
- **CI**: automatic verification when code changes.
- **Project docs**: the documents that help another person understand and use the project.

## Before and After

**Before**: all validation happens manually and depends on the author remembering what to click.

**After**: code changes trigger repeatable checks, and the repository gives another person a clear path to understanding the project.

The difference is repeatability. One successful run is less convincing than a project that can prove itself again.

## Step by Step

### Step 1 — Start with a unit test

The fastest failures are often the cheapest to fix.

```python
def test_add():
    assert 1 + 1 == 2
```

The example is tiny on purpose. The point is to create the habit of verifying logic explicitly.

### Step 2 — Add an integration check

Many issues only appear when multiple pieces meet.

```python
def test_api(client):
    assert client.get("/health").status_code == 200
```

Even one integration test gives the reviewer a stronger signal that the project was checked as a system, not just as isolated functions.

### Step 3 — Name one end-to-end path

You do not need dozens of E2E flows. You do need one meaningful one.

For example, define the core end-to-end path as `login -> create -> delete`.

A single core user path tells people what the project considers essential.

### Step 4 — Automate the verification

Checks are stronger when they do not depend on memory.

```yaml
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
```

CI is especially persuasive in a portfolio because it shows you treat verification as default behavior.

### Step 5 — Keep docs beyond the README

The README is the entrance, but not the whole documentation story.

The documentation baseline is usually strong enough with these three files:

- `README`
- `API.md`
- `CHANGELOG.md`

An API note, a changelog, or a short architecture page helps the reviewer see that the project can be understood and maintained over time.

## What to Notice in the Code

- Unit tests are the fastest safety net.
- Integration and end-to-end checks show what the project trusts as a real flow.
- CI and docs turn one person’s memory into a repeatable team habit.

## Common Mistakes

1. Keeping only unit tests and never checking the main user path.
2. Having no end-to-end proof before deployment.
3. Leaving verification entirely manual.
4. Providing no API or usage docs beyond a thin README.
5. Failing to record how the project changed over time.

Tests and docs are not nice extras. They are what make the project believable.

## How This Reads in Practice

Well-run open source projects also rely on push-time verification, small but explicit docs, and visible change history. The same habits matter in portfolio work because they reveal how you think about maintenance, not just implementation.

A small project with one unit test, one important user flow, and clear docs can feel much stronger than a larger project with none of those signals.

## Checklist

- [ ] There is at least one unit test.
- [ ] One core user flow is described or checked end to end.
- [ ] Verification runs automatically on code changes.
- [ ] The repository has docs beyond the README when the project needs them.

## Practice Problems

1. Pick the first function in your project that deserves a unit test.
2. Write the three steps of your most important user flow.
3. Choose one extra document you should add next.

## Wrap-up and Next Steps

In a portfolio project, tests and documentation are evidence. Unit checks create the fast safety net. Integration and user-flow checks raise confidence. Docs and CI make the whole thing reusable. Together they turn "it worked once" into "it can be verified again."

Next, we will look at how to record the technical decisions behind the project so reviewers can see not just the result, but the judgment behind it.

### Deployment Environment Comparison (Learning Projects)

Test and documentation quality connects to the deployment environment. If the environment is unstable, test result confidence also wavers.

| Environment | Strengths | Watch Out | Best For |
| --- | --- | --- | --- |
| Local Docker Compose | High reproducibility, easy team sharing | Initial setup required | Dev/integration test baseline |
| Render/Railway | Simple deploy, easy log access | Free tier may sleep | Public demo hosting |
| Fly.io | Container-friendly, broad operational control | Config learning curve | API-focused demos |
| Vercel (frontend) + separate API | Fast frontend deploys | Backend separation needed | SPA demo projects |

The choice is not a right-or-wrong question. The key criterion is whether you can maintain test reproducibility and documentation consistency.

### Docker Configuration Example (Test-Friendly)

To strengthen testing and documentation, explicitly defining container start order and health checks helps.

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    build: .
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    command: bash -lc "pytest -q && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

The advantage of this setup is automating "verify then run." If tests break, the server does not count as successfully deployed.

### Minimum Documentation Set

A README alone cannot adequately convey test strategy and operational judgment. Adding three documents raises project trust significantly.

1. `docs/testing.md` - Test scope, run commands, failure interpretation
2. `docs/runbook.md` - Failure check order, rollback procedure, log locations
3. `CHANGELOG.md` - Change history and user impact

```markdown
## docs/testing.md example sections
- Test pyramid summary
- Local run instructions
- Tests that only run in CI
- Flaky test handling rules
```

This document set is also useful in interviews. It lets you explain not just "I tested" but "how I managed failures."

### Test Strategy Table (Pre-Release)

Even in portfolio projects, defining pre-release test criteria stabilizes quality.

| Phase | Required Tests | Pass Criteria |
| --- | --- | --- |
| Local dev | Unit tests | All core logic passes |
| PR review | Unit + Integration | CI green |
| Pre-deploy | Smoke tests | Key APIs respond normally |
| Post-deploy | Real-user scenario | Login-query-result verified |

### Documentation Update Rules

Docs tend to lag behind code. These rules reduce documentation debt:

1. Changes affecting user behavior require simultaneous README update
2. API schema changes require simultaneous `API.md` update
3. Deploy process changes require simultaneous `runbook.md` update
4. Every release adds one line to `CHANGELOG.md`

These rules are effective even in small projects. Reducing doc-code mismatch quickly raises reviewer trust.

Tip: adding a "documentation updated?" checkbox to your PR template helps reviewers catch missing docs naturally. One line in `.github/PULL_REQUEST_TEMPLATE.md` is all it takes.

### Project Documentation Directory Structure

A project with both tests and docs well-organized typically has this `docs/` structure:

```text
docs/
├── architecture.md      # system structure, layers, data flow
├── testing.md           # test strategy, run instructions, coverage criteria
├── api.md               # endpoints, request/response, error codes
├── runbook.md           # failure response order, rollback, log locations
└── decisions/           # ADR (Architecture Decision Records)
    ├── 001-database-choice.md
    └── 002-auth-strategy.md
```

Each document serves a different reader:

| Document | Reader | Core Question |
| --- | --- | --- |
| architecture.md | New joiners | "How does this system work?" |
| testing.md | Contributors/reviewers | "How do I run the tests?" |
| api.md | Frontend developers | "What endpoints exist?" |
| runbook.md | Operators | "What do I do during an outage?" |
| decisions/ | Future self | "Why was this decided this way?" |

You do not need all five in a portfolio project. Just `testing.md` and `architecture.md` already differentiate significantly.

### docs/testing.md Full Template

```markdown
# Testing Strategy

## Test Pyramid

| Layer | Target | Tool | When |
| --- | --- | --- | --- |
| Unit | Pure functions, utilities | pytest | Every commit |
| Integration | API endpoints | pytest + httpx | PR |
| E2E | User scenarios | playwright | Pre-deploy |

## Local Run

```bash
# Full test suite
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Specific module only
pytest tests/test_scheduler.py -v
```

## CI Test Configuration

GitHub Actions runs `pytest` automatically.
PRs do not merge unless CI is green.

## Flaky Test Handling

- Network-dependent tests: isolate with mock
- Time-dependent tests: use freezegun
- DB-dependent tests: apply transaction rollback
```

Copy this template directly or adapt it for your project. What matters is showing not "tests exist" but "a test strategy exists."

### Test Report Template

Recording test results lets you track quality changes over time.

```markdown
## Test Report - 2024-03-15

| Metric | Value | Note |
| --- | --- | --- |
| Total tests | 47 | +5 from last week |
| Passing | 45 | |
| Failing | 0 | |
| Skipped | 2 | E2E - external API dependency |
| Coverage | 78% | Goal: 80% |
| Run time | 12s | CI baseline |

### Failure Analysis
- None

### Skip Reasons
- test_external_webhook: External API rate limit (mock migration planned)
- test_email_send: SMTP config required (CI env var addition planned)
```

Maintaining this report weekly proves the project is actively managed. In interviews you can say "I raised coverage from 60% to 78%" with actual numbers.

### Adding CI Badges to README

CI badges are small but strong signals. A green badge at the top of the README says "this project has automated verification."

```markdown
<!-- Top of README.md -->
![CI](https://github.com/username/project/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/username/project/branch/main/graph/badge.svg)
```

To add badges:

1. Create a GitHub Actions workflow file (`.github/workflows/ci.yml`)
2. GitHub repo → Actions tab → select workflow → "…" menu → "Create status badge"
3. Paste the generated Markdown at the top of your README

For coverage badges, connect a service like Codecov or Coveralls. Both offer free tiers suitable for portfolio projects.

### conftest.py Pattern: Test Fixture Organization

Test code quality is also evaluated in portfolios. A well-organized conftest.py demonstrates test design ability.

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.database import get_test_db, reset_db


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """API test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_database():
    """Reset DB before and after each test."""
    reset_db()
    yield
    reset_db()
```

Key points in this fixture setup:

1. **Session scope control**: Separates one-time setup from per-test setup.
2. **DB isolation**: Ensures each test runs independently.
3. **Real API testing**: Uses httpx ASGITransport to simulate actual HTTP requests.

### CHANGELOG Writing

Change history is the most intuitive evidence that a project is actively maintained. Following [Keep a Changelog](https://keepachangelog.com/) format maintains consistency.

```markdown
# Changelog

## [0.3.0] - 2024-03-15

### Added
- OAuth2 authentication support (Google, GitHub)
- Automatic weekly report generation

### Changed
- Database connection pool optimization (5 → 10)
- API response format unified to snake_case

### Fixed
- Bug where deleting a team member left tasks unassigned

## [0.2.0] - 2024-02-28

### Added
- Dashboard basic UI
- Seed data auto-generation script

### Fixed
- Docker Compose network configuration error
```

Important CHANGELOG principles:

1. **Write from the user's perspective**: "Improved response time by 30%" instead of "refactored code."
2. **Use version numbers**: Semantic versioning communicates change scale.
3. **Date stamps**: Visually show project activity.

### Common Testing Mistakes

| Mistake | Symptom | Solution |
| --- | --- | --- |
| Testing implementation | Tests break on refactor | Verify behavior/results only |
| Test interdependency | Changing order causes failure | Isolate with fixtures |
| Direct external API calls | Fails without network | Use mock/stub |
| Hard-coded magic numbers | Changing values breaks tests | Extract to variables/constants |
| Testing everything | Maintenance cost explodes | Focus on core logic |

In portfolios especially, "testing the most important thing well" beats "testing everything." Focus tests on core logic like scheduler time calculations, auth token validation, or payment amount computation. A small number of well-targeted tests delivers high trust.

### Workflow for Keeping Tests and Docs in Sync

Tests and docs drift apart quickly when managed separately. Including both in a PR checklist naturally synchronizes them.

```markdown
<!-- .github/pull_request_template.md -->
## PR Checklist
- [ ] Tests added/modified (new feature or bugfix)
- [ ] No coverage decrease (pytest --cov verified)
- [ ] README impact checked
- [ ] docs/api.md updated if API changed
- [ ] CHANGELOG entry added
```

This checklist structurally prevents "modified code but forgot docs." PR templates are useful even for solo projects—they are reminders to your future self.

### Minimal Verification Strategy Without Tests

If writing test code feels daunting, start gradually in this order:

1. **Add a linter** (5 min): Just `ruff check .` creates a code quality baseline.
2. **Type checking** (10 min): `mypy src/` catches type errors and prevents bugs.
3. **One smoke test** (15 min): Write one test that sends a GET to your core API and checks for 200.
4. **Business logic test** (30 min): Test your most important calculation/validation function.
5. **CI integration** (20 min): Configure GitHub Actions to run the above automatically.

The key is not "perfect testing" but "progressive verification culture." Even step 1 lets you write "Lint: ruff" in your README, and step 3 lets you add a CI badge. Starting small verification now beats waiting for perfection.

## Answering the Opening Questions

- **What does each of unit tests, integration tests, and end-to-end tests prove?**
  - Unit tests prove one function's correctness, integration tests prove module connections, and end-to-end tests prove the entire user scenario. 30% coverage of core logic sends a stronger signal than 90% overall coverage.
- **Why is automated verification an important criterion even for small portfolios?**
  - Automated verification proves the project is a repeatedly validated artifact, not something that worked by accident. Just having a CI pipeline demonstrates operational awareness.
- **What trust do API docs or changelogs add?**
  - API docs show evidence of frontend collaboration, and changelogs show maintenance ability. Even for a small project, having a CHANGELOG gives the impression of "an actively improved project."
<!-- toc:begin -->
## In this series

- [Portfolio Project 101 (1/10): What is a Portfolio Project](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): Traits of a Good Project](./02-traits-of-a-good-project.md)
- [Portfolio Project 101 (3/10): Writing the README](./03-writing-the-readme.md)
- [Portfolio Project 101 (4/10): Building the Demo](./04-building-the-demo.md)
- [Portfolio Project 101 (5/10): Deploying the Project](./05-deploying-the-project.md)
- **Tests and Documentation (current)**
- Recording Tech Decisions (upcoming)
- Summarizing as Blog Posts (upcoming)
- Explaining in Interviews (upcoming)
- Portfolio Improvement Checklist (upcoming)

<!-- toc:end -->

## References

- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [pytest documentation](https://docs.pytest.org/)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Keep a Changelog](https://keepachangelog.com/)

Tags: Portfolio, Testing, Documentation, Quality, Beginner
