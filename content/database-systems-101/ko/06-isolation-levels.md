---
series: database-systems-101
episode: 6
title: "Database Systems 101 (6/10): 격리 수준"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Database
  - Isolation
  - MVCC
  - 동시성
  - 이상현상
seo_description: 격리 수준과 MVCC가 동시성 이상 현상을 막는 원리와 안전성 대 처리량의 트레이드오프를 예제와 함께 정리합니다.
last_reviewed: '2026-05-12'
---

# Database Systems 101 (6/10): 격리 수준

이 글은 Database Systems 101 시리즈의 여섯 번째 글입니다.

동시성 버그는 이상하게도 한가할 때는 잘 보이지 않습니다. 그런데 부하가 몰리고, 두 사용자가 같은 자원을 동시에 만지고, 특정 타이밍이 겹치는 순간 갑자기 잔액이 이상해지고 재고가 음수가 되며 같은 주문이 두 번 생깁니다. 이때 많은 팀이 애플리케이션 코드만 뒤지지만, 실제 원인은 데이터베이스의 격리 수준 선택에 있는 경우가 많습니다.

격리성은 켜고 끄는 스위치가 아니라, 안전성과 처리량 사이를 조정하는 다이얼에 가깝습니다. 너무 느슨하면 이상 현상이 남고, 너무 엄격하면 처리량이 급격히 떨어집니다. 이 글에서는 그 다이얼을 어떻게 읽어야 하는지, 그리고 MVCC와 행 잠금이 어떤 역할을 하는지 정리합니다.

## 먼저 던지는 질문

- 고전적인 동시성 이상 현상 네 가지는 무엇일까요?
- READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE은 무엇이 다를까요?
- MVCC는 어떻게 일관된 읽기를 잠금 없이 제공할까요?

## 큰 그림

![Database Systems 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/database-systems-101/06/06-01-big-picture.ko.png)

*Database Systems 101 6장 흐름 개요*

## 이 글에서 배울 내용

- 고전적인 동시성 이상 현상 네 가지
- 주요 격리 수준들의 차이
- MVCC가 잠금 없이 일관된 읽기를 제공하는 방식
- 워크로드별로 격리 수준을 고르는 감각

## 왜 중요한가

격리 수준을 모르면 “재현되지 않는 버그”의 절반은 설명되지 않습니다. 결제가 두 번 청구되거나, 잔액이 음수가 되거나, 같은 주문이 중복 생성되는 문제는 대개 단위 테스트만으로는 드러나지 않습니다. 동시성 문제는 평온한 환경에서 숨어 있다가, 가장 비싼 순간에 터집니다.

> 동시성 버그는 조용한 날에는 숨어 있다가, 시스템이 가장 바쁠 때 얼굴을 드러냅니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart LR
    A["READ UNCOMMITTED"] --> B["READ COMMITTED"]
    B --> C["REPEATABLE READ"]
    C --> D["SERIALIZABLE"]
    A -.->|"fast but risky"| E["many anomalies"]
    D -.->|"slow but safe"| F["no anomalies"]
```

왼쪽에서 오른쪽으로 갈수록 더 안전하지만 비용도 커집니다. 대부분의 DBMS 기본값은 READ COMMITTED 또는 REPEATABLE READ에 놓여 있습니다.

## 핵심 용어

- **Dirty Read**: 다른 트랜잭션이 아직 커밋하지 않은 값을 읽는 현상입니다.
- **Non-repeatable Read**: 같은 행을 두 번 읽었는데 값이 달라지는 현상입니다.
- **Phantom Read**: 같은 조건으로 두 번 읽었는데 행 개수가 달라지는 현상입니다.
- **Lost Update**: 두 트랜잭션이 같은 행을 동시에 갱신해 한쪽 변경이 사라지는 현상입니다.
- **MVCC**: 한 행의 여러 버전을 유지해 읽기와 쓰기가 서로를 덜 막도록 하는 방식입니다.

## Before/After

**Before — wrong isolation: balance debited twice**

```sql
-- T1: SELECT balance FROM accounts WHERE id=1; -- 1000
-- T2: SELECT balance FROM accounts WHERE id=1; -- 1000
-- T1: UPDATE ... SET balance=900 WHERE id=1;
-- T2: UPDATE ... SET balance=900 WHERE id=1;  -- overwrites T1 (Lost Update)
```

**After — SERIALIZABLE or SELECT ... FOR UPDATE**

```sql
BEGIN;
SELECT balance FROM accounts WHERE id=1 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id=1;
COMMIT;
```

읽는 순간 행 잠금을 잡아 두면, 다른 트랜잭션이 같은 행을 건드리지 못하게 할 수 있습니다.

## 실습: 이상 현상을 직접 재현해 보기

### 1단계 — 두 세션 준비

```python
# Open two psql shells, or two sqlite3 connections.
import sqlite3
c1 = sqlite3.connect("iso.db", isolation_level="DEFERRED")
c2 = sqlite3.connect("iso.db", isolation_level="DEFERRED")

