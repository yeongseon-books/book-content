---
title: "바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다"
series: clean-code-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- CleanCode
- AI코딩
- 테스트가능성
- 의존성주입
- 단위테스트
seo_description: "바이브코딩 시대, AI가 생성한 코드를 테스트 가능하게 만드는 방법과 의존성 주입, 순수 함수 분리 기법을 실용적으로 설명합니다."
---

# 바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다

이 글은 바이브코딩을 위한 클린 코드 시리즈의 8번째 글입니다.

AI가 만들어준 쿠폰 발행 함수를 테스트하려고 했습니다. 그런데 테스트를 쓰기 시작하자마자 막혔습니다.

```python
def issue_coupon(user_id):
    from datetime import datetime
    code = f"CP-{user_id}-{int(datetime.now().timestamp())}"
    db.execute("INSERT INTO coupons (code, user_id) VALUES (%s, %s)", (code, user_id))
    email.send(user_id, f"쿠폰 코드: {code}")
    return code
```

이 함수를 테스트하려면 데이터베이스가 필요합니다. 이메일 클라이언트도 필요합니다. 그리고 `datetime.now()`가 매번 다른 값을 반환하기 때문에 같은 입력에 대해 같은 출력을 기대할 수 없습니다. 테스트 환경을 구성하는 데만 한 시간이 걸렸고, 결국 "이건 나중에 테스트 쓰자"로 넘어갔습니다.

AI는 기능이 동작하도록 코드를 작성하는 데 최적화되어 있습니다. 데이터베이스, 현재 시간, 외부 API가 함수 내부에 직접 들어가는 것은 AI 입장에서 가장 자연스러운 방식입니다. 하지만 이 방식은 테스트를 매우 어렵게 만듭니다.

테스트하기 어려운 코드는 바꾸기도 어렵습니다. 외부 의존이 코드 안에 깊게 붙어 있을수록, 작은 변경도 전체를 다시 검증해야 합니다. 테스트 가능성은 단순한 QA 편의가 아니라 설계 품질의 측정치입니다.

> 테스트하기 어려운 코드를 발견했을 때, 그것은 테스트 문제가 아니라 설계 문제라는 신호입니다.

---

## 이 글에서 다룰 문제
- AI가 만든 코드에서 테스트를 막는 요소들은 무엇인가요?
- 외부 의존성을 주입하면 왜 테스트가 쉬워지나요?
- 순수 함수와 부수 효과를 어떻게 분리해야 하나요?
- Fake 객체와 Spy 객체는 언제 사용하나요?
- AI에게 테스트 가능한 코드를 요청하는 방법은 무엇인가요?

---

## AI 코드가 테스트하기 어려운 이유

AI가 생성하는 코드에서 테스트를 막는 요소들이 있습니다.

**1. 함수 내부에서 직접 현재 시간 호출**
```python
# 테스트하기 어려운 패턴
def is_business_hour():
    now = datetime.datetime.now()  # 매번 다른 결과
    return 9 <= now.hour < 18
```

**2. 함수 내부에서 데이터베이스 직접 호출**
```python
# 테스트하려면 실제 DB가 필요
def get_user(user_id):
    return db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**3. 외부 API를 함수 내부에서 직접 호출**
```python
# 테스트할 때마다 실제 API 호출
def fetch_exchange_rate():
    return requests.get("https://api.exchangerates.io/latest").json()
```

### 해결책: 의존성 주입

외부 의존성을 함수의 인자로 받으면, 테스트할 때 가짜 구현체를 넣을 수 있습니다.

```python
# 테스트 가능한 버전
def is_business_hour(now=None):
    if now is None:
        now = datetime.datetime.now()
    return 9 <= now.hour < 18

# 테스트
from datetime import datetime
assert is_business_hour(datetime(2026, 1, 1, 10, 0)) == True   # 10시
assert is_business_hour(datetime(2026, 1, 1, 20, 0)) == False  # 20시
```

```python
# 의존성 주입으로 테스트 가능
def issue_coupon(user_id: str, clock, db, email) -> str:
    code = f"CP-{user_id}-{clock.now_ts()}"
    db.save_coupon(code, user_id)
    email.send(user_id, f"쿠폰 코드: {code}")
    return code

# 테스트용 가짜 구현체
class FakeClock:
    def __init__(self, fixed_ts: int):
        self.fixed_ts = fixed_ts

    def now_ts(self) -> int:
        return self.fixed_ts

class FakeDb:
    def __init__(self):
        self.saved = []

    def save_coupon(self, code, user_id):
        self.saved.append((code, user_id))

class SpyEmail:
    def __init__(self):
        self.sent = []

    def send(self, user_id, body):
        self.sent.append((user_id, body))

# 깔끔한 단위 테스트
clock = FakeClock(fixed_ts=1000000)
db = FakeDb()
email = SpyEmail()

code = issue_coupon("user123", clock, db, email)

assert code == "CP-user123-1000000"
assert len(db.saved) == 1
assert len(email.sent) == 1
```

## Before / After

```python
# AI가 생성한 코드 - 테스트하기 어려움
def issue_coupon(user_id):
    from datetime import datetime
    code = f"CP-{user_id}-{int(datetime.now().timestamp())}"
    db.execute("INSERT INTO coupons ...", (code, user_id))
    email_client.send(user_id, f"쿠폰 코드: {code}")
    return code
