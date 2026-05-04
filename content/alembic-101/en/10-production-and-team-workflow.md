---
title: 'Production and team workflow: PR, CI, monitoring, and incident response'
series: alembic-101
episode: 10
language: en
status: publish-ready
targets:
  tistory: true
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
last_reviewed: '2026-05-03'
seo_description: A migration is "the most irreversible kind of code change". Ordinary
  code can be reverted with a single click; a schema change carries data with it…
---

# Production and team workflow: PR, CI, monitoring, and incident response

## What you will learn

- The one-revision-per-PR rule and why it matters
- How to compose an Alembic-aware PR template and the matching CI checks
- How to manage multiple environments where dev=SQLite and staging+prod=PostgreSQL
- A monitoring pattern that detects schema drift in production
- The forward-fix procedure when a migration causes an incident

## Why this matters

Everything in the previous nine posts described how a single engineer can apply migrations safely in their own environment. Once a team starts changing the schema concurrently, a different class of problems appears. Two people creating a new revision at the same time produce a multi-head; if no one tests downgrade, rollback breaks; if production schema starts drifting, you have no idea where to start. Operational stability comes from workflow quality, not from code quality.

## Mental Model

> A migration is **"the most irreversible kind of code change"**. Ordinary code can be reverted with a single click; a schema change carries data with it and is very hard to undo. So you must treat it more strictly than ordinary code at the PR stage.

The starting point of the operational workflow is: one PR equals one revision, and that revision's upgrade and downgrade are both verified.

## Core concepts

### One revision per PR

Bundling several schema changes into one PR creates two problems.

- The reviewer must understand all changes at once → higher incident probability
- If only one change is wrong, you cannot revert just that part → you must revert all of them together

When each revision is its own PR, reviews are simpler and the blast radius on failure is smaller. Expand-contract also decomposes naturally into per-phase PRs.

### CI check items

```text
1. python3 -m pytest                                    # unit tests
2. alembic check                                        # model vs schema drift
3. alembic upgrade head && alembic downgrade -1         # downgrade verification
4. alembic upgrade head --sql                           # SQL preview, attached as PR artifact
5. python3 scripts/check_alembic_heads.py               # confirm head count = 1
6. python3 scripts/migrate_smoke_test.py                # apply migrations to a fresh DB
```

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
1. Detect the incident (alarm, error rate, /health version mismatch)
2. Classify the cause:
   - code issue → code rollback (leave schema as is; safe if you are in expand phase)
   - schema issue → write a forward-fix revision
3. forward-fix revision: "fix <broken_revision_id>: <issue>"
4. After recovery, post-mortem investigates which verification step was missing for the broken revision
```

A forward-fix adds a new revision that brings the broken state back to a valid one. Unlike downgrade, the alembic_version graph stays moving forward, which gives better traceability and is compatible with blue/green.

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

Keeping PRs small and forcing downgrade verification in CI removes about half of all incidents.

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
    alembic upgrade head
    alembic downgrade -1
    alembic upgrade head
- name: head count guard
  run: |
    HEADS=$(alembic heads | wc -l)
    [ "$HEADS" = "1" ] || (echo "multi-head detected"; exit 1)
- name: SQL preview
  run: alembic upgrade head --sql > migration_preview.sql
- uses: actions/upload-artifact@v4
  with:
    name: migration-preview
    path: migration_preview.sql
```

This single job blocks multi-head, broken downgrade, and missing revisions.

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
- [ ] CI auto-runs alembic check, upgrade+downgrade, head-count guard, and SQL preview
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

## References

- Alembic: Cookbook — https://alembic.sqlalchemy.org/en/latest/cookbook.html
- Alembic: `alembic check` — https://alembic.sqlalchemy.org/en/latest/autogenerate.html#detecting-changes-in-models
- GitHub: PR templates — https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
- "Database Reliability Engineering" by Laine Campbell & Charity Majors

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, Production, CI, workflow, SQLite
