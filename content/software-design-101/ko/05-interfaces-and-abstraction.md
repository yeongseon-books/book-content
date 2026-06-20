---
series: software-design-101
episode: 5
title: "Software Design 101 (5/10): 인터페이스와 추상화"
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
  - SoftwareDesign
  - Interfaces
  - Abstraction
  - LSP
  - Polymorphism
seo_description: 인터페이스의 조건과 추상화 설계법을 학습하고 다형성으로 분기를 줄입니다. LSP, ISP 원칙으로 유연한 구조를 만드는 실무 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (5/10): 인터페이스와 추상화

알림 기능 하나를 만들 때 `notify("email", ...)`, `notify("sms", ...)`, `notify("push", ...)` 같은 분기가 계속 늘어나기 시작하면 인터페이스가 구현 세부를 바깥으로 흘리고 있다는 신호일 수 있습니다. 호출자가 원하는 일보다 구현 방식이 더 많이 드러날수록 구조는 빨리 뻣뻣해집니다.

이 글은 Software Design 101 시리즈의 5번째 글입니다.

여기서는 좋은 인터페이스가 무엇인지, 추상화 수준을 어떻게 맞춰야 하는지, 다형성이 분기를 어떻게 줄이는지, LSP와 ISP가 왜 인터페이스 품질을 판단하는 기준이 되는지 설명합니다. 구현 교체가 쉬운 구조가 어떻게 만들어지는지도 함께 보겠습니다.

![Software Design 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/05/05-01-concept-at-a-glance.ko.png)
*Software Design 101 5장 흐름 개요*

> 좋은 인터페이스는 호출자가 원하는 것을 말하게 하고, 어떻게 할지는 숨깁니다 — `notify('email', ...)` 같은 분기가 늘어나는 것은 인터페이스가 구현 세부를 바깥으로 흘리고 있다는 신호입니다.

## 이 글에서 다룰 문제

- 더 나은 인터페이스는 무엇으로 판단할 수 있을까요?
- 추상화 수준이 너무 낮거나 높으면 어떤 문제가 생길까요?
- 다형성은 분기문을 어떻게 줄여 줄까요?
- 이 설계 원칙을 무시하면 코드베이스가 어떻게 변질될까요?
- 팀 규모가 커질 때 이 원칙의 중요성은 어떻게 달라질까요?

인터페이스는 약속입니다. 약속이 작고 분명하면 구현과 호출자 양쪽 모두 움직일 여지가 생깁니다. 반대로 인터페이스에 구현 세부가 너무 많이 드러나면 호출자는 내부 사정을 함께 떠안게 됩니다.

실무에서 인터페이스 품질은 교체 비용으로 드러납니다. 같은 결제 게이트웨이인데 벤더만 바꾸려 했을 뿐인데 호출자 전부를 손봐야 한다면, 문제는 구현체보다 인터페이스 설계에 있을 가능성이 큽니다.

## 전체 그림

호출자는 하나의 모양만 알고, 여러 구현은 그 뒤에 놓입니다. 이 구조가 잘 작동하려면 인터페이스가 호출자의 관심사와 같은 높이에서 설계되어야 합니다.

```text
좋은 인터페이스 구조

호출자            인터페이스         구현들
                 ┌──────────┐     ┌─────────────┐
notify(user, msg)│  Notifier  │────▶│ EmailNotifier│
                 │  .send()  │     ├─────────────┤
                 └──────────┘     │  SmsNotifier │
                                  ├─────────────┤
                                  │ PushNotifier │
                                  └─────────────┘
호출자는 "어떻게 보낼지" 몰라도 됨
```

## 기본 용어

- <strong>인터페이스</strong>: 호출 가능한 약속의 모양입니다.
- <strong>추상화 수준</strong>: 인터페이스가 호출자의 어휘와 얼마나 잘 맞는지를 뜻합니다.
- <strong>다형성</strong>: 같은 호출이 여러 구현으로 분기될 수 있는 성질입니다.
- <strong>LSP</strong>: 하위 타입은 상위 타입이 쓰이는 자리에 문제없이 들어갈 수 있어야 한다는 원칙입니다.
- <strong>누수된 추상화</strong>: 내부 구현 세부가 인터페이스 밖으로 새는 상태입니다.

