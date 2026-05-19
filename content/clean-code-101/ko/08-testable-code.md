---
series: clean-code-101
episode: 8
title: 테스트 가능한 코드
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
  - CleanCode
  - Testability
  - Testing
  - DependencyInjection
  - Refactoring
seo_description: 테스트 가능성을 높이는 구체적인 기법을 배웁니다. 순수 함수와 의존성 주입을 활용해 흔들리지 않는 견고한 단위 테스트 작성법을 배웁니다.
last_reviewed: '2026-05-15'
---

# 테스트 가능한 코드

어떤 코드는 테스트 한 줄로 끝나는데, 어떤 코드는 테스트를 쓰려는 순간부터 거대한 준비 작업이 필요합니다.

이 글은 Clean Code 101 시리즈의 8번째 글입니다.

여기서는 그 차이가 어디서 오는지, 그리고 설계를 바꾸면 왜 테스트가 자연스럽게 따라오는지 설명하겠습니다.

---

## 이 글에서 다룰 문제

- 순수 로직과 부수 효과는 어떻게 분리해야 할까요?
- 의존성 주입은 어떻게 테스트용 이음새를 만들까요?
- Fake와 Spy는 각각 언제 쓰는 편이 좋을까요?
- 시간과 난수처럼 비결정적인 의존성은 어떻게 다뤄야 할까요?
- 어떤 리팩토링이 테스트 가능성을 직접 개선할까요?

> 테스트 가능성은 사후 결과가 아니라 설계의 부산물이며, 부수 효과와 의존성을 어떻게 밀어내는지가 그 품질을 결정합니다.

## 왜 중요한가

테스트하기 어려운 코드는 대개 바꾸기도 어렵습니다. 데이터베이스, 네트워크, 현재 시간, 전역 싱글턴이 함수 내부에 깊게 붙어 있으면, 작은 규칙 하나를 검증하는 일조차 무겁고 느려집니다.

반대로 핵심 로직을 순수하게 만들고, 외부 의존성을 경계로 밀어내면 테스트는 놀랄 만큼 단순해집니다. 그래서 테스트 가능성은 단순한 QA 편의가 아니라 설계 품질의 측정치로 보는 편이 정확합니다.

## 한눈에 보는 개념

![테스트 가능한 코드](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/08/08-01-concept-at-a-glance.ko.png)

*테스트 가능성의 흐름: 순수 로직과 IO 경계를 나누면 단위 테스트와 통합 테스트가 각자 자리를 찾습니다.*

가장 좋은 구조는 순수한 핵심 로직을 얇은 어댑터가 둘러싸는 형태입니다.

## 핵심 용어

- **Pure function**: 같은 입력에 같은 출력을 내고, 부수 효과가 없는 함수입니다.
- **Dependency Injection**: 외부 의존성을 인자로 받는 방식입니다.
- **Seam**: 동작을 교체할 수 있는 경계 지점입니다.
- **Fake**: 테스트용으로 단순화한 동작 구현체입니다.
- **Spy**: 호출 기록을 남기는 테스트 더블입니다.

## Before/After

**Before**

```python
import datetime, requests
def is_business_hour():
    now = datetime.datetime.now()
    return 9 <= now.hour < 18

def fetch_user(uid):
    return requests.get(f"https://api/users/{uid}").json()
```

**After**

```python
def is_business_hour(now):
    return 9 <= now.hour < 18

def fetch_user(uid, http):
    return http.get(f"/users/{uid}").json()
```

시간과 HTTP를 함수 밖에서 넣어 주면, 핵심 로직은 훨씬 쉽게 검증할 수 있습니다. 테스트 가능한 코드는 보통 더 작은 경계와 더 명시적인 의존성을 가집니다.

## 실전 적용: 테스트 가능성을 높이는 다섯 단계

### Step 1 — Extract pure logic

```python
# 1_pure.py
def total(items):
    return sum(it.price * it.qty for it in items)
```

입출력 없이 계산만 하는 부분은 항상 순수 함수 후보입니다. 이런 핵심 계산을 먼저 분리하면 단위 테스트가 거의 공짜가 됩니다.

### Step 2 — Inject time

```python
# 2_clock.py
from datetime import datetime
def is_overdue(due, now=None):
    now = now or datetime.now()
    return now > due
```

시간은 흐르기 때문에 테스트를 깨뜨립니다. 고정 가능한 값으로 받아들이는 순간 테스트는 안정성을 얻습니다.

### Step 3 — Fake objects

