---
series: sre-101
episode: 1
title: SRE란 무엇인가?
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - SRE
  - Reliability
  - DevOps
  - Operations
  - Engineering
seo_description: SRE의 정의, 등장 배경, DevOps와의 차이, 핵심 활동, 시작점을 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# SRE란 무엇인가?

> SRE 101 시리즈 (1/10)


## 이 글에서 다룰 문제

*기능* 을 *빨리* 만들어도 *서비스* 가 *자주* *내려가면* *고객* 이 떠납니다. *신뢰성* 은 *제품* 의 일부입니다.

## 전체 흐름
```mermaid
flowchart LR
    Dev["dev"] --> Build["build"]
    Build --> Run["run"]
    Run --> SLO["measure"]
    SLO --> Feedback["feedback"]
    Feedback --> Dev
```

## Before/After

**Before**: *운영팀* 과 *개발팀* 이 *분리*.

**After**: *SRE* 가 *코드* 로 *운영* 을 *대신* 한다.

## 첫 SLO 그려보기

### 1단계 — 지표 선정

```python
# 예: HTTP 성공률
indicator = "http_2xx / http_total"
```

### 2단계 — 목표 정하기

```python
slo = {"indicator": indicator, "target": 0.999, "window": "30d"}
```

### 3단계 — 측정

```python
def availability(success, total):
    return success / total
```

### 4단계 — 에러 버짓

```python
def error_budget(target, total):
    return (1 - target) * total
```

### 5단계 — 의사결정

```python
def can_release(spent, budget):
    return spent < budget
```

## 이 코드에서 주목할 점

- *지표* 는 *고객 경험* 을 반영.
- *목표* 는 *현실적* 으로.
- *버짓* 으로 *속도* 와 *안정성* 을 *조율*.

## 자주 하는 실수 5가지

1. ***100% 가용성* 을 *목표* 로.**
2. ***기술 지표* 를 *고객 지표* 로 착각.**
3. ***SLO* 를 *문서* 로만 두기.**
4. ***운영* 을 *수동* 으로 처리.**
5. ***개발팀* 과 *분리* 운영.**

## 실무에서는 이렇게 쓰입니다

*SRE 팀* 은 *플랫폼* 과 *제품팀* 사이에서 *공통 SLO* 를 *합의* 합니다.

## 체크리스트

- [ ] *핵심 SLO* 1개 정의.
- [ ] *에러 버짓* 계산.
- [ ] *toil 비율* 측정.
- [ ] *오너* 명시.

## 정리 및 다음 단계

다음 글은 *Reliability* 의 *정의* 와 *모델* 입니다.

<!-- toc:begin -->
- **SRE란 무엇인가? (현재 글)**
- Reliability (예정)
- SLI, SLO, SLA (예정)
- Error Budget (예정)
- Monitoring (예정)
- Incident Response (예정)
- Postmortem (예정)
- Toil 줄이기 (예정)
- Capacity Planning (예정)
- 운영 가능한 시스템 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)
- [What is SRE - Google Cloud](https://cloud.google.com/architecture/devops)
- [Site Reliability Engineering - Wikipedia](https://en.wikipedia.org/wiki/Site_reliability_engineering)

Tags: SRE, Reliability, DevOps, Operations, Engineering
