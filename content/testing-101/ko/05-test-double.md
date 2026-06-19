---
series: testing-101
episode: 5
title: "Testing 101 (5/10): 테스트 더블"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Testing
  - Test Double
  - Fake
  - Stub
  - Spy
seo_description: Stub, Fake, Spy, Mock, Dummy를 한 번에 정리하고 언제 무엇을 쓸지 결정하는 가이드.
last_reviewed: '2026-05-12'
---

# Testing 101 (5/10): 테스트 더블

단위 테스트를 쓰다 보면 곧 외부 의존과 마주칩니다. 메일 전송, 결제 API, 현재 시간, 데이터베이스처럼 실제로 호출하면 느리거나 비싸거나 불안정한 대상들입니다. 이런 의존을 매번 진짜로 호출하면 테스트가 느려지고, 실패 원인도 코드가 아니라 외부 환경으로 번집니다.

그래서 테스트에서는 실제 의존 대신 대역을 씁니다. 다만 대역도 하나로 뭉뚱그리면 금방 헷갈립니다. 반환값만 흉내 내는 경우와 호출 자체를 기록하는 경우는 목적이 다르기 때문입니다.

이 글은 Testing 101 시리즈의 다섯 번째 글입니다. 여기서는 테스트 더블의 다섯 종류를 구분하고, 언제 무엇을 써야 하는지, 그리고 왜 과한 목 사용이 문제를 만드는지 정리하겠습니다.

![Testing 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/05/05-01-diagram.ko.png)
*Testing 101 5장 흐름 개요*
> 테스트 더블은 외부 의존을 제어함으로써 빠르고 반복 가능한 테스트를 만듭니다.

## 이 글에서 다룰 문제

- 테스트 더블은 무엇을 대체하는 장치일까요?
- Dummy, Stub, Spy, Mock, Fake는 어떻게 다를까요?
- 어떤 상황에서 어떤 종류를 골라야 할까요?
- 과한 Mock 사용이 보내는 설계 신호는 무엇일까요?
- Fake를 만들 때 지켜야 할 계약 조건은 무엇일까요?

테스트는 빠르고 결정적이어야 합니다. 실제 결제 API나 SMTP 서버를 부르면 속도도 느려지고 실패 원인도 외부로 번집니다. 테스트 더블은 이런 의존을 통제 가능한 대역으로 바꿔 테스트를 짧고 안정적으로 만듭니다.

문제는 대역을 쓰는 순간 거짓 확신도 함께 들어올 수 있다는 사실입니다. 실제 계약과 너무 다른 Fake를 만들거나, 호출 횟수만 지나치게 검증하면 테스트는 초록색인데 설계는 오히려 경직될 수 있습니다.

## 테스트 더블 종류 비교표

| 종류 | 목적 | 반환값 | 호출 기록 | 구현 복잡도 | 사용 예시 |
|---|---|---|---|---|---|
| Dummy | 자리 채우기 | 없음 | 없음 | 매우 낮음 | 사용하지 않는 인자 |
| Stub | 결과 제어 | 고정값 | 없음 | 낮음 | 시간, 난수, 외부 API 응답 |
| Spy | 결과 + 추적 | 고정값 | 기록 | 중간 | 메일 전송 기록, 로그 호출 추적 |
| Mock | 상호작용 검증 | 설정 가능 | 검증 | 중간 | 메서드 호출 여부/인자 확인 |
| Fake | 실제 동작 흉내 | 동적 | 선택 | 높음 | 인메모리 DB, 로컬 파일 시스템 |

각 종류는 테스트 목적에 따라 선택됩니다. Dummy는 컴파일을 통과하기 위해, Stub은 결과 검증을 위해, Spy는 호출 추적과 결과 검증을 함께 할 때, Mock은 상호작용 자체가 핵심일 때, Fake는 복잡한 로직을 가볍게 흉내 내야 할 때 씁니다.

## 실제 의존 직접 호출 vs 대역으로 교체

**실제 의존 직접 호출**

```python
def test_send_welcome_email():
    user = create_user("a@b.com")
    send_welcome_email(user)   # 실제 SMTP 호출 — 느리고 불안정
```

**대역으로 교체**

```python
class FakeMailer:
    def __init__(self):
        self.sent = []

    def send(self, to: str, body: str):
        self.sent.append((to, body))

def test_send_welcome_email():
    mailer = FakeMailer()
    send_welcome_email(User("a@b.com"), mailer=mailer)
    assert mailer.sent == [("a@b.com", "Welcome!")]
```

진짜 SMTP 대신 `FakeMailer`를 쓰면 네트워크와 무관하게 메일 전송 결과를 확인할 수 있습니다. 이처럼 테스트 더블은 외부 비용을 잘라 내고 검증 대상을 코드 안으로 끌고 옵니다.