## 변경 전과 변경 후

**변경 전 — 구현 방식이 인터페이스에 드러남**

```python
def notify(kind: str, user: str, msg: str) -> None:
    if kind == "email":
        smtp = smtplib.SMTP("smtp.example.com")
        smtp.sendmail(user, "noreply@example.com", msg)
    elif kind == "sms":
        twilio = TwilioClient(ACCOUNT_SID, AUTH_TOKEN)
        twilio.messages.create(to=user, from_=FROM_NUM, body=msg)
    elif kind == "push":
        fcm = FCMClient(API_KEY)
        fcm.send(registration_id=user, message=msg)
    # 새 채널 추가 = 이 함수 수정
```

**변경 후 — 다형성으로 분기 제거**

```python
from typing import Protocol

class Notifier(Protocol):
    def send(self, user: str, msg: str) -> None: ...

class EmailNotifier:
    def send(self, user: str, msg: str) -> None:
        smtp = smtplib.SMTP("smtp.example.com")
        smtp.sendmail(user, "noreply@example.com", msg)

class SmsNotifier:
    def send(self, user: str, msg: str) -> None:
        twilio = TwilioClient(ACCOUNT_SID, AUTH_TOKEN)
        twilio.messages.create(to=user, from_=FROM_NUM, body=msg)

def notify(notifier: Notifier, user: str, msg: str) -> None:
    notifier.send(user, msg)
    # 새 채널을 추가해도 이 함수는 건드리지 않음
```

두 번째 구조에서는 새 채널을 추가할 때 기존 함수 내부 분기를 늘릴 필요가 없습니다. 호출자는 "보낸다"는 의도만 알고 있으면 됩니다.

## 좋은 인터페이스를 만드는 다섯 단계

### 1단계 — 호출자의 언어로 이름 짓기

```python
# 1_naming.py
# Bad: process_data()
# Good: charge_user()

# Bad: execute_notification_procedure()
# Good: notify()

# Bad: perform_persistence_operation()
# Good: save()
```

메서드 이름은 구현 절차보다 의도를 담아야 합니다. `process_data`보다 `charge_user`가 훨씬 많은 문맥을 전달합니다.

### 2단계 — 추상화 높이를 맞춘다

```python
# 2_level.py
# Bad: 너무 낮은 추상화 (구현 세부가 보임)
def send_bytes_over_tcp(host: str, port: int, payload: bytes) -> None: ...

# Good: 호출자 수준의 추상화
def notify(user: str, message: str) -> None: ...
```

호출자가 네트워크 소켓 세부를 신경 쓰지 않아도 된다면 인터페이스에 올릴 이유도 없습니다. 추상화는 필요한 디테일만 남기고 나머지는 숨기는 일입니다.

### 3단계 — 인자는 적게, 의도는 분명하게 둔다

```python
# 3_params.py
# 나쁜 예: 인자가 많고 의도가 불분명
def charge(u, a, c, r, m, x, y): ...

# Good: 키워드 인자로 의도를 명확히
def charge(user: User, amount: int, *, reason: str) -> Receipt: ...
```

위치 인자가 계속 늘어나면 호출 의도가 흐려집니다. 인자 수가 많아질수록 인터페이스가 너무 많은 일을 요구하는지 의심해 볼 필요가 있습니다.

### 4단계 — LSP를 확인한다

```python
# 4_lsp.py
# LSP 위반 예시
class Bird:
    def fly(self) -> None: ...

class Penguin(Bird):
    def fly(self) -> None:
        raise NotImplementedError("펭귄은 날 수 없음")
    # 호출부가 깨집니다 — Bird 자체를 재설계해야 합니다.

# LSP를 지키는 설계
class Bird:
    def move(self) -> None: ...  # 날거나 걸을 수 있음

class FlyingBird(Bird):
    def fly(self) -> None: ...

class Penguin(Bird):
    def move(self) -> None:
        self._walk()  # 걸어서 이동
```

