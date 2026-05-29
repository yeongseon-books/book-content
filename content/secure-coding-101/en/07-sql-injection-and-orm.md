---
series: secure-coding-101
episode: 7
title: "Secure Coding 101 (7/10): SQL Injection and Safe ORM Usage"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SQLInjection
  - ORM
  - Database
  - SecureCoding
  - OWASP
seo_description: Parameterized queries, safe ORM patterns, raw SQL pitfalls, and a five-step playbook to defeat SQL injection for good.
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (7/10): SQL Injection and Safe ORM Usage

SQL injection is old, but it remains expensive because one mistake can hand over not just a page or a user account, but the entire database behind the application. A single f-string in the wrong place can become an authentication bypass, a data dump, and a destructive write path at the same time.

This is the 7th post in the Secure Coding 101 series.

Here, we will treat SQL injection as a structural error in how code combines syntax and data, not as a problem that disappears automatically once an ORM is in place. That distinction is what helps you reason clearly about raw SQL, dynamic identifiers, ORM escape hatches, and database account permissions.

> SQL injection almost always comes from the same root cause: building SQL by string composition instead of sending data as data.


![secure coding 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/07/07-01-concept-at-a-glance.en.png)
*secure coding 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying SQL Injection and Safe ORM Usage?
- Which signal should the example or diagram make visible for SQL Injection and Safe ORM Usage?
- What failure should be prevented first when SQL Injection and Safe ORM Usage reaches a real system?

## Questions This Chapter Answers

- How *SQL injection* works
- Why *parameterized queries* matter
- When ORMs *still leak*
- How to use *raw SQL* safely
- A five-step routine and five common mistakes

## Why It Matters

A single SQLi exposes the *entire database*. Auth bypass, data exfiltration, and tampering — all at once.

> *If SQL is built from string concatenation, it *will leak* one day.*

## Key Terms

- **SQL Injection**: input that *changes the meaning* of the SQL.
- **Parameterized query**: SQL and data are *syntactically separated*.
- **Prepared statement**: SQL the DB *pre-compiles*.
- **ORM**: a library that builds SQL from an *object model*.
- **Stored procedure**: a function *stored inside the DB*.

## Before/After

**Before**: `f"SELECT * FROM users WHERE name='{name}'"` — *plain SQLi*.

**After**: `cursor.execute("SELECT * FROM users WHERE name=%s", (name,))` — *parameter*.

## Hands-on: Defend SQLi in Five Steps

### Step 1 — Use parameters

```python
cursor.execute(
    "SELECT id FROM users WHERE name=%s AND status=%s",
    (name, "active"),
)
```

### Step 2 — Use the ORM properly

```python
from sqlalchemy import select
stmt = select(User).where(User.name == name)
result = session.scalars(stmt).all()
```

### Step 3 — Allowlist any dynamic column

```python
ALLOWED = {"name", "created_at", "id"}
def order_by(field):
    if field not in ALLOWED:
        raise ValueError("invalid order field")
    return field  # safe to splice into SQL
```

### Step 4 — Even raw SQL must use *parameters*

```python
session.execute(text("SELECT * FROM logs WHERE user_id=:uid"), {"uid": uid})
```

### Step 5 — Split DB privileges

```sql
-- The app account does DML only; DDL belongs to a separate account.
GRANT SELECT, INSERT, UPDATE ON db.* TO 'app'@'%';
```

## How to verify the query path before production

It is worth checking the dangerous cases explicitly instead of assuming the ORM got everything right.

```python
payload = "' OR 1=1 --"

# Safe path: returns only matching rows for the literal payload value
cursor.execute("SELECT id FROM users WHERE name=%s", (payload,))

# Unsafe path: payload changes the SQL itself
sql = f"SELECT id FROM users WHERE name='{payload}'"
```

**Expected result:** the parameterized version treats the payload as a string value and returns either zero or legitimate matches. The interpolated version changes the query meaning and can return unintended rows. This is the fastest possible demonstration to keep in a team code review.

