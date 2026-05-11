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
last_reviewed: '2026-05-11'
---

# 데이터 포트폴리오

데이터 포트폴리오를 준비할 때 많은 입문자가 모델 코드나 노트북만 GitHub에 올리면 된다고 생각합니다. 물론 코드도 중요합니다. 하지만 채용 관점에서는 코드만으로는 충분하지 않은 경우가 많습니다. 면접관이 짧은 시간 안에 보고 싶은 것은 “무슨 문제를 풀었고, 어떤 데이터를 썼고, 어떤 판단을 했고, 결론이 무엇이었는가”입니다.

즉 포트폴리오는 숫자 자체보다 이야기가 중요합니다. 문제에서 출발해 데이터와 분석 과정을 거쳐 결론에 도달하고, 다른 사람이 다시 실행할 수 있게 정리되어 있어야 신뢰가 생깁니다. 좋은 포트폴리오는 실력을 보여 주는 동시에, 협업 가능한 사람이라는 신호도 보냅니다.

## 이 글에서 다룰 문제

- 데이터 포트폴리오는 어떤 프로젝트들로 구성하는 편이 좋을까요?
- 코드만 올린 저장소가 약하게 보이는 이유는 무엇일까요?
- README는 어떤 구조를 갖춰야 할까요?
- 재현 가능성이 왜 신뢰와 연결될까요?
- 시각화와 문서화는 어느 정도까지 들어가야 적절할까요?

> 포트폴리오는 결과물 모음이 아니라, 문제에서 결론까지 따라갈 수 있게 정리된 작업 기록입니다.

## 한눈에 보는 전체 흐름

```mermaid
flowchart LR
    Q[질문] --> D[데이터]
    D --> A[분석]
    A --> R[결과]
    R --> Repro[재현 가능]
```

이 흐름은 포트폴리오가 왜 단순한 코드 저장소가 아닌지 설명해 줍니다. 질문이 없으면 맥락이 없고, 데이터 설명이 없으면 신뢰가 떨어지며, 결론이 없으면 인상이 남지 않습니다. 마지막에 재현 가능성까지 있어야 다른 사람이 실제로 검증할 수 있습니다.

## 핵심 용어

- **portfolio**: 가장 좋은 작업을 골라 보여 주는 선별된 묶음입니다.
- **reproducible**: 다른 사람도 같은 결과를 다시 실행할 수 있는 상태입니다.
- **storytelling**: 문제에서 결론까지의 흐름을 이해하기 쉽게 전달하는 방식입니다.
- **README**: 저장소를 처음 열었을 때 가장 먼저 읽게 되는 안내 문서입니다.
- **notebook**: 분석 과정을 순서대로 기록한 작업 문서입니다.

## Before/After

**Before**: "모델 코드만 GitHub에 올려 두면 포트폴리오가 되는 줄 알았다."

**After**: "문제, 데이터, 접근 방식, 결과, 재현 방법까지 함께 정리해야 한다는 점을 이해했다."

## 실습: 포트폴리오 구성해 보기

여기서는 포트폴리오를 거창한 작품집으로 보지 않고, 채용 담당자나 면접관이 5분 안에 읽을 수 있는 구조로 생각해 보겠습니다.

### Step 1 — Three Projects

```text
- one analytics (dashboard)
- one model (classification or regression)
- one data engineering (pipeline)
```

이 세 종류는 서로 다른 역량을 보여 주기 좋습니다. 분석 프로젝트는 질문과 해석 능력을, 모델 프로젝트는 문제 정의와 평가 지표 감각을, 데이터 엔지니어링 프로젝트는 재현 가능한 데이터 흐름 설계 역량을 보여 줍니다.

### Step 2 — README Template

```markdown
# Title
## Problem
## Data
## Approach
## Results
## How to Reproduce
```

README는 저장소의 얼굴입니다. 무엇을 만들었는지보다 먼저 왜 만들었는지 설명해야 합니다. 특히 `How to Reproduce`가 있으면 읽는 사람이 “이 프로젝트는 정리된 작업이구나”라고 느끼기 쉽습니다.

### Step 3 — Reproducible Environment

```bash
uv pip install -r requirements.txt
make data
make run
```

