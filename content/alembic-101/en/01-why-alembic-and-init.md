---
title: Why Alembic, and getting to alembic init
series: alembic-101
episode: 1
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
- SQLAlchemy
- Migration
- SQLite
last_reviewed: '2026-05-03'
seo_description: Alembic is git for your database schema. Each migration file is a
  commit, the alembic_version table is the current HEAD pointer, upgrade head is…
---

# Why Alembic, and getting to alembic init

When a team first meets Alembic, the real question is not the command syntax but why raw SQL files stop scaling. Once schema history depends on memory instead of revision history, deploys and rollbacks turn into guesswork.

This is the first post in the Alembic 101 series. Here we will frame why Alembic exists and what `alembic init` actually sets up.

## What you will learn

- What problem a "migration tool" actually solves
- Why `Base.metadata.create_all` is not enough for production
- Alembic's core concepts: revision, head, version table
- How to scaffold a project with `alembic init`
- The two or three traps you usually hit on a SQLite-based Alembic setup

## Why this matters

Schema changes are a recurring source of production incidents. Code lives in git, infrastructure lives in Terraform, but it is surprisingly common to manage "who ran which SQL on which environment" by hand. Staging quietly drifts away from production, and when something needs to roll back nobody can confidently say how far the schema should rewind.

Alembic is the migration tool by SQLAlchemy's author, and it treats this problem the way git treats code. Each change is a revision, head is the latest state, and every environment walks the same history up or down. This article covers the first two questions: why you need it, and how to start.

## Mental model

> Alembic is **git for your database schema**. Each migration file is a commit, the `alembic_version` table is the current HEAD pointer, `upgrade head` is fast-forward, and `downgrade -1` is a one-step reset.

Once that analogy lands, almost every command makes sense. `revision` creates a new commit, `merge` reconciles two heads, and `stamp` is like `git reset` — it changes HEAD without touching the working tree.

## Core concepts

### Revisions and head

Every migration file has a unique `revision` ID and a parent `down_revision`. The revisions form a directed graph; the leaf nodes (no children) are `head`s. Normally there is exactly one head, but branches can give you more than one.

### The `alembic_version` table

Alembic creates a single-row meta table called `alembic_version` in your DB. Its value is "which revision this database is currently on." Every Alembic command reads it, compares against the graph, and decides what to do.

### How it differs from `create_all`

| Aspect | `Base.metadata.create_all` | Alembic |
| --- | --- | --- |
| Use case | Tests, early prototypes | Production operation |
| Change tracking | None | Revision graph |
| Column changes/drops | Cannot do them | Yes |
| Cross-environment sync | None | Same history |
| Rollback | None | `downgrade` command |

`create_all` is "make tables that don't exist." Add a single column and `create_all` will never put it in production for you.

### What `alembic init` creates

```text
project/
├── alembic.ini           # global config (DB URL, logging, file template)
└── alembic/
    ├── env.py            # migration runtime context
    ├── script.py.mako    # revision file template
    └── versions/         # the actual migration files
```

You will mostly touch `env.py` (next episode) and the files inside `versions/` (every time something changes).

## Before / after

```bash
# Before: hand-running SQL on production
psql -h prod -U app -d main -c "ALTER TABLE users ADD COLUMN tier VARCHAR(16) NOT NULL DEFAULT 'free';"
# Nobody can reconstruct who, when, on which environment, after the fact
```

```bash
# After: the revision file IS the change log
alembic revision -m "add users.tier"
# alembic/versions/3f9c..._add_users_tier.py is created
# Code review, environment sync, rollback all become possible
alembic upgrade head
```

The "after" version shows up in `git diff`, becomes part of the PR review, and lets staging and production reach the same state with the same command.

## Step-by-step walkthrough

### Step 1: Install

```bash
mkdir alembic-demo && cd alembic-demo
python3 -m venv .venv && source .venv/bin/activate
pip install "sqlalchemy>=2.0" "alembic>=1.13"
```

### Step 2: Define a model

```python
# app/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
```

### Step 3: `alembic init`

```bash
alembic init alembic
```

This creates:

```text
alembic-demo/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

### Step 4: Point the URL at SQLite

In `alembic.ini`, find the line:

```ini
sqlalchemy.url = sqlite:///./app.db
```

The next episode shows the safer pattern of reading it from an environment variable (`os.environ["DATABASE_URL"]`), but for now this is fine.

### Step 5: First empty revision

```bash
alembic revision -m "init"
```

A file at `alembic/versions/<hash>_init.py` is generated, with empty `upgrade()` and `downgrade()` functions. This is your first commit.

### Step 6: Upgrade and inspect the version table

```bash
alembic upgrade head
sqlite3 app.db "SELECT * FROM alembic_version;"
# result: <hash>
```

Seeing that single row in `alembic_version` makes the model click. That table is the reference point for every migration command.

## Common mistakes

- **Starting production with `create_all`.** Adopting Alembic later means an extra step of stamping the current schema as the first revision. Use Alembic from day one if you can.
- **Hard-coding production credentials in `alembic.ini`.** Override from the environment in `env.py` (next episode).
- **Editing `alembic_version` by hand.** Possible, almost always an incident. Use `alembic stamp` instead.
- **Modifying a revision file after pushing it.** Revision IDs are part of history. If the revision was already applied elsewhere, write a new revision instead of editing the old one.
- **Two people running `revision -m` in parallel.** You get a branch. Episode 5 explains how to merge them, but ideally rebase-like cleanup happens just before PR merge.

## Production patterns

- **Revision files belong in the same PR as the code.** "Feature code + migration + tests" travel together.
- **Print DDL in CI with `alembic upgrade head --sql`.** Reading auto-generated SQL with human eyes catches a surprising number of incidents.
- **Make file templates meaningful.** The default uses only the hash; switch to `file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s` so files sort by time.
- **Avoid branches when you can.** A single head is enough for most teams.
- **First revision = baseline.** When introducing Alembic into an existing DB, run `alembic revision --autogenerate -m "baseline"` and immediately mark HEAD with `alembic stamp head`.

## Checklist

- [ ] After `alembic init`, you can identify `alembic.ini`, `env.py`, and `versions/`
- [ ] `sqlalchemy.url` points at the right database (SQLite for this series)
- [ ] You created the first empty revision and saw `alembic_version` materialize after `upgrade head`
- [ ] `create_all` is reserved for tests; production uses Alembic only
- [ ] Revision files are committed to git and reviewed in PRs
- [ ] Credentials are read from the environment, not stored as plaintext in `alembic.ini` (implemented in the next episode)

## Exercises

1. Walk through the steps above on SQLite + `alembic init` and verify the `alembic_version` table appears.
2. Run `alembic history` and `alembic current` and compare the outputs.
3. Run `alembic downgrade base` to roll everything back, then check what happens to the `alembic_version` table.

## Wrap-up and what is next

Alembic boils down to one analogy: it is git for your database schema. Once you have revisions, head, and the version table in your head, the rest is mostly memorizing commands.

The next episode opens up `env.py`. We will wire it to your model metadata, read the DB URL safely from the environment, and look at what online vs offline mode actually means.

## References

- Alembic: Tutorial — https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Alembic: Configuration — https://alembic.sqlalchemy.org/en/latest/config.html
- SQLAlchemy: MetaData — https://docs.sqlalchemy.org/en/20/core/metadata.html
- SQLite Documentation — https://www.sqlite.org/docs.html

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, Alembic, SQLAlchemy, Migration, init, SQLite
