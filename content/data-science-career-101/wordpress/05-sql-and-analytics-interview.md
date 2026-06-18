---
title: "바이브코딩을 위한 데이터 사이언스 커리어 (5/10): SQL과 분석 인터뷰"
targets:
  wordpress: true
tags:
  - 바이브코딩
  - DataCareer
  - SQL
  - Analytics
  - Interview
  - Beginner
---

# 바이브코딩을 위한 데이터 사이언스 커리어 (5/10): SQL과 분석 인터뷰

이 글은 **바이브코딩을 위한 데이터 사이언스 커리어** 시리즈의 다섯 번째 글입니다.

---

"ChatGPT한테 물어보면 SQL 다 써주는데 면접에서 왜 SQL 실력을 봐요?" 이런 질문을 하는 사람들이 늘어나고 있습니다. 맞는 말이기도 하지만, 면접관이 SQL 문제를 내는 이유는 SQL 문법을 외웠는지 확인하려는 게 아닙니다.

면접관이 보고 싶은 것은 "이 사람이 비즈니스 질문을 데이터로 번역할 수 있는가"입니다. NULL을 어떻게 처리할지, 분모를 어떻게 정의할지, JOIN key가 1:N인지 N:N인지 확인하는지, 결과를 보고 어떤 다음 질문을 던지는지입니다. AI가 SQL을 써줘도 이 사고 과정은 본인이 만들어야 합니다.

바이브코딩 환경에서 SQL 인터뷰를 준비하는 올바른 방법은 AI에게 "이 문제 풀어줘"가 아니라 "내 풀이에 어떤 가정이 숨어 있는지 찾아줘"입니다. AI는 검증 도구로 써야 합니다.

> SQL과 분석 인터뷰에서 가장 중요한 것은 쿼리 문법이 아니라 질문을 구조화하고 결과를 해석하는 사고력입니다.

## 이 글에서 다룰 문제

- SQL 면접에서 실제로 무엇을 평가하는가
- 바이브코딩 환경에서 SQL 실력을 어떻게 증명하는가
- JOIN, 집계, 윈도우 함수, 퍼널 분석의 대표 패턴은 무엇인가
- AI에게 SQL을 받은 뒤 면접에서 설명할 수 있게 이해하는 방법은 무엇인가
- 분석 인터뷰에서 숫자를 해석하는 방법을 어떻게 연습하는가

## 5가지 핵심 SQL 패턴

### 패턴 1: 단일 테이블 집계

```sql
-- AI에게 받아도 이 설명은 직접 할 수 있어야 함
SELECT DATE_TRUNC('day', event_at) AS day,
       COUNT(DISTINCT user_id) AS dau
FROM events
WHERE event_type = 'login'
  AND event_at >= '2026-01-01'
GROUP BY 1
ORDER BY 1;
-- 설명: event_at >= 조건으로 풀스캔 방지, DISTINCT로 중복 사용자 제거
```

### 패턴 2: JOIN (분모 정의가 핵심)

```sql
-- 왜 LEFT JOIN인지 설명할 수 있어야 함
SELECT u.country,
       COUNT(o.order_id) AS orders,
       COUNT(u.user_id) AS users,
       ROUND(COUNT(o.order_id)::NUMERIC / COUNT(u.user_id), 3) AS conversion
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
  AND o.created_at >= '2026-01-01'  -- JOIN 조건에 날짜 필터
GROUP BY u.country
ORDER BY conversion DESC;
-- 핵심: LEFT JOIN이므로 주문 없는 사용자도 분모에 포함됨
```

### 패턴 3: 윈도우 함수

```sql
-- 누적 매출 계산: PARTITION BY와 ORDER BY 의미 설명 필수
SELECT user_id,
       payment_date,
       amount,
       SUM(amount) OVER (
           PARTITION BY user_id
           ORDER BY payment_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cumulative_amount
FROM payments;
```

### 패턴 4: 퍼널 분석

```sql
WITH funnel AS (
    SELECT user_id,
           MAX(CASE WHEN step = 'visit'    THEN 1 ELSE 0 END) AS visited,
           MAX(CASE WHEN step = 'signup'   THEN 1 ELSE 0 END) AS signed_up,
           MAX(CASE WHEN step = 'purchase' THEN 1 ELSE 0 END) AS purchased
    FROM user_events
    GROUP BY user_id
)
SELECT
    SUM(visited)    AS step1_visit,
    SUM(signed_up)  AS step2_signup,
    SUM(purchased)  AS step3_purchase,
    ROUND(SUM(signed_up)::NUMERIC / NULLIF(SUM(visited), 0), 3) AS visit_to_signup,
    ROUND(SUM(purchased)::NUMERIC / NULLIF(SUM(signed_up), 0), 3) AS signup_to_purchase
FROM funnel;
```

### 패턴 5: 한 문장 해석 (가장 중요)

```text
결과 해석 구조:
"전환율이 X%에서 Y%로 하락했습니다.
 가설: [Z 이유]로 인해 [A 단계]에서 이탈이 증가했을 가능성이 있습니다.
 검증: [B 데이터]로 [C 방법]으로 확인할 수 있습니다."
```

