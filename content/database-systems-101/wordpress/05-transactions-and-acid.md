---
series: database-systems-101
episode: 5
title: "바이브코딩을 위한 데이터베이스 시스템 기초 (5/10): 트랜잭션과 ACID"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - Database
  - 트랜잭션
  - ACID
  - WAL
  - 동시성
seo_description: AI가 만든 코드에서 데이터가 부분적으로 저장되거나 사라지는 이유는 트랜잭션 없이 여러 쿼리를 실행하기 때문입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 데이터베이스 시스템 기초 (5/10): 트랜잭션과 ACID

이 글은 **바이브코딩을 위한 데이터베이스 시스템 기초** 시리즈의 5번째 글입니다. AI 코딩 도구로 빠르게 서비스를 만들 때 데이터베이스가 왜 그렇게 동작하는지 이해하면, AI가 만든 쿼리의 문제를 직접 발견하고 수정할 수 있습니다.

---

AI에게 "주문 생성 코드 짜줘"라고 요청하면 주문 행 INSERT, 재고 차감 UPDATE, 결제 기록 INSERT를 순서대로 실행하는 코드가 나옵니다. 기능은 맞지만, 두 번째 UPDATE 중에 서버가 죽으면 어떻게 될까요? 주문은 생성됐지만 재고는 차감되지 않은 상태가 됩니다. 이것이 트랜잭션 없이 여러 쿼리를 실행할 때 생기는 문제입니다.

비즈니스 시스템에서 중요한 작업은 거의 항상 두 단계 이상입니다. 이런 작업이 중간에서 끊기면 데이터는 금방 이상한 상태가 됩니다. 트랜잭션은 이런 여러 SQL 문을 하나의 작업 단위로 묶는 장치입니다. ACID는 그 약속을 네 가지 관점에서 더 정밀하게 설명하는 언어입니다.

> "전부 또는 전무." 이 한 문장이 트랜잭션의 본질을 가장 정확하게 설명합니다.

## 이 글에서 다룰 질문

- 트랜잭션은 정확히 무엇이며 왜 필요할까요?
- ACID 네 글자는 실제로 무엇을 보장할까요?
- `BEGIN`, `COMMIT`, `ROLLBACK`은 어떻게 사용해야 할까요?
- AI가 만든 코드에서 트랜잭션이 빠진 곳을 어떻게 찾을까요?
- 트랜잭션을 너무 길게 열면 어떤 문제가 생길까요?

---

## 트랜잭션의 구조

트랜잭션을 시작한 뒤 여러 변경을 수행하고, 마지막에 한 번에 COMMIT하거나 ROLLBACK합니다. 외부에서는 모든 변경이 한 시점에 반영된 것처럼 보입니다.

```
BEGIN
  → UPDATE A balance -100
  → UPDATE B balance +100
  → 성공? COMMIT | 실패? ROLLBACK
```

**핵심 용어**

- **트랜잭션**: 여러 SQL 문으로 구성된 하나의 작업 단위입니다.
- **원자성(Atomicity)**: 모든 변경이 적용되거나, 아무것도 적용되지 않는 성질입니다.
- **일관성(Consistency)**: 트랜잭션 전후로 무결성 제약이 유지되는 성질입니다.
- **격리성(Isolation)**: 동시에 실행되는 트랜잭션들이 마치 순차적으로 실행된 것처럼 보이게 하는 성질입니다.
- **영속성(Durability)**: 커밋된 변경이 전원 장애 이후에도 살아남는 성질입니다.
- **WAL**: 데이터를 바꾸기 전에 변경 의도를 로그에 먼저 쓰는 방식으로, 복구의 토대입니다.

## 바이브코딩 관점: AI가 트랜잭션을 빠뜨리는 패턴

AI는 여러 쿼리를 순서대로 실행하는 코드를 잘 만들지만, 트랜잭션으로 묶는 것을 자주 빠뜨립니다. 다음은 전형적인 위험 패턴입니다.

| 비즈니스 작업 | AI가 만드는 코드 | 실제 위험 |
|---|---|---|
| 주문 생성 + 재고 차감 | 두 쿼리를 순서대로 실행 | 중간 실패 시 주문만 생성 |
| 포인트 지급 + 사용 내역 기록 | INSERT 두 번 따로 | 지급은 됐지만 기록 없음 |
| 계좌 이체 | UPDATE 두 번 따로 | 출금은 됐지만 입금 안 됨 |
| 사용자 삭제 + 관련 데이터 삭제 | DELETE 여러 번 따로 | 부분 삭제로 참조 오류 발생 |

## Before / After: 트랜잭션 없는 이체 vs 트랜잭션으로 묶기

**Before — 트랜잭션 없이 두 쿼리 실행 (AI가 자주 만드는 패턴)**

```sql
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- (서버 장애 발생)
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- 100원이 사라짐
```

**After — 트랜잭션으로 묶기**

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- 서버 장애가 나도 BEGIN 이전 상태로 자동 복구
```

이 한 줄의 원자성이 시스템의 신뢰도를 가릅니다.

## Python에서 트랜잭션 올바르게 사용하기

AI가 생성하는 Python DB 코드에서 트랜잭션을 안전하게 다루는 방법입니다.

```python
import sqlite3

