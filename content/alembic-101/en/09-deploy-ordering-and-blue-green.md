---
title: 'Deploy ordering and blue/green: synchronizing schema and application code
  safely'
series: alembic-101
episode: 9
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
- deploy
- blue-green
- ordering
- SQLite
last_reviewed: '2026-05-03'
seo_description: A migration always ships "before the code, and with broader compatibility
  than the code".
---

# Deploy ordering and blue/green: synchronizing schema and application code safely

## What you will learn

- The difference between migration-first and code-first deploy ordering
- Why a blue/green deploy requires schema changes that are compatible with two app versions at once
- How to split a NOT NULL tightening into two phases via expand-contract
- The four-phase pattern for a column rename
- How to run a migration exactly once across many application instances

## Why this matters

Most production schema incidents are caused by code and schema being deployed in the wrong order. If a new column exists before the code that uses it, you are safe. If the code starts using a new column before the schema catches up, you get an immediate 500. In a blue/green deploy two app versions hit the same database at the same time, so the schema must always be compatible with both.

## Mental Model

> A migration always ships **"before the code, and with broader compatibility than the code"**. When you add a column the column exists first; when you drop a column the code stops using it first. Memorize those two directions and most deploy incidents disappear.

If git is your analogy, a migration is a PR that lands earlier than the code PR, and a drop is a PR that lands later than the "stop using" PR.

## Core concepts

### migration-first vs code-first

| Change kind | Deploy order | Reason |
| --- | --- | --- |
| **Add column / table** | migration → code | The column must already exist before the code can use it |
| **Drop column / table** | code → migration | Drop only after the code stops using it |
| **Type widen** (`String(50)` → `String(100)`) | migration → code | Bigger storage must be available before code writes wider values |
| **Type narrow** | code → migration | Narrow only after code starts writing smaller values |

The key rule is that the previous version of the code must keep working during the transition. That is the basic assumption of blue/green and rolling deploys.

### Schema compatibility requirement under blue/green

```text
t0: only blue (v1) running, schema=S1
t1: migrate schema to S2 (S1, S2 both compatible with v1)
t2: bring up green (v2); blue (v1) and green (v2) run concurrently (both work with S2)
t3: shut down blue, only green runs
t4 (next deploy): migrate schema to S3 (now safe to drop S2 compatibility)
```

The schema change at t1 must be compatible with both v1 and v2. This is exactly why expand-contract is mandatory.

### NOT NULL tightening as two phases

Bundling `nullable=False` into a single revision is an immediate incident under blue/green. Split it into two phases.

```text
phase 1 (now):
  - DB: add column as nullable=True with a default
  - code: always writes a value into the new column
  - deploy: migration → code

(time passes; verify every row has a value)

phase 2 (next deploy):
  - DB: tighten column to nullable=False
  - code: unchanged
  - deploy: migration only
```

The interval between phases can be short or long, but you only apply phase 2 after you have proved that no row is still NULL.

### Four phases for a column rename

```text
phase 1: add new column (nullable=True); code keeps using the old column
phase 2: code dual-writes (writes both old and new)
phase 3: backfill data; code reads and writes only the new column
phase 4: drop the old column (code already stopped using it)
```

Each phase is its own PR, and you confirm production stability between phases. It takes time, but it is the safest pattern available.

### Running once across many instances

If every application instance runs `alembic upgrade` you create a race condition. Alembic itself takes a lock on the `alembic_version` table, but a safer approach is one of the following.

- **Have the deploy script call it exactly once**: run the migration in a separate stage before any application instance starts
- **Kubernetes Job / initContainer**: run the migration in a dedicated Job before the application containers start
- **Split the CI/CD pipeline**: place a `migrate` stage before the `deploy` stage

Calling `alembic upgrade head` at application startup is fine for single-instance dev, but is not recommended in production.

## Before-After

```text
# Before: code-first deploy, immediate 500 errors
1. deploy v2 (code that uses the new column)
2. every request fails with "no such column"
3. 30 minutes later, schema migrate
```

```text
# After: migration-first deploy
1. schema migrate (add new column as nullable=True)
2. v1 instances keep running normally (they ignore the new column)
3. deploy v2 (code that uses the new column)
4. blue/green both work correctly
```

