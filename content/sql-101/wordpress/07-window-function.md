---
title: "바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다"
series: sql-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 윈도우 함수(OVER, PARTITION BY, ROW_NUMBER, LAG)를 이해하는 방법을 설명합니다"
---

# 바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 7번째 글입니다.

"AI야, 각 사용자의 주문 목록을 보여주는데, 옆에 그 사용자의 총 주문 금액도 같이 보여줘."

AI가 만들어준 쿼리:

```sql
SELECT
    user_id,
    order_id,
    total,
    SUM(total) OVER (PARTITION BY user_id) AS user_total
FROM orders;
```

`OVER (PARTITION BY user_id)` — 이게 뭔지 모르겠다면 이 글을 읽어라.

윈도우 함수는 AI가 분석 쿼리를 만들 때 자주 쓰는 패턴이다. GROUP BY처럼 집계를 하지만, 원본 행을 사라지게 하지 않는다. 각 행을 유지하면서 그룹별 계산 결과를 옆에 붙인다.

이 글에서는 윈도우 함수를 읽는 방법과, AI가 만든 윈도우 함수 쿼리를 검증하는 방법을 설명한다.

> 윈도우 함수는 AI가 가장 잘 쓰는 SQL 기능 중 하나다. 이걸 모르면 AI가 만든 분석 쿼리의 절반을 읽지 못한다.

---

## 이 글에서 다룰 문제
- `OVER (PARTITION BY ...)`는 정확히 무슨 뜻일까요?
- 윈도우 함수와 GROUP BY의 차이가 뭘까요?
- `ROW_NUMBER`, `RANK`, `DENSE_RANK`는 어떻게 다를까요?
- `LAG`와 `LEAD`가 왜 분석에서 자주 나올까요?
- AI가 윈도우 함수를 썼을 때 어떻게 검증할까요?

순위, 전월 대비 변화, 누적 합계, 이동 평균 — 실무에서 자주 요청되는 분석이다. AI는 이런 분석을 윈도우 함수로 만든다. 읽지 못하면 맞는지 틀린지 판단할 수 없다.

## 윈도우 함수 읽는 법

```sql
함수이름() OVER (PARTITION BY 그룹기준 ORDER BY 정렬기준)
```

- **함수이름()**: SUM, COUNT, AVG, ROW_NUMBER, RANK, LAG, LEAD 등
- **PARTITION BY**: 어떤 그룹별로 계산할지 (GROUP BY와 비슷하지만 행을 유지함)
- **ORDER BY**: 그룹 안에서 어떤 순서로 계산할지

```sql
-- 각 사용자의 주문 금액 + 그 사용자 전체 합계
SELECT
    user_id,
    order_id,
    total,
    SUM(total) OVER (PARTITION BY user_id) AS user_total
FROM orders;
```

결과:

| user_id | order_id | total | user_total |
| --- | --- | --- | --- |
| 1 | 101 | 50000 | 130000 |
| 1 | 102 | 80000 | 130000 |
| 2 | 103 | 30000 | 30000 |

GROUP BY와 달리 원본 행이 그대로 있고, `user_total` 컬럼만 추가됐다.

## 주요 윈도우 함수 패턴

### ROW_NUMBER: 순번 붙이기

```sql
SELECT user_id, order_id, total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rank_in_user
FROM orders;
```

각 사용자별로 주문 금액 순으로 번호를 붙인다. `PARTITION BY user_id`가 없으면 전체 테이블에서 번호를 붙인다.

**활용**: "각 카테고리별 상위 3개 상품만 가져오기"

```sql
WITH ranked AS (
    SELECT product_id, category, total,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY total DESC) AS rn
    FROM product_sales
)
SELECT * FROM ranked WHERE rn <= 3;
```

### RANK vs DENSE_RANK: 동률 처리

```sql
SELECT name, score,
    RANK() OVER (ORDER BY score DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank
FROM scores;
```

| name | score | rank | dense_rank |
| --- | --- | --- | --- |
| A | 100 | 1 | 1 |
| B | 100 | 1 | 1 |
| C | 90 | 3 | 2 |

- `RANK`: 동률이면 같은 순위, 다음 순위는 건너뜀 (1,1,3)
- `DENSE_RANK`: 동률이면 같은 순위, 다음 순위는 연속 (1,1,2)

### LAG / LEAD: 이전/다음 행 값

