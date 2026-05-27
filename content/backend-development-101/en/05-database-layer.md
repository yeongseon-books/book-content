---
series: backend-development-101
episode: 5
title: "Backend Development 101 (5/10): The Database Layer"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Backend
  - Database
  - SQL
  - SQLAlchemy
  - Python
seo_description: Use the repository pattern to isolate database access — transactions, migrations, and the N+1 query problem covered in one place.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (5/10): The Database Layer

The moment services start writing SQL directly, query duplication and data-access drift begin to spread. It feels convenient at first, but the cost shows up later when you need to tune performance, add caching, or swap test storage.

This is the 5th post in the Backend Development 101 series. Here, we use the repository pattern to separate the database layer and then walk through ORM basics, migrations, transaction boundaries, and the N+1 problem.


![backend development 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/05/05-01-concept-at-a-glance.en.png)
*backend development 101 chapter 5 flow overview*

## Questions to Keep in Mind

- The role of the repository pattern?
- Why we use an ORM and where its *traps* live?
- The flow of transactions, commits, and rollbacks?

## Why It Matters

Databases are *what changes most often* and *what should change least*. Splitting the layer early means swapping a database, adding a cache, or running tests on an in-memory engine all happen in *one file*.

> A repository is the *translator between the database and the service*.

The service does not know SQL — only the repository does.

## Key Terms

- **Repository**: an object that wraps database access in *function-like* methods.
- **ORM**: a tool that maps objects to tables.
- **Migration**: schema changes versioned in code.
- **Transaction**: a unit that commits or rolls back together.
- **N+1**: one query plus N child queries — the most common performance trap.

## Before/After

**Before (SQL inside the service)**

```python
def create_user(name):
    cur = db.execute("INSERT INTO users(name) VALUES(?)", (name,))
    return cur.lastrowid
```

**After (wrapped by a repository)**

```python
# repositories/user_repo.py
class UserRepository:
    def __init__(self, session):
        self.session = session

    def save(self, user):
        self.session.add(user)
        self.session.flush()
        return user
```

A query change now lives in *one file*.

## Hands-on: Five Steps Through the Database Layer

### Step 1 — SQLite + SQLAlchemy setup

```python
# 1_setup.py
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)
```

### Step 2 — Session and repository

```python
# 2_repo.py
from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, name: str) -> User:
        u = User(name=name)
        self.session.add(u)
        self.session.flush()
        return u

    def get(self, uid: int) -> User | None:
        return self.session.get(User, uid)
```

### Step 3 — Transactions

```python
# 3_tx.py
from sqlalchemy.orm import Session
with Session(engine) as s, s.begin():
    repo = UserRepository(s)
    repo.add("Alice")
    repo.add("Bob")
# Exiting cleanly commits; an exception rolls back.
```

### Step 4 — Migrations

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "add users"
alembic upgrade head
```

Schema changes become *code under version control*.

### Step 5 — Killing N+1

```python
# 5_eager.py
from sqlalchemy.orm import selectinload
stmt = select(Order).options(selectinload(Order.items))
orders = session.scalars(stmt).all()
```

Loading the children in *one shot* eliminates N+1.

## Verification points

**Expected output:** after `Base.metadata.create_all(engine)`, the `users` table should exist, and both `add()` calls inside one transaction block should commit together unless an exception triggers rollback.

### First failure modes to check

- Long-lived sessions often show up later as leaked connections or lock contention.
- Manual schema edits start environment drift immediately when no migration records the change.
- If list endpoints suddenly slow down, check for repeated relation fetches before looking anywhere else.

## What to Notice in This Code

- Sessions stay *short* — one per request is standard.
- Repositories return *domain objects*, not raw dicts.
- Migrations are always safer than direct `ALTER TABLE`.

## Five Common Mistakes

1. **Returning ORM objects straight to the client.** Use a Pydantic *DTO* instead.
2. **Sharing a session globally.** Concurrency bugs follow.
3. **Editing the production schema by hand.** Environments drift apart.
4. **Leaving every relation as lazy.** N+1 builds up *quietly*.
5. **Using the real database in tests.** Use in-memory SQLite or mocks for speed.

## How This Shows Up in Production

Most backends start with *PostgreSQL + ORM + Alembic + Repository*. As traffic grows you add read replicas, Redis, or Elasticsearch — and the service is untouched. Only the inside of the repository changes. That boundary is what lets the system *evolve*.

## How a Senior Engineer Thinks

- Every query is checked against an *index*.
- Every migration writes a *down* path too.
- Repository methods speak the *domain language* (`find_active_users`).
- Transactions stay *as short as possible*.
- The slow-query log is *always* on in production.

## Checklist

- [ ] You can put SQL behind a repository.
- [ ] You can write a transaction block.
- [ ] You can create an Alembic migration.
- [ ] You can spot N+1 and fix it with eager loading.
- [ ] You can tell a DTO from an ORM object.

## Practice Problems

1. Implement `OrderRepository.find_recent(limit=10)` and check the index.
2. Add an Alembic migration that adds a `users.email` column.
3. Trigger an N+1 query on purpose and measure the difference after `selectinload`.

## Wrap-up and Next Steps

A repository is a *translator over the database*. Next, we look at *who can see what* — authentication and authorization.

## Answering the Opening Questions

- **The role of the repository pattern?**
  - The article treats The Database Layer as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why we use an ORM and where its *traps* live?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The flow of transactions, commits, and rollbacks?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Backend Development 101 (1/10): What Is Backend Development?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): Building an HTTP Server](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing and Controllers](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): The Service Layer](./04-service-layer.md)
- **The Database Layer (current)**
- Authentication and Authorization (upcoming)
- Logging and Error Handling (upcoming)
- Testing the Backend (upcoming)
- Deploying the Backend (upcoming)
- A Production-Ready Backend Structure (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy relationship loading techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)

### Further Reading

- [Repository pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/repository.html)

Tags: Backend, Database, SQL, SQLAlchemy, Python
