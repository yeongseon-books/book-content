---
title: 'autogenerate: the line between what it catches and what it misses'
series: alembic-101
episode: 4
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
- autogenerate
- compare_type
- MetaData
- SQLite
last_reviewed: '2026-05-12'
seo_description: Autogenerate is a tool that diffs the live database (ground truth)
  against target_metadata (desired state) and serializes that diff into op calls.
---

# autogenerate: the line between what it catches and what it misses

Autogenerate can diff the live database against `target_metadata`, but it cannot infer your intent. Renames are the classic example: the tool sees structural change, while you still have to judge safety.

This is post 4 in the Alembic 101 series. Here we will separate what autogenerate handles well from the cases that still need a human pass.

## What you will learn

- What `alembic revision --autogenerate` actually compares under the hood
- Which kinds of changes autogenerate handles well, and which it misses
- The `compare_type`, `compare_server_default`, `include_object`, and `include_name` options
- How to handle table and column renames safely
- Why you still need to read the generated file by eye

## Why it matters

Autogenerate is alembic's most powerful feature, but the moment you treat it as a "press a button and you're done" tool, production incidents start. Committing a generated file as-is and watching a column rename get expanded into drop+create — losing the data — is a real, common failure.

The goal of this post is not to make you afraid of autogenerate, but to map its limits precisely so you can patch the parts that need a human touch.

## Mental Model

> Autogenerate is **a tool that diffs the live database (ground truth) against `target_metadata` (desired state)** and serializes that diff into op calls. Anything the diff algorithm cannot see — semantic intent at the data level, identifier renames, DB-specific objects — cannot be detected automatically.

The git diff analogy fits: autogenerate is a line-level diff. A semantically equivalent change (a rename) shows up as two-line delete plus two-line add, with the same blind spot you would expect.

### Diagram: the autogenerate diff pipeline

![Diagram: the autogenerate diff pipeline](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/04/04-01-diagram-the-autogenerate-diff-pipeline.en.png)
*Autogenerate builds a diff, but intent-heavy decisions such as renames still belong to a human review.*

## Core concepts

### How it works

Running `alembic revision --autogenerate -m "..."` does the following in order:

1. `env.py` connects to the database.
2. The current schema is introspected via the SQLAlchemy `Inspector` into a `MetaData`.
3. That introspected metadata is compared against `target_metadata` (usually `Base.metadata`).
4. The differences are turned into a `MigrationOps` tree.
5. The result is rendered as op calls into `versions/<hash>_<msg>.py`.

The key point is that everything up to step 4 is an in-memory diff. What gets caught and what gets missed is fully decided in that diff phase.

### What autogenerate handles well

| Change | Notes |
| --- | --- |
| New table created or dropped | Reliable |
| New column added or dropped | Reliable |
| Index added or dropped | When defined on the `MetaData` |
| Foreign key added or dropped | Basic cases |
| `nullable` change | On by default |

### What it misses (or needs an option for)

| Change | Default | Required setting |
| --- | --- | --- |
| Column type change (e.g., `String(50)` → `String(100)`) | Ignored | `compare_type=True` |
| `server_default` change | Ignored | `compare_server_default=True` |
| `CHECK` constraint | Mostly ignored | DB-dependent |
| **table rename** | Seen as drop + create | Hand-edit to `op.rename_table` |
| **column rename** | Seen as drop + add | Hand-edit to `op.alter_column(... new_column_name=...)` |
| trigger / function / sequence (PostgreSQL) | Ignored | Write by hand |
| Data changes | Ignored (always) | `op.execute` or a data migration |

In particular, **renames** can never be detected automatically. This is the most common cause of data-loss incidents.

### `compare_type` and `compare_server_default`

To detect type and default changes, both options need to go into your `context.configure(...)` call inside `env.py`.

```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=connection.dialect.name == "sqlite",
    compare_type=True,
    compare_server_default=True,
)
```

The reason these default to `False` is that they produce false positives. `String(50)` and `VARCHAR(50)` mean the same thing but show up as different in the diff. Turning them on is generally safer, but be aware that on first enable you may see one or two "why is this here?" revisions.

### `include_object` and `include_name`

Use these when you want to exclude certain tables or schemas from the diff.

```python
def include_object(object, name, type_, reflected, compare_to):
    # Skip audit tables managed by an external system
    if type_ == "table" and name.startswith("legacy_"):
        return False
    return True

context.configure(
    connection=connection,
    target_metadata=target_metadata,
    include_object=include_object,
)
```

This is useful in multi-tenant setups, when another team owns some tables, or when there are temporary tables you do not want in your diff.

## Before-After

```python
# Before: column rename misread as drop + add
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100)))
    op.drop_column("users", "name")  # ← data loss!

def downgrade() -> None:
    op.add_column("users", sa.Column("name", sa.String(100)))
    op.drop_column("users", "display_name")
```