## 각 더블 종류 상세 예시

### Dummy — 자리만 채우는 객체

```python
def test_dummy_passthrough():
    # logger는 이 테스트에서 실제로 사용되지 않음
    user = User(email="a@b.com", logger=None)
    assert user.email == "a@b.com"
```

### Stub — 미리 정한 값을 반환

```python
class StubClock:
    def now(self) -> str:
        return "2026-05-04"

def test_greeting_uses_stub_date():
    clock = StubClock()
    result = greet(clock)
    assert result == "Hello, today is 2026-05-04"
```

### Spy — 값을 돌려주면서 호출 기록도 남김

```python
class SpyMailer:
    def __init__(self):
        self.sent_messages = []

    def send(self, to: str, subject: str, body: str):
        self.sent_messages.append({"to": to, "subject": subject, "body": body})
        return True

def test_welcome_flow_spy():
    mailer = SpyMailer()
    user = register_user("test@example.com", mailer=mailer)

    # 결과 검증
    assert user.email == "test@example.com"

    # 호출 기록 검증
    assert len(mailer.sent_messages) == 1
    assert mailer.sent_messages[0]["to"] == "test@example.com"
    assert "Welcome" in mailer.sent_messages[0]["subject"]
```

### Mock — 기대한 호출이 일어났는지 검증

```python
from unittest.mock import MagicMock

def test_payment_calls_gateway_with_correct_args():
    gateway = MagicMock()
    gateway.charge.return_value = {"status": "success", "tx_id": "12345"}

    result = process_payment(amount=100, currency="USD", gateway=gateway)

    # 상호작용 검증
    gateway.charge.assert_called_once_with(amount=100, currency="USD")
    assert result["tx_id"] == "12345"
```

### Fake — 실제처럼 동작하는 가벼운 구현

```python
class InMemoryUserRepository:
    def __init__(self):
        self._users: dict[int, dict] = {}
        self._next_id = 1

    def add(self, email: str) -> int:
        user_id = self._next_id
        self._users[user_id] = {"id": user_id, "email": email}
        self._next_id += 1
        return user_id

    def find(self, user_id: int) -> dict | None:
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> dict | None:
        for user in self._users.values():
            if user["email"] == email:
                return user
        return None

def test_user_registration_with_fake_repo():
    repo = InMemoryUserRepository()

    user_id = register_user("alice@example.com", repo=repo)

    found = repo.find(user_id)
    assert found is not None
    assert found["email"] == "alice@example.com"

def test_duplicate_email_rejected():
    repo = InMemoryUserRepository()
    register_user("alice@example.com", repo=repo)

    import pytest
    with pytest.raises(ValueError, match="already exists"):
        register_user("alice@example.com", repo=repo)
```

## 의사결정 흐름 — 어떤 더블을 쓸까

```text
외부 의존 발견
    ↓
의존이 실제로 사용되는가?
    → NO → Dummy (null, None, 빈 객체)
    ↓ YES
고정된 결과만 필요한가?
    → YES → Stub (return_value 고정)
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

이 흐름은 절대적인 규칙이 아니라 출발점입니다. 실제로는 테스트 계층, 팀 관습, 언어 도구에 따라 조합해서 씁니다.

## 과한 Mock 사용이 보내는 신호

Mock은 강력하지만 남용하면 테스트가 구현에 과하게 결합됩니다.

### 신호 1 — Mock 설정이 테스트보다 길어짐

```python
def test_order_creation():
    # Mock 설정 20줄
    user_repo = MagicMock()
    product_repo = MagicMock()
    payment_gateway = MagicMock()
    email_service = MagicMock()
    logger = MagicMock()
    user_repo.find.return_value = User(id=1)
    product_repo.find.return_value = Product(id=10, price=100)
    payment_gateway.charge.return_value = {"status": "ok"}
    # ...

    # 실제 테스트 3줄
    order = create_order(user_id=1, product_id=10,
                         user_repo=user_repo, product_repo=product_repo,
                         payment=payment_gateway, mailer=email_service, logger=logger)
    assert order.status == "pending"
```

Mock 설정이 이렇게 길어지면 의존이 너무 많거나 함수 책임이 과한 경우가 많습니다. 리팩터링 신호입니다.

### 신호 2 — 리팩터링 때마다 테스트가 깨짐

```python
# 내부 구조를 바꿨을 뿐인데 호출 순서나 인자가 달라져 테스트 실패
repo.find.assert_called_with(user_id=1)  # 내부 변수명이 id로 바뀌면 실패
```

상호작용을 과하게 검증하면 내부 리팩터링이 어려워집니다. 결과 검증으로 대체할 수 있는지 먼저 고려해야 합니다.

### 신호 3 — Mock이 실제 계약과 달라짐

```python
# Mock은 dict 반환
mock_repo.find.return_value = {"id": 1, "email": "a@b.com"}