하위 타입이 상위 타입의 약속을 깨면, 문제는 펭귄 하나가 아니라 상위 인터페이스 설계일 가능성이 큽니다. 타입 계층을 다시 생각해야 합니다.

### 5단계 — 큰 인터페이스 하나보다 작은 인터페이스 여러 개를 둔다

```python
# 5_isp.py
# 나쁜 예: 모든 것이 하나의 인터페이스에
class DataStore(Protocol):
    def read(self, key: str) -> bytes: ...
    def write(self, key: str, data: bytes) -> None: ...
    def delete(self, key: str) -> None: ...
    def list_keys(self) -> list[str]: ...
    def snapshot(self) -> bytes: ...  # 읽기 전용 사용자도 구현해야 함

# 좋은 예: 역할별로 나눔
class Readable(Protocol):
    def read(self, key: str) -> bytes: ...

class Writable(Protocol):
    def write(self, key: str, data: bytes) -> None: ...

class Snapshottable(Protocol):
    def snapshot(self) -> bytes: ...
```

읽기만 필요한 호출자에게 쓰기 메서드까지 강요하면 불필요한 결합이 생깁니다. 인터페이스도 책임별로 나뉘는 편이 좋습니다.

## 추상화 수준 비교

| 수준 | 예시 | 호출자 부담 | 적합한 상황 |
| --- | --- | --- | --- |
| 너무 낮음 | `send_bytes_over_tcp(host, port, payload)` | 네트워크 세부를 알아야 함 | 저수준 라이브러리 내부 |
| 적당함 | `notify(user, message)` | 의도만 전달 | 일반 비즈니스 코드 |
| 너무 높음 | `handle_business_event(event)` | 어떤 이벤트인지 명확하지 않음 | 과도하게 일반화된 경우 |

## 빠르게 검증해 보기

인터페이스 품질을 빠르게 보려면 메서드 이름과 인자 목록만 따로 빼서 읽어 보세요. 구현 설명 없이도 호출 의도가 보이면 추상화 높이가 맞을 가능성이 큽니다.

```python
class Notifier:
    def send(self, user, msg): ...
```

**Expected output:** 이름만 봐도 호출자가 무엇을 원하는지 읽히고, 구현 교체가 필요할 때도 호출 코드가 크게 바뀌지 않아야 합니다.

그다음 하위 구현 하나를 골라 상위 계약을 깨지 않는지 확인합니다. `NotImplementedError`를 던지기 시작하면 인터페이스 설계를 다시 봐야 합니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 메서드 이름이 구현 용어로 가득하다 | 호출자 언어가 아니라 구현자 언어인지 봅니다 |
| 인자가 계속 늘어난다 | 인터페이스가 여러 책임을 품고 있는지 확인합니다 |
| 하위 타입이 예외로 계약을 회피한다 | 상위 타입의 약속 자체를 다시 설계합니다 |

좋은 인터페이스는 구현을 감추는 것보다, 호출자의 의도를 짧고 안정적으로 표현하는 데 더 가깝습니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 올바른 접근 |
| --- | --- | --- |
| 구현 용어로 인터페이스 이름 지음 | `flush_buffer()`는 내부 구현 세부를 드러냄 | 호출자의 언어로 `save()`, `persist()` |
| 인자를 계속 추가 | `charge(u, a, c, r, m)` 은 의도 파악 불가 | 파라미터 객체나 키워드 전용 인자 사용 |
| 큰 인터페이스 하나 | 읽기만 필요한 구현체도 쓰기를 구현해야 함 | ISP: 역할별로 작은 인터페이스로 분리 |
| LSP 위반을 하위 클래스 탓으로 봄 | 실제 문제는 상위 인터페이스 설계에 있음 | 상속 계층을 재설계하거나 조합으로 변경 |
| 추상화 없이 if-else 분기 추가 | 새 채널마다 기존 함수를 수정해야 함 | 다형성으로 분기를 객체로 대체 |

