---
series: sql-101
episode: 9
title: "SQL 101 (9/10): 인덱스와 쿼리 계획"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - SQL
  - Index
  - QueryPlan
  - Performance
  - Postgres
seo_description: B-tree 인덱스, EXPLAIN 읽기, 인덱스가 건너뛰어지는 이유, 합성 인덱스 설계를 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (9/10): 인덱스와 쿼리 계획

같은 SQL인데 어떤 쿼리는 0.1초 만에 끝나고, 어떤 쿼리는 수십 초가 걸립니다. 이 차이는 대개 운이 아니라 실행 계획에서 나옵니다. 데이터베이스가 어떤 경로로 데이터를 읽기로 결정했는지 이해하지 못하면 튜닝은 추측에 머물기 쉽습니다.

이 글은 SQL 101 시리즈의 아홉 번째 글입니다. 여기서는 인덱스의 기본 원리와 `EXPLAIN`을 읽는 법, 그리고 인덱스가 왜 기대대로 쓰이지 않는지를 설명합니다.

## 먼저 던지는 질문

- B-tree 인덱스는 어떤 생각으로 이해하면 될까요?
- `EXPLAIN`과 `EXPLAIN ANALYZE`는 무엇이 다를까요?
- 인덱스가 있어도 왜 순차 스캔이 선택될까요?

## 큰 그림

![SQL 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/09/09-01-plan-selection-flow.ko.png)

*SQL 101 9장 흐름 개요*

이 그림에서는 인덱스가 있을 때와 없을 때 쿼리 실행 계획이 어떻게 달라지는지 봅니다. 인덱스는 조회 속도를 빠르게 하지만, 모든 열에 인덱스를 만들면 쓰기 성능이 나빠집니다.

> 인덱스와 쿼리 계획의 핵심은 실행 계획을 읽고, 의도한 대로 인덱스를 탈 수 있는 쿼리를 짜고, 성능 개선이 정말 필요한 지점에만 인덱스를 만드는 데 있습니다.

## 왜 중요한가

데이터가 작을 때는 웬만한 쿼리도 빨라 보입니다. 하지만 행 수가 늘어나면 작은 조건식 차이가 큰 성능 차이로 바뀝니다. 이 시점부터는 쿼리 문장만 보는 것으로는 부족하고, 데이터베이스가 실제로 어떤 방식으로 읽고 있는지를 확인해야 합니다.

또 인덱스는 읽기를 빠르게 만드는 대신 쓰기 비용을 늘립니다. 많이 만들수록 좋은 것이 아니라, 어떤 조회를 빠르게 만들고 어떤 쓰기 부담을 감수할지 설계하는 문제에 가깝습니다.

## 실행 계획 선택 흐름

사용자가 SQL을 보내면 플래너가 여러 실행 방식을 검토합니다. 그리고 비용 추정을 바탕으로 순차 스캔을 할지, 인덱스 스캔을 할지, 어떤 조인 순서를 택할지 결정합니다. 성능 튜닝은 결국 이 선택을 읽고 이해하는 과정입니다.

## 핵심 개념 정리

### B-tree 인덱스는 가장 흔한 기본 인덱스다

정렬된 구조를 유지하면서 값을 빠르게 찾도록 돕는 인덱스입니다. 동등 비교와 범위 비교에서 특히 자주 쓰입니다.

### 순차 스캔은 무조건 나쁜 것이 아니다

전체 테이블을 읽는 방식이라서 느려 보이지만, 조건 선택도가 낮거나 테이블이 작으면 오히려 합리적인 선택일 수 있습니다. 인덱스가 있다고 항상 인덱스를 타는 것은 아닙니다.

### 선택도는 조건이 얼마나 많이 줄여 주는가를 뜻한다

거의 모든 행이 조건을 통과한다면 인덱스를 타는 이점이 작습니다. 반대로 아주 적은 행만 남긴다면 인덱스 사용 가치가 커집니다.

