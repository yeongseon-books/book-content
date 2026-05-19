---
series: web-development-101
episode: 7
title: Connecting to a Database
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - WebDevelopment
  - Database
  - SQL
  - ORM
  - Backend
seo_description: SQL basics, ORMs, and connection pools — how a web app talks to a database without falling over under load, explained for new web developers.
last_reviewed: '2026-05-15'
---

# Connecting to a Database

A web app can feel complete while everything still lives in process memory, right up until the first restart, the first concurrent write, or the first report that data disappeared. Durable storage changes how you design correctness, concurrency, and performance.

This is post 7 in the Web Development 101 series. Here we move from in-memory thinking to database thinking by covering SQL basics, ORMs, connection pools, and transactions as the backbone of persistent application state.

## What you will learn

- Why we need a database in the first place
- The four basic SQL operations (SELECT/INSERT/UPDATE/DELETE)
- What an ORM is and when to use it
- Connections and connection pools
- The meaning of a transaction

## Why It Matters

Almost all *state* in a web app lives in the database. Mishandle the connection and a server falls over with *dozens* of users. Learn it once and it pays back for years.

> The database is *the keeper of truth*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/web-development-101/07/07-01-concept-at-a-glance.en.png)

*A high-level view of an app talking to a database through a reusable connection pool.*

The app does not just “use SQL.” It opens or borrows a connection, issues work, and often needs to bundle multiple statements into one transaction. That lifecycle matters as much as the query text itself.

### What to verify yourself

- Create a SQLite table and confirm that inserted rows persist across process restarts.
- Pass attacker-like input through a parameterized query and verify that the SQL shape does not change.
- Force an exception inside a transaction and confirm that rollback leaves the database in its previous state.

**Expected output:** Parameter binding treats malicious strings as values, and rollback prevents half-finished writes from surviving an error.

**Failure mode to watch for:** String-built SQL introduces injection risk. Opening a brand-new connection for every request makes connection overhead the first scaling bottleneck.

## Key Terms

- **SQL**: the language for talking to a relational DB.
- **Schema**: the *shape* of a table (columns and types).
- **ORM**: a tool that maps SQL to objects.
- **Connection**: the channel between app and DB.
- **Transaction**: a *single unit* that bundles multiple writes.

## Before/After

**Before (write to a file)**

```python
open("users.txt", "a").write("alice\n")  # races break it
```

**After (write to a DB)**

```python
import sqlite3
con = sqlite3.connect("app.db")
con.execute("INSERT INTO users(name) VALUES (?)", ("alice",))
con.commit()
```

The DB owns *concurrency* and *durability*.

## Hands-on: Drive a Small DB in 5 Steps

### Step 1 — Create a table

```python
# 1_init.py
import sqlite3
con = sqlite3.connect("app.db")
con.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE
)
""")
con.commit()
```

### Step 2 — Insert and read

```python
# 2_crud.py
import sqlite3
con = sqlite3.connect("app.db")
con.execute("INSERT INTO users(name, email) VALUES (?, ?)", ("alice", "a@x.com"))
con.commit()
for row in con.execute("SELECT id, name FROM users"):
    print(row)
```

### Step 3 — Parameter binding (block SQL injection)

```python
name = "alice'; DROP TABLE users; --"  # attacker input
con.execute("SELECT * FROM users WHERE name = ?", (name,))  # safe
```

Building SQL via f-strings is *fatal*.

### Step 4 — ORM (SQLAlchemy)

```python
# 4_orm.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)
S = sessionmaker(bind=engine)
s = S()
s.add(User(name="bob"))
s.commit()
```

### Step 5 — Transaction

```python
# 5_tx.py
import sqlite3
con = sqlite3.connect("app.db")
try:
    con.execute("BEGIN")
    con.execute("UPDATE users SET name='ALICE' WHERE id=1")
    con.execute("INSERT INTO users(name) VALUES ('charlie')")
    con.commit()
except Exception:
    con.rollback()
    raise
```

Either *all* commits, or *all* roll back.

## What to Notice in This Code

- SQL without parameter binding (`?`) *will* break someday.
- ORMs are convenient but you must occasionally read the *generated SQL*.
- Transactions wrap *business units*, not single statements.

## Five Common Mistakes

1. **Stitching SQL with strings.** SQL injection.
2. **Opening a new connection per request.** No pool.
3. **Big SELECTs without indexes.** Slow as molasses.
4. **Two writes without a transaction.** Half-applied disasters.
5. **Swallowing errors.** Data integrity slips.

## How This Shows Up in Production

Most web backends pair PostgreSQL or MySQL with an ORM. Under traffic, *read replicas* and *Redis caches* show up. Every tool ultimately rests on *connection pools and transactions*.

## How a Senior Engineer Thinks

- Sketch the *schema first*.
- Add indexes by *query pattern*.
- Make transaction boundaries *explicit*.
- Always suspect N+1 queries.
- Use a *migration tool* to track schema changes.

## Checklist

- [ ] You know the four basic SQL operations.
- [ ] You always use parameter binding.
- [ ] You can explain what a connection pool is.
- [ ] You can read code that uses transactions.
- [ ] You can log the SQL an ORM generates.

## Practice Problems

1. Build a small `posts` table in SQLite with full CRUD.
2. Rewrite the same queries with an ORM and log the actual SQL.
3. Trigger an exception inside a transaction and confirm rollback.

## Wrap-up and Next Steps

The DB is *the keeper of truth*. Next, we ship our app to the world — deployment.

<!-- toc:begin -->
- [How the Web Works](./01-how-the-web-works.md)
- [HTML, CSS, and JavaScript](./02-html-css-javascript.md)
- [The Browser and the DOM](./03-browser-and-dom.md)
- [HTTP and APIs](./04-http-and-api.md)
- [Frontend and Backend](./05-frontend-and-backend.md)
- [Authentication and Sessions](./06-auth-and-sessions.md)
- **Connecting to a Database (current)**
- Deployment (upcoming)
- Performance and Caching (upcoming)
- Building a Small Web App (upcoming)
<!-- toc:end -->

## References

### Official Docs
- [sqlite3 — DB-API 2.0 interface for SQLite databases](https://docs.python.org/3/library/sqlite3.html)
- [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Database transaction (Wikipedia)](https://en.wikipedia.org/wiki/Database_transaction)

### Verification Resources
- [SQL injection (OWASP)](https://owasp.org/www-community/attacks/SQL_Injection)
- [EXPLAIN QUERY PLAN (SQLite)](https://www.sqlite.org/eqp.html)

Tags: Computer Science, WebDevelopment, Database, SQL, ORM, Backend