## 이 코드에서 먼저 볼 점

- 이름이 구현이 아니라 호출자의 어휘에 맞춰져 있습니다.
- 인자 목록이 짧고 의미가 선명합니다.
- 구현을 바꿔도 호출자 쪽 파급이 작습니다.

## 어디서 많이 헷갈릴까

인터페이스를 추가하는 것과 추상화를 잘하는 것은 다릅니다. 메서드 이름이 `flush_buffer`, `get_redis_client`처럼 구현 용어를 그대로 담고 있다면, 타입만 인터페이스일 뿐 추상화 높이는 거의 그대로일 수 있습니다.

또 하나 흔한 실수는 LSP 문제를 하위 클래스 탓으로만 보는 것입니다. 펭귄이 날 수 없는 것이 잘못이 아니라, `Bird`라는 상위 타입이 "날 수 있음"을 기본 약속으로 삼은 설계가 잘못됐을 가능성이 큽니다.

## 실무에서는 이렇게 본다

결제 게이트웨이, 저장소, 알림 채널처럼 구현 교체가 자주 일어나는 곳에서 인터페이스 품질은 바로 비용으로 이어집니다. 잘 설계된 인터페이스는 벤더 교체나 테스트 대체 구현이 들어와도 호출자가 거의 변하지 않게 합니다.

코드 리뷰에서는 이런 질문을 던지면 좋습니다. "이 이름이 호출자의 의도를 말하는가?", "이 인자 중 구현 세부가 섞여 있지 않은가?", "하위 타입이 상위 계약을 정말 지키는가?", "읽기 전용 호출자에게 쓰기까지 강요하고 있지 않은가?"

```python
# 실무 패턴: 다형성으로 분기 제거
class PaymentGateway(Protocol):
    def charge(self, amount: int, currency: str) -> Receipt: ...

class StripeGateway:
    def charge(self, amount: int, currency: str) -> Receipt:
        result = stripe.Charge.create(amount=amount, currency=currency)
        return Receipt(id=result.id, amount=amount)

class TossGateway:
    def charge(self, amount: int, currency: str) -> Receipt:
        result = toss_api.payment.confirm(amount=amount)
        return Receipt(id=result.payment_key, amount=amount)

# 새 게이트웨이 추가 = 새 클래스만 작성, 기존 코드 수정 없음
def process_payment(gateway: PaymentGateway, amount: int) -> Receipt:
    return gateway.charge(amount, "KRW")
```

## 운영 체크리스트

- [ ] 메서드 이름이 호출자의 언어로 읽히는가?
- [ ] 인자 수가 적고 의도가 분명한가?
- [ ] 하위 타입이 상위 타입의 계약을 깨지 않는가?
- [ ] 인터페이스가 한 가지 책임에 집중하는가?
- [ ] 구현 세부가 인터페이스 밖으로 새지 않는가?

## 연습 문제

1. 현재 코드의 인터페이스 하나를 골라 인자 수를 줄여 보세요.
2. 큰 인터페이스 하나를 두 개의 좁은 인터페이스로 나눠 보세요.
3. 코드베이스에서 LSP 위반 사례 하나를 찾고 무엇을 바꿔야 할지 적어 보세요.

## 인터페이스 설계 체크리스트 적용 예시

알림 시스템의 인터페이스를 처음 설계할 때 흔히 저지르는 실수와 올바른 접근을 비교합니다.

