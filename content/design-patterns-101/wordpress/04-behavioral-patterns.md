---
series: design-patterns-101
episode: 4
title: "바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Behavioral
  - Strategy
  - Observer
  - Command
seo_description: AI가 생성한 코드의 책임 흐름을 읽고 행위 패턴으로 객체 협력 구조를 개선하는 바이브코딩 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 네 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 비즈니스 로직을 짜달라고 하면, 종종 한 클래스가 너무 많은 책임을 지는 코드를 받게 됩니다. 주문 처리 클래스가 알림도 보내고, 상태도 변경하고, 로그도 기록합니다. 행위 패턴은 이 책임을 어떻게 나누고 객체들이 어떻게 협력하게 만드는지를 다룹니다.

---

코드를 잘 나눠 놓았는데도 변경이 어려운 순간이 있습니다. 클래스 하나를 고치면 알림 로직이 깨지고, 상태 전이를 추가하면 기존 분기가 흔들리고, 정렬 방식을 바꾸려면 호출부 전체를 뒤져야 합니다. 이런 문제는 구조가 아니라 **객체 사이의 책임 흐름**이 꼬여 있을 때 나타납니다. Behavioral 패턴은 바로 이 흐름에 이름을 붙이고, 변경이 번지지 않도록 경계를 만드는 도구입니다.

AI가 만든 코드에서도 이 문제가 자주 나타납니다. "주문 제출 로직을 짜줘"라고 하면 `submit()` 메서드 안에 메일 발송, 슬랙 알림, 창고 예약, 포인트 적립이 모두 들어간 코드를 받게 됩니다. 한 달 뒤 SMS 알림을 추가해야 한다면, AI에게 다시 요청할 때 패턴 이름을 알면 훨씬 나은 구조를 요청할 수 있습니다.

> "Behavioral 패턴은 런타임에 객체들이 어떻게 협업하는지를 다루고, 누가 시작하고 누가 응답하며 누가 상태를 들고 가는지를 깔끔하게 정리합니다."

## 이 글에서 다룰 문제

- AI가 만든 코드에서 Command 패턴을 발견하면 어떤 이점이 있을까요?
- State와 Strategy는 코드 모양이 비슷한데, AI에게 어떻게 구분해서 요청할까요?
- 행위 패턴이 없을 때 AI가 만들어 주는 코드의 전형적인 문제는 무엇일까요?
- 바이브코딩에서 행위 패턴을 잘못 적용하면 어떤 문제가 생길까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## Strategy와 Observer 개요

**Strategy**는 알고리즘을 호출부에서 분리해 교체 가능하게 만듭니다. Python에서는 함수가 일급 객체이므로 클래스 없이도 Strategy를 적용할 수 있습니다.

```python
from typing import Callable

PricingStrategy = Callable[[int], int]

def no_discount(price: int) -> int:
    return price

def vip_discount(price: int) -> int:
    return int(price * 0.7)

def checkout(price: int, strategy: PricingStrategy = no_discount) -> int:
    return strategy(price)
```

**Observer**는 한 객체의 상태 변화를 여러 구독자에게 전파합니다. Django signals, JavaScript의 `addEventListener`, Redis Pub/Sub이 모두 이 구조입니다. Strategy는 1:1 교체이고, Observer는 1:N 전파라는 점이 다릅니다.

## Command: 함수 호출 vs. 객체로 저장 가능한 행위

AI에게 텍스트 에디터를 만들어 달라고 할 때 Undo 기능을 요청하면 Command 패턴 구조가 나와야 합니다.

```python
from typing import Protocol
from dataclasses import dataclass, field

class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...

@dataclass
class InsertText:
    document: list[str]
    position: int
    text: str

    def execute(self) -> None:
        self.document.insert(self.position, self.text)

    def undo(self) -> None:
        self.document.pop(self.position)

@dataclass
class Editor:
    document: list[str] = field(default_factory=list)
    history: list[Command] = field(default_factory=list)

    def run(self, cmd: Command) -> None:
        cmd.execute()
        self.history.append(cmd)

    def undo_last(self) -> None:
        if self.history:
            self.history.pop().undo()
```

Command가 함수 호출과 다른 점은 세 가지입니다. 직렬화 가능, 취소 가능, 조합 가능. AI에게 "Command 패턴으로 Undo 지원해줘"라고 하면 이 구조를 만들어 줍니다.

## State와 Strategy의 차이

둘 다 "행위를 별도 객체에 위임한다"는 구조입니다. 차이는 **의도**에 있습니다.

- **Strategy**: 호출자가 알고리즘을 선택합니다. 한번 주입하면 보통 바뀌지 않습니다.
- **State**: 객체 스스로가 내부 상태에 따라 행위를 전환합니다. 전환은 런타임에 반복적으로 일어납니다.

AI에게 TCP 연결 상태 머신을 만들어 달라고 하면 State 패턴 구조가 나와야 합니다.

