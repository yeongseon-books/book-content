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
seo_description: 디자인 패턴을 정답집이 아니라 반복되는 설계 문제를 빠르게 합의하기 위한 공통 어휘로 이해하도록 돕는 입문 글입니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (1/10): 디자인 패턴이란 무엇인가?

처음 디자인 패턴을 배우면 대부분 이름부터 외우게 됩니다. Singleton, Strategy, Adapter, Observer, Factory. GoF 책을 펼치면 23개가 줄지어 등장하니까, 자연스럽게 "이걸 다 알아야 코드를 잘 짜는구나" 하는 인상을 받습니다. 그런데 실무에서 패턴이 실제로 힘을 발휘하는 순간은 따로 있습니다. 시험 문제를 푸는 순간이 아니라, 코드 리뷰에서 "여기 분기가 자꾸 늘어나니까 Strategy로 빼는 게 어떨까요"라고 한 줄 던졌을 때, 팀원 전체가 같은 구조를 머리에 떠올리는 순간입니다.

이 글은 Design Patterns 101 시리즈의 첫 번째 글입니다. 디자인 패턴을 "외워야 할 23개 정답"이 아니라, **반복되는 설계 문제를 짧게 설명하고 빠르게 합의하기 위한 공통 어휘**로 다시 정의해 보겠습니다. 이름이 가진 무게는 그다음입니다.

![Design Patterns 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/01/01-01-concept-at-a-glance.ko.png)

*문제 인식에서 패턴 선택까지의 흐름*

## 먼저 던지는 질문

- 디자인 패턴은 결국 무엇을 가리키는 말일까요?
- 패턴 이름을 외우는 것과 패턴을 이해하는 것은 어떻게 다를까요?
- 같은 문제에 패턴을 쓰는 팀과 안 쓰는 팀의 차이는 어디에서 생길까요?

## 디자인 패턴을 한 문장으로 다시 정의하기

디자인 패턴은 "이 코드를 이렇게 짜라"는 답안이 아닙니다. 더 정확히 말하면 **이런 종류의 문제가 반복해서 나타날 때, 사람들이 비슷한 모양으로 풀어 온 해법에 붙인 이름**입니다. 패턴의 본체는 코드가 아니라 문제-해법 쌍입니다.

이 점이 중요한 이유는 단순합니다. 같은 패턴이라도 언어가 다르면 구현 모양이 완전히 달라지기 때문입니다. Java에서 Singleton은 보통 `private` 생성자 + `static` 인스턴스로 구현되지만, Python에서는 모듈 자체가 한 번만 import되니까 그냥 모듈 변수가 더 자연스럽습니다. 코드는 다르지만 둘 다 같은 패턴입니다. 풀려는 문제, 즉 "전역에서 단일 인스턴스를 공유한다"가 같기 때문입니다.

그래서 패턴을 배운다는 말은 두 가지를 동시에 익힌다는 뜻입니다.

1. 어떤 문제 신호를 보면 어떤 패턴 후보가 떠올라야 하는가
2. 그 패턴을 내가 쓰는 언어에서 가장 자연스럽게 어떻게 표현하는가

이 두 가지가 분리되지 않으면, "Singleton 클래스 만드는 법"만 외우고 "Singleton이 풀려고 하는 문제가 무엇인지"는 모르는 상태가 됩니다. 그런 상태에서 패턴을 적용하면 거의 항상 과한 설계가 됩니다.

## GoF의 23개 패턴은 왜 세 묶음으로 나뉠까

1994년에 나온 *Design Patterns: Elements of Reusable Object-Oriented Software*, 흔히 GoF(Gang of Four) 책이라 불리는 이 책은 23개 패턴을 세 가지로 분류합니다.

| 분류 | 풀려는 문제 | 대표 패턴 |
| --- | --- | --- |
| Creational | 객체를 어떻게 만들고 누가 그 결정을 내리는가 | Factory Method, Builder, Singleton |
| Structural | 객체들을 어떻게 묶고 인터페이스를 어떻게 맞추는가 | Adapter, Decorator, Facade |
| Behavioral | 객체들 사이에 책임을 어떻게 나누고 어떻게 소통하는가 | Strategy, Observer, Command |

이 분류는 시험에 나오는 분류가 아닙니다. 실제로 코드 리뷰에서 "이건 어떤 패턴이 어울릴까"를 빠르게 좁힐 때 쓰는 도구입니다. 새 객체 생성 코드가 자꾸 복잡해지면 Creational부터 봅니다. 외부 API가 우리가 원하는 모양과 안 맞으면 Structural을 봅니다. 같은 동작을 여러 가지 방식으로 바꿔 가며 실행하고 싶으면 Behavioral을 봅니다.

