---
series: testing-101
episode: 5
title: 테스트 더블
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

# 테스트 더블

단위 테스트를 쓰다 보면 곧 외부 의존과 마주칩니다. 메일 전송, 결제 API, 현재 시간, 데이터베이스처럼 실제로 호출하면 느리거나 비싸거나 불안정한 대상들입니다. 이런 의존을 매번 진짜로 호출하면 테스트가 느려지고, 실패 원인도 코드가 아니라 외부 환경으로 번집니다.

그래서 테스트에서는 실제 의존 대신 대역을 씁니다. 다만 대역도 하나로 뭉뚱그리면 금방 헷갈립니다. 반환값만 흉내 내는 경우와 호출 자체를 기록하는 경우는 목적이 다르기 때문입니다.

이 글은 Testing 101 시리즈의 다섯 번째 글입니다. 여기서는 테스트 더블의 다섯 종류를 구분하고, 언제 무엇을 써야 하는지, 그리고 왜 과한 목 사용이 문제를 만드는지 정리하겠습니다.

---

## 이 글에서 다룰 문제

- 테스트 더블은 무엇을 대체하는 장치일까요?
- Dummy, Stub, Spy, Mock, Fake는 어떻게 다를까요?
- 어떤 상황에서 어떤 종류를 골라야 할까요?
- 왜 Mock 남용이 깨지기 쉬운 테스트를 만들까요?

> 테스트 더블은 실제 의존을 테스트용 대역으로 바꾸는 장치입니다. 같은 대역이라도 역할은 서로 다르므로 구분해서 써야 합니다.

## 왜 중요한가

테스트는 빠르고 결정적이어야 합니다. 실제 결제 API나 SMTP 서버를 부르면 속도도 느려지고 실패 원인도 외부로 번집니다. 테스트 더블은 이런 의존을 통제 가능한 대역으로 바꿔 테스트를 짧고 안정적으로 만듭니다.

문제는 대역을 쓰는 순간 거짓 확신도 함께 들어올 수 있다는 점입니다. 실제 계약과 너무 다른 Fake를 만들거나, 호출 횟수만 지나치게 검증하면 테스트는 초록색인데 설계는 오히려 경직될 수 있습니다. 그래서 종류를 구분하는 일이 중요합니다.

## 한눈에 보는 구조

![한눈에 보는 구조](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/05/05-01-diagram.ko.png)

*한눈에 보는 구조*
테스트 대상 시스템은 실제 의존 대신 테스트 더블을 바라봅니다. 여기서 핵심은 대체 자체보다 대체 목적입니다. 값을 돌려주기 위해 바꾸는지, 호출 기록을 남기기 위해 바꾸는지, 간단한 실제 구현처럼 동작하게 만들려는지에 따라 선택이 달라집니다.

## 핵심 용어

- **Dummy**: 자리를 채우기만 하는 객체입니다.
- **Stub**: 미리 정한 값을 돌려주는 대역입니다.
- **Spy**: 값을 돌려주면서 호출 기록도 남기는 대역입니다.
- **Mock**: 미리 기대를 심어 두고 그 호출이 일어났는지 검증하는 대역입니다.
- **Fake**: 실제와 비슷하게 동작하지만 단순하고 빠른 구현입니다.

## 바꾸기 전과 후

**바꾸기 전 — 실제 의존 직접 호출**

```python
def test_send_welcome_email():
    user = create_user("a@b.com")
    send_welcome_email(user)   # 실제 SMTP 호출
```

**바꾼 뒤 — 대역으로 교체**

```python
class FakeMailer:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))

def test_send_welcome_email():
    mailer = FakeMailer()
    send_welcome_email(User("a@b.com"), mailer=mailer)
    assert mailer.sent == [("a@b.com", "Welcome!")]
```

진짜 SMTP 대신 `FakeMailer`를 쓰면 네트워크와 무관하게 메일 전송 결과를 확인할 수 있습니다. 이처럼 테스트 더블은 외부 비용을 잘라 내고 검증 대상을 코드 안으로 끌고 옵니다.

## 다섯 단계로 대역 종류 익히기

### 1단계 — Dummy

```python
def test_dummy_passthrough():
    user = User(email="a@b.com", logger=None)  # logger는 사용하지 않음
    assert user.email == "a@b.com"
```

### 2단계 — Stub

```python
class StubClock:
    def now(self): return "2026-05-04"

def test_uses_stub_clock():
    assert greet(StubClock()) == "Hello, today is 2026-05-04"
```

### 3단계 — Spy

```python
class SpyMailer:
    def __init__(self): self.calls = []
    def send(self, to, body): self.calls.append((to, body))

def test_spy_records_calls():
    m = SpyMailer(); send_welcome("a@b.com", m)
    assert len(m.calls) == 1
```

### 4단계 — Mock

```python
from unittest.mock import MagicMock

def test_mock_with_expectation():
    repo = MagicMock()
    repo.find.return_value = User(email="a@b.com")
    assert get_user(1, repo).email == "a@b.com"
    repo.find.assert_called_once_with(1)
```

### 5단계 — Fake

