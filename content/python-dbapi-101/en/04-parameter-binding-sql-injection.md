---
title: Parameter binding and SQL injection defense (sqlite3, PEP 249)
series: python-dbapi-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLite
- SQL Injection
- Parameter Binding
- PEP 249
- Security
last_reviewed: '2026-05-03'
seo_title: Parameter binding and SQL injection defense
seo_description: 'The key point: SQL tokenization happens before binding. ? tells
  the parser "a single value goes here." Whatever value arrives is never re-parsed
  as…'
---

# Parameter binding and SQL injection defense (sqlite3, PEP 249)

SQL injection starts the moment query text and user input become the same string. This post uses sqlite3 to show how PEP 249 parameter binding keeps them separate and why that design matters in production.

This is the 4th article in the Python DB-API 101 series.

![Parameter binding and SQL injection defense (sqlite3, PEP 249)](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-01-parameter-binding-and-sql-injection-defe.en.png)

*Parameter binding and SQL injection defense (sqlite3, PEP 249)*
## Questions this post answers

- Why is building SQL with f-strings dangerous?
- When do you use `?` versus `:name` placeholders?
- How does binding work with `executemany` for bulk inserts?
- Why can't you bind table or column names?
- What does it mean that `paramstyle` differs by driver?

> SQL injection happens at the moment the query string and user input meet. PEP 249's parameter binding keeps the two separate end-to-end.

## What you will learn

This post covers PEP 249 parameter binding in depth using `sqlite3`. Specifically:

1. **Two placeholder styles** — `?` (qmark) and `:name` (named), both supported by sqlite3.
2. **`executemany` and binding** — list-of-tuples versus list-of-dicts inputs.
3. **Driver-specific paramstyles** — why PEP 249 defines five (`qmark`, `format`, `named`, `pyformat`, `numeric`).
4. **Where binding does not work** — table names, column names, ORDER BY direction, and how to handle them safely.
5. **Reproduce a real attack** — write deliberately vulnerable code, watch SQL injection succeed, then fix it with binding.

---

## Why this matters

SQL injection has stayed in the OWASP Top 10 for nearly two decades for one reason: **developers assemble SQL strings by hand**. A single `f"SELECT * FROM users WHERE name = '{name}'"` lets `name = "' OR 1=1 --"` return every row in the table.

PEP 249 standardises a defence at the driver layer. `cursor.execute(sql, params)` separates SQL parsing from value binding into **distinct stages**, so user input cannot be reinterpreted as SQL tokens.

This post reproduces the attack with sqlite3 and contrasts it with the binding fix line by line. Once you have seen it work, you stop writing f-string SQL forever.

---

## Mental Model — keep query string and values separate

![Mental model - keep query string and values separate](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-02-mental-model-keep-query-string-and-value.en.png)

*Mental model - keep query string and values separate*
```text
[ User input ] ─┐
                │
                ▼
        [ cursor.execute(SQL, params) ]
                │
       ┌────────┴─────────┐
       ▼                  ▼
  [ SQL parser ]    [ value binder ]
   (parses ?, :name)   (sqlite3 type-checks
                        and escapes safely)
       │                  │
       └────────┬─────────┘
                ▼
        [ prepared statement ]
                │
                ▼
        [ SQLite executes ]
```

The key point: SQL tokenization happens **before** binding. `?` tells the parser "a single value goes here." Whatever value arrives is never re-parsed as SQL. The string `' OR 1=1 --` is treated as a 12-character text value, nothing more.

---

## Core concepts

![Core concepts](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-03-core-concepts.en.png)

*Core concepts*
### qmark style (`?`)

The sqlite3 default. Position-based, so order matters.

```python
cur.execute('SELECT * FROM users WHERE name = ? AND age >= ?', ('Alice', 18))
```

### named style (`:name`)

Native to sqlite3. Bind with a dict, no order dependency, and the same value can appear multiple times.

```python
cur.execute(
    'SELECT * FROM users WHERE name = :name AND created_by = :name',
    {'name': 'Alice'},
)
```

### paramstyle

PEP 249 requires every driver to expose its placeholder style as `module.paramstyle`.

| Style | Example | Drivers |
|---|---|---|
| `qmark` | `WHERE id = ?` | sqlite3 |
| `numeric` | `WHERE id = :1` | (rare) |
| `named` | `WHERE id = :id` | sqlite3, oracledb |
| `format` | `WHERE id = %s` | mysql-connector |
| `pyformat` | `WHERE id = %(id)s` | psycopg, pymysql |

sqlite3 supports both `qmark` and `named`. `import sqlite3; print(sqlite3.paramstyle)` → `'qmark'`. For portable code, either match the target driver's `paramstyle` or use an abstraction such as SQLAlchemy Core.

