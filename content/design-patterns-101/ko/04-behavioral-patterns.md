---
series: design-patterns-101
episode: 4
title: "디자인 패턴 101 (4/10): 행위 패턴"
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
  - Behavioral
  - Strategy
  - Observer
  - Command
seo_description: Behavioral 패턴으로 객체 협력과 흐름을 읽기 쉬운 구조로 바꾸는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# 디자인 패턴 101 (4/10): 행위 패턴

객체를 잘 나누는 것만으로는 충분하지 않을 때가 있습니다. 누가 누구에게 알릴지, 어떤 알고리즘을 바꿔 끼울지, 요청을 어떻게 객체로 다룰지, 상태 변화에 따라 행동을 어떻게 나눌지가 결국 시스템의 읽기 쉬움과 변경 비용을 좌우하기 때문입니다.

이 글은 Design Patterns 101 시리즈의 4번째 글입니다.

이번 글에서는 Behavioral 패턴을 객체 사이의 협력 방식을 설명하는 공통 언어로 정리해 보겠습니다. 핵심은 if/elif로 흩어진 흐름을 이름 붙은 구조로 바꿔, 협력이 어떻게 일어나는지 코드 위에 드러나게 만드는 것입니다.

![Design Patterns 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/04/04-01-concept-at-a-glance.ko.png)
*Design Patterns 101 4장 흐름 개요*

## 먼저 던지는 질문

- Behavioral 패턴은 어떤 행위 문제를 다룰까요?
- Strategy, Observer, Command는 각각 흐름을 어떻게 분리할까요?
- State와 Iterator는 무엇을 객체로 끌어올릴까요?

## 왜 중요한가

객체 협력이 커질수록 분기와 조건은 눈에 띄지 않게 퍼집니다. 처음에는 단순한 `if/elif`였던 코드가 어느새 정책 선택, 알림 호출, 상태 전이, 순회 로직을 한곳에 끌어안게 되면, 변경 하나가 여러 조건문에 번지는 구조가 됩니다.

Behavioral 패턴은 이런 흐름에 이름과 모양을 줍니다. 알고리즘은 Strategy로, 알림은 Observer로, 요청은 Command로, 상태별 행동은 State로, 순회는 Iterator로 분리하면 책임 경계가 훨씬 선명해집니다.

## 한눈에 보는 개념

## 핵심 용어

- **Strategy**: 알고리즘을 객체나 함수로 분리해 교체 가능하게 만듭니다.
- **Observer**: 한 객체의 변화가 여러 구독자에게 통지되게 만듭니다.
- **Command**: 요청 자체를 객체로 만들어 큐잉, 재시도, 취소 같은 처리를 쉽게 합니다.
- **State**: 상태별 행동을 상태 객체로 분리합니다.
- **Iterator**: 내부 구조를 노출하지 않고 컬렉션을 순회합니다.

## 변경 전후 비교

**Before**

```python
def discount(kind, price):
    if kind == "vip":
        return price * 0.7
    elif kind == "member":
        return price * 0.9
    return price
```

**After**

```python
class Discount:
    def apply(self, p): return p

class Vip(Discount):
    def apply(self, p): return p * 0.7

class Member(Discount):
    def apply(self, p): return p * 0.9
```

새 등급이 생겨도 기존 분기를 뜯어고치지 않아도 됩니다. 행위가 이름 붙은 구조로 분리되면 확장 지점도 훨씬 명확해집니다.

## 행위 패턴을 익히는 5단계

### 1단계 — 전략로 알고리즘을 바꿔 끼웁니다

```python
# 1_strategy.py
class Sorter:
    def __init__(self, strategy): self.strategy = strategy
    def sort(self, data): return self.strategy(data)

asc = Sorter(sorted)
desc = Sorter(lambda d: sorted(d, reverse=True))
```

Python에서는 함수가 일급 객체이기 때문에 Strategy가 꼭 클래스로 시작할 필요는 없습니다. 알고리즘을 분리할 수 있다는 사실이 더 중요합니다.

### 2단계 — 옵저버로 알림을 분리합니다

```python
# 2_observer.py
class Subject:
    def __init__(self): self._subs = []
    def subscribe(self, fn): self._subs.append(fn)
    def notify(self, e):
        for fn in self._subs: fn(e)

s = Subject()
s.subscribe(lambda e: print("LOG:", e))
s.notify("created")
```

이 구조의 이점은 Subject가 구독자를 몰라도 된다는 점입니다. 발행자는 “무슨 일이 일어났는지”만 알리고, 누가 반응할지는 바깥으로 밀어낼 수 있습니다.

