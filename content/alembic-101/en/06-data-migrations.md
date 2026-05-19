---
title: 'Data migrations: separating schema changes from data changes'
series: alembic-101
episode: 6
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
- data-migration
- op.execute
- batch
- SQLite
last_reviewed: '2026-05-12'
seo_description: A data migration is a revision that leaves the schema alone and transforms
  rows.
---

# Data migrations: separating schema changes from data changes

Data migrations are often slower and more irreversible than the schema changes around them. How you isolate row transformation work inside revisions determines lock time, retry behavior, and recovery difficulty.

This is post 6 in the Alembic 101 series. Here we will focus on why schema changes and data changes should be split, and what safe execution patterns look like.

## What you will learn

- How a "data migration" is different from a schema migration
- Two writing styles for `op.execute` — raw SQL and SQLAlchemy core
- A pattern for splitting a large dataset into batches
- Why schema-only and data-only revisions should be separated
- How to ensure idempotency and safe re-execution

## Why it matters

`ALTER TABLE` is not the only kind of migration. Column renames, enum value changes, JSON structure conversions — these all change the data alongside the schema. If you mix a data migration into the same revision as a schema change, large datasets cause lock issues and timeouts, and `downgrade` becomes effectively impossible.

## Mental Model

> A data migration is **a revision that leaves the schema alone and transforms rows**. Separating it from schema-only revisions lets you (1) split a giant transaction into smaller batches, (2) preserve the schema part and re-run only the data part on failure, and (3) make the intent obvious to reviewers.

To borrow a git analogy: schema changes are code refactors, and data changes are database migration scripts. Mixing both into one commit clouds the history.

### Diagram: the three-stage split for data migrations

![Diagram: the three-stage split for data migrations](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/06/06-01-diagram-the-three-stage-split-for-data-m.en.png)
*Isolating row transformation in the middle stage keeps long-running work separate from short schema changes.*

## Core concepts

### Two styles of `op.execute`

**Raw SQL**

```python
def upgrade() -> None:
    op.execute("UPDATE users SET tier = 'free' WHERE tier IS NULL")
```

Fast and simple, but dialect-bound and your IDE cannot help much.

**SQLAlchemy core**

```python
from sqlalchemy import table, column, String

def upgrade() -> None:
    users = table("users", column("tier", String))
    op.execute(
        users.update()
        .where(users.c.tier.is_(None))
        .values(tier="free")
    )
```

A bit longer but dialect-agnostic, and safer when the transformation logic is complex. **Important**: do not import models from `Base.metadata` inside migrations. If a model changes in the future, an old migration will break. Use `table()` / `column()` to declare an inline schema that captures the schema as it was at that moment.

### Batched processing

A single `UPDATE` over millions of rows blows up locks and the transaction log. SQLite hits concurrency issues, while PostgreSQL and MySQL block other transactions.

```python
def upgrade() -> None:
    bind = op.get_bind()
    batch_size = 1000
    while True:
        result = bind.execute(text(
            "UPDATE users SET tier = 'free' "
            "WHERE id IN (SELECT id FROM users WHERE tier IS NULL LIMIT :n)"
        ), {"n": batch_size})
        if result.rowcount == 0:
            break
```

If you also commit explicitly inside the loop, it gets even safer. SQLite is single-writer, so the time a large transaction blocks other work shrinks.

### Splitting schema and data revisions

The standard form is three steps:

1. **schema add**: add the new column or table with `nullable=True` (fast).
2. **data backfill**: a data migration that fills existing rows (slow, batched).
3. **schema tighten**: enforce `nullable=False`, drop the default, etc. (fast).

Each step is its own revision and the deploys are decoupled. Episode 9 formalizes this as the expand-contract pattern.

## Before-After

```python
# Before: schema and data bundled into one revision and timing out
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))
    # 100M-row UPDATE — lock + transaction log explosion
    op.execute("UPDATE users SET tier = 'paid' WHERE last_payment_at IS NOT NULL")
    op.alter_column("users", "tier", server_default=None)
```

```python
# After: split into three revisions
# revision 1: schema add (nullable=True)
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=True))

# revision 2: data backfill (batch loop)
def upgrade() -> None:
    bind = op.get_bind()
    while True:
        result = bind.execute(text(
            "UPDATE users SET tier = CASE "
            "  WHEN last_payment_at IS NOT NULL THEN 'paid' ELSE 'free' END "
            "WHERE id IN (SELECT id FROM users WHERE tier IS NULL LIMIT 1000)"
        ))
        if result.rowcount == 0:
            break

# revision 3: schema tighten
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier", existing_type=sa.String(16), nullable=False)
```

The After version finishes each step quickly and moves on. Even if revision 2 takes a long time, the other steps are unaffected.

## Step-by-step walkthrough

### Step 1: add the schema

```bash
alembic revision -m "add users.tier (nullable)"
```

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

### Step 2: data backfill revision

```bash
alembic revision -m "backfill users.tier"
```