```python
# 3_fake.py
class FakeRepo:
    def __init__(self): self.users = {}
    def save(self, u): self.users[u.id] = u
    def get(self, uid): return self.users.get(uid)

def register(repo, user):
    repo.save(user); return user
```

도메인 로직을 검증하는 데 실제 데이터베이스가 꼭 필요하지는 않습니다. Fake는 느리고 불안정한 외부 의존성을 테스트 밖으로 밀어냅니다.

### Step 4 — Recording calls (Spy)

```python
# 4_spy.py
class EmailSpy:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))

def notify(email, user):
    email.send(user.email, "welcome")
```

Spy는 무엇을 보냈는지, 몇 번 호출했는지 검증하게 해 줍니다. 협력 객체와의 상호작용을 확인할 때 유용합니다.

### Step 5 — Isolate external calls

```python
# 5_adapter.py
class HttpClient:
    def get(self, path): ...

def fetch_user(uid, http: HttpClient):
    return http.get(f"/users/{uid}").json()
```

외부 호출을 하나의 어댑터로 집중시키면 테스트 범위를 나누기 쉬워집니다. 단위 테스트는 Fake로, 통합 테스트는 실제 어댑터로 분리할 수 있습니다.

## 검증 방법

```bash
python -m pytest -q tests/test_total.py tests/test_notify.py
python -m pytest -q tests/test_http_adapter.py
```

**기대 결과**

- 순수 함수 테스트는 매우 빠르게 끝나야 합니다.
- 어댑터 테스트만 외부 의존성과 통합되어야 합니다.

## 실패하기 쉬운 지점

- `datetime.now()`와 난수가 아직 핵심 로직 안에 남아 있습니다.
- mock 수가 많아졌는데도 함수 책임은 그대로 큽니다.

## 이 코드에서 먼저 봐야 할 점

- 핵심 로직은 IO를 몰라야 합니다.
- 시간과 난수는 항상 주입하는 편이 좋습니다.
- Fake를 쓰면 테스트가 빠르고 안정적으로 돌아갑니다.

## 자주 하는 실수 5가지

1. **함수 안에서 `datetime.now()` 호출하기.** 시간이 지나면 테스트가 흔들립니다.
2. **DB와 네트워크를 도메인 로직에 섞기.** 단위 테스트가 사라집니다.
3. **mock 라이브러리에만 의존하기.** 숨은 결합은 그대로 남습니다.
4. **테스트를 위해 공개 메서드 늘리기.** 캡슐화가 깨집니다.
5. **전역 싱글턴 사용하기.** 격리가 어려워집니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 ports-and-adapters나 hexagonal architecture 같은 구조를 써서 도메인 코어를 IO에서 분리합니다. 그 덕분에 수천 개의 단위 테스트도 아주 빠르게 끝나고, 느린 통합 테스트는 별도 계층으로 관리할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 먼저 순수 함수부터 만듭니다.
- 의존성은 인자로 받습니다.
- mocks보다 fakes를 더 자주 선호합니다.
- 시간, 난수, IO를 경계 바깥으로 밀어냅니다.
- 느린 테스트를 설계 냄새로 봅니다.

## 체크리스트

- [ ] 핵심 로직이 순수한가?
- [ ] 외부 의존성을 주입받는가?
- [ ] 시간과 난수를 주입하는가?
- [ ] Fake로 IO 없이 테스트할 수 있는가?
- [ ] 단위 테스트가 1초 안에 끝나는가?

## 연습 문제

1. 코드 안의 `datetime.now()` 호출 하나를 주입 방식으로 바꿔 보세요.
2. DB에 묶인 함수 하나를 Fake로 단위 테스트해 보세요.
3. 외부 HTTP 호출 하나를 어댑터 클래스로 추출해 보세요.

## 정리 및 다음 단계

테스트 가능성은 설계를 비추는 거울입니다. 다음 글에서는 코드를 안전하게 바꾸는 기술, 즉 리팩토링의 기본 절차를 다룹니다.

<!-- toc:begin -->
- [Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [이름 짓기](./02-naming.md)
- [함수 작게 만들기](./03-small-functions.md)
- [조건문 줄이기](./04-simplifying-conditionals.md)
- [중복 제거](./05-removing-duplication.md)
- [오류 처리](./06-error-handling.md)
- [주석과 문서화](./07-comments-and-docs.md)
- **테스트 가능한 코드 (현재 글)**
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Working Effectively with Legacy Code (M. Feathers)](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Mocks Aren't Stubs (Martin Fowler)](https://martinfowler.com/articles/mocksArentStubs.html)
- [Pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/)
Tags: Computer Science, CleanCode, Testability, Testing, DependencyInjection, Refactoring
