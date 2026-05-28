---
title: "Alembic 101 (2/10): env.py and target_metadata: wiring models to migrations"
series: alembic-101
episode: 2
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
- env.py
- target_metadata
- Configuration
- SQLite
last_reviewed: '2026-05-12'
seo_description: env.py is a boot script Alembic runs on every command. For each invocation
  (upgrade, revision --autogenerate, etc.) Alembic (1) reads alembic.ini…
---

# Alembic 101 (2/10): env.py and target_metadata: wiring models to migrations

`env.py` is the boot script Alembic runs on every command. If this layer does not wire model metadata and connection settings cleanly, autogenerate becomes untrustworthy immediately.

This is the 2nd post in the Alembic 101 series. Here we will pin down when `env.py` runs and what `target_metadata` must provide in practice.


![alembic 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/alembic-101/02/02-01-diagram-where-env-py-assembles-metadata.en.png)
*alembic 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What `env.py` actually is and when it runs?
- Why `target_metadata` is mandatory (it is the basis for autogenerate)?
- A safe pattern for reading the DB URL from an environment variable?

## Why this matters

Episode 1 left you with a scaffolded project, but in that state Alembic does not know your models. Running `alembic revision --autogenerate` produces an empty file because `env.py` has no idea where to find the model metadata. Without that one line, Alembic has nothing to compare the live DB schema against.

The other reason: leaving the DB URL in plaintext inside `alembic.ini` puts staging and production credentials into git. This article opens up `env.py` and fixes both — the metadata wiring and the URL story.

## Mental model

> `env.py` is a **boot script** Alembic runs on every command. For each invocation (`upgrade`, `revision --autogenerate`, etc.) Alembic (1) reads `alembic.ini`, (2) runs `env.py` to obtain a connection and metadata, then (3) applies the revisions in the `versions/` directory.

The point is: it runs every time. Environment variables are re-read on every command. Model imports happen on every command. Once you accept that flow, what `env.py` should do becomes obvious.

### Diagram: where `env.py` assembles metadata and connectivity

## Core concepts

### The two functions in `env.py`

A default `env.py` defines two functions:

- `run_migrations_online()` — opens a real DB connection and applies migrations
- `run_migrations_offline()` — emits SQL only, without a connection

The bottom of the file branches on `if context.is_offline_mode(): ... else: ...` and calls one of them.

### `target_metadata`

```python
from app.models import Base
target_metadata = Base.metadata
```

This single line is the basis for autogenerate. Alembic introspects the live DB through the connection, compares against `target_metadata`, and writes the diff into a revision file. With `target_metadata = None`, autogenerate is silently a no-op.

### Online vs offline

| Mode | Command | Use |
| --- | --- | --- |
| Online | `alembic upgrade head` | Apply directly to the DB |
| Offline | `alembic upgrade head --sql > out.sql` | Emit SQL only; a DBA applies it manually |

Offline mode is common in environments where direct production DB access is restricted (separate change-management process, network isolation).

### URL precedence

Alembic normally reads `sqlalchemy.url` from `alembic.ini`, but `env.py` can override it via `config.set_main_option("sqlalchemy.url", ...)`. The environment-variable pattern uses exactly that override.

## Before / after

```python
# Before: scaffolded defaults (autogenerate produces empty files)
from alembic import context
config = context.config
target_metadata = None  # ← leaving this empty disables autogenerate

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), ...)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

```python
# After: model wired in, URL from environment
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.models import Base   # ← import the model

config = context.config

# Override alembic.ini if DATABASE_URL is set in the environment
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata   # ← basis for autogenerate

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=url.startswith("sqlite"),  # SQLite-only batch mode
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

The "after" version (1) knows the model so autogenerate works, (2) reads production credentials from the environment so git is safe, and (3) auto-enables batch mode on SQLite to work around its ALTER limitations.

## Step-by-step walkthrough

### Step 1: Make sure model imports work

`env.py` is imported from wherever you run the `alembic` command — usually the project root. Either structure your packages so `from app.models import Base` works directly, or push the project root onto `sys.path` explicitly:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app.models import Base
```

### Step 2: Set `target_metadata`

```python
target_metadata = Base.metadata
```

If you have multiple `Base` instances, merge their `MetaData`:

```python
from sqlalchemy import MetaData
combined = MetaData()
for m in [Base.metadata, OtherBase.metadata]:
    for t in m.tables.values():
        t.tometadata(combined)
target_metadata = combined
```

### Step 3: Override URL from the environment

```python
import os
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)
```

Keep `alembic.ini` populated with a safe default (a local SQLite path) and inject staging/production via the environment.

### Step 4: `render_as_batch` for SQLite

SQLite barely supports `ALTER TABLE` for column drops, type changes, and so on. Alembic's batch mode works around it: (1) create a temp table, (2) copy rows, (3) drop the original, (4) rename the temp. If you target SQLite, this should almost always be on.

### Step 5: Verify autogenerate

```bash
# Add a column to the model
# class User(Base):
#     ...
#     tier: Mapped[str] = mapped_column(default="free")

