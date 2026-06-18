---
series: database-systems-101
episode: 6
title: "바이브코딩을 위한 데이터베이스 시스템 기초 (6/10): 격리 수준"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - Database
  - Isolation
  - MVCC
  - 동시성
  - 이상현상
seo_description: AI가 만든 서비스에서 잔액이 음수가 되거나 재고가 중복 차감되는 이유는 격리 수준을 이해하지 못한 동시성 설계 때문입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 데이터베이스 시스템 기초 (6/10): 격리 수준

이 글은 **바이브코딩을 위한 데이터베이스 시스템 기초** 시리즈의 6번째 글입니다. AI 코딩 도구로 빠르게 서비스를 만들 때 데이터베이스가 왜 그렇게 동작하는지 이해하면, AI가 만든 쿼리의 문제를 직접 발견하고 수정할 수 있습니다.

---

AI가 만든 재고 관리 시스템을 여러 사용자가 동시에 쓰기 시작하면 이상한 일이 생깁니다. 재고가 1개 남아있는데 두 사람이 동시에 구매하면 둘 다 성공하고 재고가 -1이 됩니다. 이 문제는 코드 버그가 아니라 격리 수준 설계 문제입니다.

동시성 버그는 이상하게도 한가할 때는 잘 보이지 않습니다. 그런데 부하가 몰리고, 두 사용자가 같은 자원을 동시에 만지고, 특정 타이밍이 겹치는 순간 갑자기 잔액이 이상해지고 재고가 음수가 되며 같은 주문이 두 번 생깁니다. 이때 많은 팀이 애플리케이션 코드만 뒤지지만, 실제 원인은 데이터베이스의 격리 수준 선택에 있는 경우가 많습니다.

> 동시성 버그는 조용한 날에는 숨어 있다가, 시스템이 가장 바쁠 때 얼굴을 드러냅니다.

## 이 글에서 다룰 질문

- 고전적인 동시성 이상 현상 네 가지는 무엇일까요?
- READ COMMITTED, REPEATABLE READ, SERIALIZABLE은 무엇이 다를까요?
- MVCC는 어떻게 일관된 읽기를 잠금 없이 제공할까요?
- AI가 만든 서비스에서 동시성 버그를 어떻게 찾을까요?
- 재고 차감이나 잔액 변경을 안전하게 처리하려면 어떻게 해야 할까요?

---

## 격리 수준의 스펙트럼

격리성은 켜고 끄는 스위치가 아니라, 안전성과 처리량 사이를 조정하는 다이얼에 가깝습니다.

```
READ UNCOMMITTED → READ COMMITTED → REPEATABLE READ → SERIALIZABLE
(빠르지만 위험)                                        (느리지만 안전)
```

왼쪽에서 오른쪽으로 갈수록 더 안전하지만 비용도 커집니다. 대부분의 DBMS 기본값은 READ COMMITTED 또는 REPEATABLE READ에 놓여 있습니다.

**핵심 용어**

- **Dirty Read**: 다른 트랜잭션이 아직 커밋하지 않은 값을 읽는 현상입니다.
- **Non-repeatable Read**: 같은 행을 두 번 읽었는데 값이 달라지는 현상입니다.
- **Phantom Read**: 같은 조건으로 두 번 읽었는데 행 개수가 달라지는 현상입니다.
- **Lost Update**: 두 트랜잭션이 같은 행을 동시에 갱신해 한쪽 변경이 사라지는 현상입니다.
- **MVCC**: 한 행의 여러 버전을 유지해 읽기와 쓰기가 서로를 덜 막도록 하는 방식입니다.

## 바이브코딩 관점: AI가 만드는 동시성 취약 패턴

AI는 단일 사용자 시나리오를 기준으로 코드를 만듭니다. 여러 사용자가 동시에 같은 자원을 수정하는 경우를 거의 고려하지 않습니다.