## What to Notice in This Code

- *String concatenation* into SQL is a *red flag* every time.
- An ORM is no shield if you misuse `text()` or raw escapes.
- *Dynamic identifiers* require an *allowlist* — there is no other safe option.

## Five Common Mistakes

1. **f-strings inside SQL.** The most common SQLi.
2. **String composition inside an ORM `.filter()`.** False sense of safety.
3. **Order-by columns taken *directly from input*.** Dynamic-column SQLi.
4. **Granting *DROP* to the app account.** Catastrophic blast radius.
5. **Echoing the *raw SQL* in error messages.** Fuel for *blind SQLi*.

## How This Shows Up in Production

Most teams default to the ORM and treat *raw SQL* as the exception. Every raw SQL line is reviewed for *parameter use*. The application's DB account is on *least privilege*.

## How a Senior Engineer Thinks

- *Treat string-built SQL as *not allowed*.*
- *Dynamic identifiers go through an *allowlist*.*
- *DB accounts also follow *least privilege*.*
- *Never let *SQL leak into error messages*.*
- *ORMs are a *safe habit*, not a magic shield.*

## Checklist

- [ ] All SQL uses *parameters*.
- [ ] Dynamic columns/tables go through an *allowlist*.
- [ ] DB accounts are *role-separated*.
- [ ] Error messages stay *safe*.

## Practice Problems

1. Explain *blind SQLi* in one paragraph.
2. Show two safe patterns for using *raw text* in an ORM.
3. Write the *order-by allowlist* helper.

## Wrap-up and Next Steps

A safe DB removes the attacker's *biggest prize*. Next we cover the two browser-side attacks — *XSS and CSRF*.

## Answering the Opening Questions

- **How exactly does SQL injection alter SQL semantics?**
  - When user input enters SQL built via string concatenation, closing quotes or inserting comments (`--`) can nullify the original query's conditions or append new SQL statements. As the Blind SQLi section showed, even without visible results, response time or true/false condition differences can extract data.
- **Why is a parameterized query the most important fundamental?**
  - Parameter binding separates SQL syntax from values at the grammar level. The database interprets the query first and fills values afterward, so no matter how malicious the input, it cannot alter SQL semantics. This single principle structurally blocks regular SQLi, Blind SQLi, and second-order injection.
- **When can SQL injection occur even when using an ORM?**
  - As the SQLAlchemy mistake patterns section showed, using f-strings inside `text()`, passing string conditions to `filter`, or directly accepting input values as sort columns causes injection even with an ORM. Use the ORM's query builder, but at any raw SQL point, always verify bind parameters.

## Deep Dive: Blind SQLi, Second-Order Injection, NoSQL Injection, Stored Procedures

### Understanding and Detecting Blind SQL Injection

Blind SQLi succeeds even when query results never appear on screen. Attackers extract data one character at a time by observing response differences (Boolean-based) or timing (Time-based).

```python
# Boolean-based blind SQLi demonstration
# Attacker sends these as the 'name' parameter
payload_true  = "admin' AND SUBSTRING(password,1,1)='a' --"
payload_false = "admin' AND SUBSTRING(password,1,1)='z' --"

# Vulnerable code — string concatenation
query = f"SELECT * FROM users WHERE name='{name}'"
# payload_true → returns data (200 OK with results)
# payload_false → empty result (200 OK, no data)
# The difference leaks the password character by character
```

```python
# Time-based blind SQLi
payload = "admin'; SELECT CASE WHEN (SUBSTRING(password,1,1)='a') THEN pg_sleep(3) ELSE pg_sleep(0) END --"
# If response takes 3 seconds, first character is 'a'
```

Blind SQLi is harder to detect than classic injection. WAFs can block time functions (`SLEEP`, `BENCHMARK`, `pg_sleep`), but Boolean-based payloads resemble normal queries. The fundamental defense remains identical — parameter binding structurally prevents it.

