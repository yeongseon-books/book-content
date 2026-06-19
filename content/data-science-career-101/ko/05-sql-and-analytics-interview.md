---
series: data-science-career-101
episode: 5
title: "Data Science Career 101 (5/10): SQL과 분석 인터뷰"
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

# Data Science Career 101 (5/10): SQL과 분석 인터뷰

SQL 인터뷰를 준비할 때 많은 지원자가 처음에는 문법 문제집처럼 접근합니다. 어떤 JOIN이 있는지, 윈도우 함수 문법이 무엇인지 외우는 데 집중하지만, 실제 면접에서는 그보다 먼저 질문을 어떻게 분해하고 결과를 어떻게 해석하는지가 드러납니다.

분석 인터뷰도 마찬가지입니다. 쿼리를 쓸 줄 아는 것만으로는 부족하고, 지표 정의를 어떻게 세우는지, NULL과 시간대를 어떻게 다루는지, 숫자를 보고 다음 질문을 무엇으로 이어 갈지까지 보여 줘야 실무 감각이 읽힙니다.

이 글은 Data Science Career 101 시리즈의 다섯 번째 글입니다.

![Data Science Career 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/05/05-01-concept-at-a-glance.ko.png)
*Data Science Career 101 5장 흐름 개요*

> SQL과 분석 인터뷰에서 가장 중요한 것은 쿼리 완성이 아니라 "지표 정의 → 쿼리 → 결과 해석 → 후속 질문"의 흐름을 보여 주는 것입니다.

## 이 글에서 다룰 문제

- SQL과 분석 인터뷰가 실제로 무엇을 평가하는가
- 질문을 어떻게 분해하고 쿼리로 옮겨야 하는가
- JOIN, 집계, 윈도우 함수, 퍼널 분석의 대표 패턴은 무엇인가
- 면접에서 자주 나오는 질문 유형과 좋은 답변 구조는 무엇인가
- NULL, 시간대, 중복 처리에서 자주 놓치는 함정은 무엇인가

## SQL 인터뷰가 평가하는 것

면접관은 쿼리 정답보다 이것을 봅니다.

1. 문제를 지표 언어로 다시 정의하는가
2. JOIN 방향과 집계 단위를 명확히 하는가
3. NULL, 중복, 시간대를 먼저 의심하는가
4. 결과를 한 문장 해석으로 마무리하는가
5. 후속 검증 질문을 스스로 제안하는가

"쿼리가 실행되었다"와 "이 쿼리가 비즈니스 질문에 옳게 답했다"는 다릅니다. 면접관은 두 번째를 더 중요하게 봅니다.

## 다섯 가지 핵심 패턴

### 패턴 1 — 단일 테이블 집계

```sql
SELECT date, COUNT(DISTINCT user_id) AS dau
FROM events
WHERE event_name = 'login'
  AND date >= '2026-01-01'
GROUP BY date
ORDER BY date;
```

**면접 포인트:** `COUNT(*)`와 `COUNT(DISTINCT user_id)`의 차이를 설명할 수 있어야 합니다. DAU는 로그인 이벤트 수가 아니라 고유 사용자 수입니다. 이 차이를 먼저 말하면 기본기가 드러납니다.

### 패턴 2 — LEFT JOIN과 NULL 처리

```sql
SELECT u.country,
       COUNT(o.id) AS order_count,
       COUNT(u.id) AS user_count,
       ROUND(COUNT(o.id) * 100.0 / COUNT(u.id), 2) AS conversion_rate
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
    AND o.status = 'completed'
GROUP BY u.country
ORDER BY conversion_rate DESC;
```

**면접 포인트:** 왜 `LEFT JOIN`인지 설명해야 합니다. `INNER JOIN`이면 구매 이력이 없는 사용자가 제외되어 전환율이 과장됩니다. 또한 `WHERE o.status = 'completed'`를 ON 절에 넣지 않으면 LEFT JOIN이 INNER JOIN처럼 동작한다는 함정을 미리 언급하면 깊이가 드러납니다.

