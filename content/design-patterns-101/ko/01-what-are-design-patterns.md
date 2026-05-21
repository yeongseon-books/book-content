---
series: design-patterns-101
episode: 1
title: "디자인 패턴 101 (1/10): 디자인 패턴이란 무엇인가?"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - DesignPatterns
  - SoftwareDesign
  - GoF
  - Architecture
  - Foundations
seo_description: 디자인 패턴을 정답집이 아니라 반복되는 설계 문제를 설명하고 합의하는 공통 어휘로 이해하도록 돕는 입문 글입니다.
last_reviewed: '2026-05-15'
---

# 디자인 패턴 101 (1/10): 디자인 패턴이란 무엇인가?

디자인 패턴을 처음 배우면 대개 이름부터 외우기 시작합니다. Strategy, Adapter, Observer 같은 이름이 먼저 보이기 때문입니다. 하지만 실무에서 패턴이 힘을 발휘하는 순간은 암기 시험이 아니라, 같은 문제를 반복해서 만나는 시점입니다.

이 글은 Design Patterns 101 시리즈의 첫 번째 글입니다.

이번 글에서는 디자인 패턴을 “정답 모음집”이 아니라, 반복되는 설계 문제를 빠르게 설명하고 합의하기 위한 공통 어휘로 정리해 보겠습니다. 핵심은 패턴 이름보다 먼저, 그 이름이 어떤 문제와 어떤 트레이드오프를 함께 불러오는지 이해하는 것입니다.

![Design Patterns 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/01/01-01-concept-at-a-glance.ko.png)
*Design Patterns 101 1장 흐름 개요*

## 먼저 던지는 질문

- 디자인 패턴을 한 문장으로 정의하면 무엇일까요?
- GoF가 정리한 23개 패턴은 어떤 기준으로 나뉠까요?
- 패턴은 왜 코드보다 대화에서 먼저 가치를 만들까요?

## 왜 중요한가

패턴의 가장 큰 효용은 구현 자체보다 합의 속도에 있습니다. 코드 리뷰에서 “여기 분기가 계속 늘어나니 Strategy로 빼자”라고 말했을 때, 팀 전체가 비슷한 구조를 즉시 떠올릴 수 있다면 이미 절반은 해결된 셈입니다.

반대로 패턴 이름만 알고 문제를 모르면 실무에서는 오히려 더 위험합니다. 이름은 그럴듯한데 왜 도입했는지 설명하지 못하면, 패턴은 설계를 단순화하는 도구가 아니라 복잡성을 정당화하는 장식이 됩니다.

## 한눈에 보는 개념

## 핵심 용어

- **디자인 패턴**: 반복해서 나타나는 설계 문제에 검증된 해법 구조를 붙인 이름입니다.
- **GoF**: Gang of Four를 뜻하며, 23개 패턴을 체계적으로 정리한 저자 그룹입니다.
- **Creational / Structural / Behavioral**: 생성, 구조, 행위를 기준으로 나눈 세 가지 패턴 계열입니다.
- **안티패턴**: 흔히 쓰이지만 결과적으로 해로운 접근입니다.
- **이디엄(idiom)**: 특정 언어의 문법과 관용구에 밀착된 작은 패턴입니다.

## 변경 전후 비교

**Before**

```python
# "if kind" 분기 로직이 곳곳에 흩어짐
if kind == "credit": process_credit(...)
elif kind == "paypal": process_paypal(...)
```

**After**

```python
# 한 줄로 보는 Strategy pattern
processor = PROCESSORS[kind]
processor.charge(...)
```

이 차이의 핵심은 코드 길이가 아닙니다. 의도가 이름 붙은 구조로 드러났다는 점입니다. 패턴은 종종 구현보다 설명을 먼저 정리해 줍니다.

## 패턴을 익히는 5단계

### 1단계 — 문제를 먼저 알아봅니다

```python
# 1_problem.py
# 같은 분기, 같은 객체 생성, 같은 알림 흐름이 반복되는가?
# 그때가 pattern을 적용할 시점
```

패턴은 공중에서 떨어지지 않습니다. 같은 분기, 같은 생성 방식, 같은 알림 흐름이 반복될 때 비로소 패턴을 꺼낼 이유가 생깁니다.

### 2단계 — 문제에 이름을 붙입니다

```python
# 2_name.py
# 분기? Strategy. 생성? Factory. 알림? Observer.
```

이름은 단순한 라벨이 아닙니다. 문제와 해법 구조를 함께 호출하는 압축된 설명입니다.

### 3단계 — 구조를 먼저 그립니다

