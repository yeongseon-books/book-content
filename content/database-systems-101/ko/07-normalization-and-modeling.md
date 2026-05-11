---
series: database-systems-101
episode: 7
title: 정규화와 모델링
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
  - 정규화
  - 모델링
  - 1NF
  - 의존성
seo_description: 1NF부터 3NF까지 정규화의 직관과 함수 종속을 이용한 데이터 모델링 원칙을 정리합니다.
last_reviewed: '2026-05-04'
---

# 정규화와 모델링

> Database Systems 101 시리즈 (7/10)


## 이 글에서 다룰 문제

엉성한 모델은 모든 쿼리에 비용을 부과합니다. 같은 사실이 여러 곳에 흩어져 있으면 갱신할 때마다 누락이 생기고, JOIN으로 합쳐 보니 결과가 다릅니다. 정규화는 모델 단계에서 그 위험을 제거합니다.

> 좋은 모델은 "이 컬럼 값을 바꾸려면 N행을 동시에 바꿔야 한다"는 상황을 만들지 않습니다.

## 전체 흐름
```mermaid
flowchart LR
    A["원시 테이블"] --> B["1NF: 원자 값"]
    B --> C["2NF: 부분 종속 제거"]
    C --> D["3NF: 이행 종속 제거"]
```

각 단계는 직전 단계를 만족한 위에서 추가 조건을 거는 식입니다. 보통 3NF면 충분합니다.

## Before/After

**Before — 한 테이블에 모두**

```
orders(id, user_id, user_email, product_id, product_name, product_price, quantity)
```

`user_email`은 `user_id`에, `product_name`/`product_price`는 `product_id`에 종속됩니다. 이메일을 바꾸면 그 사용자의 모든 주문 행을 같이 갱신해야 합니다.

**After — 분리**

```
users(id, email)
products(id, name, price)
orders(id, user_id, product_id, quantity)
```

이메일은 `users` 한 행에서만 바뀌고, 모든 주문 쿼리는 JOIN으로 일관된 답을 받습니다.

## 단계별로 정규화하기

### 1단계 — 원시 데이터 살펴보기

```python
# raw.py
rows = [
    (1, 7, "alice@x.com", "P-1, P-2", "Bag, Hat", "20, 5"),
    (2, 7, "alice@x.com", "P-1",       "Bag",      "20"),
]
```

`product_id`가 콤마 리스트입니다. 1NF 위반입니다.

### 2단계 — 1NF: 행으로 풀기

```python
import sqlite3

with sqlite3.connect("shop.db") as db:
    db.executescript("""
        DROP TABLE IF EXISTS order_items_raw;
        CREATE TABLE order_items_raw (
            order_id INTEGER, user_id INTEGER, user_email TEXT,
            product_id TEXT, product_name TEXT, product_price INTEGER
        );
    """)
    db.executemany(
        "INSERT INTO order_items_raw VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1, 7, "alice@x.com", "P-1", "Bag", 20),
            (1, 7, "alice@x.com", "P-2", "Hat", 5),
            (2, 7, "alice@x.com", "P-1", "Bag", 20),
        ],
    )
```

이제 한 셀에 한 값만 들어 있습니다.

### 3단계 — 2NF: 부분 종속 제거

복합 키 `(order_id, product_id)`를 가정하면, `product_name`/`product_price`는 `product_id`에만 종속됩니다. 부분 종속입니다. 따로 분리합니다.

```python
with sqlite3.connect("shop.db") as db:
    db.executescript("""
        DROP TABLE IF EXISTS products;
        CREATE TABLE products (
            id    TEXT PRIMARY KEY,
            name  TEXT NOT NULL,
            price INTEGER NOT NULL
        );
    """)
    db.execute("INSERT INTO products VALUES ('P-1','Bag',20),('P-2','Hat',5)")
```

### 4단계 — 3NF: 이행 종속 제거

`order_id → user_id → user_email`은 이행 종속입니다. 사용자 정보를 별도로 분리합니다.

```python
with sqlite3.connect("shop.db") as db:
    db.executescript("""
        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id    INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE
        );
    """)
    db.execute("INSERT INTO users VALUES (7, 'alice@x.com')")
```

### 5단계 — 최종 모델

