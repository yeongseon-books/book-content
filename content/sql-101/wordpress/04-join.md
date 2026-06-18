---
title: "바이브코딩을 위한 SQL 기초 (4/10): AI가 JOIN을 썼는데 맞는지 확인하려면"
series: sql-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 JOIN 쿼리의 정합성을 검증하는 방법을 설명합니다. INNER JOIN, LEFT JOIN, 카디널리티 함정을 실무 감각으로 이해합니다"
---

# 바이브코딩을 위한 SQL 기초 (4/10): AI가 JOIN을 썼는데 맞는지 확인하려면

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 4번째 글입니다.

"AI야, 사용자 테이블이랑 주문 테이블 합쳐서 각 사용자의 주문 목록 보여줘."

AI가 아래 쿼리를 만들어줬다.

```sql
SELECT u.name, o.id AS order_id, o.total
FROM users u
JOIN orders o ON o.user_id = u.id;
```

실행하니 행이 1,500개 나왔다. 사용자는 100명인데? 왜 15배가 됐을까?

이것이 JOIN의 핵심 함정이다. JOIN을 쓰면 결과 행이 늘어날 수 있다. 한 사용자가 여러 주문을 가지면, 그 사용자의 행이 주문 수만큼 반복된다. AI가 만든 JOIN이 문법적으로 맞아도, 결과 행 수가 예상과 다르면 내가 판단해야 한다.

이 글에서는 AI가 JOIN을 만들었을 때 어떻게 검증하는지, 어떤 함정이 있는지 설명한다.

> JOIN에서 틀린 결과를 만드는 가장 흔한 원인은 문법 오류가 아니라 카디널리티를 놓치는 것이다.

---

## 이 글에서 다룰 문제
- INNER JOIN과 LEFT JOIN의 차이를 AI가 잘 구분해서 썼는지 어떻게 알까요?
- JOIN 후 결과 행이 갑자기 늘어나는 이유가 뭘까요?
- AI가 조인 조건을 빠뜨리면 어떤 재앙이 벌어질까요?
- LEFT JOIN 후 WHERE를 잘못 쓰면 왜 INNER JOIN처럼 동작할까요?
- 여러 테이블을 JOIN할 때 순서가 왜 중요할까요?

실무 쿼리의 대부분은 JOIN을 포함한다. 그리고 JOIN을 잘 쓰는 사람과 못 쓰는 사람의 차이는 문법이 아니라 카디널리티를 이해하는지 여부다. 카디널리티는 한 행이 다른 테이블에서 몇 개의 짝을 가질 수 있는지를 뜻한다.

## JOIN 유형 한눈에 보기

| JOIN 유형 | 결과 | 언제 쓰나 |
| --- | --- | --- |
| `INNER JOIN` | 양쪽에 모두 있는 행만 | 매칭되는 데이터만 필요할 때 |
| `LEFT JOIN` | 왼쪽 테이블 전체 + 오른쪽 매칭 | 왼쪽을 전부 보존해야 할 때 |
| `RIGHT JOIN` | 오른쪽 테이블 전체 + 왼쪽 매칭 | 거의 안 씀 (LEFT JOIN으로 대체) |
| `FULL OUTER JOIN` | 양쪽 모두 | 매칭 안 된 행도 모두 보고 싶을 때 |
| `CROSS JOIN` | 모든 조합 | 의도적으로 쓰는 경우 드묾 (실수 위험) |

## AI가 JOIN에서 자주 하는 실수

### 실수 1: INNER JOIN vs LEFT JOIN 구분 못함

"주문이 없는 사용자도 포함해서 보여줘"라고 했는데 AI가 INNER JOIN을 쓰면, 주문이 없는 사용자는 결과에서 사라진다.

```sql
-- AI가 만든 쿼리 (주문 없는 사용자 누락)
SELECT u.name, o.id AS order_id
FROM users u
INNER JOIN orders o ON o.user_id = u.id;

-- 올바른 쿼리 (주문 없는 사용자도 포함)
SELECT u.name, o.id AS order_id
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

AI가 JOIN 유형을 선택할 때, "없는 경우도 포함해야 하는지"를 명시하지 않으면 대부분 INNER JOIN을 쓴다.

### 실수 2: 카디널리티 무시

사용자 1명이 주문 10개를 가지고 있으면, JOIN 결과에서 그 사용자 행이 10번 반복된다. 여기서 `SUM(o.total)`을 하면 주문 합계가 10배로 부풀어버린다.

```sql
-- 합계가 부풀어지는 쿼리
SELECT u.name, SUM(o.total) AS total_spend
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN payments p ON p.order_id = o.id  -- 한 주문에 결제 여러 건이면...
GROUP BY u.id, u.name;
```

결제가 여러 건이면 주문 금액이 결제 수만큼 중복 합산된다. AI가 이런 구조를 만들면 행 수를 먼저 확인하라.

### 실수 3: LEFT JOIN 후 WHERE로 오른쪽 조건 걸기

```sql
-- LEFT JOIN이지만 사실상 INNER JOIN처럼 동작
SELECT u.name, o.id
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.status = 'paid';  -- 이 WHERE가 NULL 행을 제거해버림