The After pattern has a zero-incident window. Enforcing this order on every deploy is the operational baseline.

## Step-by-step walkthrough

### Step 1: schema add

```python
# revision: add_users_phone
def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "phone")
```

Apply via CI first. Application code does not yet touch `phone`. Both v1 and v2 keep running.

### Step 2: code deploy

Application code starts writing values into `phone`. During the blue/green overlap v1 ignores the column and v2 fills it in. Both are safe.

### Step 3: tighten to NOT NULL

Verify that every row has `phone` populated.

```python
# revision: tighten_users_phone_not_null
def upgrade() -> None:
    bind = op.get_bind()
    null_count = bind.execute(text("SELECT COUNT(*) FROM users WHERE phone IS NULL")).scalar()
    assert null_count == 0, f"{null_count} rows still NULL"
    with op.batch_alter_table("users") as batch:
        batch.alter_column("phone", existing_type=sa.String(20), nullable=False)

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("phone", existing_type=sa.String(20), nullable=True)
```

The assertion is your safety net. If any NULL is left, the migration fails and the schema is unchanged.

### Step 4: drop the old column

When you want to remove an old column, confirm that the application no longer uses it, then apply the drop revision in the next deploy cycle.

```python
def upgrade() -> None:
    op.drop_column("users", "old_phone")

def downgrade() -> None:
    raise NotImplementedError("drop is irreversible")
```

### Step 5: align the deploy pipeline

```yaml
# CI/CD
stages:
  - test
  - migrate     # alembic upgrade head
  - deploy      # rolling update
  - smoke-test
```

Force `migrate` to always run before `deploy`.

## Common mistakes

- **Code-first deploy.** If the code assumes the new schema first, you fail immediately.
- **Bundling NOT NULL into one revision.** The moment v1 writes a NULL under blue/green, you fail.
- **Dropping immediately.** Dropping right after the code stops using a column is dangerous; wait one deploy cycle.
- **Calling `alembic upgrade head` at application startup.** Race conditions and partial application risk under multi-instance.
- **Renaming in a single phase.** It decomposes into drop+add and you lose data; the four-phase dual-write pattern is mandatory.

## Production patterns

- **Split CI stages: `migrate` before `deploy`.** The simplest and most effective rule.
- **NOT NULL tightening always in two phases.** Insert a data verification migration in between.
- **Drop is delayed by one deploy cycle.** Never drop immediately.
- **Kubernetes initContainer pattern.** Use a Job to guarantee exactly-once execution.
- **`alembic check` before deploy.** Auto-detects model/schema drift.
- **Make expand-contract phase part of the PR template.** Force "which phase is this" to be explicit.

## Checklist

- [ ] Every schema add ships before the code deploy
- [ ] Every schema drop ships in the deploy cycle after the code stops using it
- [ ] NOT NULL tightenings are split into two phases
- [ ] Renames follow the four-phase dual-write pattern
- [ ] Application startup does not call `alembic upgrade`
- [ ] CI/CD has `migrate` before `deploy`
- [ ] Under Kubernetes, an initContainer or Job guarantees exactly-once execution

## Exercises

1. Simulate the add-column → code-deploy → NOT NULL tightening flow on SQLite end to end.
2. Write a column rename as a four-phase dual-write and draw the per-phase PR sequence.
3. Split your CI/CD pipeline so that a `migrate` stage always precedes the `deploy` stage.

## Wrap-up and next post

Deploy ordering is an operations policy concern, not an Alembic feature. Keep the one-liner "schema first, broader compatibility" in your head and decompose every change against that rule. In blue/green, the critical point is that the schema is compatible with both versions at once.

The next post covers real team workflows: PR conventions, CI checks, and operational automation.

## References

- Alembic: Cookbook — https://alembic.sqlalchemy.org/en/latest/cookbook.html
- Martin Fowler: Blue Green Deployment — https://martinfowler.com/bliki/BlueGreenDeployment.html
- "Refactoring Databases" by Scott Ambler & Pramod Sadalage
- Kubernetes: Init Containers — https://kubernetes.io/docs/concepts/workloads/pods/init-containers/

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, deploy, blue-green, ordering, SQLite
