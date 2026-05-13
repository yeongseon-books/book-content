---
series: data-warehouse-101
episode: 7
title: BI와 Dashboard
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataWarehouse
  - BI
  - Dashboard
  - Visualization
  - Analytics
seo_description: BI 도구와 대시보드의 역할, 좋은 화면의 조건, 시각화 원칙
last_reviewed: '2026-05-12'
---

# BI와 Dashboard

데이터 웨어하우스에 데이터를 잘 쌓아도 마지막 화면이 시끄러우면 의사결정은 느려집니다. 결국 BI와 대시보드는 숫자를 저장하는 층이 아니라, 질문 하나를 화면 하나로 바꾸는 층입니다. 좋은 대시보드는 많이 보여 주는 화면이 아니라 빠르게 같은 결론에 도달하게 만드는 화면입니다.

이 글은 Data Warehouse 101 시리즈의 7번째 글입니다.

## 이 글에서 다룰 문제

- 왜 같은 숫자를 보고도 팀마다 다른 결론을 내릴까요?
- BI 도구와 대시보드는 각각 어떤 역할을 맡을까요?
- 좋은 대시보드는 어떤 질문 구조를 가져야 할까요?
- KPI, 추세, 드릴다운은 어떤 순서로 배치해야 할까요?
- 화면이 자주 무너지는 이유는 데이터보다 설계에 있을까요?

## 이 글에서 배울 것

- BI 도구가 데이터 웨어하우스 위에서 맡는 역할
- 좋은 대시보드가 공통으로 갖는 특징
- 숫자를 의사결정으로 연결하는 시각화 원칙
- 질문에서 KPI, 추세, 드릴다운으로 이어지는 5단계 설계 흐름
- 실무에서 반복되는 대표적인 실수 5가지

## 왜 중요한가

웨어하우스 프로젝트가 실패하는 이유가 항상 적재나 모델링 때문인 것은 아닙니다. 꽤 많은 경우 마지막 소비 지점에서 문제가 생깁니다. 팀마다 같은 지표를 다르게 정의하고, 차트는 많은데 질문에 대한 답은 없고, 숫자는 보이는데 비교 기준이 없어 해석이 갈립니다.

이 지점에서 BI와 대시보드의 역할이 분명해집니다. BI는 데이터를 사람이 읽는 형태로 꺼내는 층이고, 대시보드는 그중에서도 특정 질문에 답하도록 구성한 화면입니다. 둘을 잘 만들면 회의 시간이 짧아지고, 운영팀과 제품팀이 같은 숫자를 보며 이야기할 수 있습니다.

> 대시보드의 성공은 열람 수가 아니라 실제로 내려진 결정 수로 판단합니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    DW["Warehouse / Mart"] --> Semantic["Semantic Layer"]
    Semantic --> BI["BI Tool"]
    BI --> Dashboard["Dashboard"]
    Dashboard --> Decision["Decision"]
```

## 핵심 용어

- **BI 도구**: Tableau, Looker, Power BI처럼 데이터를 시각화하고 탐색하는 도구입니다.
- **시맨틱 레이어**: 매출, 사용자 수, 전환율 같은 지표의 정의를 한곳에서 맞추는 공통 계층입니다.
- **KPI**: 핵심 성과 지표입니다. 한 줄로 설명할 수 있어야 합니다.
- **드릴다운**: 요약 숫자에서 세부 원인으로 내려가는 탐색 방식입니다.
- **갱신 주기**: 대시보드 숫자가 얼마나 자주 새로 계산되는지를 뜻합니다.

## Before / After

**Before**: 같은 매출 지표를 제품팀, 재무팀, 마케팅팀이 서로 다르게 계산합니다. 회의는 성과 리뷰가 아니라 숫자 협상으로 끝납니다.

**After**: 시맨틱 레이어에서 매출 정의를 하나로 통일합니다. 모든 팀이 같은 숫자를 보고, 논의는 계산 방식이 아니라 원인과 대응으로 이동합니다.

좋은 대시보드는 많은 정보를 담은 화면이 아닙니다. 질문에 필요한 정보만 남긴 화면입니다. 예를 들어 “이번 달 매출이 지난달보다 얼마나 늘었는가?”라는 질문을 던졌다면, 첫 화면에는 그 질문에 답하는 숫자와 비교 기준이 먼저 보여야 합니다.

이때 대시보드는 보통 세 층으로 구성됩니다. 첫째, 지금 상태를 바로 읽게 해 주는 KPI입니다. 둘째, 그 숫자가 시간 흐름에서 어떻게 변했는지 보여 주는 추세입니다. 셋째, 어떤 제품군이나 채널이 결과를 만들었는지 파고드는 드릴다운입니다. 이 순서가 뒤집히면 사용자는 화면을 오래 보면서도 핵심을 잡지 못합니다.

## 실습: 대시보드를 5단계로 설계해 보기

### 1단계 — 질문 정의하기

```text
"How much did this month's revenue grow *vs last month*?"
```

### 2단계 — 모델 확인하기

```sql
SELECT date_trunc('month', order_date) AS month,
       SUM(amount) AS revenue
FROM marts.fact_orders
GROUP BY 1;
```

### 3단계 — KPI 카드 만들기

```text
- This month revenue: $1,200,000
- vs last month: +12%
- vs same month last year: +35%
```

### 4단계 — 추세 차트 만들기

```sql
-- 12-month trend
SELECT date_trunc('month', order_date) AS month,
       SUM(amount) AS revenue