| 시나리오 | AI가 만드는 코드 | 동시성 문제 |
|---|---|---|
| 재고 차감 | `SELECT qty` → 확인 → `UPDATE qty = qty - 1` | 두 요청이 동시에 같은 qty를 읽고 차감 |
| 좌석 예약 | `SELECT count` → 확인 → `INSERT` | 마지막 좌석을 두 명이 동시에 예약 |
| 포인트 사용 | `SELECT point` → 확인 → `UPDATE` | 잔액 부족 검사 통과 후 동시 차감 |
| 순번 생성 | `SELECT MAX(seq) + 1` → `INSERT` | 중복 순번 생성 |

## Before / After: 갱신 손실 vs SELECT FOR UPDATE로 막기

**Before — 잘못된 격리로 잔액이 두 번 차감되는 상황**

```sql
-- T1: SELECT balance FROM accounts WHERE id=1; -- 1000
-- T2: SELECT balance FROM accounts WHERE id=1; -- 1000
-- T1: UPDATE accounts SET balance=900 WHERE id=1;
-- T2: UPDATE accounts SET balance=900 WHERE id=1;  -- T1의 변경이 덮어쓰임
-- 결과: balance=900 (100원이 한 번만 차감됨, Lost Update)
```

**After — SELECT FOR UPDATE로 행 잠금 사용**

```sql
BEGIN;
SELECT balance FROM accounts WHERE id=1 FOR UPDATE;
-- 이 시점에 T2는 T1이 끝날 때까지 대기
UPDATE accounts SET balance = balance - 100 WHERE id=1;
COMMIT;
```

읽는 순간 행 잠금을 잡아 두면, 다른 트랜잭션이 같은 행을 건드리지 못하게 할 수 있습니다.

## 재고 차감을 안전하게 처리하는 두 가지 방법

**방법 1: 비관적 잠금 (SELECT FOR UPDATE)**

```sql
BEGIN;
SELECT qty FROM inventory WHERE sku = 'A-100' FOR UPDATE;
-- 재고 확인
UPDATE inventory SET qty = qty - 1 WHERE sku = 'A-100' AND qty > 0;
COMMIT;
```

**방법 2: 낙관적 잠금 (버전 컬럼 활용)**

```sql
-- 먼저 현재 버전 읽기
SELECT qty, version FROM inventory WHERE sku = 'A-100';

-- 업데이트 시 버전 일치 여부 확인
UPDATE inventory
SET qty = qty - 1, version = version + 1
WHERE sku = 'A-100' AND version = 17;
-- 영향 받은 행 수가 0이면 재조회 후 재시도
```

낙관적 잠금은 잠금 경합을 낮추면서도 정합성을 지키는 데 효과적입니다.

## 자주 하는 실수 5가지

| 번호 | 실수 | 왜 문제인가 |
|---|---|---|
| 1 | 격리 수준을 의식하지 않고 재고를 갱신 | Lost Update는 생각보다 쉽게 재현됩니다 |
| 2 | SERIALIZABLE 켜고 재시도 루프 안 만듦 | 직렬화 실패가 곧바로 사용자 오류가 됩니다 |
| 3 | SELECT → 확인 → UPDATE 패턴 사용 | 읽기와 쓰기 사이에 다른 트랜잭션이 끼어들 수 있습니다 |
| 4 | `FOR UPDATE`를 과하게 남발 | 잠금 범위가 넓어지면 동시성이 급격히 나빠집니다 |
| 5 | 단위 테스트로 동시성 버그 검증 | 동시성 버그는 실제 동시 요청 환경에서만 드러납니다 |

## AI 팁: 동시성 취약 코드를 AI에게 수정 요청하는 방법

AI가 만든 재고 차감 코드에 동시성 문제가 있다면 다음처럼 요청합니다.

```
현재 코드:
1. SELECT qty FROM inventory WHERE sku = ?
2. 애플리케이션에서 qty > 0 확인
3. UPDATE inventory SET qty = qty - 1 WHERE sku = ?

이 코드는 두 요청이 동시에 실행될 때 Lost Update 문제가 있습니다.
다음 두 가지 방식으로 수정해주세요:
1. SELECT FOR UPDATE를 사용한 비관적 잠금 방식
2. 버전 컬럼을 사용한 낙관적 잠금 방식 (재시도 로직 포함)
```

