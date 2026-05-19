---
series: data-science-career-101
episode: 5
title: SQL과 분석 인터뷰
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataCareer
  - SQL
  - Analytics
  - Interview
  - Beginner
seo_description: 데이터 직군 인터뷰의 필수 관문인 SQL 및 분석 면접에 대비하기 위한 문제 풀이 패턴과 비즈니스 로직 설명 전략을 전수합니다.
last_reviewed: '2026-05-14'
---

# SQL과 분석 인터뷰

SQL 인터뷰를 준비할 때 많은 지원자가 처음에는 문법 문제집처럼 접근합니다. 어떤 JOIN이 있는지, 윈도우 함수 문법이 무엇인지 외우는 데 집중하지만, 실제 면접에서는 그보다 먼저 질문을 어떻게 분해하고 결과를 어떻게 해석하는지가 드러납니다.

분석 인터뷰도 마찬가지입니다. 쿼리를 쓸 줄 아는 것만으로는 부족하고, 지표 정의를 어떻게 세우는지, NULL과 시간대를 어떻게 다루는지, 숫자를 보고 다음 질문을 무엇으로 이어 갈지까지 보여 줘야 실무 감각이 읽힙니다.

이 글은 Data Science Career 101 시리즈의 다섯 번째 글입니다.

## 이 글에서 다룰 문제

- SQL과 분석 인터뷰가 실제로 무엇을 평가하는지 설명합니다.
- 질문을 어떻게 분해하고 쿼리로 옮겨야 하는지 정리합니다.
- JOIN, 집계, 윈도우 함수, 퍼널 분석의 대표 패턴을 살펴봅니다.
- 지표 정의가 왜 결과 해석을 바꾸는지 짚습니다.
- 결과를 한 문장으로 해석하는 연습이 왜 중요한지 설명합니다.

> SQL 인터뷰의 핵심은 문법 암기가 아니라, 질문을 구조화하고 읽기 좋은 쿼리로 풀어낸 뒤 결과를 의미 있는 해석으로 마무리하는 능력입니다.

## 이 글에서 배우는 내용

- 핵심 SQL 패턴
- 질문 분해 방식
- 지표 정의
- 결과 해석
- 모의 연습 포인트

## 왜 중요한가

SQL은 거의 모든 데이터 직무의 공용어입니다. 따라서 SQL 인터뷰는 단순한 쿼리 시험이 아니라, 질문을 숫자로 번역하는 사고력을 보는 자리이기도 합니다.

실제로 많은 면접은 SQL 문제와 제품 해석 질문을 붙여서 냅니다. 쿼리 자체보다도 어떤 가정을 두었는지, 계산 기준을 어떻게 명시하는지, 결과를 보고 어떤 후속 검증을 제안하는지가 함께 평가됩니다.

## 한눈에 보는 개념

![한눈에 보는 개념](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/05/05-01-concept-at-a-glance.ko.png)

*질문을 SQL로 구조화하고 결과를 해석으로 닫는 분석 인터뷰의 기본 흐름*
좋은 답변은 결과를 뽑는 데서 끝나지 않습니다. 결과가 무엇을 뜻하는지, 다음으로 무엇을 확인해야 하는지까지 말할 수 있어야 완성됩니다.

## 핵심 용어

- **JOIN**: 여러 테이블을 결합하는 연산입니다.
- **GROUP BY**: 기준별로 데이터를 묶어 집계하는 구문입니다.
- **window function**: 행 맥락을 유지하면서 프레임 단위 집계를 수행하는 함수입니다.
- **CTE**: common table expression으로, 쿼리를 단계별로 읽기 쉽게 나누는 방법입니다.
- **funnel**: 단계별 전환율을 보는 분석 방식입니다.

## Before / After

**Before**: "문제가 나오면 일단 SELECT *부터 쓴다."

**After**: "질문을 분해하고 CTE로 구조를 나눈 뒤 결과를 해석할 수 있다."

## 실습: 다섯 가지 질문 패턴

### Step 1 — Single-Table Aggregation

```sql
SELECT date, COUNT(*) AS dau
FROM events
WHERE event = 'login'
GROUP BY date
ORDER BY date;
```

가장 기본적인 패턴입니다. 무엇을 세는지, 어떤 기준으로 묶는지를 명확히 말할 수 있어야 합니다.

### Step 2 — JOIN

```sql
SELECT u.country, COUNT(o.id) AS orders
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.country;
```

JOIN 문제에서는 연결 기준과 NULL 처리까지 같이 봐야 합니다. 왜 `LEFT JOIN`인지 설명할 수 있어야 사고 과정이 드러납니다.

### Step 3 — Window Function

```sql
SELECT user_id, amount,
       SUM(amount) OVER (PARTITION BY user_id ORDER BY ts) AS cum
FROM payments;
```

