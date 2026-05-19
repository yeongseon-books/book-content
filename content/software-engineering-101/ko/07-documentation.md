---
series: software-engineering-101
episode: 7
title: 문서화
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareEngineering
  - Documentation
  - README
  - ADR
  - Knowledge
seo_description: README, ADR, docstring, runbook의 역할과 Diataxis 4분면을 짧게 정리합니다.
last_reviewed: '2026-05-15'
---

# 문서화

코드가 좋으면 문서는 없어도 된다는 말을 종종 듣습니다. 어느 정도는 맞는 말처럼 보입니다. 잘 이름 붙은 함수, 분리된 모듈, 읽기 쉬운 테스트가 있으면 많은 설명이 필요 없을 것 같습니다. 하지만 코드만으로는 “왜 이렇게 만들었는가”, “언제 이 절차를 따라야 하는가”, “새로 들어온 사람이 어디서부터 시작해야 하는가”를 설명하기 어렵습니다.

문서가 없을 때 생기는 가장 큰 문제는 정보가 특정 사람을 거쳐서만 이동한다는 점입니다. 그러면 질문은 늘 특정 사람에게 몰리고, 그 사람이 바쁜 시간대에는 팀 전체가 느려집니다. 문서화는 친절의 문제가 아니라 비동기 협업의 기반입니다.

이 글은 Software Engineering 101 시리즈의 일곱 번째 글입니다. 여기서는 README, ADR, docstring, 런북, 온보딩 문서의 역할과 Diataxis 4분면으로 문서를 분리하는 방법을 정리합니다.

## 이 글에서 다룰 문제

- 좋은 README는 최소한 어떤 블록을 가져야 할까요?
- ADR은 무엇을 남기고, 코드 주석과 어떻게 다를까요?
- docstring과 타입 힌트는 문서화에서 어떤 역할을 할까요?
- 런북과 온보딩 문서는 왜 별도로 있어야 할까요?
- Diataxis 4분면은 문서 구조를 어떻게 더 읽기 쉽게 만들까요?

> 코드는 어떻게를 설명하고, 문서는 왜와 언제를 설명합니다.

## 왜 중요한가

문서가 없으면 모든 질문은 누군가의 기억력에 의존합니다. 이 구조는 팀이 작을 때는 버틸 수 있어도 규모가 커질수록 병목이 됩니다. 특히 장애 대응, 신규 입사자 온보딩, 중요한 설계 변경처럼 시간이 촉박한 상황에서는 문서 부재 비용이 훨씬 크게 드러납니다.

또한 문서는 코드의 대체물이 아니라 보완물입니다. 함수 시그니처는 사용법의 절반을 말해 줄 수 있지만, 왜 그런 인터페이스를 선택했는지까지는 설명하지 못합니다. README와 ADR, 런북이 필요한 이유가 여기에 있습니다.

## 한눈에 보는 흐름

![한눈에 보는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/07/07-01-concept-at-a-glance.ko.png)
*튜토리얼·하우투·레퍼런스·설명으로 문서를 나누는 Diataxis 구조*

Diataxis는 문서를 작성자 기준이 아니라 독자의 목적 기준으로 나누게 해 줍니다.

## 핵심 용어

- **README**: 저장소의 첫 인상과 진입점입니다.
- **ADR**: 하나의 결정과 이유를 짧게 남기는 문서입니다.
- **docstring**: 함수나 클래스의 사용 계약을 설명하는 문자열입니다.
- 런북: 사고나 운영 작업을 단계별로 수행하는 절차서입니다.
- **Diataxis**: 튜토리얼, 하우투, 레퍼런스, 설명으로 문서를 구분하는 모델입니다.

## 전후 비교

**이전 — 하나의 거대한 위키**

```text
"It's all on the wiki" -> nobody knows where
```

**이후 — 목적별로 나뉜 문서 구조**

```text
docs/tutorials/  docs/how-to/  docs/reference/  docs/explanation/
```

문서가 많아지는 것이 문제가 아니라, 독자가 어디서 시작해야 할지 모르는 상태가 문제입니다.

## 단계별로 작은 문서 세트 만들기

### 1단계 — README 다섯 블록 만들기

```markdown
# 1_readme.md
## What — one-sentence description
## Why — why it exists
## Quick start — working in 60 seconds
## Configuration — env var table
## Links — go deeper
```

좋은 README는 처음 들어온 사람이 1분 안에 가치를 이해하고 다음 링크로 이동할 수 있게 만듭니다.

### 2단계 — 한 장짜리 ADR 남기기

```markdown
# 2_adr.md
# ADR 0012: introduce cache
- Context, Decision, Alternatives, Consequences
- Date, Owners
```

결정은 코드를 구현한 시점보다 오래 살아남습니다. 이유를 남기지 않으면 나중에 같은 토론을 반복하게 됩니다.

### 3단계 — docstring과 타입 힌트 쓰기

```python
# 3_docstring.py
def compute_invoice(amount: int, tax_rate: float) -> int:
    """세금을 포함한 금액을 센트 단위로 반환합니다.

    Raises:
        ValueError: amount가 음수일 때 발생합니다.
    """
```

함수 시그니처와 docstring은 가장 가까운 사용 계약입니다.

### 4단계 — 런북 만들기

```markdown
# 4_runbook.md
## Symptom
- 5xx error rate > 2% for 5 min
## Diagnose
1. Check Grafana dashboard X
2. Look at the latest deploy log
## Action
- Roll back immediately (`kubectl rollout undo ...`)
```

