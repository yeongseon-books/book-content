---
series: testing-101
episode: 5
title: "바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블"
status: content-ready
targets:
  wordpress: true
  tistory: false
  medium: false
  hashnode: false
  mkdocs: false
  ebook: false
language: ko
tags:
  - 바이브코딩
  - Testing
  - Test Double
  - Fake
  - Stub
  - Spy
seo_description: AI가 만든 코드에서 외부 의존(메일, 결제 API, DB)을 대역으로 교체해 빠르고 안정적인 테스트를 만드는 방법. Dummy, Stub, Spy, Mock, Fake 한 번에 정리.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블

이 글은 **바이브코딩을 위한 테스팅 기초** 시리즈의 다섯 번째 글입니다. AI가 만든 코드에서 메일 전송, 결제 API, 데이터베이스 같은 외부 의존을 안전하게 테스트하는 방법을 설명합니다.

---

AI에게 "메일을 보내고 DB에 저장하는 함수를 만들어 줘"라고 하면 실제 SMTP와 실제 DB에 연결하는 코드를 만들어 줍니다. 그 코드를 테스트하려면 실제 메일이 발송되고 실제 DB가 변경됩니다. 느리고, 비용이 들고, 실패 원인이 코드가 아닌 외부 환경이 될 수 있습니다.

테스트 더블은 이런 외부 의존을 통제 가능한 대역으로 바꿉니다. AI 코드를 테스트할 때 실제 의존을 호출하지 않고도 동작을 검증할 수 있습니다.

> 테스트 더블은 외부 의존을 제어함으로써 AI가 만든 코드를 빠르고 반복 가능하게 검증합니다.

## 이 글에서 다룰 문제

- 테스트 더블은 무엇을 대체하는 장치일까요?
- Dummy, Stub, Spy, Mock, Fake는 어떻게 다를까요?
- 바이브코딩에서 어떤 상황에서 어떤 종류를 골라야 할까요?
- AI가 만든 코드에서 Mock을 남용하면 어떤 문제가 생길까요?
- 테스트 더블 없이 배포하면 어떤 일이 생길까요?

AI는 외부 서비스를 직접 호출하는 코드를 자연스럽게 만듭니다. 테스트 더블 없이 이런 코드를 테스트하면 결제 API가 매번 호출되거나, 테스트 메일이 실제로 발송되는 문제가 생깁니다. 바이브코딩 팀에서 테스트 더블은 필수입니다.

## 한눈에 보는 구조

테스트 대상 시스템은 실제 의존 대신 테스트 더블을 바라봅니다. 여기서 핵심은 대체 자체보다 대체 목적입니다.

- **Dummy**: 자리를 채우기만 하는 객체입니다.
- **Stub**: 미리 정한 값을 돌려주는 대역입니다.
- **Spy**: 값을 돌려주면서 호출 기록도 남기는 대역입니다.
- **Mock**: 미리 기대를 심어 두고 그 호출이 일어났는지 검증하는 대역입니다.
- **Fake**: 실제와 비슷하게 동작하지만 단순하고 빠른 구현입니다.

## 테스트 더블 종류 비교표

| 종류 | 목적 | 반환값 | 호출 기록 | 사용 예시 |
|---|---|---|---|---|
| Dummy | 자리 채우기 | 없음 | 없음 | 사용하지 않는 인자 |
| Stub | 결과 제어 | 고정값 | 없음 | 시간, 난수, 외부 API 응답 |
| Spy | 결과 + 추적 | 고정값 | 기록 | 메일 전송 기록, 로그 호출 추적 |
| Mock | 상호작용 검증 | 설정 가능 | 검증 | 결제 API 호출 여부/인자 확인 |
| Fake | 실제 동작 흉내 | 동적 | 선택 | 인메모리 DB, 로컬 파일 시스템 |

## 바꾸기 전과 후

**바꾸기 전 — AI가 만든 코드, 실제 SMTP 직접 호출**

```python
def test_send_welcome_email():
    user = create_user("a@b.com")
    send_welcome_email(user)   # 실제 SMTP 호출 → 실제 메일 발송
```

**바꾼 뒤 — FakeMailer로 교체**

```python
class FakeMailer:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))

def test_send_welcome_email():
    mailer = FakeMailer()
    send_welcome_email(User("a@b.com"), mailer=mailer)
    assert mailer.sent == [("a@b.com", "Welcome!")]
```

네트워크와 무관하게 메일 전송 로직을 검증할 수 있습니다.

## 다섯 단계로 대역 종류 익히기

### 1단계 — Dummy (자리만 채움)

```python
def test_dummy_passthrough():
    # logger는 이 테스트에서 사용하지 않음
    user = User(email="a@b.com", logger=None)
    assert user.email == "a@b.com"
```

### 2단계 — Stub (AI가 만든 시간 의존 코드 테스트)

```python
class StubClock:
    def now(self): return "2026-05-04"

def test_uses_stub_clock():
    assert greet(StubClock()) == "Hello, today is 2026-05-04"
```

### 3단계 — Spy (메일 발송 기록 확인)

```python
class SpyMailer:
    def __init__(self): self.calls = []
    def send(self, to, body): self.calls.append((to, body))

def test_spy_records_calls():
    m = SpyMailer()
    send_welcome("a@b.com", m)
    assert len(m.calls) == 1
    assert m.calls[0][0] == "a@b.com"
```

### 4단계 — Mock (결제 API 호출 여부 검증)