### 패턴 3 — 윈도우 함수

```sql
SELECT user_id,
       payment_date,
       amount,
       SUM(amount) OVER (
           PARTITION BY user_id
           ORDER BY payment_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_amount,
       ROW_NUMBER() OVER (
           PARTITION BY user_id
           ORDER BY payment_date
       ) AS purchase_order
FROM payments;
```

**면접 포인트:** `PARTITION BY`와 `ORDER BY`의 역할을 각각 설명할 수 있어야 합니다. PARTITION BY는 계산 범위를 사용자별로 초기화하고, ORDER BY는 누적 계산 순서를 정합니다. 같은 사용자 안에서 첫 구매인지 재구매인지 구분하려면 `ROW_NUMBER()`를 써야 합니다.

### 패턴 4 — 퍼널 분석

```sql
WITH user_steps AS (
  SELECT user_id,
         MAX(CASE WHEN event_name = 'page_view' THEN 1 ELSE 0 END)  AS step1,
         MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS step2,
         MAX(CASE WHEN event_name = 'checkout' THEN 1 ELSE 0 END)    AS step3,
         MAX(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END)    AS step4
  FROM events
  WHERE event_date BETWEEN '2026-01-01' AND '2026-01-31'
  GROUP BY user_id
)
SELECT
  SUM(step1) AS view_users,
  SUM(step2) AS cart_users,
  ROUND(SUM(step2) * 100.0 / NULLIF(SUM(step1), 0), 2) AS view_to_cart_rate,
  SUM(step3) AS checkout_users,
  ROUND(SUM(step3) * 100.0 / NULLIF(SUM(step2), 0), 2) AS cart_to_checkout_rate,
  SUM(step4) AS purchase_users,
  ROUND(SUM(step4) * 100.0 / NULLIF(SUM(step3), 0), 2) AS checkout_to_purchase_rate
FROM user_steps;
```

**면접 포인트:** `NULLIF(SUM(step1), 0)`으로 분모가 0일 때 나누기 오류를 방지해야 합니다. 또한 단계 건너뜀(step1은 안 했는데 step2를 한 경우) 처리 정책을 먼저 확인하는 것이 좋습니다.

### 패턴 5 — 재구매율 계산 (자주 나오는 고급 문제)

```sql
WITH first_purchase AS (
  SELECT user_id, MIN(purchase_date) AS first_date
  FROM orders
  WHERE status = 'completed'
  GROUP BY user_id
),
second_purchase AS (
  SELECT o.user_id
  FROM orders o
  JOIN first_purchase fp ON o.user_id = fp.user_id
  WHERE o.purchase_date > fp.first_date
    AND o.purchase_date <= fp.first_date + INTERVAL '30 days'
    AND o.status = 'completed'
  GROUP BY o.user_id
)
SELECT
  COUNT(DISTINCT fp.user_id) AS first_buyers,
  COUNT(DISTINCT sp.user_id) AS repurchase_buyers,
  ROUND(COUNT(DISTINCT sp.user_id) * 100.0 / NULLIF(COUNT(DISTINCT fp.user_id), 0), 2) AS repurchase_rate
FROM first_purchase fp
LEFT JOIN second_purchase sp ON fp.user_id = sp.user_id;
```

**면접 포인트:** 재구매율의 분모 정의가 핵심입니다. "전체 사용자 중 재구매 비율"인지 "한 번이라도 구매한 사용자 중 30일 내 재구매 비율"인지 면접 시작 전에 먼저 확인해야 합니다.

## 면접 답변 구조: 90초 프레임

```text
1) 문제 재정의 (15초): "이 질문은 X를 Y 기준으로 구하는 것이죠?"
2) 가정 명시 (15초): "재구매 정의는 30일 내 2회 이상 구매로 보겠습니다."
3) 쿼리 작성 (45초): CTE로 단계를 나눠 읽기 쉽게 구성
4) 결과 해석 (15초): "전환율이 X%에서 Y%로 떨어진 주요 원인은..."
```