## Before / After 비교

| 상황 | Before (AI 의존) | After (이해 기반) |
|---|---|---|
| 문제 받았을 때 | "AI한테 물어봄" | 질문 분해 → CTE 구조 설계 → 코딩 |
| JOIN 선택 | 그냥 JOIN 씀 | 분모 정의 확인 후 LEFT/INNER 결정 |
| NULL 처리 | 생각 안 함 | 먼저 "NULL이 있나?" 질문 |
| 결과 나온 후 | "끝" | 한 문장 해석 + 다음 가설 제시 |
| 면접 답변 | "AI가 써준 거라서..." | 코드 한 줄씩 설명 가능 |

## 자주 하는 실수

| 실수 | 면접에서의 영향 | 해결 방법 |
|---|---|---|
| SELECT * 사용 | 실무 감각 없어 보임 | 필요한 컬럼만 명시 |
| NULL 무시 | 잘못된 집계 결과 | 항상 "NULL이면 어떻게?" 질문 |
| 시간대 고려 안 함 | 날짜 집계 오류 | UTC vs KST 확인 |
| 지표 정의 모호 | "활성 사용자가 뭔가요?" 막힘 | 집계 전 분모/분자 정의 |
| 해석 없이 끝냄 | "그래서 결론이 뭔가요?" 막힘 | 숫자 → 가설 → 검증 계획 연결 |

## AI 활용 팁

SQL 인터뷰 준비에서 AI를 제대로 쓰는 방법:

- **문제 이해**: "이 SQL 문제에서 면접관이 확인하고 싶은 것이 뭔지 분석해 줘"
- **내 풀이 검토**: "내 쿼리에서 숨어 있는 가정과 잠재적 버그를 찾아줘"
- **결과 해석**: "이 집계 결과를 보고 어떤 비즈니스 인사이트와 후속 질문을 뽑을 수 있어?"
- **설명 연습**: "이 CTE 기반 쿼리를 면접관에게 90초 안에 설명하는 스크립트 작성해 줘"
- **엣지 케이스**: "이 퍼널 쿼리에서 놓칠 수 있는 엣지 케이스 3가지 알려줘"

## 체크리스트

- [ ] LEFT/INNER/FULL OUTER JOIN 차이를 설명할 수 있다
- [ ] 윈도우 함수 PARTITION BY와 ORDER BY 의미를 설명할 수 있다
- [ ] 퍼널 분석 쿼리를 직접 작성해 봤다
- [ ] 집계 결과를 한 문장 가설로 연결하는 연습을 했다
- [ ] AI가 쓴 쿼리를 내 말로 설명하는 연습을 했다

## 처음 질문으로 돌아가기

- **SQL 면접에서 실제로 무엇을 평가하는가** — 문법이 아니라 비즈니스 질문을 SQL로 번역하는 구조적 사고력입니다.
- **바이브코딩 환경에서 SQL 실력 증명법** — AI가 쓴 코드를 설명할 수 있어야 하고, 결과를 해석해야 합니다.
- **분석 인터뷰 숫자 해석 방법** — 숫자 변화 → 가설 → 검증 방법 연결 구조를 연습합니다.

## 정리

SQL 인터뷰는 문법 시험이 아니라 사고력 시험입니다. 바이브코딩으로 코드를 빠르게 만들 수 있게 됐지만, 면접에서는 그 코드의 가정과 한계를 설명할 수 있어야 합니다. AI는 내 풀이를 검증하고 약점을 찾는 도구로 쓰고, 해석과 판단은 본인이 담당해야 합니다.

## 참고 자료

- [Mode - SQL Tutorial](https://mode.com/sql-tutorial/)
- [LeetCode - Top SQL 50](https://leetcode.com/studyplan/top-sql-50/)
- [PostgreSQL Documentation - Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 데이터 사이언스 커리어 (1/10): 데이터 직무란 무엇인가
- 바이브코딩을 위한 데이터 사이언스 커리어 (2/10): 분석가 vs 사이언티스트 vs 엔지니어
- 바이브코딩을 위한 데이터 사이언스 커리어 (3/10): 학습 경로 설계
- 바이브코딩을 위한 데이터 사이언스 커리어 (4/10): 데이터 포트폴리오
- **바이브코딩을 위한 데이터 사이언스 커리어 (5/10): SQL과 분석 인터뷰 (현재 글)**
- 바이브코딩을 위한 데이터 사이언스 커리어 (6/10): ML 인터뷰
- 바이브코딩을 위한 데이터 사이언스 커리어 (7/10): 케이스 인터뷰
- 바이브코딩을 위한 데이터 사이언스 커리어 (8/10): 첫 직장 적응
- 바이브코딩을 위한 데이터 사이언스 커리어 (9/10): 도메인 전문성 쌓기
- 바이브코딩을 위한 데이터 사이언스 커리어 (10/10): 시니어 데이터 직무로 가는 길

<!-- toc:end -->

Tags: 바이브코딩, DataCareer, SQL, Analytics, Interview, Beginner