```python
class InMemoryUserRepo:
    def __init__(self): self._db = {}
    def add(self, u): self._db[u.id] = u
    def find(self, id): return self._db.get(id)
```

## 이 코드에서 먼저 볼 점

- Dummy는 빈 자리를 채울 뿐입니다.
- Stub은 값을 돌려주고, Spy는 호출 기록까지 남기고, Mock은 기대한 호출을 검증합니다.
- Fake는 실제 구현과 비슷한 계약을 유지하면서도 빠르게 동작합니다.

이 구분을 익히면 테스트 목적이 훨씬 선명해집니다. 결과를 확인하려는지, 상호작용을 확인하려는지, 아니면 실제 저장소 대신 가벼운 구현이 필요한지를 분리해 생각할 수 있습니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 모든 곳에 Mock부터 꺼내는 일입니다. 그러면 구현 세부사항에 테스트가 과하게 묶여 리팩터링이 어려워집니다.

또 다른 문제는 Fake가 실제 계약과 너무 멀어지는 경우입니다. 테스트에서는 통과하지만 운영에서는 다른 방식으로 깨질 수 있습니다. Fake는 단순해야 하지만, 최소한 같은 입력과 출력 계약은 지켜야 합니다.

Spy를 쓸 때 호출 횟수만 보고 실제 결과를 확인하지 않는 문제도 자주 보입니다. 상호작용만 맞고 최종 결과가 틀릴 수 있으므로, 가능하면 결과 검증도 함께 고려해야 합니다.

## 직접 검증해 볼 것

1. `FakeMailer`가 실제 메일러와 같은 입력 계약을 지키는지 확인합니다. 메서드 이름이나 인자 모양이 다르면 테스트에서만 통과하는 가짜 안정감이 생깁니다.
2. 같은 시나리오를 Stub/Fake와 Mock 두 방식으로 각각 써 보고, 어떤 버전이 결과를 더 명확하게 설명하는지 비교합니다.
3. Spy나 Mock을 쓸 때는 호출 횟수만 보지 말고 최종 결과도 함께 점검합니다. 상호작용만 맞고 상태가 틀리는 경우가 실제로 자주 나옵니다.

**예상 결과:** 대역을 써도 테스트 목적이 더 또렷해지고, 실제 의존을 붙였을 때보다 실행 시간이 눈에 띄게 짧아져야 합니다.

## 실패 신호와 첫 점검

- Fake가 실제 계약과 다르면 운영에서만 재현되는 버그를 놓치기 쉽습니다.
- 테스트마다 Mock 설정이 너무 길어지면 구현 세부사항에 과하게 묶였는지 점검해야 합니다.
- Dummy로 충분한 자리에 Spy나 Mock을 끼우면 읽기 비용만 커집니다.

## 실무에서는 이렇게 생각합니다

대부분의 단위 테스트는 Stub과 Fake만으로도 충분합니다. Mock은 상호작용 자체가 중요한 경우, 예를 들어 메일 전송이나 결제 호출처럼 부작용이 핵심인 지점에서만 제한적으로 쓰는 편이 좋습니다.

경험 많은 엔지니어는 테스트 더블의 수가 많아질수록 설계 신호를 봅니다. 대역이 지나치게 많다면 의존이 과하게 퍼져 있거나 인터페이스가 불분명할 가능성이 큽니다. 테스트 더블은 문제를 숨기는 도구가 아니라 구조를 드러내는 도구이기도 합니다.

## 체크리스트

- [ ] 다섯 종류를 각 한 줄로 구분해 설명할 수 있습니다.
- [ ] Stub과 Fake를 직접 사용해 테스트를 작성했습니다.
- [ ] Mock은 상호작용 검증이 필요한 곳에만 사용했습니다.
- [ ] 외부 의존을 인터페이스 뒤로 분리했습니다.

## 연습 문제

1. `send_welcome` 함수를 만들고 Stub과 Mock 두 방식으로 테스트해 보세요.
2. 각 방식이 어떤 종류의 버그를 잘 잡는지 비교해 보세요.
3. 메모리 기반 저장소 Fake를 만들고 그 위에서 비즈니스 로직을 테스트해 보세요.

## 정리

테스트 더블은 외부 의존을 통제 가능한 대역으로 바꿔 테스트를 짧고 안정적으로 만듭니다. 다만 대역은 한 종류가 아니며, 목적에 맞게 골라야 합니다. 다음 글에서는 가장 자주 함께 언급되는 Mock과 Stub의 차이를 더 깊게 보겠습니다.

<!-- toc:begin -->
- [테스트란 무엇인가?](./01-what-is-testing.md)
- [단위 테스트](./02-unit-test.md)
- [통합 테스트](./03-integration-test.md)
- [E2E 테스트](./04-e2e-test.md)
- **테스트 더블 (현재 글)**
- Mock과 Stub (예정)
- 테스트 커버리지 (예정)
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)
<!-- toc:end -->

## 참고 자료

- [Martin Fowler — Test Double](https://martinfowler.com/bliki/TestDouble.html)
- [Meszaros — xUnit Test Patterns](http://xunitpatterns.com/Test%20Double.html)
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)

Tags: Testing, Test Double, Fake, Stub, Spy
