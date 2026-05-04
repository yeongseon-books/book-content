---
title: 'Online and offline modes: previewing DDL with --sql and handling SQLite batch'
series: alembic-101
episode: 7
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
- online
- offline
- batch
- SQLite
last_reviewed: '2026-05-03'
seo_description: Alembic runs in two modes. Online connects to the database and runs
  SQL directly.
---

# Online and offline modes: previewing DDL with --sql and handling SQLite batch

## What you will learn

- The two execution modes alembic offers — online and offline
- How to preview the actual SQL with `--sql`
- A workflow for producing SQL scripts that a DBA can review
- The limits of `ALTER TABLE` on SQLite and what `batch_alter_table` does internally
- Patterns to avoid when running in offline mode

## Why it matters

There are times before a production deploy when you want to see exactly what SQL a migration will run — when an external DBA needs to review it, or when the impact is so large that PR review alone is not reassuring. Alembic's offline mode is the tool for that.

SQLite also has very restricted `ALTER TABLE` support, so every alembic user eventually has to learn batch mode. The two topics are best learned together.

## Mental Model

> Alembic runs in two modes. **Online connects to the database and runs SQL directly. Offline emits the SQL text to standard output without a database connection.** Offline is for dry-run, review, and scripting. Online is for actual application.

Turning on `render_as_batch` makes calls like `op.alter_column` expand internally — for SQLite — into "create a temporary table, INSERT SELECT, swap names." Batch mode is alembic's safety net for SQLite.

## Core concepts

### Online vs offline

| Mode | DB connection | Output | Use case |
| --- | --- | --- | --- |
| online (default) | Required | Application log | Apply migration |
| offline (`--sql`) | Not needed | SQL text (stdout) | Review, scripting, dry-run |

```bash
# online (apply)
alembic upgrade head

# offline (SQL only)
alembic upgrade head --sql > migration.sql

# only a specific span
alembic upgrade <from>:<to> --sql > step.sql
```

The `<from>:<to>` syntax is the key. `head` alone means `None:head`, which prints SQL from the very beginning to the head. To skip what is already applied, write `<current>:<target>` explicitly.

### Constraints of offline mode

Without a DB, the following do not work in offline mode:

- `op.get_bind()` (no connection)
- Data verification queries
- Helpers that use introspection
- Conditional logic (branching based on row counts, etc.)

Therefore data migrations do not produce meaningful SQL in offline mode. The standard practice is to use offline mode for schema migrations only.

### `--sql` review workflow

```bash
# 1) attach an SQL preview to the PR
alembic upgrade <prev>:head --sql > review.sql
git add review.sql && git commit -m "ddl preview"

# 2) DBA reviews review.sql

# 3) production deploy uses online as usual
alembic upgrade head
```

This is a common flow in large operations. With SQL attached to the PR, reviewers can evaluate impact based on real SQL rather than op calls.

### SQLite and batch mode

SQLite supports only the following `ALTER TABLE` operations:

- `RENAME TABLE`
- `RENAME COLUMN` (3.25+)
- `ADD COLUMN`
- `DROP COLUMN` (3.35+)

That means type changes, nullable changes, default changes, and FK additions/removals cannot be done with a direct `ALTER`. Alembic's `batch_alter_table` expands them automatically:

```sql
CREATE TABLE _alembic_tmp_users (...);   -- temp table with the new schema
INSERT INTO _alembic_tmp_users SELECT ... FROM users;
DROP TABLE users;
ALTER TABLE _alembic_tmp_users RENAME TO users;
-- recreate the original indexes/triggers
```

This entire process happens inside one transaction so it is safe, but it takes time on large tables.

### Automating `render_as_batch`

In `env.py`, enable batch mode automatically only on SQLite.

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=connection.dialect.name == "sqlite",
)
```

Even with this option on, the explicit `with op.batch_alter_table(...)` context is still recommended. It makes intent clearer and lets you bundle multiple alters into one batch.

## Before-After

```sql
-- Before: applied to production without looking at the SQL
-- Result: column type changed without dropping the index, query performance regresses
```

```bash
# After: previewed with --sql
$ alembic upgrade <prev>:head --sql