```python
# ── 나쁜 인터페이스 예시 ──────────────────────────

class NotificationService:
    # 문제 1: 구현 용어가 인터페이스에 드러남
    def send_email_via_smtp(self, to: str, body: str) -> None: ...
    def send_sms_via_twilio(self, phone: str, text: str) -> None: ...
    def push_to_fcm(self, token: str, payload: dict) -> None: ...
    # 문제 2: 채널이 늘어나면 인터페이스도 늘어남
    # 문제 3: 호출자가 채널 선택 책임을 가져야 함


# ── 좋은 인터페이스 예시 ──────────────────────────

class Notifier(Protocol):
    """호출자의 언어로 이름 짓기, 추상화 높이 맞추기"""
    def send(self, user_id: str, message: str) -> None: ...

# 구현들은 Notifier를 따름
class EmailNotifier:
    def send(self, user_id: str, message: str) -> None:
        email = user_repo.get_email(user_id)
        smtp.sendmail(to=email, body=message)

class SmsNotifier:
    def send(self, user_id: str, message: str) -> None:
        phone = user_repo.get_phone(user_id)
        twilio.messages.create(to=phone, body=message)

class CompositeNotifier:
    """여러 채널에 동시 전송 — 호출자는 몰라도 됨"""
    def __init__(self, *notifiers: Notifier) -> None:
        self._notifiers = notifiers

    def send(self, user_id: str, message: str) -> None:
        for notifier in self._notifiers:
            notifier.send(user_id, message)

# 사용 코드 — 구현을 모름
def notify_order_complete(notifier: Notifier, user_id: str) -> None:
    notifier.send(user_id, "주문이 완료되었습니다")
```

## ISP 적용: 큰 인터페이스를 역할별로 분리

저장소 인터페이스를 ISP 기준으로 나누면 각 호출자가 실제로 필요한 것만 의존할 수 있습니다.

```python
# ISP 위반: 모든 것이 하나의 인터페이스에
class OrderRepo(Protocol):
    def get(self, order_id: str) -> Order: ...
    def save(self, order: Order) -> None: ...
    def delete(self, order_id: str) -> None: ...
    def list_by_user(self, user_id: str) -> list[Order]: ...
    def bulk_export(self, filters: dict) -> list[Order]: ...
    def archive(self, order_id: str) -> None: ...

# ISP 적용: 역할별 분리
class OrderReader(Protocol):
    def get(self, order_id: str) -> Order: ...
    def list_by_user(self, user_id: str) -> list[Order]: ...

class OrderWriter(Protocol):
    def save(self, order: Order) -> None: ...

class OrderArchiver(Protocol):
    def archive(self, order_id: str) -> None: ...
    def bulk_export(self, filters: dict) -> list[Order]: ...

# 각 유스케이스가 필요한 것만 요청
def view_orders(reader: OrderReader, user_id: str) -> list[Order]:
    return reader.list_by_user(user_id)

def place_order(writer: OrderWriter, order: Order) -> None:
    writer.save(order)
# 읽기 전용 기능이 삭제·아카이브 메서드를 구현할 필요 없음
```

## 현업 적용 관점에서 다시 정리

인터페이스는 "무엇을 할 수 있는가"를 드러내고 "어떻게 하는가"를 숨겨야 합니다. 추상화 레벨이 흔들리면 호출자가 구현 세부를 알게 되고 결합도가 급격히 커집니다.

## 정리

좋은 인터페이스는 호출자가 원하는 것을 말하게 하고, 어떻게 할지는 숨깁니다 — `notify('email', ...)` 같은 분기가 늘어나는 것은 인터페이스가 구현 세부를 바깥으로 흘리고 있다는 신호입니다. 이 글에서는 전체 그림부터 현업 적용 관점에서 다시 정리까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **더 나은 인터페이스는 무엇으로 판단할 수 있을까요?**
  - 구현 설명 없이 이름만 봐도 호출 의도가 읽히는가, 구현이 바뀌어도 호출 코드가 변하지 않는가로 판단합니다. 호출자는 하나의 모양만 알고, 여러 구현은 그 뒤에 놓이면 됩니다.
- **추상화 수준이 너무 낮거나 높으면 어떤 문제가 생길까요?**
  - 너무 낮으면 호출자가 구현 세부를 알아야 합니다. 너무 높으면 어떤 기능인지 파악하기 어렵습니다. 호출자의 어휘와 같은 높이에서 설계해야 합니다.
- **다형성은 분기문을 어떻게 줄여 줄까요?**
  - `if kind == "email"` 같은 분기 대신 `Notifier.send()` 인터페이스를 두면, 새 채널 추가가 기존 함수 수정이 아닌 새 클래스 추가로 끝납니다.