### Where binding does not apply

Placeholders only fill **value** positions. The following are NOT bindable.

- table names (`FROM ?` ❌)
- column names (`SELECT ? FROM users` ❌)
- ORDER BY direction (`ORDER BY age ?` ❌)
- LIMIT/OFFSET (sqlite3 supports binding here, but many drivers do not)

For these positions, validate against a whitelist and inject as a string.

---

## Before / After

![Before / after](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-04-before-after.en.png)

*Before / after*
### Before — vulnerable code

```python
import sqlite3

con = sqlite3.connect(':memory:')
con.executescript('''
    CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, secret TEXT);
    INSERT INTO users(name, secret) VALUES ('Alice', 'A-token');
    INSERT INTO users(name, secret) VALUES ('Bob',   'B-token');
''')

def find_user_BAD(name: str):
    sql = f"SELECT id, name, secret FROM users WHERE name = '{name}'"
    return con.execute(sql).fetchall()

# Normal call
print(find_user_BAD('Alice'))
# → [(1, 'Alice', 'A-token')]

# Attack
print(find_user_BAD("Alice' OR 1=1 --"))
# → [(1, 'Alice', 'A-token'), (2, 'Bob', 'B-token')]   ← all rows leaked
```

### After — parameter binding

```python
def find_user_OK(name: str):
    sql = 'SELECT id, name, secret FROM users WHERE name = ?'
    return con.execute(sql, (name,)).fetchall()

print(find_user_OK("Alice' OR 1=1 --"))
# → []   ← no user with that name, so empty
```

The diff is a single line. The security outcome is the opposite.

---

## Step-by-step walkthrough

### Step 1 — set up

```python
import sqlite3

con = sqlite3.connect(':memory:')
con.executescript('''
    CREATE TABLE products(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        category TEXT NOT NULL
    );
''')
```

### Step 2 — single-row insert with `?`

```python
con.execute(
    'INSERT INTO products(name, price, category) VALUES (?, ?, ?)',
    ('Notebook', 12000, 'stationery'),
)
con.commit()
```

Always pass values as a **tuple or list**. For a single value, do not forget the trailing comma: `(value,)`.

### Step 3 — `:name` placeholders

```python
con.execute(
    '''INSERT INTO products(name, price, category)
       VALUES (:name, :price, :category)''',
    {'name': 'Pen', 'price': 1500, 'category': 'stationery'},
)
con.commit()
```

Dict keys must match placeholder names exactly.

### Step 4 — bulk insert with `executemany`

```python
rows = [
    ('Eraser', 800,  'stationery'),
    ('Mug',    9000, 'kitchen'),
    ('Lamp',   25000,'home'),
]
con.executemany(
    'INSERT INTO products(name, price, category) VALUES (?, ?, ?)',
    rows,
)
con.commit()
```

Dict-style:

```python
rows = [
    {'name': 'Bowl', 'price': 4000, 'category': 'kitchen'},
    {'name': 'Vase', 'price': 18000,'category': 'home'},
]
con.executemany(
    'INSERT INTO products(name, price, category) VALUES (:name, :price, :category)',
    rows,
)
con.commit()
```

### Step 5 — handling `IN (...)`

A placeholder represents a single value, so `IN (?)` cannot take a list directly. Generate placeholders dynamically.

```python
ids = [1, 3, 5]
placeholders = ','.join('?' * len(ids))
sql = f'SELECT * FROM products WHERE id IN ({placeholders})'
print(con.execute(sql, ids).fetchall())
```

The `placeholders` variable contains only SQL tokens (commas and `?`), so it is safe. The actual values still travel through binding.

### Step 6 — safe dynamic ORDER BY

```python
ALLOWED = {'name', 'price', 'category'}
ALLOWED_DIR = {'ASC', 'DESC'}

def list_products(order_by: str, direction: str):
    if order_by not in ALLOWED or direction.upper() not in ALLOWED_DIR:
        raise ValueError('invalid sort')
    sql = f'SELECT * FROM products ORDER BY {order_by} {direction.upper()}'
    return con.execute(sql).fetchall()
```

The mechanism is **whitelist validation**. User input does end up in the SQL string, but only if it appears in the allowed set, so injection is impossible.

---

## Common mistakes

