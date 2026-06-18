---
series: design-patterns-101
episode: 1
title: "바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - SoftwareDesign
  - GoF
  - Architecture
  - AI코딩
seo_description: AI가 생성한 코드 구조를 이해하고 확장하기 위해 디자인 패턴의 본질을 파악하는 바이브코딩 입문 글입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?

**바이브코딩을 위한 디자인 패턴 기초** 시리즈에 오신 것을 환영합니다. 이 시리즈는 AI와 함께 코딩하는 시대에 디자인 패턴을 어떻게 읽고, 이해하고, 활용할 수 있는지를 10편에 걸쳐 다룹니다.

AI가 코드를 만들어 주는 시대에 디자인 패턴을 왜 배워야 할까요? 정확히는 반대입니다. AI가 코드를 만들수록, 그 코드가 어떤 구조로 되어 있는지 이해하는 능력이 더 중요해집니다. Cursor나 Claude가 만들어 준 코드를 확장하려고 할 때, 패턴을 모르면 어디에 무엇을 추가해야 할지 감이 잡히지 않습니다. 이 시리즈는 "AI가 만든 코드를 내 것으로 만드는 능력"을 키우는 것을 목표로 합니다.

첫 번째 글에서는 디자인 패턴이 무엇인지, 왜 배워야 하는지, 그리고 바이브코딩 맥락에서 어떤 의미를 가지는지 이야기합니다.

---

처음 디자인 패턴을 배우면 대부분 이름부터 외우게 됩니다. Singleton, Strategy, Adapter, Observer, Factory. GoF 책을 펼치면 23개가 줄지어 등장하니까, 자연스럽게 "이걸 다 알아야 코드를 잘 짜는구나" 하는 인상을 받습니다. 그런데 실무에서, 특히 AI와 함께 코드를 작성하는 바이브코딩 상황에서 패턴이 진짜 힘을 발휘하는 순간은 따로 있습니다.

AI가 만들어 준 코드에서 `if kind == "credit"`, `elif kind == "paypal"`, `elif kind == "kakao"` 같은 분기가 반복되는 패턴을 봤을 때, "아, 여기 Strategy가 들어가 있네"라고 읽어내는 순간. 그리고 새 결제 수단을 추가해야 할 때 어디에 어떤 코드를 넣어야 하는지 바로 아는 순간입니다.

> "디자인 패턴은 AI가 만든 코드를 읽고 확장하기 위한 번역기입니다. 패턴 이름을 알면 수백 줄 코드의 의도를 한 단어로 이해할 수 있습니다."

## 이 글에서 다룰 문제

- 디자인 패턴은 결국 무엇을 가리키는 말일까요?
- 패턴 이름을 외우는 것과 패턴을 이해하는 것은 어떻게 다를까요?
- AI가 만든 코드에서 패턴을 발견하면 어떤 이점이 있을까요?
- 바이브코딩에서 패턴을 잘못 이해하면 어떤 문제가 생길까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## 디자인 패턴을 한 문장으로 다시 정의하기

디자인 패턴은 "이 코드를 이렇게 짜라"는 답안이 아닙니다. 더 정확히 말하면 **이런 종류의 문제가 반복해서 나타날 때, 사람들이 비슷한 모양으로 풀어 온 해법에 붙인 이름**입니다. 패턴의 본체는 코드가 아니라 문제-해법 쌍입니다.

바이브코딩 관점에서 이 점이 중요한 이유가 있습니다. AI는 패턴을 이미 알고 있습니다. Copilot이나 Claude에게 "결제 수단별로 다른 처리를 해야 한다"고 설명하면, AI는 자연스럽게 Strategy 구조를 생성합니다. 그런데 여러분이 패턴을 모르면 AI가 왜 그런 구조를 만들었는지 이해하기 어렵고, 그 구조를 확장하거나 수정하기도 어렵습니다.

같은 패턴이라도 언어가 다르면 구현 모양이 완전히 달라집니다. Java에서 Singleton은 보통 `private` 생성자 + `static` 인스턴스로 구현되지만, Python에서는 모듈 자체가 한 번만 import되니까 그냥 모듈 변수가 더 자연스럽습니다. 코드는 다르지만 둘 다 같은 패턴입니다. 풀려는 문제, 즉 "전역에서 단일 인스턴스를 공유한다"가 같기 때문입니다.

