---
series: design-patterns-101
episode: 9
title: "바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Antipatterns
  - Simplicity
  - YAGNI
  - AI코딩
seo_description: AI가 과잉 설계한 코드를 단순하게 되돌리고, 바이브코딩에서 패턴을 언제 적용하고 언제 참아야 하는지 배우는 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 아홉 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 "확장 가능하게 만들어줘"라고 하면 모든 함수에 Protocol이 생기고, 객체마다 Factory가 생기고, 설정값 하나에도 클래스가 생깁니다. 바이브코딩의 속도가 오히려 복잡한 코드를 더 빠르게 쌓는 방향으로 작용할 수 있습니다. 패턴을 아는 것과 패턴을 참는 것은 다른 능력입니다.

---

AI에게 "결제 수단을 추가할 수 있도록 확장 가능하게 해줘"라고 하면 Protocol 3개, 클래스 5개, Factory 함수, Registry dict가 생깁니다. 결제 수단은 아직 하나인데도요. 패턴을 배운 직후 열병처럼, AI도 "확장성"이라는 단어를 보면 패턴을 쏟아냅니다.

바이브코딩에서는 이 문제가 더 빠르게 쌓입니다. 기능을 하나 추가할 때마다 AI가 "더 확장 가능한 구조"를 제안하고, 거절할 이유를 모르면 코드가 점점 복잡해집니다. 패턴을 참는 능력이 필요합니다.

> "패턴은 자신이 추가하는 복잡도보다 더 큰 고통을 덜어 줄 때만 가치 있습니다. AI가 '더 확장 가능하게'라는 이유로 패턴을 제안할 때, '지금 이 변화가 실제로 반복되고 있는가'를 먼저 물어보세요."

## 이 글에서 다룰 문제

- AI가 과잉 설계한 코드를 발견하는 신호는 무엇일까요?
- "나중에 필요할 것 같아서" 미리 넣은 추상화를 어떻게 되돌릴까요?
- 바이브코딩에서 AI의 과잉 설계 제안을 어떻게 막을 수 있을까요?
- Rule of Three가 바이브코딩에서 어떻게 적용될까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## 과잉 설계의 신호

AI가 만든 코드에서 이런 신호가 보이면 과잉 설계를 의심하세요.

**구현체가 하나뿐인 Protocol이 있습니다.** Protocol을 정의했는데 그걸 구현하는 클래스가 딱 하나입니다.

**Factory가 분기 하나만 처리합니다.** Factory 함수를 열어 보면 `if` 하나에 `return SomeClass()`가 전부입니다.

**클래스 이름에 패턴명이 두 개 이상 들어갑니다.** `StrategyFactoryAdapter`, `ObserverDecoratorProxy` 같은 이름은 패턴을 전시하는 이름입니다.

**Decorator를 세 겹 이상 쌓아야 동작합니다.** 스택 트레이스가 Decorator 체인으로 가득 차면 원인을 찾는 데 시간이 배로 걸립니다.

**DI 컨테이너 설정이 실제 비즈니스 로직보다 깁니다.** 컨테이너 설정 파일이 수백 줄인데 실제 서비스 코드가 수십 줄이면 비용과 이득의 비율이 뒤집힌 겁니다.

## Rule of Three: 세 번째 케이스에서 추상화

AI에게 코드를 요청할 때 이 규칙을 기억하세요. **같은 모양의 변화가 세 번 반복되기 전에는 추상화를 요청하지 않습니다.**

```python
# 첫 번째: 그냥 직접 씁니다
def send_welcome_email(user: User) -> None:
    body = render_template("welcome.html", user=user)
    smtp_client.send(user.email, "환영합니다", body)

# 두 번째: 비슷하지만 아직 참습니다
def send_password_reset_email(user: User, token: str) -> None:
    body = render_template("reset.html", user=user, token=token)
    smtp_client.send(user.email, "비밀번호 재설정", body)

# 세 번째: 이제 추상화를 요청합니다
def send_invoice_email(user: User, invoice: Invoice) -> None:
    body = render_template("invoice.html", user=user, invoice=invoice)
    smtp_client.send(user.email, f"청구서 #{invoice.number}", body)
```

세 번째가 나왔을 때 AI에게 "이 세 함수의 공통 구조를 추출해줘"라고 요청하면, 실제 코드에서 나온 패턴이라 추상화의 모양이 현실적입니다.

## Before / After: 과잉 추상화를 단순화하기

**Before — 구현체 하나를 위한 Strategy:**

```python
from typing import Protocol

class NotificationSender(Protocol):
    def send(self, user_id: str, message: str) -> None: ...

class SlackNotificationSender:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send(self, user_id: str, message: str) -> None:
        requests.post(self.webhook_url, json={"text": f"<@{user_id}> {message}"})

class AlertService:
    def __init__(self, sender: NotificationSender) -> None:
        self.sender = sender

    def alert(self, user_id: str, event: str) -> None:
        self.sender.send(user_id, f"Alert: {event}")
```

파일 세 개, 클래스 세 개, Protocol 하나. `NotificationSender`를 구현하는 클래스는 하나뿐입니다.

**After — 함수 하나:**

```python
def send_slack_alert(webhook_url: str, user_id: str, event: str) -> None:
    requests.post(webhook_url, json={"text": f"<@{user_id}> Alert: {event}"})
```

이메일 알림이 정말 필요해지는 날이 오면, 그때 Protocol을 도입해도 됩니다.

## AI가 과잉 설계를 제안할 때 막는 방법

AI에게 요청할 때 "지금 당장 필요한 것만" 명시하면 과잉 설계를 줄일 수 있습니다.

