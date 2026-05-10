---
series: database-systems-101
episode: 4
title: 인덱스
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Database
  - Index
  - BTree
  - 선택성
  - 성능
seo_description: B-tree 인덱스가 어떻게 동작하는지, 언제 효과가 크고 언제 의미가 없는지 선택성과 함께 정리합니다.
last_reviewed: '2026-05-04'
---

# 인덱스

> Database Systems 101 시리즈 (4/10)


## 이 글에서 다룰 문제

성능 문제의 다수는 "없는 인덱스" 또는 "잘못 만든 인덱스"입니다. 동시에, 너무 많은 인덱스는 쓰기 성능을 망가뜨리고 디스크를 먹습니다. 인덱스 직관을 한 번 잡으면 EXPLAIN을 읽을 때 "왜 이걸 안 탔지?"가 보입니다.

> 인덱스는 책 뒷면의 색인과 똑같습니다. 색인이 있으면 단어 하나는 빠르게 찾지만, 모든 페이지를 한 번씩 보는 일은 더 느리게 만듭니다.

## 개념 한눈에 보기

```mermaid
flowchart TB
    A["B-tree root"] --> B["internal node"]
    A --> C["internal node"]
    B --> D["leaf: (value → row id)"]
    B --> E["leaf"]
    C --> F["leaf"]
    C --> G["leaf"]
```

루트에서 시작해 한 단계씩 좁혀 잎(leaf)에서 행 위치를 얻습니다. 깊이는 거의 일정해서 1억 행에서도 몇 단계만에 답에 닿습니다.

## Before/After

**Before — 인덱스 없이 1만 건 조회**

```sql
SELECT * FROM orders WHERE user_id = 7;
-- 100ms (풀스캔)
```

**After — 적절한 인덱스 한 개**

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id);
SELECT * FROM orders WHERE user_id = 7;
-- 1ms 미만 (인덱스 조회)
```

선택성이 충분히 좋으면 흔히 100배 이상의 차이가 납니다.

## 실습: 인덱스의 효과와 한계 직접 보기

### 1단계 — 데이터 준비

```python
# seed.py
import sqlite3, random

with sqlite3.connect("shop.db") as db:
    db.executescript("""
        DROP TABLE IF EXISTS orders;
        CREATE TABLE orders (
            id      INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            status  TEXT    NOT NULL,
            price   INTEGER NOT NULL
        );
    """)
    rows = [
        (i, random.randint(1, 1000), random.choice(["paid", "pending"]), random.randint(1, 1000))
        for i in range(1, 100001)
    ]
    db.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", rows)
```

`user_id`는 1000개의 다른 값(선택성 1/1000), `status`는 두 값(선택성 1/2)입니다.

### 2단계 — 좋은 인덱스 (선택성 높음)

```python
import sqlite3

with sqlite3.connect("shop.db") as db:
    db.execute("CREATE INDEX IF NOT EXISTS idx_user ON orders(user_id)")
    db.execute("ANALYZE")
    plan = db.execute("EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 7").fetchall()
    print(plan)
```

옵티마이저가 `idx_user`를 탑니다.

### 3단계 — 나쁜 인덱스 (선택성 낮음)

```python
with sqlite3.connect("shop.db") as db:
    db.execute("CREATE INDEX IF NOT EXISTS idx_status ON orders(status)")
    db.execute("ANALYZE")
    plan = db.execute("EXPLAIN QUERY PLAN SELECT * FROM orders WHERE status = 'paid'").fetchall()
    print(plan)
```

옵티마이저가 풀스캔을 고를 가능성이 큽니다. 절반의 행을 인덱스로 하나씩 가져오느니 다 훑는 게 빠릅니다.

### 4단계 — 복합 인덱스와 컬럼 순서

```python
with sqlite3.connect("shop.db") as db:
    db.execute("CREATE INDEX IF NOT EXISTS idx_user_status ON orders(user_id, status)")
    db.execute("ANALYZE")

    p1 = db.execute("EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id=7 AND status='paid'").fetchall()
    p2 = db.execute("EXPLAIN QUERY PLAN SELECT * FROM orders WHERE status='paid'").fetchall()
    print(p1)
    print(p2)
```

`(user_id, status)` 인덱스는 `user_id`로 시작하는 쿼리에는 효과가 큽니다. `status`만으로 시작하는 쿼리에는 거의 도움이 안 됩니다. **선두 컬럼이 핵심**입니다.

### 5단계 — 커버링 인덱스

```python
with sqlite3.connect("shop.db") as db:
    db.execute("CREATE INDEX IF NOT EXISTS idx_cover ON orders(user_id, price)")
    db.execute("ANALYZE")
    plan = db.execute("EXPLAIN QUERY PLAN SELECT user_id, price FROM orders WHERE user_id=7").fetchall()
    print(plan)