alembic revision --autogenerate -m "add users.tier"
```

When `versions/<hash>_add_users_tier.py` shows up with `op.add_column(...)` inside `upgrade()`, the metadata wiring is confirmed.

### Step 6: Preview SQL with offline mode

```bash
alembic upgrade head --sql
```

This emits DDL with no connection. Many teams put this in CI and paste the output into the PR description. Reading SQL by eye is itself a meaningful safety check.

## Verification routine

```bash
alembic revision --autogenerate -m "probe metadata wiring"
python3 - <<'PY'
from pathlib import Path
latest = sorted(Path("alembic/versions").glob("*_probe_metadata_wiring.py"))[-1]
print(latest.read_text())
PY
```

**Expected output:** the generated revision contains a real diff such as `op.add_column(...)`. If the file is empty, go back to `target_metadata` before trusting anything else.

## Common mistakes

- **Leaving `target_metadata = None`.** autogenerate writes empty files. First debugging step.
- **Importing the model module but seeing nothing.** If the model module never loads, `Base.metadata` is empty. Either explicitly import every model in `__init__.py`, or import them in `env.py`.
- **Dropping a column on SQLite without `render_as_batch`.** You get "ALTER TABLE drop column not supported."
- **Committing production URLs into `alembic.ini`.** The environment-variable override pattern is effectively the standard.
- **Leaving the default pool.** Alembic commands are usually one-shot, so `poolclass=pool.NullPool` is more appropriate.

## Production patterns

- **`env.py` is a one-time investment.** Three things are usually all you need: model import, env-var URL, batch mode (SQLite/MySQL).
- **One `env.py` for all environments (local/staging/prod).** Differences live entirely in the environment.
- **`compare_type=True`, `compare_server_default=True`.** Make autogenerate detect column type and default changes too (next episode).
- **`include_object` hook to exclude tables.** Useful when an external system manages some tables.
- **Sync vs async.** Even with async SQLAlchemy in your app, Alembic typically runs with a sync engine in `env.py`. If you really need async, use the `connectable.run_sync(...)` pattern.

## Checklist

- [ ] `from app.models import Base` (or equivalent) is at the top of `env.py` and actually works
- [ ] `target_metadata = Base.metadata` is set explicitly
- [ ] `DATABASE_URL` can override the URL via the environment
- [ ] If you target SQLite, `render_as_batch=True` is in `context.configure(...)`
- [ ] `alembic.ini` only carries safe defaults (local SQLite)
- [ ] `alembic revision --autogenerate` produces actual diffs, not empty files
- [ ] `alembic upgrade head --sql` can emit offline DDL

## Exercises

1. Run `alembic revision --autogenerate` while leaving `target_metadata = None` and verify that the file comes back empty.
2. Point `DATABASE_URL` at two different SQLite files and apply the same migration to both.
3. Disable `render_as_batch` and try a column-drop migration on SQLite to reproduce the error.

## Wrap-up and what is next

`env.py` is Alembic's boot script, and inside it you really only need two things — `target_metadata` and an env-var URL — to get going. On SQLite, add `render_as_batch`.

The next episode writes the first meaningful revision by hand. We will compare hand-written and autogenerated migrations using `op.create_table`, `op.add_column`, and `op.execute`, and walk through how to keep `upgrade` and `downgrade` symmetric.

## Answering the Opening Questions

- **What exactly is `env.py` and when does it execute?**
  - `env.py` is the boot script that Alembic runs on every command—`upgrade`, `revision --autogenerate`, `--sql`, and so on. It is where `run_migrations_online()` and `run_migrations_offline()` diverge, and where the actual connection and configuration are assembled.
- **Why is `target_metadata` mandatory rather than optional?**
  - With `target_metadata = Base.metadata`, Alembic can compare the live database against model definitions to produce diffs like `op.add_column(...)`. As the article emphasized, setting `target_metadata = None` causes autogenerate to silently produce empty files.
- **How do you safely read the DB URL from an environment variable?**
  - Read with `db_url = os.environ.get("DATABASE_URL")` and override with `config.set_main_option("sqlalchemy.url", db_url)`. This keeps a local default in `alembic.ini` while keeping staging and production credentials outside of git.
<!-- toc:begin -->
## In this series

- [Alembic 101 (1/10): Why Alembic, and getting to alembic init](./01-why-alembic-and-init.md)
- **env.py and target_metadata: wiring models to migrations (current)**
- Your first revision: writing upgrade and downgrade by hand (upcoming)
- autogenerate: the line between what it catches and what it misses (upcoming)
- branches and merges: combining revisions made in parallel (upcoming)
- Data migrations: separating schema changes from data changes (upcoming)
- Online and offline modes: previewing DDL with --sql and handling SQLite batch (upcoming)
- Downgrade strategy: when to write it for real and when to forbid it (upcoming)
- Deploy ordering and blue/green: synchronizing schema and application code safely (upcoming)
- Production and team workflow: PR, CI, monitoring, and incident response (upcoming)

<!-- toc:end -->

## References

- [sqlalchemy/alembic GitHub repository](https://github.com/sqlalchemy/alembic)
- [Alembic: env.py](https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file)
- [Alembic: target_metadata](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Alembic: Batch Mode](https://alembic.sqlalchemy.org/en/latest/batch.html)
- [Alembic: Offline Mode](https://alembic.sqlalchemy.org/en/latest/offline.html)

Tags: Python, Alembic, SQLAlchemy, Migration