c1.executescript("""
DROP TABLE IF EXISTS counter;
CREATE TABLE counter (id INTEGER PRIMARY KEY, n INTEGER);
INSERT INTO counter VALUES (1, 0);
""")
c1.commit()
```

두 세션이 같은 데이터를 동시에 만지는 상황을 의도적으로 만들기 위한 준비입니다.

### 2단계 — Lost Update 재현

```python
c1.execute("BEGIN")
c2.execute("BEGIN")
n1 = c1.execute("SELECT n FROM counter WHERE id=1").fetchone()[0]
n2 = c2.execute("SELECT n FROM counter WHERE id=1").fetchone()[0]
c1.execute("UPDATE counter SET n=? WHERE id=1", (n1 + 1,))
c2.execute("UPDATE counter SET n=? WHERE id=1", (n2 + 1,))
c1.commit()
c2.commit()
print(c1.execute("SELECT n FROM counter").fetchone())  # 1, not 2
```

두 세션 모두 0을 읽고 각자 1을 썼기 때문에, 한 번의 증가가 사라졌습니다.

### 3단계 — SELECT ... FOR UPDATE로 막기

```python
# PostgreSQL
# T1
# BEGIN;
# SELECT n FROM counter WHERE id=1 FOR UPDATE;  -- lock
# UPDATE counter SET n = n+1 WHERE id=1;
# COMMIT;
# T2: blocks on SELECT ... FOR UPDATE until T1 ends
```

명시적 행 잠금은 두 세션을 사실상 직렬화해 Lost Update를 막는 가장 흔한 도구입니다.

### 4단계 — REPEATABLE READ의 일관 읽기

```sql
-- T1
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM orders WHERE user_id=7;  -- 10

-- T2 (other session): INSERT INTO orders (user_id, ...) VALUES (7, ...); COMMIT;