```

쿼리에 필요한 컬럼이 인덱스 안에 모두 있으면 테이블 본체를 거의 안 봅니다. "index-only scan"의 가장 단순한 형태입니다.

## 이 코드에서 주목할 점

- 인덱스는 **선택성이 좋을 때** 빛납니다. 절반을 가리키는 인덱스는 옵티마이저가 일부러 무시합니다.
- 복합 인덱스는 **선두 컬럼**이 가장 중요합니다.
- 커버링 인덱스는 "빠른 읽기"의 비밀 무기지만, 컬럼이 늘면 인덱스 자체가 커집니다.
- 인덱스는 쓰기마다 갱신됩니다. INSERT/UPDATE 비용이 함께 늘어납니다.

## 자주 하는 실수 5가지

1. **모든 컬럼에 인덱스를 만든다.** 쓰기 비용과 디스크가 폭발하고 옵티마이저가 헷갈립니다.
2. **선택성 낮은 컬럼에 단일 인덱스를 만든다.** `is_active`, `gender` 같은 컬럼은 단독 인덱스로 거의 쓸모없습니다.
3. **복합 인덱스의 컬럼 순서를 데이터 모양과 다르게 정한다.** 자주 첫 조건으로 들어오는 컬럼이 선두여야 합니다.
4. **인덱스를 만들고 EXPLAIN을 안 본다.** 만들어 놨다고 옵티마이저가 쓰는 것은 아닙니다.
5. **`LIKE '%foo%'`에 단순 B-tree 인덱스를 기대한다.** 앞이 와일드카드면 인덱스가 안 탑니다. 별도 풀텍스트 인덱스가 필요합니다.

## 실무에서는 이렇게 쓰입니다

새 쿼리를 도입할 때는 거의 항상 두 단계를 합니다. (1) 의도한 쿼리에 EXPLAIN을 돌려 본다, (2) 필요한 인덱스가 있는지 확인하고, 없으면 만들고, 있는데 안 타면 이유를 본다. 인덱스를 추가할 때는 "이 인덱스가 어떤 쿼리에 쓰이는가?"를 한 줄 코멘트로 남깁니다. 그래야 1년 뒤에 안전하게 정리할 수 있습니다.

쓰기 위주 워크로드에서는 인덱스를 줄이는 것도 의식적으로 합니다. 분석 시스템처럼 쓰기가 적고 읽기가 다양하면 인덱스가 아니라 컬럼나 저장(columnar)·물리화 뷰(materialized view)·요약 테이블이 더 적절할 때가 많습니다.

## 체크리스트

- [ ] 자주 사용되는 WHERE/JOIN 컬럼에 인덱스가 있는가?
- [ ] 단일 인덱스 대상의 선택성이 충분한가?
- [ ] 복합 인덱스 선두 컬럼이 자주 사용되는 조건인가?
- [ ] 만든 인덱스를 EXPLAIN으로 사용 여부를 확인했는가?
- [ ] 쓰기 비용 증가를 감내할 수 있는 워크로드인가?

## 정리 및 다음 단계

인덱스는 "값 → 행"을 정렬해 두고 한두 번의 트리 점프로 답을 찾게 해 주는 자료 구조입니다. 가장 큰 효과는 **선택성**과 **선두 컬럼**에서 옵니다. 좋은 인덱스 설계는 "어디 만들지"보다 "어디 만들지 않을지"의 결정입니다. 다음 글에서는 같은 데이터를 둘 이상이 동시에 만질 때를 안전하게 해 주는 도구 — 트랜잭션과 ACID — 를 다룹니다.

<!-- toc:begin -->
- [데이터베이스 시스템이란 무엇인가?](./01-what-is-a-database.md)
- [관계형 모델](./02-relational-model.md)
- [SQL과 쿼리 처리](./03-sql-and-query-processing.md)
- **인덱스 (현재 글)**
- 트랜잭션과 ACID (예정)
- isolation level (예정)
- 정규화와 모델링 (예정)
- 쿼리 최적화 (예정)
- 복제와 백업 (예정)
- OLTP와 OLAP (예정)
<!-- toc:end -->

## 참고 자료

- [Use The Index, Luke!](https://use-the-index-luke.com/)
- [PostgreSQL — Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [SQLite — Query Planning](https://www.sqlite.org/queryplanner.html)
- [MySQL — How MySQL Uses Indexes](https://dev.mysql.com/doc/refman/8.0/en/mysql-indexes.html)

Tags: Computer Science, Database, Index, BTree, 선택성, 성능
