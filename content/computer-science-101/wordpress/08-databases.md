---
title: "바이브코딩을 위한 Computer Science 기초 (8/10): 데이터베이스"
series: computer-science-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - ComputerScience
  - Database
  - SQL
  - Index
  - Transaction
---

# 바이브코딩을 위한 Computer Science 기초 (8/10): 데이터베이스

이 글은 "바이브코딩을 위한 Computer Science 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 SQL 쿼리와 ORM 코드를 빠르게 만들어 줍니다. 하지만 대부분의 서비스 장애는 데이터베이스에서 일어납니다. 느린 쿼리 하나가 전체 시스템을 마비시키고, 트랜잭션 한 줄을 놓치면 데이터가 깨집니다.

수억 행 중 한 행을 1ms 안에 찾는 일은 SQL 문장 자체보다 그 뒤에 숨어 있는 자료구조와 실행 계획의 힘에 가깝습니다. 인덱스는 책의 색인과 같습니다. 본문 전체를 뒤지지 않고 색인을 따라 곧장 페이지를 펼칩니다.

AI가 만들어 준 SQL에서 인덱스 사용 여부, 트랜잭션 범위, N+1 쿼리 패턴을 확인해야 합니다. SQL과 인덱스, 트랜잭션을 이해하지 못하면 백엔드 엔지니어로 성장할 수 없습니다.

관계형 데이터베이스의 기본 개념, SQL, 인덱스, 트랜잭션과 ACID를 실무 중심으로 정리합니다.

> **핵심 인사이트:** 데이터베이스는 단순한 저장소가 아니라 동시성과 일관성을 책임지는 시스템입니다. 쿼리는 짧지만 그 뒤에는 깊은 알고리즘이 있습니다.

## 이 글에서 다룰 문제

- 데이터베이스는 많은 데이터를 어떻게 영구 저장하고 동시에 안전하게 읽고 쓸까요?
- 인덱스는 왜 조회 속도를 급격하게 바꿀까요?
- 트랜잭션과 ACID는 왜 데이터 무결성의 기초일까요?
- N+1 쿼리 문제는 어떻게 발생하고 어떻게 고칠까요?
- AI가 만든 SQL에서 확인해야 할 것은 무엇인가요?

## 데이터베이스 핵심 패턴

```sql
-- 기본 SQL 패턴
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at >= '2026-01-01'
GROUP BY u.id, u.name
ORDER BY order_count DESC
LIMIT 10;

-- 인덱스: 조회 성능의 핵심
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 트랜잭션: 원자적 연산 보장
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;
COMMIT;  -- 둘 다 성공해야 반영, 하나 실패 시 롤백

-- EXPLAIN으로 실행 계획 확인
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42;
```

## 변경 전후 비교

**Before: 인덱스/트랜잭션 없이 구현**
```python
# N+1 쿼리 (users 1번 + orders N번)
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")
```

**After: 인덱스 + JOIN + 트랜잭션**
```python
# 단일 쿼리로 N+1 해결
users_with_orders = db.query("""
    SELECT u.*, COUNT(o.id) as order_count
    FROM users u LEFT JOIN orders o ON o.user_id = u.id
    GROUP BY u.id
""")
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 인덱스 없이 대용량 테이블 조회 | 전체 테이블 스캔으로 느림 | WHERE, JOIN, ORDER BY 컬럼에 인덱스 |
| N+1 쿼리 | 요청마다 DB 쿼리 N번 추가 발생 | JOIN 또는 IN 절로 단일 쿼리 |
| 트랜잭션 없이 다중 쓰기 | 중간 실패 시 데이터 불일치 | BEGIN/COMMIT으로 원자적 처리 |
| SELECT * 남발 | 불필요한 데이터 전송, 인덱스 비효율 | 필요한 컬럼만 명시 |
| WHERE에 함수 적용 | 인덱스 무력화 | 컬럼 변환 대신 함수형 인덱스 사용 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"사용자 목록과 각 사용자의 최근 주문을 조회하는 SQL을 만들어줘.
N+1 쿼리가 없어야 하고,
인덱스 힌트도 포함해줘.
EXPLAIN ANALYZE 결과에서 확인할 포인트도 알려줘"

# AI 결과물 검증 체크포인트:
# - N+1 쿼리 여부: 루프 안에 DB 쿼리가 있으면 위험
# - 트랜잭션 범위: 여러 쓰기 연산은 하나의 트랜잭션 안에
# - 인덱스: WHERE, JOIN, ORDER BY 컬럼 확인
# - EXPLAIN ANALYZE: Seq Scan이 보이면 인덱스 누락 의심
```

## 운영 체크리스트

- [ ] 자주 사용하는 쿼리의 WHERE/JOIN 컬럼에 인덱스가 있다
- [ ] 다중 쓰기 연산은 트랜잭션으로 묶여 있다
- [ ] N+1 쿼리 패턴을 코드 리뷰에서 검사한다
- [ ] 핵심 쿼리에 EXPLAIN ANALYZE를 실행했다
- [ ] 슬로우 쿼리 로그를 모니터링한다

## 처음 질문으로 돌아가기

- **인덱스가 조회 속도를 바꾸는 이유는?** 인덱스 없이는 전체 행을 순차 스캔(O(n)), 인덱스 있으면 B-Tree로 O(log n) 탐색합니다. 수백만 행에서 차이가 극적입니다.
- **트랜잭션과 ACID는 왜 중요한가?** 여러 쓰기 연산이 원자적으로 처리되어야 중간 실패 시 데이터 불일치가 생기지 않습니다. ACID(원자성, 일관성, 격리성, 지속성)가 이를 보장합니다.
- **N+1 쿼리란?** 목록 1회 조회 후 각 항목마다 추가 쿼리가 N번 발생하는 패턴입니다. JOIN이나 IN 절로 단일 쿼리로 합쳐야 합니다.

## 정리

바이브코딩에서 AI가 만들어 준 SQL 코드에서 N+1 쿼리 패턴, 인덱스 누락, 트랜잭션 범위를 반드시 확인하세요. EXPLAIN ANALYZE로 실행 계획을 검증하는 습관이 서비스 장애를 미리 막습니다. 다음 글에서는 소프트웨어 엔지니어링의 핵심 습관을 정리합니다.

## 참고 자료

- [PostgreSQL — Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Computer Science 기초 (1/10): 컴퓨터 과학이란 무엇인가?
- 바이브코딩을 위한 Computer Science 기초 (2/10): 계산과 프로그램
- 바이브코딩을 위한 Computer Science 기초 (3/10): 데이터 표현
- 바이브코딩을 위한 Computer Science 기초 (4/10): 알고리즘과 복잡도
- 바이브코딩을 위한 Computer Science 기초 (5/10): 컴퓨터 구조
- 바이브코딩을 위한 Computer Science 기초 (6/10): 운영체제
- 바이브코딩을 위한 Computer Science 기초 (7/10): 네트워크
- **바이브코딩을 위한 Computer Science 기초 (8/10): 데이터베이스 (현재 글)**
- 바이브코딩을 위한 Computer Science 기초 (9/10): 소프트웨어 엔지니어링
- 바이브코딩을 위한 Computer Science 기초 (10/10): AI와 데이터사이언스까지의 연결
<!-- toc:end -->

Tags: 바이브코딩, ComputerScience, Database, SQL, Index, Transaction