```python
# 3_structure.py
# 코드 작성 전에 class diagram부터 그리기
```

패턴은 코드 조각이 아니라 관계의 모양입니다. 클래스를 어떻게 나누고, 누가 누구를 알고, 어디서 확장되는지 먼저 그려 보면 과한 설계를 줄이기 쉽습니다.

### 4단계 — 작게 적용합니다

```python
# 4_small.py
# 시스템 전체 적용 전에 한 module에서 먼저 검증
```

처음부터 시스템 전체에 패턴을 퍼뜨리면 실패 비용이 커집니다. 한 모듈, 한 경계, 한 분기부터 적용해 보고 실제 이득이 있는지 확인하는 편이 안전합니다.

### 5단계 — 트레이드오프를 적어 둡니다

```python
# 5_tradeoff.md
# - 얻은 점: 분기 제거, 확장 용이
# - 잃은 점: 읽어야 할 class 증가
```

패턴은 늘 무언가를 얻는 대신 다른 비용을 추가합니다. 그 비용을 적지 않는 순간, 팀은 복잡성을 공짜라고 착각하기 쉽습니다.

## 이 코드에서 주목할 점

- 패턴은 코드를 바꾸기 전에 팀의 대화 방식을 먼저 바꿉니다.
- 어떤 패턴이든 이득과 비용이 함께 움직입니다.
- 패턴 적용 범위는 대개 전역이 아니라 국소적입니다.

## 자주 하는 실수 5가지

1. **어디에나 패턴을 들이대는 경우**: 단순한 코드가 불필요하게 복잡해집니다.
2. **이름만 외우고 문제를 모르는 경우**: 적용해야 할 순간을 못 알아봅니다.
3. **언어 특성을 무시하는 경우**: Python에서 모듈이면 충분한데 Singleton 클래스를 억지로 만듭니다.
4. **트레이드오프를 빼먹는 경우**: 클래스만 늘고 설명 가능성은 오히려 떨어집니다.
5. **패턴이 곧 정답이라고 믿는 경우**: 더 단순한 해법을 놓칩니다.

## 실무에서는 이렇게 드러납니다

패턴은 보통 코드 리뷰 어휘로 가장 자주 등장합니다. “여긴 Adapter 경계가 필요합니다”, “이 분기는 Strategy 모양입니다” 같은 말이 팀 안에서 자연스럽게 통하면, 설계 대화의 해상도가 훨씬 높아집니다. 결국 패턴은 구현 세부보다 합의를 빠르게 만드는 도구입니다.

## 빠르게 검증해 보기

패턴을 붙이기 전에 아래 세 가지를 먼저 확인해 보세요.

- 같은 분기, 생성, 알림 구조가 실제 코드에 세 번 이상 반복되는지 셉니다.
- 패턴 이름을 붙이기 전에 문제를 한 문장으로 적어 봅니다.
- 패턴을 도입했을 때 설명이 쉬워지는지, 아니면 추상화만 늘어나는지 비교합니다.

**기대 결과:** 패턴이 도움이 되는 경우, “왜 이 패턴이 필요한지”와 “무슨 비용이 생기는지”를 동시에 설명할 수 있어야 합니다.

## 시니어 엔지니어는 이렇게 판단합니다

- 패턴을 해법이 아니라 공통 어휘로 다룹니다.
- 이름보다 문제를 먼저 봅니다.
- 전역 적용보다 작은 범위에서 효과를 검증합니다.
- 트레이드오프를 항상 함께 설명합니다.
- 마지막까지 더 단순한 해법이 없는지 다시 확인합니다.

## 체크리스트

- [ ] 내가 푸는 문제를 한 줄로 적을 수 있는가?
- [ ] 그 문제에 어울리는 패턴 이름이 자연스럽게 떠오르는가?
- [ ] 구조를 코드보다 먼저 설명할 수 있는가?
- [ ] 이득과 비용을 함께 적었는가?
- [ ] 패턴 없이 더 단순하게 풀 수는 없는가?

## 연습 문제

1. 현재 코드에서 같은 분기 구조가 세 번 이상 반복되는 지점을 하나 찾습니다.
2. 그 문제에 가장 잘 맞는 패턴 이름을 하나 붙여 봅니다.
3. 적용 후 얻은 점 두 가지와 잃은 점 두 가지를 적어 봅니다.

## 정리 및 다음 글

디자인 패턴은 정답이 아니라 어휘입니다. 다음 글부터는 GoF의 23개 패턴을 생성, 구조, 행위 세 묶음으로 나눠서 살펴보겠습니다. 먼저 객체를 어떻게 만들 것인가를 다루는 Creational 패턴부터 시작합니다.

