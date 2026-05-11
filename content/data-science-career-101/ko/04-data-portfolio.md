---
series: data-science-career-101
episode: 4
title: 데이터 포트폴리오
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataCareer
  - Portfolio
  - GitHub
  - Notebook
  - Beginner
seo_description: 채용에 통하는 데이터 포트폴리오 구성을 정리한 글
last_reviewed: '2026-05-04'
---

# 데이터 포트폴리오

> Data Science Career 101 시리즈 (4/10)


## 이 글에서 다룰 문제

*숫자* 가 *아니라* *서사* 가 *합격* 시킵니다.

## 전체 흐름
```mermaid
flowchart LR
    Q[Question] --> D[Data]
    D --> A[Analysis]
    A --> R[Result]
    R --> Repro[Reproducible]
```

## Before/200After

**Before**: "*깃허브* 에 *모델* *코드* 만 *올린다*."

**After**: "*문제* 와 *결론* 까지 *글* 로 *남긴다*."

## 포트폴리오 구성

### 1단계 — 프로젝트 3개

```text
- 분석 1 (대시보드)
- 모델 1 (분류 또는 회귀)
- 데이터 엔지니어링 1 (파이프라인)
```

### 2단계 — README 양식

```markdown
# Title
## Problem
## Data
## Approach
## Results
## How to Reproduce
```

### 3단계 — 재현 환경

```bash
uv pip install -r requirements.txt
make data
make run
```

### 4단계 — 시각화

```text
- 1 핵심 그래프
- 1 비교 표
- 1 결론 한 줄
```

### 5단계 — 문서화

```text
- 노트북에 markdown 셀 충분히
- 의사결정 기록
```

## 이 코드에서 주목할 점

- *재현* 이 *신뢰*.
- *서사* 가 *기억*.
- *결론* 이 *인상*.

## 자주 하는 실수 5가지

1. ***모델* 만 *있고* *문제* 가 *없다*.**
2. ***데이터 출처* *불명*.**
3. ***재현* *불가*.**
4. ***README* 가 *비었다*.**
5. ***시각화* 가 *과하다*.**

## 실무에서는 이렇게 쓰입니다

면접관은 *5분* *안에* *프로젝트* 의 *문제* 와 *결론* 을 *봅니다*.

## 체크리스트

- [ ] *프로젝트* 3개.
- [ ] *README* 5섹션.
- [ ] *재현* 명령.
- [ ] *결론* 1문장.

## 정리 및 다음 단계

다음 글은 *SQL과 분석 인터뷰* 입니다.

<!-- toc:begin -->
- [데이터 직무란 무엇인가](./01-what-is-data-career.md)
- [분석가 vs 사이언티스트 vs 엔지니어](./02-analyst-scientist-engineer.md)
- [학습 경로 설계](./03-learning-path.md)
- **데이터 포트폴리오 (현재 글)**
- SQL과 분석 인터뷰 (예정)
- ML 인터뷰 (예정)
- 케이스 인터뷰 (예정)
- 첫 직장 적응 (예정)
- 도메인 전문성 쌓기 (예정)
- 시니어 데이터 직무로 가는 길 (예정)
<!-- toc:end -->

## 참고 자료

- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
- [Made with ML](https://madewithml.com/)
- [Towards Data Science portfolio guide](https://towardsdatascience.com/)

Tags: DataCareer, Portfolio, GitHub, Notebook, Beginner