# 실제 저장소는 User 객체 반환
real_repo.find(1)  # User(id=1, email="a@b.com")
```

Mock과 실제 구현의 계약이 달라지면 통합 환경에서만 문제가 발견됩니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|------|------|------------|
| 모든 곳에 Mock부터 꺼냄 | 구현 세부사항에 묶여 리팩터링이 어려움 | Stub/Fake로 먼저 접근, Mock은 부작용 검증에만 사용 |
| Fake가 실제 계약과 멀어짐 | 테스트 통과, 운영 실패 | Fake에 동일한 입출력 계약 유지 |
| Spy에서 호출 횟수만 검증 | 상호작용은 맞지만 결과가 틀림 | 호출 기록과 최종 결과를 함께 검증 |
| Mock 없이도 되는 곳에 Mock 사용 | 읽기 비용만 증가, 의도가 불분명 | 실제 구현을 써도 느리지 않으면 실제 구현 사용 |
| Dummy로 충분한 자리에 Spy 사용 | 불필요한 복잡성 | 사용하지 않는 의존은 None 또는 Dummy로 충분 |
| 인터페이스 없이 Mock 직접 사용 | 구현 변경 시 Mock 수정 범위 폭발 | 의존을 인터페이스/프로토콜 뒤로 분리 후 대체 |

## 운영 관점에서 생각하기

대부분의 단위 테스트는 Stub과 Fake만으로도 충분합니다. Mock은 상호작용 자체가 중요한 경우, 예를 들어 메일 전송이나 결제 호출처럼 부작용이 핵심인 지점에서만 제한적으로 쓰는 편이 좋습니다.

경험 많은 엔지니어는 테스트 더블의 수가 많아질수록 설계 신호를 봅니다. 대역이 지나치게 많다면 의존이 과하게 퍼져 있거나 인터페이스가 불분명할 가능성이 큽니다. 테스트 더블은 문제를 숨기는 도구가 아니라 구조를 드러내는 도구이기도 합니다.

외부 의존을 인터페이스 뒤로 분리하는 습관이 중요합니다. 함수 시그니처에서 직접 구현체를 받는 대신 추상 인터페이스를 받으면 테스트에서 대체가 쉬워지고 프로덕션 코드의 유연성도 높아집니다.

## 직접 검증해 볼 것

1. `FakeMailer`가 실제 메일러와 같은 입력 계약을 지키는지 확인합니다. 메서드 이름이나 인자 모양이 다르면 테스트에서만 통과하는 가짜 안정감이 생깁니다.
2. 같은 시나리오를 Stub/Fake와 Mock 두 방식으로 각각 써 보고, 어떤 버전이 결과를 더 명확하게 설명하는지 비교합니다.
3. Spy나 Mock을 쓸 때는 호출 횟수만 보지 말고 최종 결과도 함께 점검합니다. 상호작용만 맞고 상태가 틀리는 경우가 실제로 자주 나옵니다.

**예상 결과:** 대역을 써도 테스트 목적이 더 또렷해지고, 실제 의존을 붙였을 때보다 실행 시간이 눈에 띄게 짧아져야 합니다.

## 운영 체크리스트

- [ ] 다섯 종류를 각 한 줄로 구분해 설명할 수 있습니다.
- [ ] Stub과 Fake를 직접 사용해 테스트를 작성했습니다.
- [ ] Mock은 상호작용 검증이 필요한 곳에만 사용했습니다.
- [ ] 외부 의존을 인터페이스 뒤로 분리했습니다.
- [ ] Fake의 입출력 계약이 실제 구현과 일치합니다.

## 연습 문제

1. `send_welcome` 함수를 만들고 Stub과 Mock 두 방식으로 테스트해 보세요.
2. 각 방식이 어떤 종류의 버그를 잘 잡는지 비교해 보세요.
3. `InMemoryUserRepository` Fake를 만들고 그 위에서 중복 이메일 거부 로직을 테스트해 보세요.
4. Mock 설정이 10줄을 넘는 테스트를 발견하면 어떤 리팩터링이 필요한지 분석해 보세요.

## 정리

테스트 더블은 외부 의존을 통제 가능한 대역으로 바꿔 테스트를 짧고 안정적으로 만듭니다. 다만 대역은 한 종류가 아니며, 목적에 맞게 골라야 합니다. 다음 글에서는 가장 자주 함께 언급되는 Mock과 Stub의 차이를 더 깊게 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- **Testing 101 (5/10): 테스트 더블 (현재 글)**
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [Martin Fowler — Test Double](https://martinfowler.com/bliki/TestDouble.html)
- [Meszaros — xUnit Test Patterns](http://xunitpatterns.com/Test%20Double.html)
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)

Tags: Testing, Test Double, Fake, Stub, Spy
