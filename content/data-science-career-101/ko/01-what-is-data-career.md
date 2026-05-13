---
series: data-science-career-101
episode: 1
title: 데이터 직무란 무엇인가
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataCareer
  - Analyst
  - Scientist
  - Engineer
  - Beginner
seo_description: 데이터 직무의 범위와 대표 역할, 진입 관점을 입문자 눈높이로 정리합니다
last_reviewed: '2026-05-12'
---

# 데이터 직무란 무엇인가

이 글은 Data Science Career 101 시리즈의 첫 번째 글입니다.

## 이 글에서 다룰 문제

- 데이터 직무라고 할 때 실제로 어떤 역할들이 함께 묶이는지 정리합니다.
- 직함보다 책임과 산출물로 역할을 구분해야 하는 이유를 설명합니다.
- 입문자가 먼저 구분해야 할 다섯 가지 핵심 역할을 살펴봅니다.
- 도구 이름보다 문제 맥락과 도메인을 먼저 봐야 하는 이유를 짚습니다.
- 내가 어느 역할에 더 맞는지 판단하는 출발점을 제시합니다.

> 데이터 직무는 통계 하나로 묶이는 단일 직군이 아니라, 질문을 데이터로 풀고 그 결과를 의사결정과 제품 변화로 연결하는 여러 역할의 집합입니다.

## 이 글에서 배우는 내용

- 데이터 커리어의 전체 지형
- 다섯 가지 주요 역할
- 역할을 가르는 핵심 역량
- 대표적인 진입 경로
- 입문자가 자주 하는 오해

## 왜 중요한가

같은 데이터라도 역할이 달라지면 기대되는 질문, 산출물, 협업 방식이 모두 달라집니다. 이 차이를 초반에 구분하지 못하면 학습 계획도 흐려지고, 지원서와 포트폴리오도 애매해집니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Q[Question] --> D[Data]
    D --> A[Analysis]
    A --> P[Product]