그래서 패턴을 배운다는 말은 두 가지를 동시에 익힌다는 뜻입니다.

1. 어떤 문제 신호를 보면 어떤 패턴 후보가 떠올라야 하는가
2. 그 패턴을 내가 쓰는 언어에서 가장 자연스럽게 어떻게 표현하는가

## AI가 만든 코드에서 패턴이 보이는 순간

바이브코딩을 하면서 AI에게 결제 처리 로직을 짜 달라고 했더니 이런 코드가 나왔다고 해 봅시다.

```python
def charge(kind: str, amount: int) -> None:
    if kind == "credit":
        # Stripe API 호출
        ...
    elif kind == "paypal":
        # PayPal API 호출
        ...
    elif kind == "kakao_pay":
        # KakaoPay API 호출
        ...
    else:
        raise ValueError(f"unsupported: {kind}")
```

처음에는 멀쩡합니다. 그런데 결제 수단이 다섯 개로 늘고, 각 결제마다 환불 로직도 필요해지고, 일부 결제는 webhook 검증이 필요해지면, 이 함수가 점점 거대해지면서 같은 모양의 `if kind == ...`가 코드 곳곳에 복제됩니다.

Strategy 패턴을 알고 있는 사람은 이 순간 AI에게 이렇게 요청할 수 있습니다. "이 분기 폭발을 Strategy 패턴으로 정리해 줘." 그러면 AI는 다음 구조를 만들어 줍니다.

```python
from typing import Protocol

class PaymentProcessor(Protocol):
    def charge(self, amount: int) -> None: ...
    def refund(self, amount: int) -> None: ...

PROCESSORS: dict[str, PaymentProcessor] = {
    "credit": StripeProcessor(),
    "paypal": PaypalProcessor(),
    "kakao_pay": KakaoPayProcessor(),
}

def charge(kind: str, amount: int) -> None:
    PROCESSORS[kind].charge(amount)
```

이 구조를 이해하면, 새 결제 수단을 추가할 때 어디에 무엇을 써야 하는지 바로 알 수 있습니다. 패턴은 AI와의 대화에서도 공통 언어가 됩니다.

## GoF의 23개 패턴은 왜 세 묶음으로 나뉠까

1994년에 나온 *Design Patterns: Elements of Reusable Object-Oriented Software*, 흔히 GoF(Gang of Four) 책이라 불리는 이 책은 23개 패턴을 세 가지로 분류합니다.

| 분류 | 풀려는 문제 | 대표 패턴 |
| --- | --- | --- |
| Creational | 객체를 어떻게 만들고 누가 그 결정을 내리는가 | Factory Method, Builder, Singleton |
| Structural | 객체들을 어떻게 묶고 인터페이스를 어떻게 맞추는가 | Adapter, Decorator, Facade |
| Behavioral | 객체들 사이에 책임을 어떻게 나누고 어떻게 소통하는가 | Strategy, Observer, Command |

이 분류는 AI가 만든 코드를 분석할 때도 유용합니다. 새 객체 생성 코드가 자꾸 복잡해지면 Creational부터 봅니다. 외부 API가 우리가 원하는 모양과 안 맞으면 Structural을 봅니다. 같은 동작을 여러 가지 방식으로 바꿔 가며 실행하고 싶으면 Behavioral을 봅니다.

## Before / After: 패턴이 만드는 변화

**Before — 분기가 계속 늘어나는 코드:**

```python
def calculate_shipping(carrier: str, weight: float) -> int:
    if carrier == "standard":
        return int(3000 + 500 * weight)
    elif carrier == "express":
        return int(6000 + 800 * weight)
    elif carrier == "same_day":
        return int(15000 + 1200 * weight)
    raise ValueError(f"Unknown carrier: {carrier}")
```

새 배송 업체를 추가할 때마다 이 함수를 열어서 `elif`를 추가해야 합니다.

**After — 확장이 추가로 이루어지는 코드:**

```python
from typing import Protocol

class ShippingStrategy(Protocol):
    def cost(self, weight: float) -> int: ...

class StandardShipping:
    def cost(self, weight: float) -> int:
        return int(3000 + 500 * weight)

class ExpressShipping:
    def cost(self, weight: float) -> int:
        return int(6000 + 800 * weight)

STRATEGIES = {
    "standard": StandardShipping(),
    "express": ExpressShipping(),
}
```