-- T1
SELECT count(*) FROM orders WHERE user_id=7;  -- still 10
COMMIT;
```

REPEATABLE READ에서는 트랜잭션 시작 시점의 스냅샷을 계속 봅니다. PostgreSQL은 이를 MVCC로 구현해 읽기와 쓰기가 서로를 덜 막도록 만듭니다.

### 5단계 — SERIALIZABLE의 비용

```sql
-- T1, T2 both SERIALIZABLE.
-- T1: SELECT with a predicate, then INSERT
-- T2: same predicate concurrently, then INSERT
-- If the database detects a conflict, one side fails with SQLSTATE 40001.
-- The application must retry.
```

SERIALIZABLE은 가장 안전하지만, 충돌 감지와 재시도라는 운영 비용을 반드시 동반합니다.

## 이 코드에서 먼저 봐야 할 점

- 격리 수준은 옵티마이저가 아니라 **개발자와 시스템 설계자**가 선택합니다.
- MVCC 덕분에 PostgreSQL에서는 “읽기는 쓰기를 막지 않고, 쓰기는 읽기를 막지 않는다”는 기본 감각이 가능합니다.
- `FOR UPDATE`는 행 잠금을 잡는 가장 실용적인 수단입니다.
- SERIALIZABLE을 재시도 로직 없이 쓰면, 시스템은 산발적 실패에 매우 약해집니다.

## 자주 하는 실수 5가지

1. **격리 수준을 의식하지 않고 카운터나 재고를 갱신한다.** Lost Update는 생각보다 쉽게 재현됩니다.
2. **SERIALIZABLE을 켜고 재시도 루프를 만들지 않는다.** 직렬화 실패가 곧바로 사용자 오류가 됩니다.
3. **REPEATABLE READ가 모든 DBMS에서 팬텀까지 막는다고 단정한다.** 구현은 엔진마다 다릅니다.
4. **`SELECT ... FOR UPDATE`를 과하게 남발한다.** 잠금 범위가 넓어지면 동시성이 급격히 나빠집니다.
5. **격리 수준 설정을 코드 어딘가에 묻어 둔다.** 어떤 트랜잭션이 어떤 수준으로 실행되는지 설명하기 어려워집니다.

## 실무에서는 이렇게 드러납니다

대부분의 OLTP 서비스는 READ COMMITTED를 기본으로 두고, 정말 중요한 쓰기 경로에서만 `SELECT ... FOR UPDATE`를 사용합니다. 반면 분석 쿼리나 스냅샷 일관성이 필요한 읽기에는 REPEATABLE READ가 잘 맞는 경우가 있습니다.

정확성이 절대적인 금융·예약 시스템은 SERIALIZABLE을 기본으로 두고, 애플리케이션 레벨에서 재시도 루프를 갖추기도 합니다. 이 경우에는 트랜잭션을 더 짧고 더 멱등하게 설계해야 합니다. 격리 수준을 올리는 선택은 데이터베이스 옵션 하나로 끝나는 일이 아니라, 애플리케이션 재시도 정책과 함께 설계되어야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- “이 트랜잭션이 다른 트랜잭션과 동시에 돌면 무엇이 깨질까?”를 반복해서 묻습니다.
- 잠금 범위를 작게 유지하려고 합니다. 행 잠금이 페이지 잠금, 테이블 잠금처럼 커지는 상황을 경계합니다.
- 재시도 가능한 실패와 불가능한 실패를 명확히 구분합니다.
- 격리 수준 변경은 최우선 코드 리뷰 주제로 다룹니다.
- 동시성 버그는 머릿속 추론만으로 끝내지 않고, 로그와 재현 시나리오로 검증합니다.

## 체크리스트

- [ ] 핵심 쓰기 경로의 격리 수준을 정확히 알고 있는가?
- [ ] Lost Update 가능 지점에 잠금 또는 SERIALIZABLE이 적용되어 있는가?
- [ ] SERIALIZABLE을 쓴다면 재시도 루프가 준비되어 있는가?
- [ ] 트랜잭션이 짧고 외부 호출이 없는가?
- [ ] 적어도 하나 이상의 동시성 시나리오를 통합 테스트로 검증하는가?

## 연습 문제

1. READ COMMITTED에서 여전히 가능한 이상 현상 두 가지를 적어 보세요.
2. MVCC가 어떻게 “읽기는 쓰기를 막지 않고, 쓰기는 읽기를 막지 않는다”를 가능하게 하는지 한 단락으로 설명해 보세요.
3. 카운터 컬럼의 동시 INCREMENT를 안전하게 처리하는 방법 두 가지를 적어 보세요.

## 정리 및 다음 단계

격리 수준은 동시성 안전성과 처리량 사이의 다이얼입니다. 이상 현상과 각 수준의 약속을 이해하면 장애를 만난 뒤에 수습하는 대신, 애초에 실패 모드를 설계할 수 있습니다. 다음 글에서는 한 단계 위로 올라가 데이터 모델 자체의 품질, 즉 정규화와 함수 종속을 살펴봅니다.

## 실전 보강: 실행 계획과 트랜잭션 설계를 한 번에 보는 연습

아래 예시는 관계형 데이터베이스를 운영할 때 자주 만나는 세 가지 질문을 한 번에 다룹니다. 첫째, 이 쿼리가 왜 느린지, 둘째, 어떤 인덱스가 실제로 선택되는지, 셋째, 실패 시 데이터가 어디까지 보존되는지입니다.

### 1) 조건과 정렬을 함께 고려한 인덱스 전략

```sql
-- 주문 조회 API: 특정 사용자 최근 주문 20건
SELECT id, user_id, status, created_at, total_amount
FROM orders
WHERE user_id = 42 AND status = 'paid'
ORDER BY created_at DESC
LIMIT 20;
```

이 쿼리는 보통 `user_id`, `status`, `created_at`의 순서를 가진 복합 인덱스 후보를 만듭니다.

```sql
CREATE INDEX idx_orders_user_status_created
ON orders (user_id, status, created_at DESC);
```

핵심은 **필터링 컬럼을 앞쪽에**, 정렬 컬럼을 그다음에 배치하는 것입니다. 이렇게 하면 WHERE와 ORDER BY를 동시에 만족해 추가 정렬 비용을 줄일 수 있습니다.

### 2) EXPLAIN으로 계획 비교하기

```sql
EXPLAIN ANALYZE
SELECT id, user_id, status, created_at, total_amount
FROM orders
WHERE user_id = 42 AND status = 'paid'
ORDER BY created_at DESC
LIMIT 20;
```

계획을 읽을 때는 다음 순서를 고정해 확인합니다.

| 확인 항목 | 의미 | 실무 해석 |
| --- | --- | --- |
| Scan 종류 | Seq Scan / Index Scan / Index Only Scan | 인덱스가 실제 사용되는지 |
| Rows (estimate vs actual) | 예상 행 수와 실제 행 수 차이 | 통계 갱신 필요 여부 판단 |
| Sort 노드 유무 | 별도 정렬 발생 여부 | 인덱스 컬럼 순서 재검토 |
| Loop 횟수 | 반복 수행 정도 | Nested Loop 과비용 여부 |

예상 행 수와 실제 행 수가 크게 어긋나면 `ANALYZE` 또는 통계 정책을 먼저 점검합니다. 인덱스를 추가하기 전에 통계부터 정상화하는 편이 안전합니다.

### 3) 트랜잭션 경계와 실패 처리 패턴

```python
import sqlite3

