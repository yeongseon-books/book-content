---
title: "Alembic 101 (10/10): Production and team workflow: PR, CI, monitoring, and incident response"
series: alembic-101
episode: 10
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- Alembic
- Production
- CI
- workflow
- SQLite
last_reviewed: '2026-05-12'
seo_description: A migration is "the most irreversible kind of code change". Ordinary
  code can be reverted with a single click; a schema change carries data with it…
---

# Alembic 101 (10/10): Production and team workflow: PR, CI, monitoring, and incident response

In production, a migration is more irreversible than ordinary application code. That is why Alembic safety has to live in team workflow, PR rules, and verification routines rather than in individual discipline alone.

This is the final post in the Alembic 101 series. Here we will pull the series together into a practical operating model for PRs, CI, monitoring, and incident response.

## Questions to Keep in Mind

- The one-revision-per-PR rule and why it matters?
- How to compose an Alembic-aware PR template and the matching CI checks?
- How to manage multiple environments where dev=SQLite and staging+prod=PostgreSQL?

## Big Picture

![alembic 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/10/10-01-diagram-the-team-level-alembic-operating.en.png)

*alembic 101 chapter 10 flow overview*

This picture places Production and team workflow: PR, CI, monitoring, and incident response inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Production and team workflow: PR, CI, monitoring, and incident response is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why this matters

Everything in the previous nine posts described how a single engineer can apply migrations safely in their own environment. Once a team starts changing the schema concurrently, a different class of problems appears. Two people creating a new revision at the same time produce a multi-head; if no one tests downgrade, rollback breaks; if production schema starts drifting, you have no idea where to start. Operational stability comes from workflow quality, not from code quality.

## Mental Model

> A migration is **"the most irreversible kind of code change"**. Ordinary code can be reverted with a single click; a schema change carries data with it and is very hard to undo. So you must treat it more strictly than ordinary code at the PR stage.

The starting point of the operational workflow is: one PR equals one revision, and that revision's upgrade and downgrade are both verified.

### Diagram: the team-level Alembic operating loop

## Core concepts

### One revision per PR

Bundling several schema changes into one PR creates two problems.

- The reviewer must understand all changes at once → higher incident probability
- If only one change is wrong, you cannot revert just that part → you must revert all of them together

When each revision is its own PR, reviews are simpler and the blast radius on failure is smaller. Expand-contract also decomposes naturally into per-phase PRs.

### CI check items

| Gate | Command | Pass condition | What failure means |
| --- | --- | --- | --- |
| unit tests | `python3 -m pytest` | application and model tests pass | the migration assumptions already diverge from runtime code behavior |
| drift guard | `alembic check` | every model change has a matching revision | a model changed without a revision, or the autogenerate review is incomplete |
| downgrade round-trip | `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` | upgrade and downgrade both succeed | an irreversible change, a broken downgrade, or a hidden stateful data assumption exists |
| single-head guard | count the lines from `alembic heads` and require exactly one | head count = 1 | concurrent revisions were created but never merged |
| SQL preview artifact | `alembic upgrade head --sql > migration_preview.sql` | preview file is produced and reviewed | risky DDL may be hidden, or reviewers have no SQL artifact to inspect |
| fresh DB smoke | create a temporary DB, run `alembic upgrade head`, then run one minimal verification query | a blank database reaches head and contains the expected core objects | new-environment bootstrap or the initial revision chain is broken |

`alembic check` is supported on 1.9 and later. If a model was added but the revision is missing, it fails immediately.

### Multi-environment strategy

| Environment | DB | Options |
| --- | --- | --- |
| dev | SQLite | `render_as_batch=True` |
| staging | PostgreSQL | `compare_type=True`, `compare_server_default=True` |
| prod | PostgreSQL | deploy script invokes `alembic upgrade` |

Using SQLite in dev lets a single engineer get started quickly and simulate migrations fast. From staging onward you use the same PostgreSQL as production, so any incidents caused by SQLite/PostgreSQL differences are caught at staging. Autogenerate verification is also done at staging.