```python
# Defense: parameter binding makes blind SQLi impossible
cursor.execute("SELECT * FROM users WHERE name=%s", (name,))
# Payload treated as a literal string value → condition manipulation impossible
```

### Second-Order Injection

Second-order injection stores a benign-looking value that becomes dangerous when used in a different query later. It demonstrates why "already validated" does not mean "safe to concatenate."

```python
# Step 1: User registration — input stored safely via parameters
username = "admin'--"
cursor.execute("INSERT INTO users (name) VALUES (%s)", (username,))
# DB stores the literal string "admin'--" (safe so far)

# Step 2: Another feature retrieves and uses the stored value
row = cursor.fetchone()  # row[0] = "admin'--"
# Vulnerable — trusts stored value and concatenates
query = f"SELECT * FROM orders WHERE user_name='{row[0]}'"
# → SELECT * FROM orders WHERE user_name='admin'--'
# → Condition neutralized, all orders exposed
```

**Lesson**: Values retrieved from the database must be treated with the same suspicion as external input. The assumption "it was already validated" is exactly what causes second-order injection.

```python
# Fix: use parameter binding even for stored values
cursor.execute("SELECT * FROM orders WHERE user_name=%s", (row[0],))
```

### NoSQL Injection

Document databases like MongoDB are also vulnerable to injection. Instead of SQL syntax, attackers inject query operators.

```python
from flask import request
from pymongo import MongoClient

db = MongoClient().mydb

# Vulnerable — request.json passed directly to query
@app.post("/login")
def login():
    body = request.json
    # body = {"username": "admin", "password": {"$ne": ""}}
    user = db.users.find_one({
        "username": body["username"],
        "password": body["password"]  # {"$ne": ""} matches all non-empty passwords
    })
    if user:
        return {"status": "logged in"}  # auth bypass
```

```python
# Fix 1: Type enforcement
@app.post("/login")
def login():
    body = request.json
    username = str(body.get("username", ""))
    password = str(body.get("password", ""))  # force string type
    user = db.users.find_one({"username": username, "password": password})

# Fix 2: Schema enforcement with Pydantic
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str  # operator objects fail validation

@app.post("/login")
def login(req: LoginRequest):
    user = db.users.find_one({"username": req.username, "password": req.password})
```

The core of NoSQL injection defense is blocking query operators (`$ne`, `$gt`, `$regex`, etc.) from entering as input. Enforce types or reject keys with `$` prefixes.

### Safe Use of Stored Procedures

A common misconception is that stored procedures automatically prevent SQL injection. If a procedure uses dynamic SQL internally, the same vulnerability applies.

```sql
-- Vulnerable stored procedure (MySQL)
CREATE PROCEDURE search_users(IN search_term VARCHAR(255))
BEGIN
    SET @query = CONCAT('SELECT * FROM users WHERE name LIKE ''%', search_term, '%''');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END;

-- Fixed: use parameter binding
CREATE PROCEDURE search_users_safe(IN search_term VARCHAR(255))
BEGIN
    SET @search = CONCAT('%', search_term, '%');
    PREPARE stmt FROM 'SELECT * FROM users WHERE name LIKE ?';
    EXECUTE stmt USING @search;
    DEALLOCATE PREPARE stmt;
END;
```

The security benefit of stored procedures is not injection prevention but privilege separation. Granting the application account EXECUTE permission on procedures rather than direct table access limits what a successful injection can do.

### Common SQLAlchemy Mistakes

Using an ORM well is safe, but these patterns create SQLi even inside ORM code.