새 배송 업체를 추가할 때 기존 코드를 수정하지 않고 새 클래스를 추가합니다. AI에게 "새 overnight 배송 업체 추가해 줘"라고 하면 어디에 무엇을 넣어야 하는지 바로 알 수 있습니다.

## 바이브코딩에서 자주 하는 실수

| 실수 | 결과 | 올바른 접근 |
| --- | --- | --- |
| AI 코드를 그대로 복사하고 구조를 모름 | 버그가 생겨도 어디를 고쳐야 할지 모름 | 패턴 이름을 AI에게 물어보고 구조 파악 |
| 패턴 이름만 외우고 문제를 모름 | 엉뚱한 곳에 패턴 적용, 복잡도 증가 | "이 패턴이 어떤 문제를 푸는지" 먼저 이해 |
| 모든 코드에 패턴 적용 | 단순한 코드가 복잡해짐 | 분기가 3번 반복될 때 패턴 검토 |
| 패턴 없이 AI에게 구조 요청 | AI가 임의 구조 생성 | "Strategy 패턴으로 짜줘" 처럼 명시 |
| Python에서 Java 스타일 패턴 강제 | 불필요한 보일러플레이트 | 언어에 맞는 표현 방식 학습 |

## AI 활용 팁

**패턴 인식 요청:** AI가 만든 코드에 패턴이 보이면 이렇게 물어보세요.

```
"이 코드에서 사용된 디자인 패턴이 뭐야? 각 부분이 어떤 역할을 하는지 설명해줘."
```

**패턴 기반 코드 생성:** 구조를 처음부터 잘 잡고 싶을 때는 이렇게 요청하세요.

```
"결제 수단이 앞으로 늘어날 가능성이 높아. Strategy 패턴을 사용해서
확장하기 쉬운 결제 처리 코드를 Python으로 짜줘."
```

**패턴 변환 요청:** 기존 코드를 개선하고 싶을 때는 이렇게 말하세요.

```
"이 if/elif 분기를 Strategy 패턴으로 리팩토링해줘.
Python Protocol을 사용하고 함수형 방식으로."
```

## 운영 체크리스트

- [ ] 디자인 패턴을 한 문장으로 정의할 수 있습니다.
- [ ] 생성·구조·행위 세 범주의 역할을 구분할 수 있습니다.
- [ ] AI가 만든 코드에서 패턴을 발견하고 이름을 붙일 수 있습니다.
- [ ] 패턴 남용이 왜 위험한지 설명할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 디자인 패턴은 코드가 아니라 문제-해법 쌍에 붙인 이름입니다. 둘째 바이브코딩에서 패턴을 알면 AI가 만든 코드를 읽고 확장하는 능력이 생깁니다. 셋째 패턴은 AI와의 대화에서 공통 언어가 됩니다. "Strategy 패턴으로 짜줘"라고 말할 수 있으면, AI가 원하는 구조로 코드를 생성해 줍니다.

## 처음 질문으로 돌아가기

- **디자인 패턴은 결국 무엇을 가리키는 말일까요?**
  - 이런 종류의 문제가 반복해서 나타날 때, 사람들이 비슷한 모양으로 풀어 온 해법에 붙인 이름입니다. 패턴의 본체는 코드가 아니라 문제-해법 쌍입니다.
- **패턴 이름을 외우는 것과 패턴을 이해하는 것은 어떻게 다를까요?**
  - 패턴 이름만 외우면 "Singleton 클래스 만드는 법"만 알고 "Singleton이 풀려는 문제가 무엇인지"는 모릅니다. 문제를 알아야 언제 쓸지 판단할 수 있습니다.
- **AI가 만든 코드에서 패턴을 발견하면 어떤 이점이 있을까요?**
  - 수백 줄 코드의 구조를 한 단어로 이해하고, AI에게 패턴 이름으로 수정을 요청하고, 어디에 새 기능을 추가해야 하는지 바로 알 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가? (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [refactoring.guru — Design Patterns](https://refactoring.guru/design-patterns)
- [Patterns of Enterprise Application Architecture (Fowler)](https://martinfowler.com/eaaCatalog/)

### 실무 확장 읽을거리

- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)
- [Refactoring (Martin Fowler)](https://martinfowler.com/books/refactoring.html)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, SoftwareDesign, GoF, Architecture, AI코딩