이 시리즈의 2-4장에서 각 묶음을 한 장씩 다루고, 5-7장에서 실무에서 가장 자주 쓰는 Strategy/Adapter/Observer 셋을 깊게 봅니다. 그래서 1장에서는 분류 자체를 외우기보다 "내가 보는 문제가 어느 묶음에 속하는지" 감을 잡는 데 집중하는 편이 좋습니다.

## 코드 한 줄로 보는 패턴의 가치

이론보다 코드 한 토막이 더 명확합니다. 결제 처리 로직이 다음과 같이 시작했다고 해 봅시다.

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

처음에는 멀쩡합니다. 결제 수단이 둘일 때는 이게 가장 읽기 쉽습니다. 그런데 결제 수단이 다섯 개로 늘고, 각 결제마다 환불 로직도 필요해지고, 일부 결제는 webhook 검증이 필요해지면, 이 함수 하나가 점점 거대해지면서 같은 모양의 `if kind == ...`가 코드 곳곳에 복제되기 시작합니다. 새 결제 수단을 추가할 때마다 여러 파일을 동시에 열어야 하고, 그중 하나를 깜빡하면 미묘한 버그가 납니다.

Strategy 패턴을 알고 있는 사람은 이 순간 단어가 하나 떠오릅니다. "이거 분기 폭발이네." 그리고 다음과 같이 정리합니다.

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

코드가 짧아진 게 핵심이 아닙니다. 핵심은 **새 결제 수단을 추가하는 작업이 "기존 함수 수정"에서 "새 클래스 한 개 추가 + dict 한 줄 추가"로 바뀌었다**는 점입니다. 변경의 모양이 바뀐 겁니다. 이 차이를 한 단어로 부를 수 있는 게 바로 패턴의 가치입니다. 팀 누구나 "Strategy로 빼자" 한 마디로 이 의도를 공유할 수 있게 됩니다.

## 패턴이 만드는 진짜 효과: 합의 속도

저는 시니어 엔지니어가 주니어와 가장 크게 차이가 나는 지점이 "코드를 빨리 짜는 것"이 아니라 "팀과 빨리 합의하는 것"이라고 생각합니다. 그리고 패턴은 이 합의 속도를 결정적으로 끌어올립니다.

리뷰에서 다음과 같은 코멘트가 달렸다고 해 봅시다.

> "여기 외부 SDK를 직접 호출하지 말고 Adapter로 감싸 주세요. 그래야 테스트할 때 SDK 의존성을 끊을 수 있고, 나중에 SDK를 갈아끼울 때도 도메인 코드는 안 건드려도 됩니다."

이 한 문단을 패턴 이름 없이 풀어 쓰면 두 단락이 됩니다. 어떤 인터페이스를 만들어야 하는지, 왜 그게 필요한지, 무슨 이득이 있는지 일일이 설명해야 합니다. Adapter라는 이름 하나가 그 두 단락을 압축합니다. 받는 사람도 "아, Adapter 적용하면 되겠네" 하고 머릿속에 구조가 바로 그려집니다.

반대로 패턴 이름만 알고 문제를 모르면 더 위험합니다. "여긴 Observer가 어울려요"라고 던졌는데 막상 왜 어울리는지 설명하지 못하면, 패턴은 단순성을 만드는 도구가 아니라 **복잡성을 정당화하는 라벨**이 됩니다. 그래서 패턴을 도입할 때는 항상 "어떤 문제를 풀고 있는가"를 먼저 말로 정리하는 습관이 중요합니다.

## 패턴을 잘못 쓰면 생기는 비용

패턴은 공짜가 아닙니다. 한쪽에서 무언가를 얻으면 다른 쪽에서 무언가를 잃습니다. 이 비용을 미리 셈하지 않으면 패턴은 코드 품질을 떨어뜨립니다.

위의 결제 예시에서 Strategy를 적용했을 때 잃은 것을 솔직하게 적어 보면 다음과 같습니다.

- **읽어야 할 클래스가 늘었습니다.** 함수 하나 보면 끝났던 흐름이 이제는 Protocol + 여러 구현 + dict까지 한 번에 봐야 이해됩니다.
- **간접 호출이 생겼습니다.** "이 결제는 정확히 어디서 처리되지"를 따라가려면 dict lookup을 한 번 더 거쳐야 합니다.
- **테스트가 약간 길어집니다.** 가짜 Processor를 만들어 주입해야 하는 경우가 생깁니다.

이 비용이 얻는 것보다 작으면 패턴을 도입할 가치가 있습니다. 결제 수단이 두 개고 앞으로도 두 개일 게 명확하다면, 위의 비용이 분기 폭발 비용보다 더 큽니다. 그러면 그냥 `if/elif`가 정답입니다. 패턴 적용 여부는 미래의 변경 가능성에 대한 베팅에 가깝습니다.