```python
from sqlalchemy import text, column, desc
from sqlalchemy.orm import Session

# ❌ Mistake 1: string formatting inside text()
def search_users(session: Session, keyword: str):
    # Vulnerable
    return session.execute(text(f"SELECT * FROM users WHERE name LIKE '%{keyword}%'"))

# ✅ Fix: bind parameters in text()
def search_users_safe(session: Session, keyword: str):
    return session.execute(
        text("SELECT * FROM users WHERE name LIKE :kw"),
        {"kw": f"%{keyword}%"}
    )

# ❌ Mistake 2: user input directly in order_by
def get_sorted(session: Session, sort_field: str):
    # What if sort_field is "name; DROP TABLE users--"?
    return session.execute(text(f"SELECT * FROM users ORDER BY {sort_field}"))

# ✅ Fix: allowlist + getattr
SORT_COLUMNS = {"name": User.name, "created_at": User.created_at, "id": User.id}

def get_sorted_safe(session: Session, sort_field: str):
    col = SORT_COLUMNS.get(sort_field)
    if col is None:
        raise ValueError(f"Invalid sort field: {sort_field}")
    return session.query(User).order_by(col).all()

# ❌ Mistake 3: string conditions in filter
def find_active(session: Session, status: str):
    # Vulnerable
    return session.query(User).filter(text(f"status = '{status}'"))

# ✅ Fix: ORM comparison operators
def find_active_safe(session: Session, status: str):
    return session.query(User).filter(User.status == status).all()
```

### Static Analysis for SQL Injection Detection

Code review alone cannot catch every SQL string concatenation. Static analysis tools in CI detect them automatically.

```bash
# Bandit — Python security static analysis
pip install bandit
bandit -r src/ -t B608  # B608: SQL injection detection rule

# Example output:
# >> Issue: [B608:hardcoded_sql_expressions]
#    Severity: Medium   Confidence: Low
#    Location: src/users/repository.py:45
#    45  query = f"SELECT * FROM users WHERE id = {user_id}"
```

```yaml
# CI pipeline integration
- name: SQL injection scan
  run: |
    pip install bandit
    bandit -r src/ -t B608 -f json -o bandit-report.json
    if [ $? -ne 0 ]; then
      echo "SQL injection risk detected"
      exit 1
    fi
```

Semgrep supports custom rules for project-specific patterns:

```yaml
# .semgrep/sql-injection.yaml
rules:
  - id: raw-sql-format-string
    patterns:
      - pattern: |
          $QUERY = f"...{$VAR}..."
      - metavariable-regex:
          metavariable: $QUERY
          regex: ".*(SELECT|INSERT|UPDATE|DELETE).*"
    message: "Do not use f-strings in SQL queries. Use parameter binding."
    severity: ERROR
    languages: [python]
```

### Incident Response After SQL Injection

Detection and response planning is needed for when defenses are breached.

```python
# Query anomaly detection — slow query / suspicious pattern monitoring
import logging
import time

logger = logging.getLogger("sql.audit")

class QueryAuditor:
    SUSPICIOUS_PATTERNS = [
        "UNION SELECT", "OR 1=1", "SLEEP(", "BENCHMARK(",
        "pg_sleep", "WAITFOR DELAY", "INTO OUTFILE",
    ]

    def audit_query(self, query: str, params: tuple, duration_ms: float):
        # 1. Time-based blind SQLi detection
        if duration_ms > 3000:
            logger.warning("slow_query", extra={
                "query_hash": hash(query),
                "duration_ms": duration_ms,
                "alert": "possible_time_based_sqli"
            })

        # 2. Suspicious pattern detection
        query_upper = query.upper()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in query_upper:
                logger.error("suspicious_query_pattern", extra={
                    "pattern": pattern,
                    "query_hash": hash(query),
                    "alert": "possible_sqli_attempt"
                })
```

```text
Operational response checklist:
1. Check DB audit logs for anomalous query patterns
2. Verify data integrity of affected tables
3. Determine scope of potentially leaked data (based on SELECT permissions)
4. Check for data tampering (UPDATE/DELETE logs)
5. Patch the vulnerable endpoint and confirm the same input is blocked
6. Request password resets for affected users (if data was exfiltrated)
```

### LIKE Clause and Wildcard Injection

Even with parameter binding, LIKE clauses allow unintended pattern matching via wildcard characters (`%`, `_`). This is not SQL injection per se, but it can leak data.

