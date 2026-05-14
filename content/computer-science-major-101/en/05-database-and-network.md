---
series: computer-science-major-101
episode: 5
title: Database and Network
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - CS
  - Database
  - Network
  - SQL
  - Beginner
seo_description: A beginner-friendly tour of database and network courses covering SQL, TCP/IP, HTTP, and how the two connect.
code_required: false
last_reviewed: '2026-05-14'
---

# Database and Network

> Computer Science Major 101 series (5/10)

<!-- a-grade-intro:begin -->

**Core question**: *Why* are *database* and *network* the *pillars* of *every service*?

> *Data* is *stored* and the *network* *delivers* it — together they *are* the service.

<!-- a-grade-intro:end -->

This is post 5 in the Computer Science Major 101 series.

## What You Will Learn

- Meaning of *relational DB*
- Role of *SQL*
- The *TCP/IP* model
- Where *HTTP* sits
- How the two courses *connect*

## Why It Matters

*Most* of *backend time* is spent in *DB* and *network* code.

## Concept at a Glance

![Request-to-database flow](../../../assets/computer-science-major-101/05/05-01-request-to-database-flow.en.png)

*The basic service path from network request to database query*

## Key Terms

- **table**: *rows and columns*.
- **primary key**: *unique* identifier.
- **index**: *faster lookup*.
- **packet**: unit of *transport*.
- **port**: *connection* number.

## Before/After

**Before**: The *DB* is a *black box*.

**After**: *Query* and *latency* are *measurable*.

## Hands-on: SQL and Sockets Basics

### Step 1 — In-memory SQL

```python
import sqlite3
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE u(id INT, name TEXT)")
```

### Step 2 — Insert

```python
con.execute("INSERT INTO u VALUES (1, 'kim')")
```

### Step 3 — Query

```python
rows = con.execute("SELECT * FROM u WHERE id = 1").fetchall()
```

### Step 4 — Index

```python
con.execute("CREATE INDEX ux ON u(id)")
```

### Step 5 — HTTP call

```python
import urllib.request
print(urllib.request.urlopen("http://example.com").status)
```

## What to Notice in This Code

- *DB connection* is *session* scoped.
- *INDEX* reduces *latency*.
- *HTTP status* is an *integer*.

## Five Common Mistakes

1. **Doing *full scans* without *WHERE*.**
2. **The *N+1* query pattern.**
3. **Concurrent writes *without transactions*.**
4. **No *connection pool*, fresh connection every call.**
5. **Confusing *port* and *protocol*.**

## How This Shows Up in Production

*Most* incidents start with a *DB lock* or *network timeout*.

## How a Senior Engineer Thinks

- Look at *read/write* mix.
- *Indexes* have *cost*.
- *Protocols* are *contracts*.
- *Latency* is *measured*.
- *Errors* are *classified*.

## Checklist

- [ ] *Index* planned.
- [ ] *Transaction* boundary.
- [ ] *Connection pool* used.
- [ ] *Timeout* set.

## Practice Problems

1. Define *primary key* in one line.
2. Define *TCP* in one line.
3. State the meaning of *HTTP* in one line.

## Wrap-up and Next Steps

Next post: *AI and Data Science*.

<!-- toc:begin -->
- [What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Understanding First Year Subjects](./02-first-year-subjects.md)
- [Data Structures and Algorithms](./03-data-structures-and-algorithms.md)
- [Understanding Systems Subjects](./04-systems-subjects.md)
- **Database and Network (current)**
- AI and Data Science (upcoming)
- Project Subjects (upcoming)
- How to Study Computer Science (upcoming)
- Build Your Portfolio (upcoming)
- Skills to Have Before Graduation (upcoming)
<!-- toc:end -->

## References

- [Database System Concepts](https://www.db-book.com/)
- [SQLite Documentation](https://sqlite.org/docs.html)
- [Computer Networking: A Top-Down Approach](https://gaia.cs.umass.edu/kurose_ross/index.php)
- [MDN HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)

Tags: CS, Database, Network, SQL, Beginner
