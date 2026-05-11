---
series: testing-101
episode: 5
title: 테스트 더블
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
last_reviewed: '2026-05-11'
---

# 테스트 더블

> Testing 101 시리즈 (5/10)


## 이 글에서 다룰 문제

테스트는 빠르고 결정적이어야 합니다. 진짜 결제 API를 호출하면 느리고 불안정해집니다. 테스트 더블은 그런 외부 의존을 통제 가능한 대역으로 바꿉니다.

> 잘 쓰면 빠른 신뢰를 만들고, 잘못 쓰면 거짓 신뢰를 만듭니다.

## 전체 흐름
```mermaid
flowchart LR
    SUT["테스트 대상 (SUT)"] --> Double["Test Double"]
    Double -.->|대체| Real[("실제 의존성")]
```

## Before/After

**Before (외부 의존 직접 호출)**

```python
def test_send_welcome_email():
    user = create_user("a@b.com")
    send_welcome_email(user)   # 실제 SMTP 호출
```

**After (Stub로 대체)**

```python
class FakeMailer:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))

def test_send_welcome_email():
    mailer = FakeMailer()
    send_welcome_email(User("a@b.com"), mailer=mailer)
    assert mailer.sent == [("a@b.com", "Welcome!")]
```

## 5가지 더블 5단계

### 1단계 — Dummy

```python
def test_dummy_passthrough():
    user = User(email="a@b.com", logger=None)  # logger는 사용되지 않음
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

### 4단계 — Mock (unittest.mock)

```python
from unittest.mock import MagicMock

def test_mock_with_expectation():
    repo = MagicMock()
    repo.find.return_value = User(email="a@b.com")
    assert get_user(1, repo).email == "a@b.com"
    repo.find.assert_called_once_with(1)
```

### 5단계 — Fake (in-memory)

```python
class InMemoryUserRepo:
    def __init__(self): self._db = {}
    def add(self, u): self._db[u.id] = u
    def find(self, id): return self._db.get(id)
```

## 이 코드에서 주목할 점

- Dummy는 단순히 자리만 채웁니다.
- Stub은 답을, Spy는 기록을, Mock은 기대를 추가합니다.
- Fake는 진짜처럼 동작하지만 작고 빠릅니다.

## 자주 하는 실수 5가지

1. **모든 곳에 Mock을 쓴다.** 깨지기 쉬운 테스트가 됩니다.
2. **테스트가 구현 디테일을 검증한다.** 리팩터링이 불가능해집니다.
3. **Fake가 진짜와 너무 달라 잡히는 버그가 운영과 다르다.**
4. **Spy의 호출 횟수만 검증한다.** 결과도 같이 봐야 합니다.
5. **Dummy가 필요한 자리에 Stub을 만들어 놓는다.** 과한 노력입니다.

## 실무에서는 이렇게 쓰입니다

대부분의 단위 테스트는 Stub과 Fake만으로 충분합니다. Mock은 상호작용 자체가 핵심인 경우(이메일 발송, 결제 호출 등)에만 씁니다.

## 체크리스트

- [ ] 5종의 더블을 구별할 수 있다.
- [ ] Stub과 Fake로 테스트를 작성했다.
- [ ] Mock을 상호작용 검증에만 썼다.
- [ ] 외부 의존이 인터페이스로 분리되어 있다.

## 정리 및 다음 단계

테스트 더블은 외부 의존을 길들이는 도구입니다. 다음 글에서는 가장 자주 쓰이는 두 종류인 Mock과 Stub을 더 깊이 봅니다.

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
