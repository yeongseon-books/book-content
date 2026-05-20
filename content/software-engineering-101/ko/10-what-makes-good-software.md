---
series: software-engineering-101
episode: 10
title: "Software Engineering 101 (10/10): 좋은 소프트웨어의 기준"
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
  - Quality
  - SOLID
  - Simplicity
  - Engineering
seo_description: 좋은 소프트웨어의 품질 속성, SOLID, 단순성, 지속 가능성, 시니어가 보는 신호를 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (10/10): 좋은 소프트웨어의 기준

기능이 동작하는 소프트웨어와 좋은 소프트웨어는 같은 말이 아닙니다. 기능은 출발점일 뿐입니다. 시간이 지나면서 기능이 늘고 팀이 바뀌고 사용량이 커질 때도 시스템이 계속 버틸 수 있어야 좋은 소프트웨어라는 말이 성립합니다. 그래서 시니어 엔지니어는 “잘 돌아간다”는 말만으로 만족하지 않습니다.

좋은 소프트웨어를 판단할 때 흔히 코드 스타일이나 추상화 수준에 먼저 시선이 갑니다. 물론 중요합니다. 하지만 실제로 더 큰 신호는 변경 리드 타임, 사고 복구 속도, 신규 입사자의 적응 시간, 사용자 만족도처럼 코드 바깥에서 드러나는 경우가 많습니다. 품질은 내부 구조와 외부 결과가 함께 맞아야 합니다.

이 글은 Software Engineering 101 시리즈의 마지막 글입니다. 여기서는 품질 속성, SOLID 원칙의 짧은 의미, 단순성과 지속 가능성의 관계, 그리고 시니어 엔지니어가 실제로 보는 외부 신호를 정리합니다.

## 먼저 던지는 질문

- 좋은 코드와 좋은 소프트웨어는 왜 같은 말이 아닐까요?
- 품질 속성은 어떤 축으로 나뉘고, 왜 균형이 중요할까요?
- SOLID 원칙은 실무에서 어떤 기준으로 읽어야 할까요?

## 큰 그림

![Software Engineering 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/10/10-01-concept-at-a-glance.ko.png)

*Software Engineering 101 10장 흐름 개요*

이 그림에서는 좋은 소프트웨어의 기준를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 좋은 소프트웨어의 기준의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

동작하는 기능 하나를 만드는 것과, 시간이 지나도 유지 가능한 시스템을 만드는 것은 다른 일입니다. 처음에는 잘 돌아가던 기능도 변경 비용이 너무 높거나, 장애가 잦거나, 새 팀원이 이해하기 어려우면 좋은 소프트웨어라고 말하기 어렵습니다.

품질을 기능의 뒤에 붙는 옵션처럼 다루면 문제는 늦게 드러납니다. 반대로 품질 속성을 초기에 함께 측정하면 설계와 구현 단계에서 더 나은 선택을 할 수 있습니다. 좋은 소프트웨어는 마지막에 다듬는 결과물이 아니라, 처음부터 누적되는 선택의 총합입니다.

## 한눈에 보는 흐름

품질은 한 축이 아니라 여러 축의 균형입니다. 한 방향만 과하게 밀어도 전체 시스템 건강도는 떨어질 수 있습니다.

## 핵심 용어

- **기능 적합성**: 요구사항을 정확히 만족하는 정도입니다.
- 신뢰성: 실패 빈도와 예측 가능성입니다.
- **유지보수성**: 변경에 드는 비용입니다.
- **성능 효율성**: 자원 대비 처리량과 응답성입니다.
- **SOLID**: 객체지향 설계에서 자주 쓰는 다섯 가지 원칙 묶음입니다.

## 전후 비교

**이전 — 기능 중심 시각**

```text
"It works" is the only metric -> change cost explodes in 6 months
```

**이후 — 품질 속성 측정**

```text
lead time, incident rate, MTTR, maintainability score -> decisions become possible
```

측정하지 않으면 개선도 어렵습니다. 좋은 소프트웨어는 감상보다 신호로 판단해야 합니다.

## 단계별로 작은 품질 키트 만들기

### 1단계 — SRP 확인하기

```python
# 1_srp.py
class Invoice:           # 책임 1: 데이터
    ...
class InvoicePrinter:    # 책임 2: 렌더링
    ...
```

하나의 클래스가 여러 이유로 바뀐다면 유지보수 비용이 빠르게 올라갑니다.

### 2단계 — DIP 확인하기

```python
# 2_dip.py
class OrderService:
    def __init__(self, repo: "Repo"):  # 인터페이스에 의존
        self.repo = repo
```

구체 구현보다 추상 경계에 의존할수록 변경 비용을 통제하기 쉬워집니다.

### 3단계 — 복잡도 측정하기

```bash
# 3_complexity.sh
radon cc app/ -a -nb
```

복잡도는 느낌이 아니라 수치로도 볼 수 있습니다. 임계값을 넘는 모듈은 쪼개는 신호로 삼을 수 있습니다.

### 4단계 — 리드 타임 보기

```bash
# 4_lead_time.sh
git log --pretty='%H %as' -- app/ | head
```

코드가 작성되어 배포되기까지 걸리는 시간은 품질과 속도의 균형을 읽는 중요한 신호입니다.

### 5단계 — 외부 신호 정하기

```text
# 5_signals.md
- Time to a new hire's first PR
- MTTR on incidents
- Average lead time for new features
- User satisfaction (NPS, CSAT)
```

내부 코드 지표만으로는 드러나지 않는 진실이 외부 신호에 담기는 경우가 많습니다.

## 품질 신호를 점검하는 방법