런북은 평온한 낮이 아니라 새벽 장애 상황에서도 그대로 따라갈 수 있어야 의미가 있습니다.

### 5단계 — 온보딩 체크리스트 두기

```markdown
# 5_onboarding.md
- [ ] Clone repo, run dev environment
- [ ] Land first PR (typo fix)
- [ ] Shadow first incident within a week
```

온보딩 문서는 새로 들어온 사람이 첫 30일 안에 무엇을 경험해야 하는지 명확하게 보여 줍니다.

## 문서 세트를 검증하는 방법

문서 품질은 양보다 찾기 쉬움과 재사용성에서 드러납니다. 실제 신규 입사자나 온콜 상황을 떠올리며 문서 세트를 따라가 보세요.

### 확인 절차

1. 저장소 README만 보고 개발 환경을 띄울 수 있는지 확인합니다.
2. 최근 큰 결정 하나가 ADR이나 RFC로 남아 있는지 찾습니다.
3. 사고 대응 절차를 런북 한 장으로 따라갈 수 있는지 검토합니다.

**예상 결과:**

- README가 좋으면 첫 5분 안에 프로젝트 목적과 실행 경로가 보입니다.
- ADR이 있으면 과거 결정을 다시 논쟁하는 횟수가 줄어듭니다.
- 런북이 있으면 새벽 장애에서도 확인 순서가 분명해집니다.

### 실패 신호

- "위키 어딘가에 있다"는 말만 있고 진입 문서가 없습니다.
- 문서 소유자나 마지막 검토 시점이 없어 신뢰하기 어렵습니다.
- 온보딩 질문이 늘 특정 사람에게만 몰립니다.

## 이 코드에서 먼저 봐야 할 점

- 독자의 목적별로 나누면 문서를 찾기 쉬워집니다.
- ADR은 결정의 이유를 회수 가능하게 만듭니다.
- 런북은 새벽 사고의 비용을 줄입니다.
- README는 사용 설명서이자 저장소의 얼굴입니다.

## 어디서 자주 헷갈릴까요?

첫 번째 오해는 자동 생성 문서만 있으면 충분하다는 생각입니다. API 레퍼런스는 필요하지만, 그것만으로는 왜 이런 구조를 택했는지 설명할 수 없습니다. 자동 생성 문서는 레퍼런스의 일부일 뿐입니다.

두 번째 오해는 모든 문서를 한 페이지 위키에 몰아넣는 것입니다. 정보는 많아 보이지만 실제로는 아무도 찾지 못합니다. 문서의 양보다 탐색 구조가 먼저 중요합니다.

세 번째 오해는 문서에 소유자가 없어도 된다고 보는 태도입니다. 마지막 검토 날짜와 책임자가 없으면 문서는 곧 믿기 어려운 정보가 됩니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 문서를 코드처럼 다룹니다. 저장소 안의 마크다운 파일로 관리하고, PR로 변경하고, CI에서 링크와 구조를 검사합니다. 새로운 기능은 RFC, 코드, 문서 업데이트가 한 흐름 안에 묶여 움직이는 경우가 많습니다.

시니어 엔지니어는 코드 리뷰만큼 문서 리뷰도 중요하게 봅니다. README가 약한 저장소는 대개 구조 설명이 약하고, 런북이 없는 시스템은 운영 복구성이 낮고, ADR이 없는 팀은 같은 설계 논쟁을 반복하는 경우가 많기 때문입니다.

## 체크리스트

- [ ] README에 다섯 개 기본 블록이 있나요?
- [ ] 큰 결정에 ADR이 있나요?
- [ ] docstring이 사용 계약을 설명하나요?
- [ ] 사고 대응용 런북이 있나요?
- [ ] 각 문서에 소유자와 검토 시점이 있나요?

## 연습 문제

1. 현재 저장소 README를 다섯 블록 구조로 다시 작성해 보세요.
2. 최근 결정 하나를 ADR 형식으로 바꿔 보세요.
3. 가장 최근 사고를 기준으로 한 장짜리 런북을 써 보세요.

## 정리

문서화는 코드가 부족해서 하는 일이 아닙니다. 사람이 없어도 지식이 움직이게 하기 위해 하는 일입니다. README, ADR, docstring, 런북, 온보딩 문서가 제자리에 있으면 팀은 특정 개인의 기억에 덜 의존하게 됩니다.

다음 글에서는 그 사람들 사이의 협업 자체를 다룹니다. RFC, 비동기 의사결정, 회의 최소화, 핸드오프 메모가 어떻게 팀 시간을 되돌려 주는지 이어서 보겠습니다.

<!-- toc:begin -->
- [소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- [요구사항 이해하기](./02-understanding-requirements.md)
- [설계와 구현의 차이](./03-design-vs-implementation.md)
- [코드 리뷰](./04-code-review.md)
- [테스트 전략](./05-testing-strategy.md)
- [버전 관리와 릴리스](./06-version-control-and-release.md)
- **문서화 (현재 글)**
- 협업 프로세스 (예정)
- 유지보수와 기술부채 (예정)
- 좋은 소프트웨어의 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Diataxis Framework](https://diataxis.fr/)
- [The Documentation System — Daniele Procida](https://documentation.divio.com/)
- [Write the Docs — Documentation Guide](https://www.writethedocs.org/guide/)
- [Google — Documentation Best Practices](https://google.github.io/styleguide/docguide/best_practices.html)

Tags: Computer Science, SoftwareEngineering, Documentation, README, ADR, Knowledge
