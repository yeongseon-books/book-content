---
title: "바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기"
series: sql-101
episode: 10
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI와 함께 DAU, 코호트 유지율, 퍼널, 그룹별 Top-N 같은 실전 분석 SQL 패턴을 짜는 방법을 설명합니다"
---

# 바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 마지막 글입니다.

"AI야, 지난달 DAU 추이 뽑아줘. 그리고 1월 가입자 중에 3월에도 활동한 사람 비율도."

AI가 만들어준 쿼리가 실행은 된다. 숫자도 나온다. 그런데 맞는 건지 어떻게 아는가?

실전 분석에서 가장 위험한 순간은 쿼리가 틀렸을 때가 아니다. 쿼리는 실행됐고 숫자도 나왔는데, 그 숫자가 원하는 것을 측정한 건지 확인을 못하는 상황이다. AI는 요청한 내용을 그럴듯하게 구현하지만, 비즈니스 정의가 맞는지는 내가 검토해야 한다.

이 글에서는 바이브코딩으로 실전 분석 SQL을 짤 때 나오는 핵심 패턴 다섯 가지와, AI가 만든 분석 쿼리를 검증하는 방법을 설명한다.

> AI는 DAU, 코호트, 퍼널 SQL을 만들 수 있다. 그 숫자가 비즈니스 정의와 맞는지 확인하는 것은 내 몫이다.

---

## 이 글에서 다룰 문제
- DAU/WAU/MAU는 어떤 쿼리 구조로 만들까요?
- 코호트 유지율은 어떤 단계로 계산할까요?
- 퍼널 분석을 한 쿼리로 깔끔하게 만드는 방법은 뭘까요?
- 그룹별 상위 N건은 윈도우 함수로 어떻게 만들까요?
- AI가 만든 분석 쿼리를 어떻게 검증할까요?

현업에서 받는 분석 요청의 대부분은 완전히 새로운 문제가 아니다. 활성 사용자, 유지율, 전환율, 상위 매출 상품처럼 이미 자주 등장한 패턴의 변형이다. 이 패턴을 알고 있으면 AI에게 더 정확하게 요청하고, 결과를 더 빠르게 검증할 수 있다.

## 패턴 1: 일별 활성 사용자 (DAU)

```sql
SELECT event_at::date AS day, COUNT(DISTINCT user_id) AS dau
FROM events
GROUP BY day
ORDER BY day;
```

가장 기본적인 분석 쿼리다. 특정 날짜에 활동한 고유 사용자 수를 계산한다.

**AI에게 요청할 때 주의점**: "활동"이 무엇인지 명시하라. 로그인만인지, 클릭 이벤트 포함인지에 따라 숫자가 달라진다.

```
"events 테이블에서 event_type = 'page_view'인 이벤트를 활동으로 보고, 일별 DAU를 계산해줘"
```

## 패턴 2: 코호트 유지율

코호트는 같은 출발점(가입일, 첫 결제일 등)을 가진 사용자 묶음이다. 이후 날짜별로 얼마나 다시 활동했는지를 계산하면 유지율이 나온다.

```sql
WITH cohort AS (
    SELECT user_id, MIN(event_at)::date AS cohort_day
    FROM events
    GROUP BY user_id
),
activity AS (
    SELECT e.user_id, c.cohort_day,
        (e.event_at::date - c.cohort_day) AS day_n
    FROM events e
    JOIN cohort c USING (user_id)
)
SELECT cohort_day, day_n, COUNT(DISTINCT user_id) AS users
FROM activity
GROUP BY cohort_day, day_n
ORDER BY cohort_day, day_n;
```

먼저 각 사용자의 출발일(cohort_day)을 만들고, 이후 활동일까지의 차이(day_n)를 계산한 뒤 집계한다.

**AI가 코호트 쿼리에서 자주 하는 실수**: 코호트 기준이 애매하면 MIN(event_at)가 원하는 것을 측정하지 않는다. "가입 이벤트만 기준으로 해줘"처럼 명시하라.

## 패턴 3: 퍼널 분석

단계별 전환을 한 쿼리로 볼 때 `FILTER (WHERE ...)`를 쓰면 깔끔하다.

```sql
SELECT
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'view')   AS s1_view,
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'cart')   AS s2_cart,
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'pay')    AS s3_pay
FROM events;
```

결과:

| s1_view | s2_cart | s3_pay |
| --- | --- | --- |
| 1200 | 420 | 180 |

한 쿼리 안에서 단계별 사용자 수를 나란히 볼 수 있다.

**주의**: 이 패턴은 단계를 시간 순서대로 밟았는지 검증하지 않는다. "장바구니를 먼저 담은 뒤 결제한 사람"처럼 순서를 보장하려면 더 복잡한 구조가 필요하다. AI에게 "단계 간 시간 순서를 보장해줘"라고 요청하면 다른 쿼리가 나온다.

## 패턴 4: 그룹별 Top-N

상품별 상위 3건처럼 그룹 안에서 순위를 매기는 패턴이다. 6편의 서브쿼리와 7편의 윈도우 함수가 결합된다.