-- LEFT JOIN의 의미를 살리려면 조건을 ON 절에 넣어야 함
SELECT u.name, o.id
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.status = 'paid';
```

AI가 LEFT JOIN에 WHERE를 붙이면 이 문제가 있는지 확인하라.

### 실수 4: 조인 조건 빠뜨리기

조인 조건이 없으면 CROSS JOIN이 된다. 테이블 100행 × 100행 = 10,000행. AI가 만든 쿼리에 `ON` 절이 있는지 반드시 확인하라.

## 카디널리티 확인 습관

JOIN 전에 행 수를 먼저 계산해보라:
```
users: 100명
orders: 한 사용자당 평균 5개 주문
=> JOIN 결과 예상: 500행
```

쿼리 실행 후 `SELECT COUNT(*)`로 실제 행 수를 확인하고, 예상과 크게 다르면 카디널리티를 다시 검토하라.

## Before / After

**Before: AI가 만든 JOIN (합계 부풀기)**
```sql
SELECT u.name, SUM(o.total)
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY u.name;
```
한 주문에 아이템이 3개면 주문 금액이 3배로 잡힌다.

**After: 집계를 먼저 한 뒤 JOIN**
```sql
WITH order_totals AS (
    SELECT order_id, SUM(quantity * unit_price) AS amount
    FROM order_items
    GROUP BY order_id
)
SELECT u.name, SUM(ot.amount) AS total_spend
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_totals ot ON ot.order_id = o.id
GROUP BY u.name;
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| 주문 없는 사용자가 필요한데 INNER JOIN 사용 | 데이터 누락 | LEFT JOIN으로 변경 요청 |
| JOIN 후 합계가 부풀어짐 | 카디널리티 미고려 | 집계를 먼저 한 뒤 JOIN |
| LEFT JOIN + WHERE로 효과 상쇄 | INNER JOIN처럼 동작 | 조건을 ON 절로 이동 |
| 조인 조건 없음 | CROSS JOIN으로 행 폭발 | ON 절 유무 확인 |

## AI에게 SQL 요청하는 팁

- "주문이 없는 사용자도 포함해서"처럼 포함 여부를 명시하라
- "JOIN 후 결과 행 수가 몇 개인지 설명해줘"라고 검증 요청을 하라
- 집계(SUM, COUNT)가 포함된 JOIN은 "카디널리티 문제 없는지 확인해줘"라고 하라
- LEFT JOIN을 쓸 때 "ON 절에 조건을 넣어줘"라고 명시하면 WHERE 실수를 방지할 수 있다

## 운영 체크리스트
- [ ] INNER JOIN과 LEFT JOIN의 차이를 설명할 수 있다
- [ ] JOIN 전에 예상 행 수를 먼저 생각하는 습관이 있다
- [ ] LEFT JOIN 후 NULL이 무엇을 뜻하는지 알고 있다
- [ ] JOIN 조건이 빠지면 CROSS JOIN이 된다는 것을 안다
- [ ] JOIN 후 집계 전에 행 수를 확인하는 습관이 있다

## 처음 질문으로 돌아가기

AI가 JOIN을 썼을 때 검증하는 방법은 하나다. JOIN 전후의 행 수를 세어보는 것이다. 예상한 행 수가 나오면 JOIN이 제대로 된 것이다. 다르다면 카디널리티 문제나 JOIN 조건 문제를 의심하라.

## 정리

JOIN의 본질은 집합과 관계를 읽는 데 있다. 어떤 키로 연결하는지, 한 행이 몇 개의 짝을 가질 수 있는지, 그 결과 행 수가 어떻게 바뀌는지를 이해해야 안전한 JOIN이 가능하다. AI가 만든 JOIN은 항상 행 수 검증과 JOIN 유형 확인으로 시작하라.

## 참고 자료
### 공식 문서
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
### 관련 시리즈
- [Database Systems 101](../../database-systems-101/ko/)
- [SQLAlchemy 101](../../sqlalchemy-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 SQL 기초 (1/10): AI에게 DB 쿼리 시키기 전에 알아야 할 것](./01-what-is-sql.md)
- [바이브코딩을 위한 SQL 기초 (2/10): AI가 만든 SELECT를 읽으려면](./02-select-basics.md)
- [바이브코딩을 위한 SQL 기초 (3/10): AI가 WHERE 조건을 잘못 짰을 때](./03-where-and-conditions.md)
- **바이브코딩을 위한 SQL 기초 (4/10): AI가 JOIN을 썼는데 맞는지 확인하려면 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때](./05-group-by-and-aggregate.md)
- [바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석](./06-subquery.md)
- [바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다](./07-window-function.md)
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, JOIN, 카디널리티