### Team conventions

- **Revision message is an imperative one-liner**: "add users phone column" (not "added", not "users phone added")
- **PR title carries the expand-contract phase tag**: `[expand]`, `[migrate]`, `[contract]`
- **One revision per PR**
- **Resolve down_revision conflicts immediately**: never leave a multi-head state for more than 24 hours

### Operational monitoring

Have your `/health` endpoint return the current `alembic_version`.

```python
@app.get("/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    return {"status": "ok", "alembic_version": version, "expected": EXPECTED_VERSION}
```

Inject EXPECTED_VERSION as an env var at deploy time, and raise an alarm if any instance reports a different version. In a multi-instance deploy, you can immediately detect a partially-applied migration or an instance still running outdated code.

### Incident response

When a migration causes an incident, the first instinct is to downgrade, but as we saw in episode 8 downgrade is only feasible in limited cases. The procedure used most often in practice is the following.

```text
1. Compare the `/health` reported version with the expected release version
2. Inspect `alembic heads` and the current `alembic_version`
3. Decide whether the failure is code-only, schema-only, or mixed code/schema
4. Roll back code only if the schema is still backward-compatible; otherwise write a forward-fix
5. Name the exact broken revision before you write `fix <broken_revision_id>: <issue>`
```

A forward-fix adds a new revision that brings the broken state back to a valid one. Unlike downgrade, the alembic_version graph stays moving forward, which gives better traceability and is compatible with blue/green.

### Drift triage table

At the start of an incident, an explicit `symptom → first command → next action` table is usually more useful than a long policy paragraph.

| Symptom | Likely cause | First command | Next action |
| --- | --- | --- | --- |
| `/health` shows different `expected` and `alembic_version` values | only some instances see the new code or schema | `curl -fsS https://api.example.com/health` | compare responses per instance and split the problem into rollout drift vs schema drift |
| `alembic heads` returns more than one line | merge revision is missing | `alembic heads` | stop deploys and create the merge-revision PR first |
| only the new version is failing | code assumed the new schema incorrectly | compare `/health` versions and the latest deploy record | if you are still in the expand phase, prefer code rollback first |
| both old and new versions are failing | the schema revision itself is broken | `SELECT version_num FROM alembic_version` | pin the broken revision ID and write the forward-fix |

## Before-After

```text
# Before: 6 revisions per PR, downgrade not verified
- reviewer spends 30 minutes tracing all revisions
- one broken downgrade is discovered in prod
- rollback impossible, 30-minute downtime
```

```text
# After: one PR = one revision, downgrade verified in CI
- reviewer sees one revision, merges in five minutes
- CI auto-runs upgrade head + downgrade -1 + upgrade head
- broken downgrade is blocked at the PR
```

Keeping PRs small and verifying downgrade, single-head, and fresh-DB bootstrap in CI makes it explicit which migration defects are being blocked before merge.

## Step-by-step walkthrough

### Step 1: write a PR template

```markdown
## Migration PR Checklist

- [ ] One revision per PR
- [ ] expand-contract phase: [ ] expand / [ ] migrate / [ ] contract
- [ ] alembic check passes
- [ ] downgrade verified (CI auto)
- [ ] alembic upgrade head --sql output attached
- [ ] data migration is idempotent (WHERE clause)
- [ ] row counts of affected tables
```

Drop this in `.github/pull_request_template.md` so every schema PR follows the format.

### Step 2: add downgrade verification to CI

