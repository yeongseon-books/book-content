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
last_reviewed: '2026-05-04'
---

# 테스트 더블

> Testing 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: DB나 외부 API에 *진짜로 호출* 하지 않고도 *동작을 검증* 할 수 있을까요?

> 테스트 더블은 *진짜 의존성* 을 *대역* 으로 바꿉니다. 종류에 따라 *역할이 다릅니다*.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *테스트 더블* 의 정의와 5가지 종류
- *언제 어떤 종류* 를 써야 하는지
- *Stub vs Mock vs Fake* 의 차이
- 테스트 더블의 *남용* 이 만드는 문제

## 왜 중요한가

테스트는 *빠르고 결정적* 이어야 합니다. 진짜 결제 API를 호출하면 *느리고 불안정* 합니다. 테스트 더블은 그 외부 의존을 *통제 가능한 대역* 으로 바꿉니다.

> 잘 쓰면 *빠른 신뢰*, 못 쓰면 *거짓 신뢰* 를 만듭니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    SUT["테스트 대상 (SUT)"] --> Double["Test Double"]
    Double -.->|대체| Real[("실제 의존성")]
```

## 핵심 용어 정리 (Meszaros 5종)

- **Dummy**: *전달만 되는* 자리 채우기 객체.
- **Stub**: *정해진 답* 만 돌려주는 가짜.
- **Spy**: *호출 기록* 을 남기는 stub.
- **Mock**: *기대된 호출* 을 사전에 정의하고 검증.
- **Fake**: *간단한 진짜 구현* (예: in-memory DB).

## Before/After

**Before (외부 의존 직접 호출)**

```python
def test_send_welcome_email():
    user = create_user("a@b.com")
    send_welcome_email(user)   # *진짜 SMTP* 호출
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

## 실습: 5가지 더블 5단계

### 1단계 — Dummy

```python
def test_dummy_passthrough():
    user = User(email="a@b.com", logger=None)  # logger는 *사용되지 않음*
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

- *Dummy* 는 단순히 *자리* 만 채웁니다.
- *Stub* 은 *답* 을, *Spy* 는 *기록* 을, *Mock* 은 *기대* 를 추가합니다.
- *Fake* 는 *진짜처럼 동작* 하지만 *작고 빠릅니다*.

## 자주 하는 실수 5가지

1. **모든 곳에 *Mock* 을 쓴다.** *깨지기 쉬운 테스트* 가 됩니다.
2. **테스트가 *구현 디테일* 을 검증한다.** 리팩터링이 *불가능해집니다*.
3. **Fake가 *진짜와 너무 달라* 잡히는 버그가 운영과 다르다.**
4. **Spy의 *호출 횟수* 만 검증한다.** *결과* 도 같이 봐야 합니다.
5. **Dummy가 필요한 자리에 *Stub을 만들어* 놓는다.** *과한 노력*.

## 실무에서는 이렇게 쓰입니다

대부분의 단위 테스트는 *Stub과 Fake* 만으로 충분합니다. *Mock* 은 *상호작용 자체* 가 핵심인 경우(이메일 발송, 결제 호출 등)에만 씁니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *기본은 Fake/Stub*, 필요할 때만 Mock.
- *행위가 아니라 결과* 를 검증한다.
- 외부 의존은 *얇은 인터페이스* 뒤에 둔다.
- Fake는 *진짜와 같은 계약* 을 지킨다.
- 테스트가 *무엇을 검증하는지* 한 줄로 말할 수 있다.

## 체크리스트

- [ ] 5종의 더블을 *구별* 할 수 있다.
- [ ] *Stub과 Fake* 로 테스트를 작성했다.
- [ ] Mock을 *상호작용 검증* 에만 썼다.
- [ ] 외부 의존이 *인터페이스* 로 분리되어 있다.

## 연습 문제

1. `send_welcome` 함수를 만들고 *Stub과 Mock 두 가지* 로 테스트하세요.
2. 두 테스트가 잡는 *버그의 종류* 가 어떻게 다른지 적어 보세요.
3. *in-memory Repo Fake* 를 만들어 비즈니스 로직을 테스트하세요.

## 정리 및 다음 단계

테스트 더블은 *외부 의존을 길들이는* 도구입니다. 다음 글에서는 가장 자주 쓰이는 두 종류, *Mock과 Stub* 을 더 깊이 봅니다.

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