```

데이터 직무를 가장 단순하게 보면 질문에서 출발해 데이터를 거쳐 분석과 제품 변화로 이어지는 흐름입니다. 차이는 이 흐름의 어느 구간을 책임지느냐에 있습니다.

## 핵심 용어

- **data analyst**: 데이터를 해석해 의사결정을 돕는 역할입니다.
- **data scientist**: 가설을 세우고 실험과 모델로 검증하는 역할입니다.
- **data engineer**: 데이터 파이프라인과 저장 구조를 만드는 역할입니다.
- **ML engineer**: 모델을 학습·배포·운영하는 역할입니다.
- **analytics engineer**: 신뢰할 수 있는 분석용 데이터 모델을 만드는 역할입니다.

## Before / After

**Before**: "데이터 일은 통계만 잘하면 되는 줄 알았다."

**After**: "다섯 가지 역할을 목적과 산출물 기준으로 구분할 수 있다."

## 실습: 역할별 한 줄 정의

### Step 1 — Analyst

```text
Drives decisions with SQL and dashboards.
```

분석가는 데이터를 해석해 팀의 판단 속도를 높이는 역할입니다. SQL, 지표, 대시보드가 중심 도구가 되는 이유도 여기에 있습니다.

### Step 2 — Scientist

```text
Tests hypotheses with experiments and models.
```

사이언티스트는 질문을 가설로 바꾸고, 실험과 모델로 그 가설을 검증합니다. 그래서 설명력과 검증력이 함께 요구됩니다.

### Step 3 — Engineer

```text
Builds pipelines and storage as data infrastructure.
```

엔지니어는 데이터가 안정적으로 흐르도록 기반을 만듭니다. 파이프라인과 스키마 품질이 무너지면 나머지 역할도 함께 흔들립니다.

### Step 4 — ML Engineer

```text
Trains, deploys, and monitors models.
```

ML 엔지니어는 모델을 연구 대상이 아니라 운영 대상로 다룹니다. 학습, 배포, 모니터링을 하나의 시스템으로 보는 감각이 중요합니다.

### Step 5 — Analytics Engineer

```text
Builds reliable analytics models with dbt and friends.
```

애널리틱스 엔지니어는 분석가와 엔지니어 사이에서 재현 가능하고 일관된 분석 기반을 만듭니다. 지표 신뢰도를 높이는 역할이라고 보면 이해가 빠릅니다.

## 이 예시에서 먼저 봐야 할 점

- 직함보다 책임을 봐야 합니다.
- 같은 이름의 직무라도 회사마다 정의가 다를 수 있습니다.
- 실무에서는 역할 경계가 생각보다 자주 겹칩니다.

입문자가 가장 많이 놓치는 부분은 도구가 아니라 목적입니다. SQL을 쓴다고 모두 같은 역할이 아니고, Python을 쓴다고 모두 모델링 중심 직무도 아닙니다. 어떤 질문을 맡고 어떤 결과를 남기는지가 훨씬 더 본질적입니다.

## 자주 하는 실수 5가지

1. **직함만 보고 역할을 판단하는 실수**
2. **모든 도구를 한 번에 배우려는 실수**
3. **문맥 없이 도구 이름만 외우는 실수**
4. **비즈니스 도메인을 가볍게 보는 실수**
5. **측정과 검증을 건너뛰는 실수**

## 실무에서는 이렇게 나타납니다

큰 조직일수록 Analyst, Scientist, ML Engineer, Analytics Engineer가 더 선명하게 분리됩니다. 반대로 작은 조직에서는 한 사람이 두세 역할을 겸하기도 합니다. 그래서 입문 단계에서는 직함보다 실제 책임을 읽는 눈을 먼저 갖추는 편이 안전합니다.

## 시니어는 이렇게 생각합니다

- 질문이 먼저이고 데이터는 수단입니다.
- 측정 가능한 결과가 있어야 일이 끝납니다.
- 도메인을 이해할수록 같은 데이터에서도 더 좋은 판단이 나옵니다.
- 역할을 연결해서 보는 사람이 더 큰 영향력을 냅니다.
- 문제 구조를 이해하는 사람이 오래 갑니다.

## 체크리스트

- [ ] 다섯 가지 주요 역할을 구분할 수 있다.
- [ ] 내가 더 끌리는 역할 한 가지를 골랐다.
- [ ] 각 역할의 기본 도구를 한 번씩 적어 봤다.
- [ ] 앞으로 1주일 동안 탐색할 방향을 정했다.

## 연습 문제

1. data analyst를 한 줄로 설명해 보세요.
2. analytics engineer가 하는 일을 한 줄로 적어 보세요.
3. ML engineer와 data scientist의 차이를 한 줄로 정리해 보세요.

## 정리 및 다음 단계

데이터 직무를 이해하는 첫걸음은 “모두 데이터를 본다”는 뭉뚱그린 시선을 버리는 일입니다. 역할마다 풀어야 하는 문제, 만드는 산출물, 협업 상대, 평가 기준이 다르기 때문입니다.

다음 글에서는 분석가, 사이언티스트, 엔지니어를 더 직접적으로 비교하면서 세 역할의 차이를 구조적으로 정리하겠습니다.

<!-- toc:begin -->
- **데이터 직무란 무엇인가 (현재 글)**
- 분석가 vs 사이언티스트 vs 엔지니어 (예정)
- 학습 경로 설계 (예정)
- 데이터 포트폴리오 (예정)
- SQL과 분석 인터뷰 (예정)
- ML 인터뷰 (예정)
- 케이스 인터뷰 (예정)
- 첫 직장 적응 (예정)
- 도메인 전문성 쌓기 (예정)
- 시니어 데이터 직무로 가는 길 (예정)
<!-- toc:end -->

## 참고 자료

- [Data roles overview](https://www.oreilly.com/library/view/data-science-from/9781492041122/)
- [dbt analytics engineering](https://www.getdbt.com/what-is-analytics-engineering)
- [Google Data Analytics Professional Certificate](https://grow.google/dataanalytics/)
- [DJ Patil — Data Scientist](https://hbr.org/2012/10/data-scientist-the-sexiest-job-of-the-21st-century)

Tags: DataCareer, Analyst, Scientist, Engineer, Beginner