```yaml
# .github/workflows/migrate.yml
- name: alembic check
  run: alembic check
- name: upgrade then downgrade
  run: |
    set -euo pipefail
    alembic upgrade head
    alembic downgrade -1
    alembic upgrade head
- name: head count guard
  run: |
    set -euo pipefail
    HEADS=$(alembic heads | python3 -c "import sys; print(sum(1 for line in sys.stdin if line.strip()))")
    [ "$HEADS" = "1" ] || { echo "Fail: multi-head detected ($HEADS)"; exit 1; }
- name: SQL preview
  run: alembic upgrade head --sql > migration_preview.sql
- name: fresh DB smoke
  run: |
    set -euo pipefail
    DB_FILE=$(mktemp /tmp/alembic-smoke-XXXX.db)
    trap 'rm -f "$DB_FILE"' EXIT
    export DATABASE_URL="sqlite:///$DB_FILE"
    alembic upgrade head
    python3 - <<'PY'
    import os
    import sqlite3

    db_path = os.environ["DATABASE_URL"].removeprefix("sqlite:///")
    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='alembic_version'"
        ).fetchone()[0]
        assert count == 1, f"alembic_version missing in {db_path}"
        print(f"Pass: fresh DB reached head at {db_path}")
    finally:
        conn.close()
PY
- uses: actions/upload-artifact@v4
  with:
    name: migration-preview
    path: migration_preview.sql
```

This example does not depend on repo-local helpers such as `scripts/check_alembic_heads.py` or `scripts/migrate_smoke_test.py`. The article stays honest only when the head guard, downgrade round-trip, and fresh-DB smoke are visible as commands the reader can reuse directly.

### Step 3: split per-environment configuration

```python
# part of env.py
def get_url():
    env = os.environ.get("APP_ENV", "dev")
    return {
        "dev": "sqlite:///./dev.db",
        "staging": "postgresql://staging-host/app",
        "prod": "postgresql://prod-host/app",
    }[env]

def run_migrations_online() -> None:
    connectable = create_engine(get_url())
    is_sqlite = connectable.url.get_backend_name() == "sqlite"
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
```

In dev, SQLite + batch mode applies automatically; in staging/prod, PostgreSQL with strict comparison is enabled.

### Step 4: wire monitoring

```python
# health.py
EXPECTED_VERSION = os.environ["EXPECTED_ALEMBIC_VERSION"]

@app.get("/health")
def health():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    ok = version == EXPECTED_VERSION
    return {"status": "ok" if ok else "drift", "alembic_version": version, "expected": EXPECTED_VERSION}
```

Inject EXPECTED_ALEMBIC_VERSION from your deploy pipeline and compare per-instance responses on your operations dashboard. Alert on drift.

## Verification routine

```bash
set -euo pipefail

alembic check
alembic upgrade head
alembic downgrade -1
alembic upgrade head
HEADS=$(alembic heads | python3 -c "import sys; print(sum(1 for line in sys.stdin if line.strip()))")
[ "$HEADS" = "1" ] || { echo "Fail: multi-head detected ($HEADS)"; exit 1; }

DB_FILE=$(mktemp /tmp/alembic-smoke-XXXX.db)
trap 'rm -f "$DB_FILE"' EXIT
export DATABASE_URL="sqlite:///$DB_FILE"
alembic upgrade head
```

**Expected output:** this block reruns the same gates the chapter taught earlier. `alembic check` validates drift, the round-trip validates downgrade, the head count validates branch hygiene, and the fresh-DB smoke validates bootstrap from zero.

### The first 10 minutes of a migration incident

```text
1. Compare `/health` expected vs `alembic_version`.
2. Check `alembic heads` and `SELECT version_num FROM alembic_version`.
3. Classify the failure as code-only, schema-only, or mixed.
4. If you are still in a backward-compatible expand phase, consider code rollback; otherwise switch to forward-fix.
5. Pin the broken revision ID and draft `fix <broken_revision_id>: <issue>`.
6. After recovery, record which CI gate was missing in the post-mortem.
```

This is not a green-check recap. It is a branching diagnostic order. If step 2 reveals a multi-head, stop deploys and return to graph repair first. If step 3 shows a mixed failure, do not treat it as a code rollback alone until schema compatibility is confirmed.

## Common mistakes