```python
# Problem: user inputs '%' and all rows match
keyword = request.args.get("q")  # user sends "%"
cursor.execute("SELECT * FROM products WHERE name LIKE %s", (f"%{keyword}%",))
# → SELECT * FROM products WHERE name LIKE '%%%' → returns everything

# Fix: escape wildcards
def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

safe_keyword = escape_like(keyword)
cursor.execute(
    "SELECT * FROM products WHERE name LIKE %s ESCAPE '\\'",
    (f"%{safe_keyword}%",)
)
```

### Multi-Database Considerations

In microservice environments, different services often use different databases. PostgreSQL, MySQL, SQLite, and Oracle each have different SQL dialects, and injection payloads differ accordingly.

```text
Time-delay functions per database (used in time-based blind SQLi):
- PostgreSQL: pg_sleep(5)
- MySQL: SLEEP(5), BENCHMARK(10000000, SHA1('test'))
- SQLite: no time function → use heavy queries instead
- MSSQL: WAITFOR DELAY '0:0:5'
- Oracle: DBMS_PIPE.RECEIVE_MESSAGE('x', 5)

Comment syntax per database:
- MySQL/PostgreSQL/SQLite: -- (space required), /* */
- MySQL only: #
- Oracle: -- (space required)
```

This means WAF rules or input filtering alone can be bypassed depending on the database type. Parameter binding works regardless of database — it must always be the foundation of defense.

### Safe Patterns for Bulk Queries and Batch Processing

Report generation and data migration scripts often need dynamic conditions, tempting developers toward raw SQL. Safe patterns exist even here.

```python
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session

# Dynamic IN clause — safe handling
def get_users_by_ids(session: Session, user_ids: list[int]):
    if not user_ids:
        return []
    # SQLAlchemy's expanding bind parameter
    stmt = text("SELECT * FROM users WHERE id IN :ids")
    stmt = stmt.bindparams(bindparam("ids", expanding=True))
    return session.execute(stmt, {"ids": user_ids}).fetchall()

# Dynamic WHERE conditions — ORM query builder
from sqlalchemy import and_, or_

def search_users(session: Session, filters: dict):
    query = session.query(User)
    conditions = []

    if "name" in filters:
        conditions.append(User.name.ilike(f"%{escape_like(filters['name'])}%"))
    if "status" in filters:
        if filters["status"] not in ("active", "inactive", "suspended"):
            raise ValueError("invalid status")
        conditions.append(User.status == filters["status"])
    if "min_age" in filters:
        conditions.append(User.age >= int(filters["min_age"]))

    if conditions:
        query = query.filter(and_(*conditions))
    return query.all()
```

Core principle: even when dynamic queries are needed, the dynamic part is *which conditions to include*, not *how to concatenate SQL strings*. The ORM's query builder naturally enforces this distinction.

<!-- toc:begin -->
## In this series

- [Secure Coding 101 (1/10): What Is Secure Coding?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): Input Validation](./02-input-validation.md)
- [Secure Coding 101 (3/10): Authentication and Session](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): Authorization and Permissions](./04-authorization-and-permissions.md)
- [Secure Coding 101 (5/10): Safe Data Storage](./05-safe-data-storage.md)
- [Secure Coding 101 (6/10): Secret and Key Management](./06-secret-and-key-management.md)
- **SQL Injection and Safe ORM Usage (current)**
- XSS and CSRF Defense (upcoming)
- Managing Dependency Vulnerabilities (upcoming)
- Safe Logging and Audit (upcoming)

<!-- toc:end -->

## References

- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger — SQL injection](https://portswigger.net/web-security/sql-injection)
- [SQLAlchemy security](https://docs.sqlalchemy.org/)
- [psycopg parameter binding](https://www.psycopg.org/psycopg3/docs/basic/params.html)
- [SQLAlchemy — Selecting with textual SQL](https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html)

Tags: SQLInjection, ORM, Database, SecureCoding, OWASP