### 합성 인덱스는 왼쪽부터 읽는다는 감각이 중요하다

예를 들어 `(user_id, created_at)` 인덱스는 보통 `user_id`를 먼저 좁히는 쿼리에 잘 맞습니다. 컬럼 순서는 단순 장식이 아니라 사용 패턴과 직결됩니다.

## 다섯 단계로 보는 튜닝 흐름

### 1단계 — 계획만 먼저 보기

```sql
EXPLAIN
SELECT * FROM users WHERE email = 'a@b.com';
```

**Expected output:**

```text
Index Scan using idx_users_email on users  (cost=0.28..8.30 rows=1 width=48)
  Index Cond: (email = 'a@b.com'::text)
```

실행하지 않고 계획만 봅니다. 어떤 스캔을 택했는지, 예상 행 수가 얼마인지부터 읽어 보는 출발점입니다.

### 2단계 — 실제 실행까지 보기

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'a@b.com';
```

실제로 실행한 뒤 실제 시간과 실제 행 수를 보여 줍니다. 운영 환경에서는 실제 실행이므로 더 조심해서 써야 합니다.

### 3단계 — 단일 컬럼 인덱스 추가하기

```sql
CREATE INDEX idx_users_email ON users (email);
```

이메일로 자주 찾는다면 기본적인 출발점이 됩니다.

### 4단계 — 합성 인덱스 설계하기

```sql
CREATE INDEX idx_orders_user_date
ON orders (user_id, created_at DESC);
```

사용자별 최근 주문을 자주 찾는 패턴에 맞춘 예시입니다. 조건과 정렬을 함께 고려한 형태입니다.

### 5단계 — 부분 인덱스 만들기

```sql
CREATE INDEX idx_users_active
ON users (id) WHERE deleted_at IS NULL;
```

## 실행 계획을 볼 때 먼저 확인할 세 가지

`EXPLAIN` 결과를 열었다면 인덱스를 추가하기 전에 먼저 아래 세 질문부터 확인하는 편이 좋습니다.

1. **어떤 스캔이 선택됐는가?** 인덱스를 기대했는데 `Seq Scan`이 보인다면 선택도나 조건식 모양을 먼저 의심해야 합니다.
2. **예상 행 수가 얼마나 되는가?** 예상 행 수와 실제 행 수가 크게 어긋나면 통계 정보나 데이터 분포를 다시 봐야 합니다.
3. **가장 비싼 단계가 어디인가?** 정렬, 해시 집계, 중첩 루프가 병목일 수 있으므로 필터만 보고 끝내면 안 됩니다.

## 자주 만나는 튜닝 점검표

| 증상 | 먼저 볼 것 | 자주 하는 대응 |
| --- | --- | --- |
| 인덱스가 있는데도 `Seq Scan`이 나온다 | 선택도, 함수/형변환 사용 여부 | 조건식을 바꾸거나 인덱스 종류를 다시 설계 |
| 합성 인덱스가 기대만큼 안 듣는다 | 왼쪽 컬럼부터 조건에 쓰였는지 | 조회 패턴에 맞게 컬럼 순서 재설계 |
| `EXPLAIN`은 좋아 보이는데 실제 시간은 길다 | 정렬, 조인, 실제 행 수 | 필터만이 아니라 전체 계획을 다시 점검 |

삭제되지 않은 사용자만 자주 읽는다면, 전체보다 작은 인덱스로도 충분한 경우가 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 합성 인덱스는 컬럼 순서가 매우 중요합니다.
- 부분 인덱스는 조건이 명확할 때 특히 강력합니다.
- `EXPLAIN ANALYZE`는 실제 쿼리를 실행하므로 환경을 가려서 써야 합니다.

## 실무에서 자주 헷갈리는 지점

### 인덱스가 있는데 왜 순차 스캔을 할까

조건이 너무 많은 행을 통과시키면, 인덱스를 타고 다시 테이블을 읽는 비용보다 그냥 전체를 읽는 편이 나을 수 있습니다. 그래서 인덱스 존재 여부만 보지 말고, 조건이 얼마나 결과를 좁히는지도 함께 봐야 합니다.

### 컬럼에 함수를 감싸면 왜 인덱스를 놓치기 쉬울까

`WHERE LOWER(email) = 'x'`처럼 쓰면 일반 인덱스는 바로 활용하기 어렵습니다. 이런 패턴이 자주 필요하다면 함수 인덱스를 고려해야 합니다.

### 합성 인덱스는 왜 순서가 핵심일까

`(user_id, created_at)`와 `(created_at, user_id)`는 서로 다른 인덱스입니다. 어떤 조건이 먼저 들어오는지, 어떤 정렬을 자주 하는지에 따라 효율이 달라집니다.

### 인덱스를 많이 만들면 왜 쓰기가 느려질까

행을 추가하거나 수정할 때마다 관련 인덱스도 함께 갱신해야 합니다. 읽기 최적화만 보고 인덱스를 늘리면 쓰기 부하가 커질 수 있습니다.

## 체크리스트

- [ ] `Seq Scan`과 `Index Scan`의 차이를 설명할 수 있다.
- [ ] `EXPLAIN`과 `EXPLAIN ANALYZE`의 차이를 알고 있다.
- [ ] 합성 인덱스에서 컬럼 순서가 중요하다는 점을 이해하고 있다.
- [ ] 함수와 타입 변환이 인덱스 사용에 영향을 줄 수 있음을 안다.
- [ ] 인덱스가 읽기와 쓰기 사이의 절충이라는 점을 알고 있다.

## 정리

성능 튜닝의 출발점은 인덱스를 많이 만드는 것이 아니라, 실행 계획을 읽는 것입니다. 어떤 쿼리가 왜 순차 스캔을 택했는지, 어떤 조건이 선택도를 높이거나 낮추는지, 합성 인덱스가 어떤 패턴에 맞는지를 이해해야 제대로 된 개선이 가능합니다.

다음 글에서는 시리즈 마지막으로, 지금까지 배운 SELECT, JOIN, GROUP BY, 윈도 함수를 조합해 실전 분석 SQL 패턴을 정리하겠습니다.

## 처음 질문으로 돌아가기

- **B-tree 인덱스는 어떤 생각으로 이해하면 될까요?**
  - 인덱스는 특정 열의 값으로 행을 빠르게 찾을 수 있게 해 줍니다. 하지만 모든 열의 모든 조합에 인덱스를 만들 수는 없습니다.
- **`EXPLAIN`과 `EXPLAIN ANALYZE`는 무엇이 다를까요?**
  - EXPLAIN으로 쿼리 실행 계획을 보면, 데이터베이스가 인덱스를 타는지, 아니면 전체 테이블을 읽는지 알 수 있습니다.
- **인덱스가 있어도 왜 순차 스캔이 선택될까요?**
  - 성능 개선은 무조건 인덱스를 추가하는 것이 아니라, 느린 쿼리를 먼저 식별하고, 그 쿼리가 정말 개선 가치가 있을 때 단계적으로 시도해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
- [SQL 101 (3/10): WHERE와 조건](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN 이해하기](./04-join.md)
- [SQL 101 (5/10): GROUP BY와 집계 함수](./05-group-by-and-aggregate.md)
- [SQL 101 (6/10): 서브쿼리와 CTE](./06-subquery.md)
- [SQL 101 (7/10): 윈도 함수](./07-window-function.md)
- [SQL 101 (8/10): 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE](./08-insert-update-delete.md)
- **인덱스와 쿼리 계획 (현재 글)**
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [PostgreSQL — EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [PostgreSQL — Partial Indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
- [PostgreSQL — Planner Statistics](https://www.postgresql.org/docs/current/planner-stats.html)

Tags: SQL, Database, Postgres, Analytics