## 실무 심화: 패턴을 설계 의사결정 문서로 연결하기

패턴 학습의 목적은 이름을 아는 데서 끝나지 않습니다. 실무에서는 "왜 이 구조를 선택했는가"를 나중에 다시 설명해야 하고, 팀이 바뀌어도 같은 판단을 재현할 수 있어야 합니다. 그래서 패턴은 코드 안에만 두지 않고 ADR(Architecture Decision Record), 리뷰 체크리스트, 테스트 설계와 함께 다뤄야 합니다.

### 유엠엘 유사 다이어그램으로 책임 경계 확인

```text
[요구사항] --> [의사결정]
[의사결정] --> [패턴 후보: Strategy/Adapter/Observer]
[패턴 후보] --> [코드 구조]
[코드 구조] --> [테스트 전략]
[테스트 전략] --> [운영 지표]
```

이 흐름을 문서로 남기면 패턴 도입이 취향 논쟁이 아니라 근거 기반 결정이 됩니다.

### 변경 전후 리팩터링

```python
# 변경 전: 주문 할인 정책이 서비스 레이어에 박혀 있는 경우

def checkout(user_tier: str, amount: int) -> int:
    if user_tier == "vip":
        return int(amount * 0.8)
    if user_tier == "partner":
        return int(amount * 0.9)
    return amount
```

```python
# 변경 후: 정책 객체로 분리
from typing import Protocol

class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int: ...

class VipPolicy:
    def apply(self, amount: int) -> int:
        return int(amount * 0.8)

class PartnerPolicy:
    def apply(self, amount: int) -> int:
        return int(amount * 0.9)

class CheckoutService:
    def __init__(self, policy: DiscountPolicy) -> None:
        self.policy = policy

    def checkout(self, amount: int) -> int:
        return self.policy.apply(amount)
```

리팩터링 포인트는 코드 길이가 아니라 변경 축의 분리입니다. 정책 변경이 서비스 로직을 흔들지 않게 만들면 배포 리스크가 줄어듭니다.

### 장고/플라스크에서 드러나는 패턴

- Django에서는 결제, 알림, 권한 정책을 서비스 객체로 분리할 때 Strategy 성격이 자연스럽게 등장합니다.
- Flask에서는 블루프린트 경계에서 외부 SDK를 Adapter로 감싼 뒤 도메인 인터페이스만 노출하면 테스트가 쉬워집니다.
- 공통적으로 "프레임워크 객체를 도메인으로 직접 흘려보내지 않는다"는 경계 규칙이 유지보수 비용을 결정합니다.

### 솔리드 매핑으로 검증하기

| 관점 | 패턴 적용 전 | 패턴 적용 후 |
| --- | --- | --- |
| SRP | 서비스가 정책+흐름을 함께 가짐 | 정책 책임과 흐름 책임 분리 |
| OCP | 정책 추가 시 기존 함수 수정 | 정책 클래스 추가로 확장 |
| DIP | 구체 조건문에 의존 | 추상 정책 인터페이스 의존 |

이 표를 리뷰 때 사용하면 "패턴을 왜 넣었는지"를 기능 관점이 아닌 설계 관점으로 합의할 수 있습니다.

### 운영 관점 체크

1. 정책이 늘어날 때 테스트 케이스가 선형적으로 증가하는지 확인합니다.
2. 새 정책 추가가 기존 코드 수정 없이 가능한지 PR 단위로 검증합니다.
3. 로그에 정책 이름과 적용 결과를 남겨 장애 시 재현 가능성을 확보합니다.

패턴은 예쁜 구조를 위한 장식이 아니라, 변경 비용과 장애 비용을 줄이기 위한 안전장치입니다.

## 처음 질문으로 돌아가기

- **디자인 패턴을 한 문장으로 정의하면 무엇일까요?**
  - 본문의 기준은 디자인 패턴이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **GoF가 정리한 23개 패턴은 어떤 기준으로 나뉠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **패턴은 왜 코드보다 대화에서 먼저 가치를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **디자인 패턴이란 무엇인가? (현재 글)**
- Creational 패턴 (예정)
- Structural 패턴 (예정)
- Behavioral 패턴 (예정)
- Strategy 패턴 (예정)
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [refactoring.guru — Design Patterns](https://refactoring.guru/design-patterns)
- [Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/)

### 실무 확장 읽을거리

- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)
- [Refactoring (Martin Fowler)](https://martinfowler.com/books/refactoring.html)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, SoftwareDesign, GoF, Architecture, Foundations