**나쁜 요청 (과잉 설계 유발):**

```
"확장 가능하고 유연한 결제 처리 시스템을 만들어줘."
```

**좋은 요청 (현재 필요한 것만):**

```
"지금은 Stripe만 지원하면 돼. 나중에 다른 결제사가 추가될
가능성이 있으면 그때 리팩토링할 예정이야.
지금은 단순하고 읽기 쉬운 코드로 만들어줘.
추상화 계층을 불필요하게 추가하지 말아줘."
```

## 과잉 적용된 패턴을 되돌리는 방법

**Strategy를 함수로 되돌리기:**

```python
# Before: Protocol + 구현 클래스 1개
class PricingStrategy(Protocol):
    def calculate(self, base: int) -> int: ...

class StandardPricing:
    def calculate(self, base: int) -> int:
        return base

class OrderService:
    def __init__(self, pricing: PricingStrategy) -> None:
        self.pricing = pricing

    def total(self, items: list) -> int:
        base = sum(item.price for item in items)
        return self.pricing.calculate(base)

# After: 함수 하나
class OrderService:
    def total(self, items: list) -> int:
        return sum(item.price for item in items)
```

`StandardPricing.calculate`가 `base`를 그대로 반환하고 있었습니다. Protocol과 클래스를 모두 지우고 인라인합니다.

## YAGNI: 지금 필요하지 않은 패턴은 지금 만들지 않는다

바이브코딩에서 YAGNI(You Aren't Gonna Need It)는 특히 중요합니다. AI는 "혹시 나중에 필요할 수도 있는" 구조를 빠르게 만들어 줍니다. 하지만 그 "나중"은 대개 오지 않습니다.

패턴 도입을 결정할 때 AI에게도 이 질문을 하게 만드세요.

```
"이 패턴을 지금 도입할 필요가 있어?
지금 이 코드에서 변화가 실제로 반복되고 있어?
패턴 없이 이 변화를 수용하면 구체적으로 어떤 고통이 생겨?
나중에 도입해도 비용이 크게 늘어나지 않으면 일단 단순하게 가자."
```

## 패턴 남용 판단 기준

| 신호 | 판단 | 처리 방법 |
| --- | --- | --- |
| 구현체가 하나뿐인 Protocol | 과잉 추상화 | Protocol 제거, 함수로 단순화 |
| 분기 하나짜리 Factory | 불필요한 간접 호출 | Factory 제거, 직접 생성 |
| 패턴명 두 개 이상인 클래스명 | 책임 과다 또는 패턴 전시 | 책임 분리 또는 이름 변경 |
| 4단 이상 Decorator 체인 | 순서 추적 불가 | 명시적 함수로 대체 |
| DI 설정 > 비즈니스 코드 | 조립 비용 > 이득 | 수동 배선으로 단순화 |

## AI 활용 팁

**과잉 설계 감지 요청:**

```
"이 코드에서 불필요하게 복잡한 부분이 있어?
구현체가 하나뿐인 Protocol, 분기 하나짜리 Factory,
필요 없는 추상화 계층이 있으면 알려줘.
단순하게 되돌릴 수 있는 부분을 보여줘."
```

**리팩토링 방향 지정:**

```
"이 코드를 더 단순하게 만들어줘. 지금 필요하지 않은
추상화는 제거하고. Rule of Three 원칙을 적용해서,
세 번 반복되는 패턴만 추상화해줘."
```

## 운영 체크리스트

- [ ] 과잉 설계의 신호를 세 가지 이상 말할 수 있습니다.
- [ ] AI가 만든 코드에서 불필요한 추상화를 발견할 수 있습니다.
- [ ] 과잉 적용된 패턴을 단순한 코드로 되돌릴 수 있습니다.
- [ ] AI에게 과잉 설계를 막는 요청 방법을 알고 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 AI도 "확장 가능하게"라는 단어에 패턴을 남발합니다. 지금 필요한 것을 명시하세요. 둘째 Rule of Three: 세 번 반복되기 전에는 추상화하지 않습니다. 셋째 최고의 코드는 패턴이 많은 코드가 아니라 패턴이 필요한 곳에만 있는 코드입니다.

## 처음 질문으로 돌아가기

- **AI가 과잉 설계한 코드를 발견하는 신호는 무엇일까요?**
  - 구현체가 하나뿐인 Protocol, 분기 하나짜리 Factory, 이름에 패턴명이 두 개 이상 들어간 클래스, 4단 이상 Decorator 체인입니다.
- **"나중에 필요할 것 같아서" 미리 넣은 추상화를 어떻게 되돌릴까요?**
  - IDE에서 Protocol의 구현체 수를 확인하고, 하나뿐이면 제거합니다. Factory가 단순 생성이면 인라인합니다. 테스트가 통과하면 패턴이 동작에 기여하지 않았다는 증거입니다.
- **바이브코딩에서 AI의 과잉 설계 제안을 어떻게 막을 수 있을까요?**
  - 요청할 때 "지금 당장 필요한 것만"을 명시하고, "추상화 계층을 불필요하게 추가하지 말아줘"를 함께 적으세요.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- **바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [YAGNI (Martin Fowler)](https://martinfowler.com/bliki/Yagni.html)
- [Refactoring to Patterns (Joshua Kerievsky)](https://www.industriallogic.com/xp/refactoring/)
- [Rule of Three (C2 wiki)](https://wiki.c2.com/?RuleOfThree)

### 실무 확장 읽을거리

- [Worse Is Better (Richard Gabriel)](https://www.dreamsongs.com/RiseOfWorseIsBetter.html)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Antipatterns, Simplicity, YAGNI, AI코딩