def create_order(db: sqlite3.Connection, user_id: int, amount: int) -> None:
    try:
        db.execute("BEGIN")
        db.execute(
            "INSERT INTO orders(user_id, status, total_amount) VALUES (?, 'paid', ?)",
            (user_id, amount),
        )
        db.execute(
            "UPDATE inventory SET stock = stock - 1 WHERE sku = ? AND stock > 0",
            ("SKU-001",),
        )
        changed = db.execute("SELECT changes()").fetchone()[0]
        if changed != 1:
            raise RuntimeError("재고 부족")
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        raise
```

이 패턴의 의도는 명확합니다. 주문 생성과 재고 차감을 **하나의 원자 단위**로 묶고, 조건이 맞지 않으면 전체를 되돌립니다. 트랜잭션 안에서 외부 API 호출을 하지 않는 것도 중요합니다. 잠금 시간이 길어지면 동시성 충돌이 급격히 늘어납니다.

### 4) 운영에서 자주 쓰는 진단 SQL

```sql
-- 값 분포 확인(선택성 감각)
SELECT status, COUNT(*) FROM orders GROUP BY status;

-- 최근 7일 데이터 비율 확인(파티션/인덱스 필요성 판단)
SELECT COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') AS recent,
       COUNT(*) AS total
FROM orders;

-- 특정 조건의 실제 데이터량 확인
SELECT COUNT(*)
FROM orders
WHERE user_id = 42 AND status = 'paid';
```

인덱스 설계는 문법 문제가 아니라 **분포 문제**입니다. 어떤 값이 얼마나 자주 등장하는지 모르면, 좋은 인덱스 순서를 고르기 어렵습니다.

### 5) 읽기/쓰기 균형 체크

| 판단 질문 | 읽기 중심 시스템 | 쓰기 중심 시스템 |
| --- | --- | --- |
| 인덱스 수 | 상대적으로 많아도 감당 가능 | 최소화가 우선 |
| 커버링 인덱스 | 적극 검토 | 신중 검토 |
| 배치 업데이트 | 야간 일괄 가능 | 짧은 배치로 분할 필요 |
| 통계 갱신 | 주기적 자동 갱신 | 대량 쓰기 직후 즉시 갱신 |

결론적으로 데이터베이스 튜닝은 “인덱스를 늘린다”가 아니라 “실행 계획을 읽고, 트랜잭션 경계를 짧게 유지하고, 분포를 근거로 선택한다”의 반복입니다.

## 처음 질문으로 돌아가기

- **고전적인 동시성 이상 현상 네 가지는 무엇일까요?**
  - 본문의 기준은 격리 수준를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE은 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **MVCC는 어떻게 일관된 읽기를 잠금 없이 제공할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Database Systems 101 (1/10): 데이터베이스 시스템이란 무엇인가?](./01-what-is-a-database.md)
- [Database Systems 101 (2/10): 관계형 모델](./02-relational-model.md)
- [Database Systems 101 (3/10): SQL과 쿼리 처리](./03-sql-and-query-processing.md)
- [Database Systems 101 (4/10): 인덱스](./04-indexes.md)
- [Database Systems 101 (5/10): 트랜잭션과 ACID](./05-transactions-and-acid.md)
- **격리 수준 (현재 글)**
- 정규화와 모델링 (예정)
- 쿼리 최적화 (예정)
- 복제와 백업 (예정)
- OLTP와 OLAP (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Jepsen — Consistency Models](https://jepsen.io/consistency)
- [A Critique of ANSI SQL Isolation Levels (Berenson et al.)](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/)
- [Designing Data-Intensive Applications — Chapter 7](https://dataintensive.net/)

Tags: Computer Science, Database, Isolation, MVCC, 동시성, 이상현상