def transfer(src: int, dst: int, amount: int) -> None:
    with sqlite3.connect("bank.db") as db:
        try:
            db.execute("BEGIN")
            db.execute(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                (amount, src)
            )
            db.execute(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                (amount, dst)
            )
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
```

`with db:` 컨텍스트 매니저를 쓰면 예외 발생 시 자동으로 롤백됩니다. SQLite에서는 다음처럼 더 간결하게 쓸 수 있습니다.

```python
with sqlite3.connect("bank.db") as db:
    with db:  # 자동 BEGIN/COMMIT, 예외 시 자동 ROLLBACK
        db.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100, 1))
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100, 2))
```

## 자주 하는 실수 5가지

| 번호 | 실수 | 왜 문제인가 |
|---|---|---|
| 1 | 트랜잭션을 너무 오래 연다 | 사용자 입력 대기나 외부 API 호출이 안에 있으면 잠금이 길어집니다 |
| 2 | 예외 처리에서 ROLLBACK을 빠뜨린다 | 암묵적 정리를 믿지 말고 명시적으로 다뤄야 합니다 |
| 3 | 자동 커밋 상태로 배치 작업 | N개의 INSERT가 N번의 커밋이 되어 성능이 급격히 나빠집니다 |
| 4 | 모든 SELECT까지 트랜잭션으로 감쌈 | 읽기는 짧게, 쓰기는 비즈니스 단위로 묶는 것이 기본입니다 |
| 5 | ROLLBACK을 "복구"라고 오해 | DB 변경은 되돌리지만 이메일 발송·결제 호출 같은 부수 효과는 되돌리지 못합니다 |

## AI 팁: AI가 만든 코드에서 트랜잭션 누락 찾기

AI가 생성한 코드에서 다음 패턴을 보면 트랜잭션 추가를 검토해야 합니다.

```python
# 위험 신호 1: 같은 함수 안에 여러 DB 쓰기가 순서대로 있음
def create_order(user_id, items):
    order_id = db.execute("INSERT INTO orders ...", ...).lastrowid
    for item in items:
        db.execute("INSERT INTO order_items ...", ...)  # 여기서 실패하면?
    db.execute("UPDATE inventory SET qty = qty - 1 WHERE ...", ...)

# 위험 신호 2: try/except에 ROLLBACK 없음
try:
    db.execute("UPDATE ...")
    db.execute("INSERT ...")
except Exception as e:
    print(e)  # ROLLBACK이 없음!
```

AI에게 다음처럼 요청하면 트랜잭션이 포함된 코드를 얻을 수 있습니다.

```
위 함수를 트랜잭션으로 감싸서 중간에 실패하면 전체 롤백되도록 수정해주세요.
예외 발생 시 ROLLBACK을 명시적으로 호출해야 합니다.
```

## 체크리스트

- [ ] 비즈니스 단위와 트랜잭션 경계가 맞아떨어지는가?
- [ ] 트랜잭션 안에 외부 호출이나 사용자 입력 대기가 없는가?
- [ ] 모든 예외 경로에서 ROLLBACK이 보장되는가?
- [ ] AI가 만든 코드에서 여러 DB 쓰기가 트랜잭션으로 묶여 있는가?
- [ ] 부수 효과(이메일, 결제)는 트랜잭션 밖에서 처리되는가?

## 처음 질문으로 돌아가기

- **트랜잭션은 정확히 무엇이며 왜 필요할까요?**
  여러 SQL 문을 하나의 "전부 또는 전무" 단위로 묶어 부분 실패 상태를 막는 메커니즘입니다.

- **ACID 네 글자는 실제로 무엇을 보장할까요?**
  원자성(전부/전무), 일관성(제약 유지), 격리성(동시 트랜잭션 간 충돌 방지), 영속성(커밋 후 장애에도 데이터 유지)입니다.

- **AI가 만든 코드에서 트랜잭션이 빠진 곳을 어떻게 찾을까요?**
  같은 함수 안에 여러 DB 쓰기가 순서대로 있고 `BEGIN`/`COMMIT`이 없는 패턴, 또는 예외 처리에 ROLLBACK이 없는 패턴을 찾습니다.

## 정리

트랜잭션은 "전부 또는 전무"의 약속이고, ACID는 그 약속을 원자성·일관성·격리성·영속성으로 풀어 쓴 언어입니다. AI가 만드는 코드는 기능은 올바르지만 이 보호막이 빠진 경우가 많습니다. 여러 DB 쓰기가 함께 이루어지는 곳은 반드시 트랜잭션으로 감싸야 합니다. 다음 글에서는 ACID의 I, 격리성으로 들어가서 동시 접근 시 어떤 이상 현상이 생길 수 있는지 살펴봅니다.

## 참고 자료

- [database-systems-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/database-systems-101/ko)
- [PostgreSQL — Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [SQLite — Transactions](https://www.sqlite.org/lang_transaction.html)
- [Designing Data-Intensive Applications — Chapter 7](https://dataintensive.net/)
- [Wikipedia — ACID](https://en.wikipedia.org/wiki/ACID)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 데이터베이스 시스템 기초 (1/10): 데이터베이스 시스템이란 무엇인가?
- 바이브코딩을 위한 데이터베이스 시스템 기초 (2/10): 관계형 모델
- 바이브코딩을 위한 데이터베이스 시스템 기초 (3/10): SQL과 쿼리 처리
- 바이브코딩을 위한 데이터베이스 시스템 기초 (4/10): 인덱스
- **바이브코딩을 위한 데이터베이스 시스템 기초 (5/10): 트랜잭션과 ACID (현재 글)**
- 바이브코딩을 위한 데이터베이스 시스템 기초 (6/10): 격리 수준
- 바이브코딩을 위한 데이터베이스 시스템 기초 (7/10): 정규화와 모델링
- 바이브코딩을 위한 데이터베이스 시스템 기초 (8/10): 쿼리 최적화
- 바이브코딩을 위한 데이터베이스 시스템 기초 (9/10): 복제와 백업
- 바이브코딩을 위한 데이터베이스 시스템 기초 (10/10): OLTP와 OLAP

<!-- toc:end -->

Tags: 바이브코딩, Computer Science, Database, 트랜잭션, ACID, WAL, 동시성