이 구조를 반복하면 문법 실수가 하나 있어도 문제 해결 능력을 충분히 보여 줄 수 있습니다.

## 실전 면접 질문 3선과 해설

### 질문 1: "지난 30일 기준 재구매율을 계산해 주세요"

**먼저 확인할 것:**
- 재구매의 정의 (첫 구매 후 X일 이내? 같은 달에 2회 이상?)
- 분모: 전체 가입자인지, 구매 이력이 있는 사용자인지
- 취소/환불 주문 처리 방법

**좋은 답변:** "먼저 재구매를 '첫 구매 후 30일 이내 2번째 구매'로 정의하고, 취소 주문을 제외하겠습니다. 분모는 기간 내 최소 한 번 구매한 사용자로 하겠습니다."

### 질문 2: "국가별 매출 상위 3개 상품을 구해 주세요"

**핵심 포인트:**
- `ROW_NUMBER()` vs `DENSE_RANK()`: 동률 처리 정책에 따라 다름
- 환불 반영 여부 명시
- 날짜 범위 필터 확인

**좋은 답변:** "동률일 때 모두 포함해야 한다면 `DENSE_RANK()`, 정확히 3개만 뽑아야 한다면 `ROW_NUMBER()`를 쓰겠습니다."

### 질문 3: "DAU가 지난주 대비 20% 하락했습니다. 쿼리로 원인을 조사해 보세요"

**접근 순서:**
1. 데이터 파이프라인 이상 여부 먼저 확인 (로깅 누락 가능성)
2. 플랫폼별 (iOS/Android/Web) 분해
3. 유입 채널별 분해
4. 시간대별 패턴 확인

**면접에서 이렇게 말하십시오:** "먼저 데이터 자체에 문제가 없는지 확인하겠습니다. 전체 로그 수를 날짜별로 확인해 누락 여부를 체크한 뒤, 플랫폼별로 쪼개겠습니다."

## 자주 하는 실수

| 실수 유형 | 구체적 사례 | 개선 방향 |
| --- | --- | --- |
| SELECT * 남발 | 필요한 컬럼만 쓰면 되는데 *로 전체 조회 | 필요한 컬럼을 명시하는 습관 형성 |
| NULL 처리 누락 | 분모에 0이 들어가 나눗셈 오류 발생 | NULLIF(), COALESCE()로 먼저 처리 |
| 시간대 무시 | UTC 기준 쿼리인데 KST 기준 결과로 해석 | 타임존 명시 습관과 시차 검증 루틴 |
| 지표 정의 없이 바로 쿼리 | 분모가 뭔지 모르고 COUNT(*) 작성 | 질문을 지표 언어로 먼저 번역 |
| 해석 없이 결과만 반환 | 쿼리 실행 후 "결과입니다"로 끝냄 | 결과를 한 문장 권고안으로 마무리 |

## 분석 인터뷰 추가 팁

**가정을 소리 내어 말하십시오.** 면접관은 완벽한 쿼리보다 논리적 사고 과정을 더 중요하게 봅니다. "이 경우 취소 주문을 포함해야 할지 제외해야 할지 애매한데, 제외하는 방향으로 가겠습니다"라고 말하면 실무 감각이 드러납니다.

**CTE로 구조를 나누십시오.** 복잡한 쿼리를 한 번에 쓰지 말고 CTE로 단계별로 분리하면 면접관이 쿼리를 읽기 쉽고, 본인도 오류를 찾기 쉽습니다.

**숫자를 보고 한 문장을 추가하십시오.** "전환율이 12%에서 8%로 떨어졌습니다. 이 변화가 실제로 의미 있는지 확인하기 위해 기간 내 샘플 크기와 통계적 유의성을 다음으로 보겠습니다"처럼 후속 검증 계획을 말하면 깊이가 달라집니다.

## 처음 질문으로 돌아가기