```

```python
# 테스트 가능한 버전
class Clock:
    def now_ts(self) -> int:
        from datetime import datetime
        return int(datetime.now().timestamp())

def issue_coupon(user_id: str, clock: Clock, db, email) -> str:
    code = f"CP-{user_id}-{clock.now_ts()}"
    db.save_coupon(code, user_id)
    email.send(user_id, f"쿠폰 코드: {code}")
    return code
```

시간, DB, 이메일을 모두 주입받으므로 테스트에서 각각을 가짜 구현으로 대체할 수 있습니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `datetime.now()` 함수 내부에서 직접 호출 | 테스트가 시간에 의존 | 시간을 인자로 주입 |
| DB와 계산 로직을 한 함수에 섞기 | 단위 테스트 불가 | 순수 계산 함수 분리 |
| mock 라이브러리에만 의존 | 숨겨진 결합이 남음 | Fake 객체로 실제 동작 시뮬레이션 |
| 전역 변수나 싱글턴 사용 | 테스트 격리 불가 | 의존성 주입으로 전환 |
| 테스트 없이 구조 변경 | 회귀 위험 | 구조 변경 PR과 기능 PR 분리 |

## AI에게 클린 코드 요청하는 팁

```
프롬프트 예시:
"쿠폰 발행 함수를 구현해줘.
테스트 가능성 규칙:
- datetime.now(), requests.get() 같은 외부 의존성은 인자로 주입받을 것
- 순수 계산 로직(쿠폰 코드 생성 등)과 IO(DB 저장, 이메일 발송)를 분리할 것
- 함수 인자로 받는 DB와 이메일 클라이언트는 인터페이스(Protocol)로 정의
- 테스트 코드도 같이 작성해줘 (FakeClock, FakeDb 포함)"
```

## 운영 체크리스트
- [ ] 핵심 계산 로직이 순수 함수인가?
- [ ] 외부 의존성(시간, DB, 이메일)을 인자로 받는가?
- [ ] Fake 또는 Spy로 IO 없이 테스트할 수 있는가?
- [ ] 단위 테스트가 1초 안에 끝나는가?
- [ ] 구조 변경 PR과 기능 추가 PR이 분리되어 있는가?

## 처음 질문으로 돌아가기

- **외부 의존성을 주입하면 왜 테스트가 쉬워지나요?**
  `FakeClock`, `FakeDb` 같은 테스트 전용 구현체를 넣을 수 있게 됩니다. 실제 DB나 시간 없이도 동작을 검증할 수 있습니다.

- **순수 함수와 부수 효과를 어떻게 분리해야 하나요?**
  쿠폰 코드 계산처럼 같은 입력에 같은 출력이 나오는 부분을 분리합니다. DB 저장이나 이메일 발송은 그 밖에서 처리합니다.

- **Fake 객체와 Spy 객체는 언제 사용하나요?**
  Fake는 DB처럼 실제 저장 동작을 단순하게 시뮬레이션할 때, Spy는 이메일처럼 "몇 번 어떤 값으로 호출됐는지" 검증할 때 사용합니다.

## 정리

AI는 동작하는 코드를 만드는 데 최적화되어 있어서 외부 의존성이 함수 내부에 직접 들어가는 코드를 자주 생성합니다. 이런 코드는 테스트하기 어렵고, 테스트하기 어렵다는 것은 바꾸기도 어렵다는 신호입니다. 시간, DB, 네트워크를 인자로 주입받는 구조로 바꾸면 Fake 객체를 사용해 빠르고 안정적인 단위 테스트를 작성할 수 있습니다. 다음 글에서는 AI 코드를 리팩터링하는 전체 흐름을 다룹니다.

## 참고 자료
### 공식 문서
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
### 관련 시리즈
- [Software Design 101](../../software-design-101/ko/)
- [Testing 101](../../testing-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 클린 코드 (1/10): AI 코드는 돌아가지만 읽기 어렵다](./01-what-is-clean-code.md)
- [바이브코딩을 위한 클린 코드 (2/10): AI가 만든 변수명이 a, b, temp](./02-naming.md)
- [바이브코딩을 위한 클린 코드 (3/10): AI가 100줄짜리 함수를 만들었다](./03-functions.md)
- [바이브코딩을 위한 클린 코드 (4/10): AI가 중첩 if를 5단계로 만들었다](./04-conditionals.md)
- [바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다](./05-dry.md)
- [바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다](./06-error-handling.md)
- [바이브코딩을 위한 클린 코드 (7/10): AI가 주석을 잔뜩 넣었는데 코드와 안 맞다](./07-comments.md)
- **바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다 (현재 글)**
- [바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법](./09-refactoring.md)
- [바이브코딩을 위한 클린 코드 (10/10): AI 코드를 리뷰하는 방법](./10-code-review.md)
<!-- toc:end -->
Tags: 바이브코딩, CleanCode, AI코딩, 테스트가능성, 의존성주입, 단위테스트