이런 재현 명령은 단순해 보이지만 매우 중요합니다. 실행 방법이 불분명한 프로젝트는 실제 역량보다 덜 신뢰받기 쉽습니다. 반대로 환경 준비와 실행이 명확하면 협업 경험이 있는 사람처럼 보입니다.

### Step 4 — Visualization

```text
- one key chart
- one comparison table
- one one-line conclusion
```

시각화는 많이 넣는다고 좋은 것이 아닙니다. 핵심 그래프 하나, 비교 표 하나, 결론 한 줄이 더 강할 때가 많습니다. 보는 사람이 무엇을 기억해야 하는지 선명해야 하기 때문입니다.

### Step 5 — Documentation

```text
- enough markdown cells in the notebook
- decision notes
```

노트북 안의 설명과 의사결정 메모는 생각보다 중요합니다. 결과만 보여 주는 사람보다, 왜 그런 선택을 했는지 남겨 두는 사람이 협업에 더 강한 신호를 줍니다.

## 이 예시에서 봐야 할 점

- 재현 가능성은 곧 신뢰입니다.
- 서사는 프로젝트를 기억하게 만듭니다.
- 결론 한 줄이 있어야 읽는 사람이 무엇을 가져가야 하는지 분명해집니다.

포트폴리오의 목적은 “엄청 복잡한 일을 했다”를 증명하는 데 있지 않습니다. 오히려 문제 정의가 분명하고, 분석 과정이 읽히고, 결과가 이해되며, 다시 실행도 가능한 프로젝트가 더 강하게 남습니다. 입문자라면 작은 프로젝트라도 끝까지 정리하는 편이 훨씬 낫습니다.

## 자주 하는 실수 5가지

1. **문제 설명 없이 모델만 올리는 실수**
2. **데이터 출처를 불분명하게 두는 실수**
3. **다른 사람이 재현할 수 없게 만드는 실수**
4. **README를 비워 두거나 너무 짧게 쓰는 실수**
5. **시각화를 과하게 넣어 핵심을 흐리는 실수**

## 실무에서는 이렇게 나타납니다

면접관은 보통 몇 분 안에 프로젝트의 문제, 데이터, 결론을 훑습니다. 이때 README 첫 화면과 시각화 한두 장, 그리고 결론 한 줄이 매우 큰 역할을 합니다. 길고 복잡한 프로젝트보다, 빠르게 이해되고 다시 실행해 볼 수 있는 프로젝트가 더 높은 평가를 받는 이유도 여기 있습니다.

## 시니어는 이렇게 생각합니다

- 재현 가능성이 먼저입니다.
- 문제 정의가 분명해야 결과도 설득력을 가집니다.
- 결론 한 줄이 프로젝트의 인상을 좌우합니다.
- 서사는 결과를 기억에 남게 만드는 장치입니다.
- 링크 하나하나가 나를 소개하는 명함이라고 생각합니다.

## 체크리스트

- [ ] 성격이 다른 프로젝트 세 개를 골랐다.
- [ ] 다섯 섹션으로 된 README 구조를 만들었다.
- [ ] 재현 명령을 적어 두었다.
- [ ] 각 프로젝트에 한 문장 결론을 남겼다.

## 연습 문제

1. reproducible을 한 줄로 설명해 보세요.
2. storytelling의 예를 한 줄로 적어 보세요.
3. 좋은 README가 갖춰야 할 기준을 한 줄로 정리해 보세요.

## 정리 및 다음 단계

좋은 데이터 포트폴리오는 코드보다 문제 정의와 결론 전달이 더 또렷합니다. 분석 프로젝트, 모델 프로젝트, 데이터 엔지니어링 프로젝트를 균형 있게 고르고, README와 재현 방법과 핵심 시각화를 함께 정리해 두면 입문자 포트폴리오의 설득력이 크게 올라갑니다. 결국 채용은 숫자만 보는 일이 아니라, 그 숫자를 다루는 사고방식과 협업 가능성을 함께 보는 과정입니다.

다음 글에서는 데이터 직무 면접에서 빠지지 않는 SQL과 분석 인터뷰를 다뤄 보겠습니다.

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