좋은 소프트웨어는 추상적인 미감보다 반복 측정 가능한 신호에서 더 분명하게 보입니다. 지금 맡은 시스템에서 내부 지표와 외부 지표를 같이 적어 보세요.

### 확인 절차

1. 기능 적합성, 신뢰성, 유지보수성 가운데 가장 약한 축 하나를 고릅니다.
2. 그 축을 보여 주는 내부 신호 하나와 외부 신호 하나를 적습니다.
3. 다음 분기 안에 추적할 수 있는 기준선과 목표값을 정합니다.

**예상 결과:**

- 품질 논의가 "느낌"에서 "신호"로 바뀝니다.
- 복잡도, 리드 타임, MTTR, 신규 입사자의 첫 PR 시간 같은 값이 서로 연결됩니다.
- SOLID 원칙도 교리가 아니라 변경 비용을 줄이는 도구로 읽히기 시작합니다.

### 실패 신호

- 기능 추가 속도만 보고 나머지 품질 축은 설명하지 못합니다.
- 외부 신호 없이 내부 코드 스타일만으로 품질을 판단합니다.
- 분기마다 다시 보지 않아 수치가 있어도 의사결정에 쓰이지 않습니다.

## 이 코드에서 먼저 봐야 할 점

- 한 클래스에는 하나의 변경 이유가 있어야 합니다.
- 추상 경계에 의존하는 구조가 변경 비용을 좌우합니다.
- 복잡도와 리드 타임은 측정 가능한 품질 신호입니다.
- 사용자와 팀이 겪는 외부 결과가 품질 판단의 중요한 근거입니다.

## 어디서 자주 헷갈릴까요?

첫 번째 실수는 기능만 측정하는 것입니다. 지금은 잘 동작하더라도 변경 속도가 계속 느려지고 사고 복구가 어렵다면 좋은 소프트웨어라고 보기 어렵습니다.

두 번째 실수는 SOLID를 교리처럼 적용하는 태도입니다. 원칙은 생각 도구이지 자동 정답 생성기가 아닙니다. 추상화가 많다고 항상 좋은 구조가 되지는 않습니다.

세 번째 실수는 외부 신호를 무시하는 것입니다. 코드가 아무리 깔끔해 보여도 사용자가 불만족하고 신규 입사자가 적응하지 못하고 MTTR이 길다면 품질 판단은 다시 해야 합니다.

## 실무에서는 이렇게 생각합니다

강한 팀은 DORA 네 가지 지표처럼 외부에서 드러나는 운영 신호를 꾸준히 봅니다. 배포 빈도, 리드 타임, 변경 실패율, MTTR은 코드 품질과 팀 프로세스가 실제로 어떤 결과를 내는지 보여 줍니다. 이런 신호가 있어야 품질 논의가 취향 싸움으로 흐르지 않습니다.

시니어 엔지니어는 단순함을 미학이 아니라 지속 가능성의 조건으로 봅니다. 설명하기 쉬운 구조, 바꾸기 쉬운 경계, 복구하기 쉬운 운영 흐름이 있어야 시스템과 팀이 함께 오래 갈 수 있기 때문입니다.

## 체크리스트

- [ ] 여섯 가지 품질 속성을 설명할 수 있나요?
- [ ] DORA 네 가지 지표를 어떤 방식으로든 추적하나요?
- [ ] 복잡도와 리드 타임을 보고 있나요?
- [ ] SOLID를 도구로 사용하고 있나요?
- [ ] 분기마다 외부 신호를 검토하나요?

## 연습 문제

1. 현재 프로젝트의 DORA 네 가지 지표를 추정해 보세요.
2. SRP나 DIP 관점에서 다시 볼 수 있는 구조 하나를 골라 보세요.
3. 여러분 시스템에 맞는 외부 신호 네 가지를 정의해 보세요.

## 정리

좋은 소프트웨어는 단순하고, 측정 가능하고, 시간이 지나도 팀을 성장시키는 시스템입니다. 기능 적합성, 신뢰성, 유지보수성, 성능, 보안, 사용성을 함께 보고, SOLID 같은 원칙은 생각 도구로만 쓰고, 외부 신호로 실제 결과를 확인해야 합니다.

이 시리즈는 여기서 마무리되지만, 다룬 주제들은 곧바로 더 깊은 주제로 이어집니다. 클린 코드, 설계 패턴, API 설계, 운영 자동화 같은 후속 시리즈를 볼 때도 이 열 편의 관점이 기본 뼈대가 됩니다.

## 처음 질문으로 돌아가기

- **좋은 코드와 좋은 소프트웨어는 왜 같은 말이 아닐까요?**
  - 본문의 기준은 좋은 소프트웨어의 기준를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **품질 속성은 어떤 축으로 나뉘고, 왜 균형이 중요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **SOLID 원칙은 실무에서 어떤 기준으로 읽어야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Engineering 101 (1/10): 소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): 요구사항 이해하기](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): 설계와 구현의 차이](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): 코드 리뷰](./04-code-review.md)
- [Software Engineering 101 (5/10): 테스트 전략](./05-testing-strategy.md)
- [Software Engineering 101 (6/10): 버전 관리와 릴리스](./06-version-control-and-release.md)
- [Software Engineering 101 (7/10): 문서화](./07-documentation.md)
- [Software Engineering 101 (8/10): 협업 프로세스](./08-collaboration-process.md)
- [Software Engineering 101 (9/10): 유지보수와 기술부채](./09-maintenance-and-tech-debt.md)
- **좋은 소프트웨어의 기준 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [ISO/IEC 25010 — Product Quality Model](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [Robert C. Martin — SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [DORA — State of DevOps](https://dora.dev/)
- [A Philosophy of Software Design — John Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)

Tags: Computer Science, SoftwareEngineering, Quality, SOLID, Simplicity, Engineering