```python
class Connection:
    def __init__(self) -> None:
        self.state: ConnectionState = Closed()

    def open(self) -> None:
        self.state.open(self)

    def close(self) -> None:
        self.state.close(self)

    def send(self, data: bytes) -> None:
        self.state.send(self, data)
```

`Connection`은 자신의 상태를 모릅니다. 각 상태 객체가 "다음에 어떤 상태로 갈지"를 결정합니다. 새 상태를 추가할 때 기존 상태 클래스를 수정하지 않아도 됩니다.

## Before / After: Observer로 책임 분리하기

**Before — 하나의 메서드가 모든 후속 작업을 직접 호출:**

```python
class Order:
    def submit(self):
        self.save()
        send_email(self.user)
        slack_notify(self.channel)
        warehouse.reserve(self.items)
        analytics.track("order_submitted", self.id)
        points.accrue(self.user, self.total)
```

새 후속 작업이 추가될 때마다 이 메서드를 열어야 합니다.

**After — Observer로 책임 분리:**

```python
class Order:
    def __init__(self, bus: "EventBus") -> None:
        self.bus = bus

    def submit(self) -> None:
        self.save()
        self.bus.publish(OrderSubmitted(user=self.user, items=self.items))
```

`Order`의 책임이 "주문 저장 + 이벤트 발행"으로 줄었습니다. 새 후속 작업은 구독자로 추가합니다.

## 행위 패턴 트레이드오프 정리

| 패턴 | 얻는 것 | 잃는 것 | AI 요청 방법 |
| --- | --- | --- | --- |
| Strategy | 알고리즘 교체가 한 줄 | 간접 호출 추가 | "Strategy 패턴으로 분기 교체해줘" |
| Observer | 발행자-구독자 완전 분리 | 흐름 추적 어려움 | "Observer로 이벤트 기반 구조 만들어줘" |
| Command | 저장·취소·큐잉 가능 | 행위 하나당 클래스 하나 | "Command 패턴으로 Undo 지원해줘" |
| State | 상태 전이 규칙이 명시적 | 상태 수만큼 클래스 증가 | "State 패턴으로 상태 머신 만들어줘" |
| Chain of Responsibility | 핸들러 추가/제거 유연 | 요청 추적 어려움 | "미들웨어 체인으로 요청 처리해줘" |

## AI 활용 팁

**Observer 패턴 요청:**

```
"주문이 제출되면 메일 발송, 슬랙 알림, 포인트 적립이 필요해.
이 후속 작업들이 앞으로 더 늘어날 수 있어.
Observer 패턴으로 Order가 직접 호출하지 않고
이벤트를 발행하면 구독자들이 처리하는 구조로 만들어줘."
```

**Command 패턴 요청:**

```
"텍스트 에디터에 Undo/Redo 기능이 필요해.
Command 패턴을 사용해서 각 편집 작업을 객체로 캡슐화하고
history 스택에 저장해줘."
```

**State 패턴 요청:**

```
"주문 상태가 pending → confirmed → paid → shipped → delivered로
전환돼. 각 상태에서 할 수 있는 동작이 달라.
State 패턴으로 각 상태를 클래스로 만들어줘."
```

## 운영 체크리스트

- [ ] Strategy와 State 패턴의 차이를 설명할 수 있습니다.
- [ ] Observer 패턴이 직접 호출보다 나은 경우를 말할 수 있습니다.
- [ ] Command 패턴이 단순 함수 호출과 다른 점을 설명할 수 있습니다.
- [ ] 행위 패턴이 해결하는 공통 문제를 설명할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 행위 패턴은 객체 사이의 책임 흐름을 정리합니다. 둘째 State와 Strategy는 구조가 비슷하지만 의도가 다릅니다. State는 객체가 스스로 상태를 전환하고, Strategy는 호출자가 알고리즘을 선택합니다. 셋째 AI에게 패턴 이름을 명시하면 책임이 명확하게 분리된 코드를 받을 수 있습니다.

## 처음 질문으로 돌아가기

- **AI가 만든 코드에서 Command 패턴을 발견하면 어떤 이점이 있을까요?**
  - Command 패턴이 적용된 코드는 Undo, 작업 큐, 직렬화를 자연스럽게 지원합니다. 패턴을 알면 "어떻게 Undo를 추가할까"가 바로 보입니다.
- **State와 Strategy는 코드 모양이 비슷한데 어떻게 구분하나요?**
  - Strategy는 호출자가 알고리즘을 선택하고 바꿉니다. State는 객체 자신이 내부 조건에 따라 상태를 전환합니다. 전환의 주체가 다릅니다.
- **행위 패턴이 없을 때 AI가 만드는 코드의 전형적인 문제는?**
  - 하나의 메서드에 모든 후속 작업이 직접 호출됩니다. 새 작업이 추가될 때마다 메서드를 열어야 하고, 하나가 실패하면 전체가 실패합니다.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- **바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Command Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/command)
- [State Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/state)

### 실무 확장 읽을거리

- [Chain of Responsibility (refactoring.guru)](https://refactoring.guru/design-patterns/chain-of-responsibility)
- [Python `functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Behavioral, Strategy, Observer, Command