- **Multiple revisions in one PR.** Reviews are hard and partial revert is impossible.
- **Not verifying downgrade in CI.** You only learn it is broken when you have an incident in prod.
- **Forcing PostgreSQL in dev.** Setup cost goes up and quick single-engineer experiments become painful.
- **Verifying only on dev SQLite, going straight to prod.** SQLite/PostgreSQL differences cause incidents at staging.
- **No alembic_version in monitoring.** No way to detect a partially-applied state.

## Production patterns

- **PR template + CI enforcement combined.** Even when humans forget, the system enforces.
- **dev=SQLite, staging+prod=PostgreSQL.** Fast experiments and accuracy at the same time.
- **Forward-fix as the default incident response.** Downgrade only when truly necessary.
- **Include the GitHub issue number in the revision message.** "add users phone column (#1234)".
- **Schema changes during business hours.** Late-night deploys actually leave you without on-call coverage when an incident happens.
- **Always include the schema-change verification flow in the post-mortem.** Look back at what was missing.

## Checklist

- [ ] PR template enforces one PR = one revision
- [ ] CI auto-runs alembic check, upgrade+downgrade, head-count guard, SQL preview, and fresh DB smoke
- [ ] Per-environment split: dev=SQLite, staging+prod=PostgreSQL
- [ ] `/health` response includes alembic_version
- [ ] Forward-fix template and procedure are documented
- [ ] Revision message is an imperative one-liner with issue number

## Exercises

1. Add the PR template and CI workflow above to your project, deliberately introduce a broken downgrade, and confirm CI blocks it.
2. Add alembic_version to your `/health` endpoint, and write a one-line monitoring script that fires an alarm on drift.
3. Pick a hypothetical incident scenario (e.g., a revision that left some rows broken) and write the forward-fix revision.

## Wrap-up and next post

Across ten episodes we covered Alembic from init all the way to a production workflow. The core in one sentence:

> "Schema changes ship before code, with broader compatibility, one PR per revision, downgrade verified in CI, monitoring detects drift, incidents respond with forward-fix."

This series ends here, but in real operations every item above must be automated and locked in via PR templates and CI enforcement. The next learning step is the depth of SQLAlchemy ORM (relationship, query optimization, async).

## Answering the Opening Questions

- **The one-revision-per-PR rule and why it matters?**
  - The article treats Production and team workflow: PR, CI, monitoring, and incident response as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How to compose an Alembic-aware PR template and the matching CI checks?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How to manage multiple environments where dev=SQLite and staging+prod=PostgreSQL?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Alembic 101 (1/10): Why Alembic, and getting to alembic init](./01-why-alembic-and-init.md)
- [Alembic 101 (2/10): env.py and target_metadata: wiring models to migrations](./02-env-py-and-target-metadata.md)
- [Alembic 101 (3/10): Your first revision: writing upgrade and downgrade by hand](./03-first-revision-upgrade-downgrade.md)
- [Alembic 101 (4/10): autogenerate: the line between what it catches and what it misses](./04-autogenerate-and-its-limits.md)
- [Alembic 101 (5/10): branches and merges: combining revisions made in parallel](./05-branches-and-merges.md)
- [Alembic 101 (6/10): Data migrations: separating schema changes from data changes](./06-data-migrations.md)
- [Alembic 101 (7/10): Online and offline modes: previewing DDL with --sql and handling SQLite batch](./07-online-vs-offline-and-batch.md)
- [Alembic 101 (8/10): Downgrade strategy: when to write it for real and when to forbid it](./08-downgrade-strategy.md)
- [Alembic 101 (9/10): Deploy ordering and blue/green: synchronizing schema and application code safely](./09-deploy-ordering-and-blue-green.md)
- **Production and team workflow: PR, CI, monitoring, and incident response (current)**

<!-- toc:end -->

## References

- [sqlalchemy/alembic GitHub repository](https://github.com/sqlalchemy/alembic)
- [Alembic: Cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- [Alembic: `alembic check`](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#detecting-changes-in-models)
- [GitHub: PR templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- "Database Reliability Engineering" by Laine Campbell & Charity Majors

Tags: Python, Alembic, SQLAlchemy, Migration