윈도우 함수는 누적 합, 순위, 이동 평균처럼 맥락이 있는 계산에 자주 쓰입니다. 인터뷰에서는 문법보다 `PARTITION BY`와 `ORDER BY`의 의미를 설명하는 힘이 중요합니다.

### Step 4 — Funnel

```sql
WITH steps AS (
  SELECT user_id,
         MAX(CASE WHEN step='visit' THEN 1 ELSE 0 END) AS s1,
         MAX(CASE WHEN step='signup' THEN 1 ELSE 0 END) AS s2,
         MAX(CASE WHEN step='purchase' THEN 1 ELSE 0 END) AS s3
  FROM funnel GROUP BY user_id
)
SELECT SUM(s1), SUM(s2), SUM(s3) FROM steps;
```

퍼널 문제는 제품 분석 직군에서 특히 자주 나옵니다. 단계 정의와 사용자 중복 처리 방식에 따라 결론이 크게 달라집니다.

### Step 5 — One-Sentence Interpretation

```text
"Conversion fell from X to Y, hypothesis Z."
```

마지막 한 문장이 중요합니다. 숫자가 어떻게 달라졌고, 어떤 가설이 가능한지 말할 수 있어야 분석 답변으로 완성됩니다.

## 이 예시에서 먼저 봐야 할 점

- CTE는 가독성을 높입니다.
- 지표 정의가 결론을 바꿉니다.
- 해석까지 가야 답변이 끝납니다.

면접관은 SQL 자체보다 사고 과정을 함께 봅니다. 어떤 가정을 두는지, 시간대를 고려하는지, NULL을 어떻게 처리하는지가 모두 드러나기 때문입니다.

## 자주 하는 실수 5가지

1. **SELECT *를 남발하는 실수**
2. **NULL 처리를 무시하는 실수**
3. **시간대를 무시하는 실수**
4. **지표 정의를 모호하게 두는 실수**
5. **해석 없이 끝내는 실수**

## 실무에서는 이렇게 나타납니다

분석 인터뷰는 보통 SQL 문제 하나와 케이스 질문 하나를 함께 묶습니다. SQL로 기본기를 보고, 이어서 그 결과를 제품이나 비즈니스 판단으로 연결할 수 있는지 확인하는 방식입니다.

## 시니어는 이렇게 생각합니다

- 지표를 먼저 정의합니다.
- CTE로 동료가 읽기 쉬운 쿼리를 만듭니다.
- 해석이 실제 가치라고 봅니다.
- NULL을 먼저 의심합니다.
- 시간대를 명시합니다.

## 체크리스트

- [ ] 네 가지 JOIN 차이를 설명할 수 있다.
- [ ] 윈도우 함수 패턴 세 가지를 풀어 봤다.
- [ ] 퍼널 문제를 한 번 직접 풀어 봤다.
- [ ] 결과를 한 문장으로 해석하는 연습을 했다.

## 연습 문제

1. CTE를 한 줄로 설명해 보세요.
2. 퍼널 분석의 예를 한 줄로 적어 보세요.
3. 좋은 지표 정의의 기준을 한 줄로 정리해 보세요.

## 정리 및 다음 단계

SQL과 분석 인터뷰는 쿼리 시험이면서 동시에 사고력 시험입니다. 질문을 분해하고, 적절한 JOIN과 집계를 고르고, 필요하면 CTE로 구조를 정리한 뒤, 마지막에 결과를 해석하는 흐름이 핵심입니다.

다음 글에서는 머신러닝 인터뷰에서 어떤 질문이 나오고 어떻게 답해야 하는지 살펴보겠습니다.

<!-- toc:begin -->
- [데이터 직무란 무엇인가](./01-what-is-data-career.md)
- [분석가 vs 사이언티스트 vs 엔지니어](./02-analyst-scientist-engineer.md)
- [학습 경로 설계](./03-learning-path.md)
- [데이터 포트폴리오](./04-data-portfolio.md)
- **SQL과 분석 인터뷰 (현재 글)**
- ML 인터뷰 (예정)
- 케이스 인터뷰 (예정)
- 첫 직장 적응 (예정)
- 도메인 전문성 쌓기 (예정)
- 시니어 데이터 직무로 가는 길 (예정)
<!-- toc:end -->

## 참고 자료

- [Mode - SQL Tutorial](https://mode.com/sql-tutorial/)
- [LeetCode - Top SQL 50](https://leetcode.com/studyplan/top-sql-50/)
- [PostgreSQL Documentation - Window Functions Tutorial](https://www.postgresql.org/docs/current/tutorial-window.html)
- [Ron Kohavi et al. - Trustworthy Online Controlled Experiments](https://experimentguide.com/)

Tags: DataCareer, SQL, Analytics, Interview, Beginner