1. **Building SQL with f-strings.** The most common and most dangerous pattern. Treat it as a hard rule in code review.
2. **Quoting the placeholder.** `WHERE name = '?'` is not a placeholder — it is a literal question mark. The driver fails to recognise it and either errors out or returns wrong results.
3. **Missing trailing comma.** `con.execute(sql, ('Alice'))` treats the string as an iterable of five characters. Use `('Alice',)`.
4. **Trying to bind table or column names.** `cursor.execute('SELECT ? FROM ?', ('id', 'users'))` is a syntax error. Use a whitelist plus f-string for these positions.
5. **Using `%` to "escape".** `sql % values` is Python string formatting, not binding. Injection passes through untouched.
6. **Passing a single dict to `executemany`.** `executemany(sql, {'a': 1})` iterates the dict's keys and misbehaves. Pass a list of dicts: `[{'a': 1}, {'a': 2}]`.
7. **Assuming a paramstyle.** Code written for sqlite3's `?` will not work on psycopg as-is. Check `module.paramstyle` first when adopting a new driver, or move to SQLAlchemy.

---

## Production application

### Static analysis in CI

`bandit` rule `B608` flags SQL string formatting.

```bash
pip install bandit
bandit -r src/ -ll
```

Wire this into CI to block merges.

### Mask values in query logs

If your operational logs print SQL with raw values, PII can leak. With binding, mask values in your log adapter.

```python
def log_sql(sql, params):
    masked = tuple('***' if isinstance(p, str) and len(p) > 0 else p for p in params)
    logger.info('sql=%s params=%s', sql, masked)
```

### Prepared-statement caching

Drivers cache prepared statements keyed by the SQL string. Therefore **keep the SQL string constant and pass values via binding** — that is also faster. Building a different f-string each call invalidates the cache.

### Driver migration

When moving from sqlite3 to PostgreSQL, the most common breakage is paramstyle. Adopting SQLAlchemy Core (`text(':name')` + `bindparam`) or the ORM from the start dramatically reduces driver-swap cost — covered in the upcoming `sqlalchemy-101` series.

---

## Checklist

- [ ] All SQL goes through `cursor.execute(sql, params)`.
- [ ] f-strings, `%`, and `+` for value concatenation into SQL are blocked in code review.
- [ ] Single-value bindings always use `(value,)` with the trailing comma.
- [ ] Non-bindable positions (table/column names) are validated against a whitelist.
- [ ] `IN (...)` generates placeholders dynamically and binds the values.
- [ ] Static analysis such as `bandit B608` runs in CI.
- [ ] Bound values are masked in logs.
- [ ] When introducing a new driver, `module.paramstyle` is checked first.

---

## Exercises

1. **Reproduce the attack.** Run `find_user_BAD` above and confirm every row is returned, then verify the binding version returns an empty result.
2. **`UPDATE` injection.** Try `UPDATE users SET name = '{new_name}' WHERE id = {id}` with `new_name = "x', secret='leaked"`. Then switch to `?` and try again.
3. **Dict-style executemany.** Read a CSV into dicts and insert 1000 rows using `:name` placeholders. Compare wall time against the tuple version.
4. **Whitelist sort.** Call `list_products(direction='DROP TABLE products; --')` and confirm `ValueError` is raised.
5. **Inspect paramstyle.** Install `psycopg2` (or `psycopg`) and `mysql-connector-python` and print each module's `paramstyle`.

---

## Summary and next post

PEP 249 parameter binding is the simplest yet strongest tool for blocking SQL injection. The principle is to keep values and SQL syntax separate end-to-end; for positions where that separation breaks (such as table names), compensate with whitelist validation.

The next post covers **transactions and isolation levels** — the precise meaning of `commit`/`rollback`, sqlite3's `isolation_level=None` autocommit mode, and the BEGIN variants (DEFERRED, IMMEDIATE, EXCLUSIVE) with their lock behaviour, all illustrated with code.

<!-- toc:begin -->
## In this series

- [Why DB-API 2.0 - The Problem PEP 249 Solved](./01-why-db-api-pep-249.md)
- [Connection and Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [execute, executemany, and Fetch Patterns](./03-execute-fetch-patterns.md)
- **Parameter binding and SQL injection defense (sqlite3, PEP 249) (current)**
- Transactions and isolation levels (sqlite3, PEP 249) (upcoming)
- Row factories and type adapters (sqlite3, PEP 249) (upcoming)
- PEP 249 Exception Hierarchy and SQLite Error Handling (upcoming)
- SQLite Connection Management: thread-safety, check_same_thread, and Pooling (upcoming)
- Asynchronous SQLite with aiosqlite (upcoming)
- SQLite Production Patterns: retry, timeout, observability, backup (upcoming)

<!-- toc:end -->

---

## References

- [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 — placeholders](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders)
- [OWASP — SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Bandit — B608 hardcoded_sql_expressions](https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html)
- [SQLite SQL parameters](https://www.sqlite.org/lang_expr.html#varparam)

Tags: Python, DB-API, PEP 249, Database