```sql
SELECT
    order_date,
    revenue,
    LAG(revenue) OVER (ORDER BY order_date) AS prev_revenue,
    revenue - LAG(revenue) OVER (ORDER BY order_date) AS diff
FROM daily_revenue;
```

`LAG`는 이전 행의 값, `LEAD`는 다음 행의 값을 가져온다. 전일 대비, 전월 대비 변화를 계산할 때 핵심이다.

### 누적 합계

```sql
SELECT day, revenue,
    SUM(revenue) OVER (ORDER BY day) AS running_total
FROM daily_revenue;
```

날짜 순서로 누적 매출을 계산한다. `ORDER BY`가 없으면 전체 합계가 모든 행에 붙는다.

## GROUP BY vs 윈도우 함수

| | GROUP BY | 윈도우 함수 |
| --- | --- | --- |
| 결과 행 수 | 그룹 수만큼 줄어듦 | 원본 행 수 유지 |
| 원본 데이터 | 사라짐 | 유지됨 |
| 사용 목적 | 요약 | 각 행에 그룹 통계 첨부 |

"국가별 사용자 수"는 GROUP BY, "각 사용자 옆에 그 국가 전체 사용자 수"는 윈도우 함수.

## Before / After

**Before: AI가 만든 쿼리 (PARTITION BY 없음)**
```sql
SELECT user_id, ROW_NUMBER() OVER (ORDER BY total DESC) AS rn
FROM orders;
```
전체 테이블에서 한 번에 번호가 붙는다. 각 사용자별 순번이 아니다.

**After: PARTITION BY 추가**
```sql
SELECT user_id, order_id, total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn
FROM orders;
```
사용자별로 독립적으로 순번이 붙는다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| PARTITION BY 빠뜨림 | 전체 테이블 기준으로 계산됨 | 그룹 기준 명시 확인 |
| ORDER BY 없는 LAG/LEAD | 순서 보장 없어 의미 없음 | ORDER BY 필수 확인 |
| RANK vs ROW_NUMBER 혼동 | 동률 처리 정책이 달라짐 | 보고서 정의에 맞는 함수 선택 |
| 윈도우 함수를 WHERE에 사용 | 오류 발생 | CTE로 감싸서 사용 |

## AI에게 SQL 요청하는 팁

- "각 [그룹]별로 [기준]에 따라 순위를 매겨줘"라고 명시하면 PARTITION BY가 정확하게 나온다
- "전월 대비 증감을 보여줘"라고 하면 LAG를 사용한 패턴이 나온다
- AI가 만든 윈도우 함수에서 "PARTITION BY가 뭘 기준으로 그룹을 나누는지 설명해줘"라고 확인하라
- "동률이 있을 때 RANK를 써야 할지 ROW_NUMBER를 써야 할지 설명해줘"라고 물어보라

## 운영 체크리스트
- [ ] `OVER (PARTITION BY ...)`가 어떤 그룹별 계산인지 읽을 수 있다
- [ ] GROUP BY와 윈도우 함수의 차이를 설명할 수 있다
- [ ] `ROW_NUMBER`와 `RANK`의 차이를 알고 있다
- [ ] `LAG`로 이전 행 값을 가져오는 패턴을 이해하고 있다
- [ ] `PARTITION BY`가 없을 때 전체 테이블이 하나의 그룹이 된다는 것을 안다

## 처음 질문으로 돌아가기

AI가 윈도우 함수를 썼을 때 확인할 두 가지: PARTITION BY가 내가 원하는 그룹 기준인지, ORDER BY가 의미 있는 정렬 기준인지. 이 두 가지가 맞으면 윈도우 함수 결과는 대부분 의도대로 나온다. 틀렸다면 PARTITION BY 기준을 수정하면 된다.

## 정리

윈도우 함수는 행을 줄이지 않고 그룹별 계산을 붙이는 도구다. AI가 분석 쿼리를 만들 때 가장 자주 쓰는 기능 중 하나다. PARTITION BY(그룹), ORDER BY(순서), 함수이름(무엇을 계산) 세 부분만 이해하면 AI가 만든 윈도우 함수 쿼리를 읽고 검증할 수 있다.

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
- [바이브코딩을 위한 SQL 기초 (4/10): AI가 JOIN을 썼는데 맞는지 확인하려면](./04-join.md)
- [바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때](./05-group-by-and-aggregate.md)
- [바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석](./06-subquery.md)
- **바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, 윈도우함수, OVER