- **SQL과 분석 인터뷰가 실제로 무엇을 평가하는가**
  - 쿼리 정확도 외에 지표 정의 능력, NULL/중복 처리 감각, 결과 해석력, 후속 질문 제안 능력을 함께 평가합니다.
- **질문을 어떻게 분해하고 쿼리로 옮겨야 하는가**
  - 먼저 지표 언어로 번역 (분자/분모), 다음 가정 명시, CTE로 단계 분리, 마지막 해석 순서를 지키면 됩니다.
- **JOIN, 집계, 윈도우 함수, 퍼널 분석의 대표 패턴은 무엇인가**
  - LEFT JOIN의 방향과 NULL 패턴, SUM-CASE 기반 퍼널, PARTITION BY와 ORDER BY 조합이 핵심입니다.
- **면접에서 자주 나오는 질문 유형과 좋은 답변 구조는 무엇인가**
  - 재구매율, 퍼널 전환, DAU 하락 진단이 가장 자주 나옵니다. 문제 재정의 → 가정 명시 → 쿼리 → 결과 해석 순서를 지키십시오.
- **NULL, 시간대, 중복 처리에서 자주 놓치는 함정은 무엇인가**
  - 분모가 0일 때 NULLIF 처리, UTC/KST 혼용 확인, INNER JOIN과 LEFT JOIN의 차이로 인한 사용자 제외 문제가 대표적입니다.

## 운영 체크리스트

- [ ] 네 가지 JOIN 차이를 설명할 수 있다
- [ ] 윈도우 함수 패턴 세 가지를 직접 풀어 봤다
- [ ] 퍼널 문제를 NULLIF 포함해 한 번 직접 풀어 봤다
- [ ] 결과를 한 문장으로 해석하는 연습을 했다
- [ ] 90초 답변 구조를 소리 내어 연습했다

## 정리

SQL과 분석 인터뷰는 쿼리 시험이면서 동시에 사고력 시험입니다. 질문을 지표 언어로 번역하고, 가정을 소리 내어 말하고, CTE로 구조를 잡고, 결과를 해석하는 흐름이 반복되어야 면접 답변이 완성됩니다. 쿼리 정확도보다 이 과정의 일관성이 면접 결과를 더 많이 좌우합니다.

다음 글에서는 머신러닝 인터뷰에서 어떤 질문이 나오고 어떻게 답해야 하는지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Science Career 101 (1/10): 데이터 직무란 무엇인가](./01-what-is-data-career.md)
- [Data Science Career 101 (2/10): 분석가 vs 사이언티스트 vs 엔지니어](./02-analyst-scientist-engineer.md)
- [Data Science Career 101 (3/10): 학습 경로 설계](./03-learning-path.md)
- [Data Science Career 101 (4/10): 데이터 포트폴리오](./04-data-portfolio.md)
- **Data Science Career 101 (5/10): SQL과 분석 인터뷰 (현재 글)**
- [Data Science Career 101 (6/10): ML 인터뷰](./06-ml-interview.md)
- [Data Science Career 101 (7/10): 케이스 인터뷰](./07-case-interview.md)
- [Data Science Career 101 (8/10): 첫 직장 적응](./08-first-job.md)
- [Data Science Career 101 (9/10): 도메인 전문성 쌓기](./09-domain-expertise.md)
- [Data Science Career 101 (10/10): 시니어 데이터 직무로 가는 길](./10-path-to-senior.md)

<!-- toc:end -->

## 참고 자료

- [book-examples 데이터 직무 커리어 예제 저장소](https://github.com/yeongseon-books/book-examples/tree/main/data-science-career-101/ko)
- [Mode - SQL Tutorial](https://mode.com/sql-tutorial/)
- [LeetCode - Top SQL 50](https://leetcode.com/studyplan/top-sql-50/)
- [PostgreSQL Documentation - Window Functions Tutorial](https://www.postgresql.org/docs/current/tutorial-window.html)
- [Ron Kohavi et al. - Trustworthy Online Controlled Experiments](https://experimentguide.com/)

Tags: DataCareer, SQL, Analytics, Interview, Beginner
