---
title: 'Production patterns: pools, observability, migrations, and deploys'
series: sqlalchemy-101
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
- SQLAlchemy
- Production
- pool
- Observability
- SQLite
last_reviewed: '2026-05-03'
seo_description: Production SQLAlchemy has three knobs. The pool sets concurrency
  and tail latency. Observability tells you where slow is.
---

# Production patterns: pools, observability, migrations, and deploys

Production SQLAlchemy has three knobs: the pool, observability, and deployment sequencing. This post focuses on the decisions in those areas that most often turn into real incidents.

This is the final article in the SQLAlchemy 101 series.

![Production patterns: pools, observability, migrations, and deploys](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-01-production-patterns-pools-observability.en.png)

*Production patterns: pools, observability, migrations, and deploys*
## What you will learn

- The core connection pool options (`pool_size`, `max_overflow`, `pool_pre_ping`, `pool_recycle`)
- How to choose between `QueuePool`, `NullPool`, and `StaticPool`, especially for SQLite
- How to wire SQL queries into traces with OpenTelemetry
- How to catch slow queries and N+1 in production
- How to sequence migrations and code deploys safely (blue/green rules)
- The boundary for retrying transient errors

## Why this matters

![Why this matters](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-02-why-this-matters.en.png)

*Why this matters*
Everything so far has been about whether the code is correct. Production adds another layer. The same code falls apart under load if the pool is wrong, you cannot tell what is slow without observability, and a single deploy becomes an incident if the migration order is bad.

This article is about that layer. The examples use SQLite, but most of the patterns apply equally to PostgreSQL and MySQL.

## Mental model

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-03-mental-model.en.png)

*Mental model*
> Production SQLAlchemy has three knobs. The **pool** sets concurrency and tail latency. **Observability** tells you where slow is. The **migration policy** defines the safety line for deploys. Leave any one of them empty and the other two lose most of their value.

A pool that is too small queues requests; too large blows past the DB-side connection limit. Without observability you cannot even tell that the pool is wrong. And without a migration policy, "the five minutes after deploy" becomes a recurring outage window.

## Core concepts

![Core concepts](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-04-core-concepts.en.png)

*Core concepts*
### Pool options

| Option | Meaning | Sensible start |
| --- | --- | --- |
| `pool_size` | connections kept open at steady state | 5–20 (depends on service size) |
| `max_overflow` | extra connections allowed during bursts | same as `pool_size` |
| `pool_pre_ping` | run SELECT 1 before checkout to detect dead connections | True |
| `pool_recycle` | drop connections older than N seconds before reuse | 1800 (shorter than the DB idle timeout) |
| `pool_timeout` | max seconds to wait for a checkout | 10–30 |

### Pool classes

- **`QueuePool`** (default): standard sync web servers.
- **`NullPool`**: short-lived scripts, lambdas. New connection every time.
- **`StaticPool`**: a single connection shared across callers. Common for SQLite + multi-thread tests.

### SQLite specifics

SQLite is a single-writer database. Concurrent writers serialize on a file lock, so a big pool buys nothing. Typical setup is `StaticPool` plus `check_same_thread=False`, or in async, the default `aiosqlite` pool.

### Observability

You can time queries directly with `event.listens_for(engine, "before_cursor_execute" / "after_cursor_execute")`, or use OpenTelemetry's `SQLAlchemyInstrumentor` to attach SQL spans to existing traces automatically.

## Before / after

```python
# Before: an engine built with defaults
engine = create_engine(DATABASE_URL)
# pool, pre-ping, recycle, observability all default → 5xx at 3am from stale connections
```

```python
# After: production basics
from sqlalchemy import create_engine, event
import time, logging

log = logging.getLogger("db.slow")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
    future=True,
)

SLOW_MS = 200

@event.listens_for(engine, "before_cursor_execute")
def _t0(conn, cursor, stmt, params, ctx, many):
    ctx._t0 = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def _t1(conn, cursor, stmt, params, ctx, many):
    ms = (time.perf_counter() - ctx._t0) * 1000
    if ms >= SLOW_MS:
        log.warning("slow %.1fms %s", ms, stmt[:200])
```

The "after" version (1) recovers automatically from a dead connection on the next request via `pool_pre_ping`, (2) drops connections older than 30 minutes via `pool_recycle`, and (3) logs any query above 200ms to a dedicated logger.

## Step-by-step walkthrough

![Step-by-step walkthrough](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/10/10-05-step-by-step-walkthrough.en.png)

*Step-by-step walkthrough*
### Step 1: Sizing the pool

A reasonable starting heuristic is `(average concurrent requests) × (avg time a request holds a connection / total request time)`. For a typical web process, 5–20 is enough. If that is not enough, add worker processes rather than enlarging `pool_size`.

### Step 2: pre-ping and recycle

Set `pool_recycle` shorter than the DB idle timeout (PostgreSQL 8h, MySQL 8h, load balancer often 5 min). `pool_pre_ping=True` should be on almost always.

### Step 3: A query counter to block N+1 regressions

Take the `before_cursor_execute` counter from Episode 8 and turn it into a test:

```python
def test_no_n_plus_one(session):
    counter["n"] = 0
    result = list_users_with_posts(session)  # uses selectinload
    assert counter["n"] <= 2  # users SELECT + posts IN-SELECT
```

