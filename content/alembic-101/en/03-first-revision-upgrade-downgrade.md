---
title: 'Your first revision: writing upgrade and downgrade by hand'
series: alembic-101
episode: 3
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
- revision
- upgrade
- downgrade
- SQLite
last_reviewed: '2026-05-03'
seo_description: 'A revision file is a pair of functions: upgrade(): N → N+1 and downgrade():
  N+1 → N.'
---

# Your first revision: writing upgrade and downgrade by hand

## What you will learn

- The shape of the file that `alembic revision` generates
- The core operations: `op.create_table`, `op.add_column`, `op.drop_column`, `op.execute`
- Rules for keeping `upgrade()` and `downgrade()` symmetric
- How the revision graph (`down_revision`) gets formed
- The explicit batch-mode pattern for SQLite

## Why it matters

No matter how good autogenerate is, what it produces in the end is a combination of the same `op` calls. There is a real difference between someone who has written one of these by hand and someone who has not. The difference is whether you can read an auto-generated file and say "this part is not what I intended."

There is one more reason. Writing a real `downgrade` is what keeps production safe. You can have a policy that says "we never downgrade in production," but the moment you leave `downgrade` empty, you also lose your fastest way to roll back a bad migration that slipped through.

## Mental Model

> A revision file is **a pair of functions: `upgrade(): N → N+1` and `downgrade(): N+1 → N`**. If the two are exact inverses of each other, alembic can move freely up and down the graph. If either side is asymmetric, that revision is effectively a one-way commit.

To use a git analogy, `upgrade` is the commit and `downgrade` is its precise revert. A good commit is one that reverts cleanly; a good revision is one whose downgrade is precise.

## Core concepts

### The auto-generated revision file

```python
"""add users.tier

Revision ID: 3f9c8b21de7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-05-03 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "3f9c8b21de7a"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("users", sa.Column("tier", sa.String(16), nullable=False, server_default="free"))

def downgrade() -> None:
    op.drop_column("users", "tier")
```

Read top to bottom and you get (1) this revision's ID and its parent's ID, and (2) the `upgrade`/`downgrade` pair. That is the entire file. We cover `branch_labels` and `depends_on` in episode 5.

### The `op` module

`op` is the DDL helper that alembic exposes. The ones you reach for most often:

| Operation | Purpose |
| --- | --- |
| `op.create_table(name, *columns)` | Create a table |
| `op.drop_table(name)` | Drop a table |
| `op.add_column(table, column)` | Add a column |
| `op.drop_column(table, name)` | Drop a column |
| `op.alter_column(table, name, ...)` | Change type / nullable / default |
| `op.create_index(name, table, cols)` | Create an index |
| `op.drop_index(name, table)` | Drop an index |
| `op.execute(sql)` | Execute arbitrary SQL |

### The `down_revision` graph

When a new revision is created, alembic stamps the current head's ID into `down_revision` automatically. That single line is what builds the graph. The hash-style revision ID is usually unique enough on its own, but if two people generate a revision from the same head at the same time, both revisions point to the same `down_revision` and you get a branch (covered in episode 5).

## Before-After

```python
# Before: a dangerous revision with empty downgrade
def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])

def downgrade() -> None:
    pass  # ← leaving this empty makes it a one-way commit
```

```python
# After: a precise inverse
def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])

def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
```

The After version cleans up in exact reverse order (index → table). That order matters because of foreign-key and index dependencies.

## Step-by-step walkthrough

### Step 1: create an empty revision

```bash
alembic revision -m "create orders"
```

This creates `versions/<hash>_create_orders.py` with empty `upgrade` and `downgrade` functions.

### Step 2: write `upgrade`

```python
def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.current_timestamp(), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
```

Putting the default on the database side with `server_default=sa.func.current_timestamp()` means existing rows get a value too, without any application code change.

### Step 3: write `downgrade` (reverse order)

```python
def downgrade() -> None:
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
```

Create order: table → index. Drop order: index → table. If a foreign key is involved, drop child tables first.

### Step 4: apply and roll back

```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

If all three steps succeed cleanly, that is your proof that upgrade and downgrade are symmetric.

### Step 5: changing a column on SQLite (batch mode)

SQLite cannot change a column's type or nullability directly. Wrap the change in batch mode.

```python
def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("tier", sa.String(16), nullable=False, server_default="free"))

def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("tier")
```

If you turned on `render_as_batch=True` in episode 2, batch mode is applied automatically, but using the `batch_alter_table` context manager explicitly makes the intent obvious.

### Step 6: fixing data with `op.execute`

```python
def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(100)))
    op.execute("UPDATE users SET display_name = name WHERE display_name IS NULL")
```

You can bundle a schema change and a data fix into the same revision. For larger datasets, splitting the data change into a separate data migration (episode 6) is safer.

## Common mistakes

- **Leaving `downgrade` empty.** "We will never roll back" is fine until something breaks and you need to. If you really want to forbid downgrade, raise `NotImplementedError` explicitly instead.
- **Testing only `upgrade`.** Run `downgrade -1 && upgrade head` once locally on every PR. That is the minimum check for symmetry.
- **Ignoring foreign-key order on drops.** Drop child tables before their parents. Otherwise you hit FK violations.
- **Committing autogenerate output as-is.** Autogenerate is a starting point. Table creation order, index names, server defaults — all of those still need a human review.
- **Using `ALTER` on SQLite without batch mode.** It will fail with "syntax error" or "not supported."

## Practical patterns

- **Review `upgrade` and `downgrade` as a pair.** Add "is the downgrade an exact reverse" to your PR review checklist.
- **`server_default` is a database-side default.** SQLAlchemy's `default` only fires through ORM calls. For migrations, `server_default` is the right choice.
- **Revision messages are imperative one-liners.** `add users.tier`, `create orders` — short and direct.
- **One change per revision.** Two `add_column` calls in one revision is fine, but do not mix changes from unrelated modules. Recovery becomes painful when something regresses.
- **Drop in two stages.** First a release that stops using the column, then a later revision that drops it. Episode 9 covers this in detail.

## Checklist

- [ ] `upgrade()` and `downgrade()` are exact inverses
- [ ] The order respects foreign-key and index dependencies
- [ ] `batch_alter_table` is used explicitly on SQLite
- [ ] DB-side defaults use `server_default` (not application-side `default`)
- [ ] Revision message is an imperative one-liner with clear intent
- [ ] Verified locally with one `downgrade -1 && upgrade head` cycle
- [ ] Autogenerate output (if any) was reviewed by a human

## Exercises

1. Write a revision that adds two columns (`tier`, `last_login_at`) to `users` by hand and verify the `downgrade` works.
2. Create the `orders` table, then run `downgrade -1 && upgrade head` five times in a row and confirm data integrity.
3. Use `op.alter_column` on SQLite to change a column's nullability. Try it both with and without batch mode.

## Wrap up, next post

A revision file boils down to a pair: `upgrade` and `downgrade`. Building the habit of keeping them symmetric is the single biggest safety line you have in production. On SQLite, also remember that batch mode is essentially required.

The next post covers `--autogenerate` in earnest — the option that automates this hand-written work. The key question is where the boundary lies between what it catches and what it misses.

## References

- Alembic: Operation Reference — https://alembic.sqlalchemy.org/en/latest/ops.html
- Alembic: Working with Branches — https://alembic.sqlalchemy.org/en/latest/branches.html
- Alembic: Batch Mode — https://alembic.sqlalchemy.org/en/latest/batch.html
- SQLAlchemy: Schema Definition — https://docs.sqlalchemy.org/en/20/core/schema.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, revision, upgrade, downgrade, SQLite