```python
# After: hand-edited to a real rename
def upgrade() -> None:
    op.alter_column("users", "name", new_column_name="display_name")

def downgrade() -> None:
    op.alter_column("users", "display_name", new_column_name="name")
```

The After version preserves the data. This is the single biggest reason to read every autogenerate result before you commit it.

## Step-by-step walkthrough

### Step 1: change a model

```python
# models.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    tier: Mapped[str] = mapped_column(String(16), server_default="free")  # ← new
```

### Step 2: run autogenerate

```bash
alembic revision --autogenerate -m "add users.tier"
```

### Step 3: review the generated file

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(length=16), server_default="free", nullable=False))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

Something this simple is safe to commit as-is. But if a type change or rename is mixed in, you always need to fix it by hand.

### Step 4: a change that needs a rename

If you rename the model column from `name` to `display_name` and run autogenerate, you get the Before snippet above — drop + add. Fix it by hand:

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("name", new_column_name="display_name")

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.alter_column("display_name", new_column_name="name")
```

On SQLite, batch mode is required (see episode 3).

### Step 5: exclude what should not be diffed

If your test environment has a temporary table that someone made by hand, use `include_object` to keep it out of every diff.

## Verification routine

```bash
alembic revision --autogenerate -m "rename probe"
python3 - <<'PY'
from pathlib import Path
latest = sorted(Path("alembic/versions").glob("*_rename_probe.py"))[-1]
print(latest.read_text())
PY
```

**Expected output:** intent-heavy changes such as renames usually show up as `drop_column` + `add_column`. That is the signal that the generated file still needs a human patch.

## Common mistakes

- **Committing autogenerate output as-is.** The most common cause of incidents. Always read it like a git diff and fix anything suspicious by hand.
- **Renaming by changing the model and trusting autogenerate.** It expands to drop + add and your data is gone.
- **Changing types without `compare_type`.** The revision is empty while the schema actually drifts.
- **Missing `server_default` changes.** You need `compare_server_default=True`.
- **Catching another team's tables.** Isolate them with `include_object`.

## Practical patterns

- **PR diff review checklist.** "Is any rename expanded into drop+add?" and "Is any type change missing?" are non-negotiable items.
- **Run with `compare_type` and `compare_server_default` on.** Accept the false positives in the first one or two revisions in exchange for ongoing safety.
- **For large changes, take the autogenerate result as a draft, then write the final revision by hand.** Keep the auto output open beside you for reference.
- **Isolate library-owned tables.** Celery, APScheduler, and similar third-party tables go into `include_object` exclusions or a separate metadata.
- **Run `alembic check` in CI.** It detects when the model and migrations have drifted (alembic 1.9+).

## Checklist

- [ ] Read the generated file line by line and patched anything suspicious
- [ ] No rename expanded into drop + add
- [ ] `compare_type=True` and `compare_server_default=True` are on
- [ ] Tables owned by other teams or libraries are excluded via `include_object`
- [ ] Large changes follow the "empty revision, write by hand" policy
- [ ] CI runs `alembic check` (1.9+)

## Exercises

1. Add a `bio` column to the `User` model, run autogenerate, and decide whether the result is safe to commit as-is.
2. Rename the `name` column to `display_name`, then fix the broken autogenerate output by hand.
3. Change the `users.tier` default from `"free"` to `"basic"` and compare the autogenerate output with `compare_server_default` off vs on.

## Wrap up, next post

Autogenerate is highly efficient when used well, but ignoring its limits leads directly to data loss. Keep the "it makes a diff" mental model in your head and build the habit of reading every result with human eyes.

The next post covers the branches that appear when several people generate revisions concurrently, and how to consolidate them with `alembic merge`.

<!-- toc:begin -->
## In this series

- [Why Alembic, and getting to alembic init](./01-why-alembic-and-init.md)
- [env.py and target_metadata: wiring models to migrations](./02-env-py-and-target-metadata.md)
- [Your first revision: writing upgrade and downgrade by hand](./03-first-revision-upgrade-downgrade.md)
- **autogenerate: the line between what it catches and what it misses (current)**
- branches and merges: combining revisions made in parallel (upcoming)
- Data migrations: separating schema changes from data changes (upcoming)
- Online and offline modes: previewing DDL with --sql and handling SQLite batch (upcoming)
- Downgrade strategy: when to write it for real and when to forbid it (upcoming)
- Deploy ordering and blue/green: synchronizing schema and application code safely (upcoming)
- Production and team workflow: PR, CI, monitoring, and incident response (upcoming)

<!-- toc:end -->

## References

- [sqlalchemy/alembic GitHub repository](https://github.com/sqlalchemy/alembic)
- [Alembic: Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Alembic: Comparing Types](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#comparing-types)
- [Alembic: Comparing Server Defaults](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#comparing-server-defaults)
- [Alembic: Limitations of Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)

Tags: Python, Alembic, SQLAlchemy, Migration