FROM marts.fact_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1;
```

### 5단계 — drill-down 열기

```sql
-- Contribution by category
SELECT p.category, SUM(f.amount) AS revenue
FROM marts.fact_orders f
JOIN marts.dim_product p ON p.product_key = f.product_key
WHERE f.order_date >= date_trunc('month', CURRENT_DATE)
GROUP BY p.category
ORDER BY revenue DESC;
```

## 이 코드에서 먼저 봐야 할 점

- 한 화면은 질문 하나에 답합니다.
- KPI, 추세, 드릴다운이라는 세 층이 자연스럽게 이어집니다.
- 모든 숫자가 같은 모델과 같은 지표 정의에서 나옵니다.

이 세 가지가 지켜지면 대시보드는 설명 자료가 아니라 운영 도구가 됩니다. 반대로 하나라도 흔들리면 숫자는 많은데 해석은 갈리는 화면이 되기 쉽습니다.

## 자주 하는 실수 5가지

1. **차트를 너무 많이 넣습니다.** 한 화면에 모든 질문을 담으려 하면 아무 질문에도 답하지 못합니다. 보통 한 화면에 3~5개 정도가 균형이 좋습니다.
2. **지표 정의가 대시보드마다 다릅니다.** 같은 매출인데 환불 포함 여부가 화면마다 다르면 신뢰를 잃습니다. 시맨틱 레이어나 공통 모델로 정의를 통일해야 합니다.
3. **비교 기준이 없습니다.** 숫자만 놓고 증감 비교가 없으면 사용자는 그 숫자가 좋은지 나쁜지 판단하기 어렵습니다.
4. **색상 규칙이 흔들립니다.** 어떤 화면에서는 빨강이 증가, 다른 화면에서는 감소를 뜻하면 해석 속도가 급격히 떨어집니다. 색은 일관성이 먼저입니다.
5. **소수점을 과하게 보여 줍니다.** 대시보드는 보고서가 아니라 의사결정 도구입니다. 읽기 쉬운 자리수로 반올림하는 편이 낫습니다.

## 실무에서는 이렇게 나타납니다

분기 리뷰 자료의 첫 장은 대개 대시보드 캡처입니다. 제품팀은 Looker나 Tableau 화면을 보며 기능 출시 효과를 확인하고, 운영팀은 일별 주문 수나 오류율을 같은 방식으로 추적합니다. 여기서 중요한 점은 차트 도구가 아니라 숫자의 공통 언어입니다. 지표 정의가 코드나 메타데이터로 관리되지 않으면, 화려한 화면을 만들어도 결국 다시 스프레드시트로 돌아갑니다.

실무 팀은 보통 대시보드 사용량도 함께 봅니다. 아무도 열지 않는 화면은 시각화가 나쁜 것일 수도 있지만, 더 자주 묻는 질문을 담지 못했을 가능성도 큽니다. 대시보드는 만드는 순간 끝나는 산출물이 아니라, 팀의 질문이 바뀔 때 같이 조정해야 하는 운영 자산입니다.

## 실무에서는 이렇게 생각합니다

- 대시보드는 데이터 전시장보다 질문 응답 화면에 가깝습니다.
- 시맨틱 레이어는 조직이 같은 숫자를 말하게 만드는 공통 언어입니다.
- 비교 기준이 없는 숫자는 해석 비용이 높습니다.
- 첫 화면 KPI는 세 개 안팎으로 제한하는 편이 읽기 쉽습니다.
- 사용률이 낮은 대시보드는 디자인보다 질문 정의를 먼저 다시 봐야 합니다.

## 체크리스트

- [ ] 시맨틱 레이어가 왜 필요한지 설명할 수 있습니다.
- [ ] 좋은 대시보드의 특징 세 가지를 말할 수 있습니다.
- [ ] KPI, 추세, 드릴다운의 역할 차이를 구분할 수 있습니다.
- [ ] 비교 기준이 왜 필요한지 설명할 수 있습니다.

## 연습 문제

1. 여러분 팀이 매주 보는 핵심 질문 하나를 고르고, 그 질문에 맞는 KPI 세 개를 적어 보세요.
2. 차트가 지나치게 많은 기존 대시보드 하나를 떠올린 뒤, 질문 하나만 남긴다면 무엇을 지우고 무엇을 남길지 정리해 보세요.
3. 팀마다 매출이나 활성 사용자 정의가 다를 때 어떤 기준으로 시맨틱 레이어를 정리할지 설명해 보세요.

## 마무리와 다음 글

BI는 데이터 웨어하우스의 마지막 소비 지점입니다. 저장과 모델링이 잘 되어도 마지막 화면이 흔들리면 의사결정이 느려집니다. 반대로 질문, KPI, 추세, 드릴다운이 한 흐름으로 연결되면 숫자는 바로 행동으로 이어집니다.

다음 글에서는 데이터 마트를 다룹니다. 데이터 마트는 조직 전체 웨어하우스에서 한 도메인이나 한 팀이 자주 쓰는 분석용 부분집합입니다. BI가 마지막 화면이라면, 데이터 마트는 그 화면이 빠르고 일관되게 작동하도록 받쳐 주는 중간 층이라고 보면 됩니다.

<!-- toc:begin -->
- [Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [OLTP와 OLAP](./02-oltp-and-olap.md)
- [Fact와 Dimension](./03-fact-and-dimension.md)
- [Star Schema](./04-star-schema.md)
- [Partition과 Clustering](./05-partition-and-clustering.md)
- [ETL과 ELT](./06-etl-and-elt.md)
- **BI와 Dashboard (현재 글)**
- Data Mart (예정)
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)
<!-- toc:end -->

## 참고 자료

- [Looker — Semantic Layer](https://cloud.google.com/looker/docs/intro)
- [Tableau — Visual Best Practices](https://www.tableau.com/learn/articles/data-visualization-tips)
- [Power BI — Star Schema](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [dbt — Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)

Tags: DataWarehouse, BI, Dashboard, Visualization, Analytics