```python
from sqlalchemy import text

def upgrade() -> None:
    bind = op.get_bind()
    batch = 1000
    while True:
        result = bind.execute(text(
            "UPDATE users SET tier = 'free' "
            "WHERE id IN (SELECT id FROM users WHERE tier IS NULL LIMIT :n)"
        ), {"n": batch})
        if result.rowcount == 0:
            break

def downgrade() -> None:
    pass  # data migrations usually do not roll back (raise NotImplementedError is also fine)
```

### Step 3: tighten the schema

```bash
alembic revision -m "tighten users.tier NOT NULL"
```

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier", existing_type=sa.String(16), nullable=False)

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier", existing_type=sa.String(16), nullable=True)
```

### Step 4: ensure idempotency

Write the migration so that if it fails partway through and is re-run, nothing breaks.

```python
op.execute("UPDATE users SET tier = 'free' WHERE tier IS NULL")  # idempotent
op.execute("UPDATE users SET counter = counter + 1")              # non-idempotent (dangerous)
```

Use a `WHERE` clause to exclude rows that have already been processed.

### Step 5: verification query

```python
def upgrade() -> None:
    bind = op.get_bind()
    # ... backfill work ...
    remaining = bind.execute(text("SELECT COUNT(*) FROM users WHERE tier IS NULL")).scalar()
    assert remaining == 0, f"backfill incomplete: {remaining} rows remain"
```

An assertion validates backfill completeness. On failure, the transaction rolls back and the schema-tighten step never runs.

## Verification routine

```bash
alembic upgrade head
sqlite3 app.db "SELECT COUNT(*) FROM users WHERE tier IS NULL;"
```

**Expected output:** the NULL row count is zero before you ship the tighten revision. If it is not zero, the backfill is incomplete.

## Common mistakes

- **Bundling schema and data into one revision.** The leading cause of timeouts and lock incidents on large datasets.
- **Importing models inside the migration.** When the model changes in the future, the old revision breaks. Use inline `table()` / `column()` instead.
- **`UPDATE` over the entire table without batching.** Transactions explode at millions of rows.
- **Ignoring idempotency.** Non-idempotent code that processes the same row twice on re-run is dangerous.
- **Writing a serious `downgrade` for a data migration.** Data is generally a one-way commit. `pass` or `raise NotImplementedError` is honest.

## Practical patterns

- **Three-stage split: schema / data / tighten.** The standard expand-contract pattern (episode 9).
- **Use `op.get_bind()` to grab a connection and use SQLAlchemy core.** High portability.
- **Inline schema (`table` / `column`) to freeze the moment.** Cuts the dependency on the live model.
- **Batch loop with explicit commits.** Safe across SQLite, PostgreSQL, and MySQL.
- **Finish with a verification query.** A single assertion prevents production incidents.
- **Dry-run data migrations in CI.** Run the batch loop on a small dataset and confirm it terminates cleanly.

## Checklist

- [ ] Schema and data migrations are split into separate revisions
- [ ] No model imports — inline `table()` / `column()` is used instead
- [ ] Large `UPDATE` statements run in a batch loop
- [ ] A `WHERE` clause makes the operation idempotent
- [ ] An assertion verifies backfill completeness
- [ ] The data migration's `downgrade` is intentionally empty or raises `NotImplementedError`

## Exercises

1. Add a `display_name` column to `users`, backfill from `name`, and drop `name` in a separate revision. Three-stage migration.
2. Generate one million fake rows and measure how long the batch loop takes.
3. Force the backfill assertion to fail and confirm the transaction rolls back as expected.

## Wrap up, next post

The standard form for data migrations is to split them out as separate revisions from schema changes. Batch loops, idempotency, and verification assertions are the three core tools.

The next post goes deep on `--sql` for offline DDL and the SQLite-specific batch mode — the online vs offline DDL story.

<!-- toc:begin -->
## In this series

- [Why Alembic, and getting to alembic init](./01-why-alembic-and-init.md)
- [env.py and target_metadata: wiring models to migrations](./02-env-py-and-target-metadata.md)
- [Your first revision: writing upgrade and downgrade by hand](./03-first-revision-upgrade-downgrade.md)
- [autogenerate: the line between what it catches and what it misses](./04-autogenerate-and-its-limits.md)
- [branches and merges: combining revisions made in parallel](./05-branches-and-merges.md)
- **Data migrations: separating schema changes from data changes (current)**
- Online and offline modes: previewing DDL with --sql and handling SQLite batch (upcoming)
- Downgrade strategy: when to write it for real and when to forbid it (upcoming)
- Deploy ordering and blue/green: synchronizing schema and application code safely (upcoming)
- Production and team workflow: PR, CI, monitoring, and incident response (upcoming)

<!-- toc:end -->

## References

- [sqlalchemy/alembic GitHub repository](https://github.com/sqlalchemy/alembic)
- [Alembic: Operation Reference (`op.execute`)](https://alembic.sqlalchemy.org/en/latest/ops.html#alembic.operations.Operations.execute)
- [Alembic: Run Code at Migration Time](https://alembic.sqlalchemy.org/en/latest/cookbook.html#run-arbitrary-python-during-migrations)
- [SQLAlchemy: SQL Expression Language Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/index.html)
- [Alembic: Working With Custom Types and Data](https://alembic.sqlalchemy.org/en/latest/cookbook.html)

Tags: Python, Alembic, SQLAlchemy, Migration