```python
from unittest.mock import MagicMock

def test_mock_payment_called():
    gateway = MagicMock()
    gateway.charge.return_value = {"status": "ok", "tx_id": "abc"}
    result = process_payment(amount=100, gateway=gateway)
    gateway.charge.assert_called_once_with(amount=100, currency="USD")
    assert result["tx_id"] == "abc"
```

### 5단계 — Fake (인메모리 저장소로 DB 대체)

```python
class InMemoryUserRepo:
    def __init__(self): self._db = {}
    def add(self, u): self._db[u.id] = u
    def find(self, id): return self._db.get(id)
```

## 바이브코딩에서 자주 만나는 외부 의존 대역 처리

AI가 만든 코드에서 자주 등장하는 외부 의존과 대역 처리 패턴입니다.

```python
# 패턴 1: 결제 API — Mock으로 호출 검증
def test_payment_charged_with_correct_amount():
    gateway = MagicMock()
    gateway.charge.return_value = {"status": "ok"}
    order_service.checkout(order, gateway=gateway)
    gateway.charge.assert_called_once_with(amount=order.total, currency="KRW")

# 패턴 2: 이메일 서비스 — Spy로 발송 내용 검증
def test_welcome_email_sent_after_signup():
    mailer = SpyMailer()
    register_user("alice@example.com", mailer=mailer)
    assert len(mailer.sent_messages) == 1
    assert "Welcome" in mailer.sent_messages[0]["subject"]

# 패턴 3: 외부 날씨 API — Stub으로 응답 고정
def test_weather_greeting_sunny_day():
    weather_stub = MagicMock()
    weather_stub.get_weather.return_value = {"condition": "sunny"}
    greeting = make_greeting(weather_stub)
    assert "오늘 날씨가 좋군요" in greeting
```

## 의사결정 흐름

```text
외부 의존 발견
    ↓
의존이 사용되는가?
    → NO → Dummy (null, 빈 객체)
    ↓ YES
고정된 결과만 필요한가?
    → YES → Stub (canned return)
    ↓ NO
호출 자체가 핵심 검증 대상인가?
    → YES → Mock (assert_called_*)
    ↓ NO
호출 기록 + 결과 둘 다 확인하는가?
    → YES → Spy (기록 + 반환)
    ↓ NO
복잡한 내부 상태와 로직이 필요한가?
    → YES → Fake (in-memory impl)
```

## 자주 하는 실수

가장 흔한 실수는 모든 곳에 Mock부터 꺼내는 일입니다. 바이브코딩에서는 AI가 생성한 코드에 Mock을 남발하다가 구현 세부사항에 테스트가 과하게 묶여 AI가 리팩토링할 때마다 테스트가 깨지는 문제가 생깁니다.

또 다른 문제는 Fake가 실제 계약과 너무 멀어지는 경우입니다. AI에게 Fake를 만들어 달라고 요청할 때 실제 인터페이스와 같은 메서드명과 입력/출력 형식을 지정해야 합니다.

## AI 팁: 테스트 더블 프롬프트

```text
프롬프트 예시:
"send_welcome_email(user, mailer) 함수의 테스트를 작성해 줘.
실제 SMTP 대신 FakeMailer를 만들어서 사용해 줘.
mailer.send가 올바른 수신자와 제목으로 호출됐는지 검증해 줘."

확인 포인트:
1. Fake가 실제 mailer와 같은 메서드명과 인자를 사용하는지
2. 단언문이 호출 여부와 결과 모두를 확인하는지
3. 실제 외부 서비스를 호출하지 않는지
```

## 운영 체크리스트

- [ ] 다섯 종류를 각 한 줄로 구분해 설명할 수 있습니다.
- [ ] AI가 만든 외부 호출 코드에 Stub 또는 Fake를 적용했습니다.
- [ ] Mock은 상호작용 검증이 필요한 곳에만 사용했습니다.
- [ ] Fake의 인터페이스가 실제 구현과 일치하는지 확인했습니다.

## 처음 질문으로 돌아가기

- **테스트 더블은 무엇을 대체하는 장치일까요?**
  AI 코드가 호출하는 외부 의존(메일, 결제 API, DB)을 통제 가능한 대역으로 교체해 빠르고 결정적인 테스트를 만드는 장치입니다.

- **Dummy, Stub, Spy, Mock, Fake는 어떻게 다를까요?**
  목적이 다릅니다. Stub은 값을 돌려주고, Mock은 호출을 검증하고, Fake는 실제와 비슷하게 동작합니다.

- **AI가 만든 코드에서 Mock을 남용하면 어떤 문제가 생길까요?**
  AI가 코드를 리팩토링할 때마다 테스트가 깨지고, Mock 설정이 실제 코드보다 길어져 유지비가 증가합니다.

## 정리

테스트 더블은 AI 코드의 외부 의존을 안전하게 다루는 핵심 도구입니다. 대역을 목적에 맞게 고르면 빠르고 안정적인 테스트를 유지할 수 있습니다. 다음 글에서는 가장 자주 혼동하는 Mock과 Stub의 차이를 더 깊게 보겠습니다.

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [Martin Fowler — Test Double](https://martinfowler.com/bliki/TestDouble.html)
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 테스팅 기초 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트](./02-unit-test.md)
- [바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트](./03-integration-test.md)
- [바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트](./04-e2e-test.md)
- **바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블 (현재 글)**
- [바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [바이브코딩을 위한 테스팅 기초 (8/10): 회귀 테스트](./08-regression-test.md)
- [바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [바이브코딩을 위한 테스팅 기초 (10/10): 테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

Tags: 바이브코딩, Testing, Test Double, Fake, Stub, Spy