### 3단계 — 커맨드로 요청을 객체로 만듭니다

```python
# 3_command.py
class Command:
    def execute(self): ...

class SendEmail(Command):
    def __init__(self, to, body): self.to, self.body = to, body
    def execute(self): mailer.send(self.to, self.body)

queue = [SendEmail("a@x", "hi"), SendEmail("b@x", "hi")]
for c in queue: c.execute()
```

요청이 객체가 되는 순간 큐잉, 재시도, 지연 실행 같은 운영 관점의 기능을 붙이기 쉬워집니다. 단순 함수 호출을 실행 가능한 데이터로 바꾸는 셈입니다.

### 4단계 — 상태로 상태 전이를 분리합니다

```python
# 4_state.py
class Order:
    def __init__(self): self.state = Draft()
    def submit(self): self.state = self.state.submit()

class Draft:
    def submit(self): return Pending()

class Pending:
    def submit(self): return self  # idempotent
```

상태 전이가 복잡해질수록 분기문은 급격히 읽기 어려워집니다. 상태 객체로 분리하면 어떤 상태에서 어떤 전이가 가능한지 훨씬 잘 보입니다.

### 5단계 — 이터레이터로 순회 계약을 노출합니다

```python
# 5_iterator.py
class Bag:
    def __init__(self, items): self.items = items
    def __iter__(self):
        for x in self.items: yield x

for x in Bag([1, 2, 3]):
    print(x)
```

호출자에게 내부 자료구조를 보여 주지 않고도 순회를 허용할 수 있습니다. 이는 데이터 구조 변경 비용을 낮추는 아주 실용적인 계약입니다.

## 이 코드에서 주목할 점

- if/elif에 숨어 있던 흐름이 객체나 함수로 올라옵니다.
- 알고리즘과 그것을 사용하는 컨텍스트가 분리됩니다.
- 요청과 알림이 데이터처럼 다뤄져 저장, 큐잉, 재실행이 가능해집니다.

## 자주 하는 실수 5가지

1. **사소한 로직까지 Strategy 클래스로 만드는 경우**: 함수로도 충분한데 구조만 무거워집니다.
2. **Observer에 순환 알림이 생기는 경우**: A→B→A 루프가 끝나지 않습니다.
3. **Command 안에 비즈니스 로직을 잔뜩 넣는 경우**: 요청 표현과 정책이 섞입니다.
4. **State 객체가 서로 내부를 과도하게 아는 경우**: 결합도가 다시 높아집니다.
5. **Iterator 대신 인덱스와 내부 구조를 그대로 노출하는 경우**: 캡슐화가 깨집니다.

## 실무에서는 이렇게 드러납니다

Django signals는 Observer 모양이고, Celery task는 Command로 읽을 수 있으며, 상태 머신 라이브러리는 State 패턴을 전면에 드러냅니다. Python 컬렉션이 `__iter__`를 제공하는 방식은 Iterator의 일상적인 예입니다. Behavioral 패턴은 프레임워크 속에 이미 많이 들어와 있습니다.

## 빠르게 검증해 보기

Behavioral 패턴이 흐름을 정말 단순하게 만드는지 확인해 보세요.

- 하나의 비즈니스 동작이 몇 개의 분기와 직접 호출로 퍼지는지 따라가 봅니다.
- 그 흐름을 알고리즘, 알림, 요청, 상태 전이, 순회 중 무엇으로 설명할 수 있는지 정리합니다.
- 행동 하나를 바꿀 때 관련 없는 호출자까지 함께 수정해야 하는지 점검합니다.

**기대 결과:** 주 흐름을 추적하기 쉬워지고, 한 종류의 행동 변화가 긴 조건문 전체를 다시 열게 만들지 않아야 합니다.

## 시니어 엔지니어는 이렇게 판단합니다

- Strategy의 첫 후보는 클래스가 아니라 함수라고 봅니다.
- Observer 알림은 한 방향으로만 흐르게 합니다.
- 단순 요청에 Command를 과하게 올리지 않습니다.
- 실제 상태 머신일 때만 State를 도입합니다.
- Iterator를 내부 구조를 숨기는 계약으로 이해합니다.

## 체크리스트

- [ ] Strategy가 꼭 클래스여야 하는가?
- [ ] Observer 알림에 순환 경로가 없는가?
- [ ] Command가 요청 그 자체만 표현하는가?
- [ ] 상태 전이가 한눈에 보이는가?
- [ ] Iterator가 내부 구조를 가리고 있는가?

## 연습 문제

1. 현재의 if/elif 분기 하나를 Strategy로 바꿔 봅니다.
2. 결제 성공 후 메일·슬랙·재고 처리를 Observer 구조로 나눠 봅니다.
3. 외부 API 호출 큐를 Command 객체 형태로 표현해 봅니다.