BEGIN;
-- Running upgrade abc123 -> def456, change users.tier type
DROP INDEX ix_users_tier;
ALTER TABLE users ALTER COLUMN tier TYPE VARCHAR(64);
CREATE INDEX ix_users_tier ON users (tier);
COMMIT;
```

If this SQL had been on the PR, the reviewer could have evaluated the cost of "drop and rebuild the index." That is the value of the dry-run workflow.

## Step-by-step walkthrough

### Step 1: emit offline SQL

```bash
alembic upgrade head --sql > preview.sql
cat preview.sql
```

On first use, you will notice it includes `BEGIN;` ... `COMMIT;` blocks and the `INSERT INTO alembic_version` statements as well.

### Step 2: only a specific revision span

```bash
alembic upgrade abc123:def456 --sql > step.sql
```

Use this when production is already on `abc123` and you want to advance to `def456`.

### Step 3: apply SQLite batch

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("tier",
                           existing_type=sa.String(16),
                           type_=sa.String(64))
        batch.create_index("ix_users_tier", ["tier"])
```

Bundling multiple changes in one batch means the temp-table create-and-copy happens once.

### Step 4: identify ops that do not work offline

```python
def upgrade() -> None:
    bind = op.get_bind()                  # None in offline mode
    if bind:                              # add a guard
        bind.execute(text("UPDATE ..."))
```

Or split data migrations into separate revisions and only preview the schema-only revisions in offline mode.

### Step 5: add `--sql` dry-run to CI

```yaml
- run: alembic upgrade head --sql > /tmp/preview.sql && cat /tmp/preview.sql
```

This single line effectively prints the SQL on every PR.

## Common mistakes

- **Running `--sql head` and being surprised that everything from the start prints out.** Learn the `<from>:<to>` form.
- **Expecting data migration SQL in offline mode.** Offline produces meaningful output mainly for schema changes.
- **`ALTER` on SQLite without batch.** Fails with "no such function ALTER" or "syntax error."
- **Ignoring the temp-table cost in batch mode.** For tables with millions of rows, the schema add → data backfill → schema tighten pattern (episode 6) is safer.
- **Trusting `render_as_batch=True` and skipping the explicit batch context.** Intent becomes muddled, and you lose the per-batch bundling effect.

## Practical patterns

- **Attach `--sql` previews to PRs.** Standard for environments where DBA review is required.
- **Auto-print the dry-run from CI.** Reduces reviewer effort.
- **Always write SQLite schema changes inside a batch context.** Makes the difference from PostgreSQL behavior explicit.
- **Production deploys use online + transaction.** Hand-running an offline SQL file is not recommended (transaction-boundary and `alembic_version` sync risks).
- **Alias `alembic upgrade <prev>:head --sql` to `make ddl-preview`.** Standardize as a single command.

## Checklist

- [ ] `--sql` is invoked with `<from>:<to>` syntax
- [ ] Data migration output is not expected in offline mode
- [ ] SQLite `ALTER` changes always run inside a `batch_alter_table` context
- [ ] An SQL preview is attached to PRs or auto-printed from CI
- [ ] Production deploys go through online (no manual offline SQL execution)

## Exercises

1. Make any schema change and run `alembic upgrade head --sql > out.sql`; inspect the output structure.
2. On SQLite, try to change a column type with `op.alter_column` outside a batch context and observe the error.
3. Use the `<prev>:<head>` syntax to extract only the SQL for the last single step.

## Wrap up, next post

Online for application, offline for review. The division of labor between the two modes increases safety in operations. On SQLite, build the habit of always using batch mode explicitly.

The next post is downgrade strategy: when to seriously write a downgrade and when to deliberately forbid it.

## References

- Alembic: Generating SQL Scripts (Offline Mode) — https://alembic.sqlalchemy.org/en/latest/offline.html
- Alembic: Running Batch Migrations for SQLite and Other Databases — https://alembic.sqlalchemy.org/en/latest/batch.html
- SQLite: ALTER TABLE — https://www.sqlite.org/lang_altertable.html
- Alembic: Operation Reference — https://alembic.sqlalchemy.org/en/latest/ops.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, online, offline, batch, SQLite