```sql
WITH ranked AS (
    SELECT product_id, order_id, total,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY total DESC) AS rk
    FROM orders
)
SELECT * FROM ranked WHERE rk <= 3;
```

`PARTITION BY product_id`가 상품별로 순위를 독립적으로 매기는 핵심이다.

## 패턴 5: 전월 대비 성장률

LAG로 직전 월 값을 가져와서 성장률을 계산한다.

```sql
WITH monthly AS (
    SELECT DATE_TRUNC('month', day) AS month, SUM(revenue) AS rev
    FROM daily_revenue
    GROUP BY month
)
SELECT month, rev,
    rev - LAG(rev) OVER (ORDER BY month) AS diff,
    (rev - LAG(rev) OVER (ORDER BY month)) * 100.0
        / NULLIF(LAG(rev) OVER (ORDER BY month), 0) AS mom_pct
FROM monthly;
```

`NULLIF(값, 0)`는 0으로 나누는 오류를 막는다. 직전 월 매출이 0이면 NULL을 반환한다.

## Before / After

**Before: AI가 만든 퍼널 쿼리 (순서 미보장)**
```sql
SELECT
    COUNT(DISTINCT user_id) FILTER (WHERE event_name = 'view') AS views,
    COUNT(DISTINCT user_id) FILTER (WHERE event_name = 'pay')  AS paid
FROM events;
```
조회도 하지 않고 결제한 사람이 포함될 수 있다. 전환율이 실제보다 높게 나온다.

**After: CTE로 단계별 검증 가능하게**
```sql
WITH viewers AS (
    SELECT DISTINCT user_id FROM events WHERE event_name = 'view'
),
payers AS (
    SELECT DISTINCT user_id FROM events WHERE event_name = 'pay'
)
SELECT
    (SELECT COUNT(*) FROM viewers) AS view_users,
    (SELECT COUNT(*) FROM viewers v JOIN payers p USING (user_id)) AS converted_users;
```
각 단계를 CTE로 분리하면 중간 결과를 별도로 확인할 수 있다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| 활동 이벤트 정의 없이 DAU 요청 | 팀마다 다른 숫자가 나옴 | event_type, event_name 조건 명시 |
| 코호트 기준 미명시 | MIN(event_at)이 가입이 아닐 수 있음 | 코호트 시작 이벤트 명시 |
| 퍼널에서 순서 미검증 | 전환율이 과장됨 | 단계 간 시간 순서 조건 추가 요청 |
| 성장률에 NULLIF 미사용 | 0으로 나누기 오류 | NULLIF(값, 0) 패턴 확인 |
| CTE 없이 중첩 서브쿼리 | 중간 단계 검증 불가 | CTE로 단계 분리 요청 |

## AI에게 SQL 요청하는 팁

- \"활성 사용자는 event_type = 'login'으로 정의하고 DAU 구해줘\"처럼 비즈니스 정의를 먼저 명시하라
- \"각 CTE 단계가 몇 행인지 확인할 수 있게 주석 달아줘\"라고 하면 검증이 쉬워진다
- \"퍼널에서 단계 간 시간 순서를 보장해줘\"라고 명시하면 엄격한 퍼널을 만든다
- \"성장률 계산에서 0으로 나누는 경우를 처리해줘\"라고 요청하면 NULLIF 패턴이 들어간다
- AI가 만든 분석 쿼리는 \"중간 단계 CTE 결과를 먼저 SELECT해서 보여줘\"로 검증하라

## 운영 체크리스트
- [ ] DAU를 기본 형태로 작성할 수 있다
- [ ] 코호트와 활동 단계를 CTE로 나눌 수 있다
- [ ] 퍼널 단계별 사용자 수를 FILTER로 집계할 수 있다
- [ ] 그룹별 Top-N을 ROW_NUMBER로 구할 수 있다
- [ ] 성장률 계산에서 NULLIF로 0 나누기를 막는다
- [ ] 비즈니스 정의(활동, 코호트 기준)를 쿼리 요청 전에 명시한다

## 처음 질문으로 돌아가기

AI가 만든 분석 쿼리에서 숫자가 나왔을 때 확인할 것은 하나다. 그 숫자가 원하는 비즈니스 정의를 측정하는가? DAU라면 어떤 이벤트를 활동으로 봤는지, 코호트라면 기준이 가입인지 첫 결제인지, 퍼널이라면 순서를 보장하는지. 이 정의가 맞으면 숫자를 믿을 수 있다. 정의가 불분명하면 숫자가 나와도 믿을 수 없다.

## 정리

실전 분석 SQL은 새로운 문법이 아니라 이미 배운 도구의 조합이다. DAU는 GROUP BY, 코호트는 CTE + JOIN, 퍼널은 FILTER, Top-N은 ROW_NUMBER, 성장률은 LAG. 이 다섯 가지 패턴을 알고 있으면 대부분의 분석 요청에 AI와 함께 첫 초안을 빠르게 만들 수 있다. AI가 쿼리를 만드는 속도보다, 그 쿼리가 정확한지 검증하는 능력이 바이브코딩 분석의 핵심이다.

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
- [바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다](./07-window-function.md)
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- **바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기 (현재 글)**
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, 데이터분석, 실전SQL