## 정리 및 다음 글

행동을 객체와 함수로 드러내면 분기가 줄고 협력 구조가 보이기 시작합니다. 다음 글에서는 Behavioral 패턴 가운데 가장 자주 손에 잡히는 Strategy 패턴을 따로 확대해 봅니다.

## 실무 케이스 스터디: 장고/플라스크에서 패턴 선택 기준

패턴 선택은 프레임워크보다 요구사항의 변화 양상에 의해 결정됩니다. 다음 기준은 두 프레임워크에서 공통으로 유효합니다.

### 판단 기준 표

| 질문 | 선택 기준 | 권장 패턴 |
| --- | --- | --- |
| 조건 분기가 월 단위로 늘어나는가 | 정책 확장이 핵심 | Strategy |
| 외부 API 계약이 자주 바뀌는가 | 경계 안정화가 핵심 | Adapter |
| 객체 조립 단계가 많고 옵션이 많은가 | 생성 과정을 명시화 | Builder/Factory |
| 이벤트 수신자가 유동적인가 | 발행/구독 분리 | Observer |

### 파이썬 구현 앵커

```python
from dataclasses import dataclass
from typing import Protocol

class Sender(Protocol):
    def send(self, msg: str) -> None: ...

@dataclass
class SlackSender:
    webhook: str

    def send(self, msg: str) -> None:
        # requests.post(self.webhook, json={"text": msg})
        pass

class SenderAdapter:
    def __init__(self, sender: Sender) -> None:
        self.sender = sender

    def notify(self, message: str) -> None:
        self.sender.send(message)
```

### 유엠엘 유사 구조

```text
[UseCase] --> [Notifier]
[Notifier] --> <<interface>> [Sender]
[SlackSender] --implements--> [Sender]
[SenderAdapter] --wraps--> [Sender]
```

### 변경 전후 비교

- 변경 전: 라우트/서비스 내부에서 외부 SDK를 직접 호출해 테스트와 교체 비용이 큽니다.
- 변경 후: 인터페이스 경계를 두고 패턴을 적용해 변경이 한 계층에서 끝납니다.

### 솔리드 점검표

| 원칙 | 점검 질문 |
| --- | --- |
| SRP | 클래스가 생성/정책/전송을 동시에 담당하지 않는가 |
| OCP | 새 요구를 기존 코드 수정 없이 추가할 수 있는가 |
| LSP | 대체 구현이 같은 계약을 유지하는가 |
| ISP | 과도하게 큰 인터페이스를 강요하지 않는가 |
| DIP | 상위 계층이 구체 구현 대신 추상에 의존하는가 |

이 점검표를 PR 템플릿에 넣으면 패턴 적용 품질이 팀 단위로 안정됩니다.

## 추가 검증 메모: 리팩터링 품질을 수치로 확인하기

패턴 리팩터링은 체감만으로 평가하면 흔들리기 쉽습니다. 아래 지표를 배포 전후로 비교하면 패턴 도입 효과를 더 객관적으로 확인할 수 있습니다.

- 변경 파일 수: 신규 요구 1건당 수정 파일 수가 줄어드는지 확인합니다.
- 테스트 시간: 단위 테스트 비중이 늘어 통합 테스트 의존이 줄어드는지 봅니다.
- 장애 복구 시간: 로그만으로 실패 계층을 특정하는 시간이 단축되는지 측정합니다.

```text
평가 주기: 2주
지표 1: 평균 PR 수정 파일 수
지표 2: 테스트 실패 원인 분류 가능 비율
지표 3: 회귀 버그 재발률
```

이 지표가 개선되지 않는다면 패턴 자체가 아니라 경계 설정 또는 인터페이스 설계가 잘못되었을 가능성이 큽니다. 이 경우 패턴을 더 추가하기보다 책임 분리 기준을 먼저 재정의하는 편이 안전합니다.

## 처음 질문으로 돌아가기

- **Behavioral 패턴은 어떤 행위 문제를 다룰까요?**
  - 본문의 기준은 Behavioral 패턴를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Strategy, Observer, Command는 각각 흐름을 어떻게 분리할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **State와 Iterator는 무엇을 객체로 끌어올릴까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- **Behavioral 패턴 (현재 글)**
- Strategy 패턴 (예정)
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Command Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/command)
- [State Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/state)

### 실무 확장 읽을거리

- [The Python Language Reference — Data model (`__iter__`)](https://docs.python.org/3/reference/datamodel.html)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Behavioral, Strategy, Observer, Command