저는 팀이 패턴을 도입할 때마다 짧은 메모를 남기는 걸 권합니다. 길게 쓸 필요 없습니다.

```text
# decisions/payment-strategy.md
- 도입: Strategy
- 이유: 결제 수단이 분기 2 → 5로 늘었고, 각 수단마다 charge/refund/webhook 흐름이 다름
- 비용: 클래스 수 +5, dict lookup 1회
- 다시 검토할 시점: 결제 수단이 다시 2개 이하로 줄거나, 동작이 완전히 같아질 때
```

이런 기록이 있으면 6개월 뒤에 새로 합류한 동료가 "왜 이렇게 복잡하게 짰지" 하는 질문을 던졌을 때, "분기가 그때 5개였고 이런 트레이드오프로 선택했어요"라고 30초 안에 설명할 수 있습니다. 패턴은 결정이고, 결정은 기록될 때만 자산이 됩니다.

## 패턴이 아닌 것을 패턴이라고 부르지 않기

마지막으로 한 가지 구분이 필요합니다. 코드에서 자주 보는 모양 중에는 패턴이 아니라 **이디엄(idiom)** 이거나 **언어 기능** 인 경우가 많습니다.

- Python의 context manager (`with` 문)는 패턴이 아니라 **언어 기능**입니다. RAII 같은 개념을 언어가 직접 지원하는 것에 가깝습니다.
- 리스트 내포 (`[x*2 for x in items]`)는 패턴이 아니라 **이디엄**입니다. 특정 언어에서 자연스러운 표현 방식이지, 다른 언어로 가져갈 수 있는 구조적 해법이 아닙니다.
- `dataclass`로 값 객체를 표현하는 것도 패턴보다는 언어 기능입니다.

이걸 구분하는 게 왜 중요할까요? 모든 좋은 코딩 습관을 "패턴"이라고 부르기 시작하면, 정작 패턴이라는 단어가 가진 합의 속도라는 가치가 흐려지기 때문입니다. 패턴은 언어와 무관하게 같은 문제-해법 구조를 가리킬 때 쓰는 단어로 남겨 두는 편이 깨끗합니다.

## 1장에서 가져갈 한 가지

이 장에서 단 하나만 가져가야 한다면 이겁니다. **패턴 이름을 외우기 전에, 그 패턴이 어떤 문제를 풀고 어떤 비용을 부르는지 먼저 한 문장으로 말할 수 있어야 합니다.** 이게 되면 23개를 다 외우지 않아도 실무에서 필요한 5-7개만으로 충분히 강력해집니다. 이게 안 되면 23개를 다 외워도 적용하는 순간마다 팀에 부담이 됩니다.

다음 장에서는 GoF 분류 중 첫 번째인 Creational 패턴을 봅니다. "객체를 어떻게 만들고, 그 결정을 누가 내리는가"라는 질문을 중심으로, Factory Method와 Builder가 왜 필요한지부터 시작합니다.

## 처음 질문으로 돌아가기

- **디자인 패턴은 결국 무엇을 가리키는 말일까요?**
  - 코드가 아니라 **문제-해법 쌍**입니다. "이런 종류의 문제가 반복해서 나타날 때 이런 모양으로 풀어 온 사례"에 붙인 이름이고, 그래서 같은 패턴도 언어에 따라 구현이 달라집니다. Singleton이 Java에서는 `private` 생성자 + `static` 인스턴스지만 Python에서는 모듈 변수인 이유가 여기에 있습니다.
- **패턴 이름을 외우는 것과 패턴을 이해하는 것은 어떻게 다를까요?**
  - 이름만 외우면 "어떤 코드를 쓰는가"는 알지만 "왜 쓰는가"는 모릅니다. 결제 분기 예시에서 본 것처럼, 같은 Strategy도 결제 수단이 2개일 때는 과한 설계이고 5개일 때는 적절한 추상화입니다. 패턴 이해의 핵심은 **언제 비용을 치를 가치가 있는지 판단할 수 있는가**입니다.
- **같은 문제에 패턴을 쓰는 팀과 안 쓰는 팀의 차이는 어디에서 생길까요?**
  - 코드 품질보다 **합의 속도**에서 가장 크게 갈립니다. "여기 Adapter로 감싸 주세요" 한 문장이 두 단락의 설명을 압축하기 때문입니다. 단, 이 효과는 팀 전체가 같은 어휘를 공유할 때만 나타납니다. 한 명만 패턴 이름을 쓰면 오히려 소통 비용이 늘어납니다.

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
- [Patterns of Enterprise Application Architecture (Fowler)](https://martinfowler.com/eaaCatalog/)

### 실무 확장 읽을거리

- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)
- [Refactoring (Martin Fowler)](https://martinfowler.com/books/refactoring.html)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, SoftwareDesign, GoF, Architecture, Foundations