## 체크리스트

- [ ] 핵심 쓰기 경로의 격리 수준을 정확히 알고 있는가?
- [ ] Lost Update 가능 지점에 잠금 또는 원자적 UPDATE가 적용되어 있는가?
- [ ] SELECT → 확인 → UPDATE 패턴이 FOR UPDATE 없이 쓰이고 있지 않은가?
- [ ] 재고 차감, 잔액 변경 등 경쟁 조건이 생길 수 있는 곳을 식별했는가?
- [ ] 동시 접근 시나리오를 실제로 테스트해봤는가?

## 처음 질문으로 돌아가기

- **고전적인 동시성 이상 현상 네 가지는 무엇일까요?**
  Dirty Read(미커밋 값 읽기), Non-repeatable Read(같은 행 두 번 읽기 시 값 변경), Phantom Read(같은 조건 두 번 조회 시 행 수 변경), Lost Update(동시 갱신으로 한쪽 변경 손실)입니다.

- **재고 차감이나 잔액 변경을 안전하게 처리하려면 어떻게 해야 할까요?**
  `UPDATE inventory SET qty = qty - 1 WHERE qty > 0`처럼 조건부 원자적 UPDATE를 사용하거나, `SELECT FOR UPDATE`로 행 잠금을 먼저 잡은 뒤 처리합니다.

- **AI가 만든 서비스에서 동시성 버그를 어떻게 찾을까요?**
  SELECT → 애플리케이션 레벨 확인 → UPDATE 순서로 진행되는 코드를 찾습니다. 이 패턴이 `FOR UPDATE` 없이 사용되면 동시성 문제가 생길 수 있습니다.

## 정리

격리 수준은 동시성 안전성과 처리량 사이의 다이얼입니다. AI가 만든 코드는 단일 사용자 시나리오에서는 완벽하게 동작하지만 동시 접근 상황에서는 갱신 손실, 중복 처리 같은 문제가 생길 수 있습니다. 재고 차감, 잔액 변경, 순번 생성 같은 경쟁 조건이 생길 수 있는 곳은 반드시 잠금이나 원자적 UPDATE로 보호해야 합니다. 다음 글에서는 데이터 모델 자체의 품질, 즉 정규화와 모델링을 살펴봅니다.

## 참고 자료

- [database-systems-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/database-systems-101/ko)
- [PostgreSQL — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Jepsen — Consistency Models](https://jepsen.io/consistency)
- [A Critique of ANSI SQL Isolation Levels (Berenson et al.)](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/)
- [Designing Data-Intensive Applications — Chapter 7](https://dataintensive.net/)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 데이터베이스 시스템 기초 (1/10): 데이터베이스 시스템이란 무엇인가?
- 바이브코딩을 위한 데이터베이스 시스템 기초 (2/10): 관계형 모델
- 바이브코딩을 위한 데이터베이스 시스템 기초 (3/10): SQL과 쿼리 처리
- 바이브코딩을 위한 데이터베이스 시스템 기초 (4/10): 인덱스
- 바이브코딩을 위한 데이터베이스 시스템 기초 (5/10): 트랜잭션과 ACID
- **바이브코딩을 위한 데이터베이스 시스템 기초 (6/10): 격리 수준 (현재 글)**
- 바이브코딩을 위한 데이터베이스 시스템 기초 (7/10): 정규화와 모델링
- 바이브코딩을 위한 데이터베이스 시스템 기초 (8/10): 쿼리 최적화
- 바이브코딩을 위한 데이터베이스 시스템 기초 (9/10): 복제와 백업
- 바이브코딩을 위한 데이터베이스 시스템 기초 (10/10): OLTP와 OLAP

<!-- toc:end -->

Tags: 바이브코딩, Computer Science, Database, Isolation, MVCC, 동시성, 이상현상