Drop the `selectinload` and the counter immediately exposes the regression.

### Step 4: Wire SQL into OpenTelemetry traces

```python
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

SQLAlchemyInstrumentor().instrument(engine=engine)
```

Now every SQL statement attaches as a child span of the active trace. You can answer "which SQL ran in this request and how long did it take" directly.

### Step 5: Retry transient errors

```python
import tenacity

@tenacity.retry(
    retry=tenacity.retry_if_exception_type(OperationalError),
    wait=tenacity.wait_exponential(multiplier=0.1, max=2),
    stop=tenacity.stop_after_attempt(3),
)
def write_with_retry(session, obj):
    session.add(obj)
    session.commit()
```

Use this only for errors that are obviously safe to retry: a remote DB blip, `SQLITE_BUSY`. Never wrap business errors in retry.

### Step 6: Migration and deploy ordering

The default rule: **migrations first, code second.** For column adds and removes:

- **Adding a column**: (1) migration that adds it as nullable → (2) deploy code that uses the new column → (3) optionally a follow-up migration to NOT NULL.
- **Removing a column**: (1) deploy code that no longer references the column → (2) drop column in a later migration. Never both in the same deploy.

The next series, alembic-101, makes this concrete with commands.

## Common mistakes

- **Cranking `pool_size` only.** If you ignore the DB-side max_connections, the database starts refusing.
- **Disabling `pool_pre_ping` and getting 3am 5xx from stale connections.** There is rarely a good reason to turn it off.
- **Retrying every exception.** Integrity errors and validation errors will fail the same way again. Use an explicit allow-list.
- **Bundling migration and code in one deploy step.** That kills the rollback path.
- **Setting the slow-query threshold too low.** Start at 200ms as a meaningful signal and tighten toward 50ms over time.
- **Using `QueuePool` for production SQLite.** SQLite is single-writer; a big pool only creates a false sense of concurrency.

## Production patterns

- **One engine per process.** Build it at module import, call `dispose()` on shutdown.
- **Session per request or per task.** Enforce with a dependency or a context manager.
- **Keep transactions short.** External HTTP calls and heavy CPU work belong outside transactions.
- **Healthchecks**: `SELECT 1` with a tight timeout, wired straight into Kubernetes liveness/readiness.
- **Separate IAM/account for schema migrations.** Application accounts should not be allowed to run DDL — that prevents many accidents.
- **Slow query log + APM trace + alerts**: those three together catch most regressions before users do.

## Checklist

- [ ] `pool_size`, `max_overflow`, `pool_pre_ping`, `pool_recycle`, `pool_timeout` are all explicit
- [ ] Total pool capacity stays under the DB's max_connections
- [ ] A slow query logger exists, with a starting threshold like 200ms
- [ ] SQL statements appear in OpenTelemetry (or equivalent) traces
- [ ] Retry is limited to transient errors (`OperationalError`, `SQLITE_BUSY`) with a max of 3 attempts
- [ ] Migrations and code deploys never share the same step
- [ ] One engine per process; `dispose()` is called on shutdown

## Exercises

1. Set `pool_size=2` and `max_overflow=0`, then send 5 concurrent requests and observe `pool_timeout` in action.
2. Tighten the slow query threshold from 200ms to 50ms and record which queries become signal.
3. Trigger `SQLITE_BUSY` by writing from two threads simultaneously and verify that the retry decorator recovers.

## Wrap-up and what is next

Production decisions converge on three axes: pool, observability, and migration policy. Decide them early and you get a system you can debug. Decide them late and you patch them with after-hours deploys.

This series ends here. The next series, **alembic-101**, turns the migration policy in this article into concrete commands and workflows: `autogenerate`, branches and merges, data migrations, and a usable downgrade strategy.

<!-- toc:begin -->
## In this series

- [Getting Started with SQLAlchemy 2.x - Engine and Connection Demystified](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy Core - Modeling Schema as Python Objects with MetaData, Table, and Column](./02-core-metadata-table-types.md)
- [SQLAlchemy Core - select, insert, update, delete in 2.x Style](./03-core-select-insert-update-delete.md)
- [ORM Basics: Defining Models with DeclarativeBase and mapped_column](./04-orm-declarative-mapped-column.md)
- [Session in Depth: How Unit of Work and Identity Map Actually Work](./05-session-unit-of-work-identity-map.md)
- [ORM Relationships: Connecting Both Sides Safely with relationship and back_populates](./06-relationships-back-populates.md)
- [Loading Strategies and the N+1 Problem: When to Pick lazy, joined, or selectin](./07-loading-strategies-n-plus-one.md)
- [Events, hybrid_property, and custom types](./08-events-hybrid-types.md)
- [Async SQLAlchemy with aiosqlite and AsyncSession](./09-async-aiosqlite.md)
- **Production patterns: pools, observability, migrations, and deploys (current)**

<!-- toc:end -->

## References

- SQLAlchemy: Connection Pooling — https://docs.sqlalchemy.org/en/20/core/pooling.html
- SQLAlchemy: Engine Configuration — https://docs.sqlalchemy.org/en/20/core/engines.html
- OpenTelemetry SQLAlchemy instrumentation — https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/sqlalchemy/sqlalchemy.html
- Tenacity — https://tenacity.readthedocs.io/

Tags: Python, SQLAlchemy, ORM, Database