```python
with sqlite3.connect("shop.db") as db:
    db.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS order_items;
        CREATE TABLE orders (
            id      INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id)
        );
        CREATE TABLE order_items (
            order_id   INTEGER NOT NULL REFERENCES orders(id),
            product_id TEXT    NOT NULL REFERENCES products(id),
            quantity   INTEGER NOT NULL,
            PRIMARY KEY (order_id, product_id)
        );
    """)
```

각 사실이 단 한 곳에만 존재합니다. 이메일 변경은 `users`에서 한 줄만 고치면 됩니다.

## 이 코드에서 주목할 점

- 정규화는 결국 **함수 종속을 따라 테이블을 쪼개는 일**입니다.
- 외래 키는 일관성을 보장하는 강력한 도구입니다.
- 3NF면 대부분의 OLTP 모델에 충분합니다. BCNF/4NF는 특수한 종속이 있을 때만 고려합니다.

## 자주 하는 실수 5가지

1. **콤마 리스트로 다대다를 표현한다.** 1NF 위반이고, 검색·조인이 모두 깨집니다.
2. **이메일·전화번호 같은 자주 바뀌는 정보를 여러 테이블에 중복한다.** 갱신 누락이 발생합니다.
3. **자연 키(이메일)를 PK로 쓴다.** 값이 바뀔 때마다 외래 키가 전부 따라가야 합니다.
4. **모든 테이블을 끝까지 정규화한다.** 분석 워크로드에서는 종종 비정규화가 옳습니다.
5. **외래 키 제약을 빼고 테이블만 분리한다.** "분리된 척"만 한 모델이 됩니다.

## 실무에서는 이렇게 쓰입니다

OLTP 시스템은 보통 3NF에 가까운 모델로 시작합니다. 이후 특정 화면이 너무 많은 JOIN을 요구하면 캐시 테이블이나 비정규화 컬럼을 의식적으로 추가합니다. 비정규화는 "성능 문제를 측정한 다음" 도입하는 결정이지, 처음부터 손대는 일이 아닙니다.

분석/리포트 영역은 다릅니다. 별도의 OLAP 모델(스타 스키마 등)을 만들어 의도적으로 비정규화합니다. 두 세계가 같은 DB에 함께 살면 자주 충돌하므로, 보통은 데이터 웨어하우스로 분리합니다.

## 체크리스트

- [ ] 모든 컬럼이 원자 값인가?
- [ ] 부분 종속·이행 종속이 없는가?
- [ ] 외래 키 제약이 켜져 있는가?
- [ ] 비정규화 컬럼이 있다면 갱신 책임이 명확한가?
- [ ] 모델 다이어그램이 코드와 동기화되어 있는가?

## 정리 및 다음 단계

정규화는 함수 종속을 따라 모델을 쪼개 "같은 사실은 한 곳에" 두는 작업입니다. 1NF·2NF·3NF는 그 원칙을 단계별 체크리스트로 정리한 것이고, 외래 키는 그 원칙을 강제하는 도구입니다. 다음 글에서는 모델과 인덱스를 받아 옵티마이저가 어떻게 빠른 실행 계획을 만드는지 — 쿼리 최적화 — 를 다룹니다.

<!-- toc:begin -->
- [데이터베이스 시스템이란 무엇인가?](./01-what-is-a-database.md)
- [관계형 모델](./02-relational-model.md)
- [SQL과 쿼리 처리](./03-sql-and-query-processing.md)
- [인덱스](./04-indexes.md)
- [트랜잭션과 ACID](./05-transactions-and-acid.md)
- [isolation level](./06-isolation-levels.md)
- **정규화와 모델링 (현재 글)**
- 쿼리 최적화 (예정)
- 복제와 백업 (예정)
- OLTP와 OLAP (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Database Normalization](https://en.wikipedia.org/wiki/Database_normalization)
- [PostgreSQL — Data Modeling](https://www.postgresql.org/docs/current/ddl.html)
- [Designing Data-Intensive Applications — Chapter 2](https://dataintensive.net/)
- [Microsoft — Description of the database normalization basics](https://learn.microsoft.com/en-us/office/troubleshoot/access/database-normalization-description)

Tags: Computer Science, Database, 정규화, 모델링, 1NF, 의존성
