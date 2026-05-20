---
series: clean-code-101
episode: 6
title: "Clean Code 101 (6/10): 오류 처리"
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
  - ErrorHandling
  - Exceptions
  - Robustness
  - Reliability
seo_description: 깔끔한 오류 처리 기법을 배웁니다. 예외와 반환값 선택 기준, Fail Fast 원칙, 재시도 전략을 구현하며 견고함을 높이는 법을 배웁니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (6/10): 오류 처리

오류 처리는 꼭 필요하지만, 그 코드가 비즈니스 로직보다 더 눈에 띄기 시작하면 구조가 이미 흐려진 경우가 많습니다.

이 글은 Clean Code 101 시리즈의 6번째 글입니다.

여기서는 예외와 반환값을 언제 구분해서 써야 하는지, 그리고 재시도와 경계 처리까지 어떤 기준으로 설계해야 하는지 정리하겠습니다.

## 먼저 던지는 질문

- 예외를 던질지 값을 반환할지 어떻게 판단할까요?
- Fail Fast는 어떤 상황에서 특히 중요할까요?
- "값으로서의 오류" 패턴은 언제 유용할까요?

## 큰 그림

![Clean Code 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/06/06-01-concept-at-a-glance.ko.png)

*Clean Code 101 6장 흐름 개요*

이 그림에서는 오류 처리를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 오류 처리의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

오류 처리 코드는 시스템의 견고함을 결정하지만, 동시에 가독성을 쉽게 망가뜨리기도 합니다. 모든 곳에서 넓게 잡고, 로그만 찍고, 계속 진행하는 식의 코드는 실제 장애를 숨기고 나중의 디버깅 비용을 키웁니다.

좋은 오류 처리는 "모든 예외를 막는다"가 아니라 "어디서 어떤 실패를 처리할지 경계를 분명히 나눈다"에 가깝습니다. 입력 검증, 도메인 예외, 외부 호출 재시도, API 경계 매핑이 각각 다른 책임이라는 감각이 중요합니다.

## 한눈에 보는 개념

입력은 먼저 검증하고, 흐름을 잃는 순간에만 예외를 써야 오류 처리가 구조를 해치지 않습니다.

## 핵심 용어

- **Fail Fast**: 잘못된 상태를 가능한 한 빨리 드러내는 원칙입니다.
- **Result/Either**: 성공과 실패를 값으로 표현하는 패턴입니다.
- **Exception**: 호출자가 그 자리에서 복구하기 어려운 상황을 나타냅니다.
- **Retry**: 일시적 실패를 다시 시도하는 전략입니다.
- **Backoff**: 재시도 간격을 점점 늘리는 방식입니다.

## Before/After

**Before**

```python
def fetch(url):
    try:
        ...
    except Exception:
        return None  # swallows everything
```

**After**

```python
class FetchError(Exception): ...

def fetch(url):
    try:
        return _http_get(url)
    except TimeoutError as e:
        raise FetchError(f"timeout: {url}") from e
```

좋은 오류 처리는 정보를 잃지 않습니다. 무엇이 실패했고 왜 올려보냈는지가 유지되어야 상위 계층도 올바르게 판단할 수 있습니다.

## 실전 적용: 견고한 오류 처리 다섯 단계

### Step 1 — Fail fast

```python
# 1_fail_fast.py
def transfer(amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    ...
```

잘못된 입력은 최대한 입구에서 막는 편이 좋습니다. 오류를 뒤로 미루면 문제는 더 멀리 퍼지고, 원인도 흐려집니다.

### Step 2 — Errors as values

```python
# 2_result.py
from dataclasses import dataclass
@dataclass
class Result:
    ok: bool
    value: object = None
    error: str = ""

def parse_int(s):
    try: return Result(True, int(s))
    except ValueError as e: return Result(False, error=str(e))
```

호출자가 분기해야 하는 실패라면 값으로 돌려주는 편이 낫습니다. 파싱, 검증, 사용자 입력 처리 같은 영역이 대표적입니다.

### Step 3 — Exception chaining

```python
# 3_chain.py
class ConfigError(Exception): ...

def load_config(path):
    try:
        with open(path) as f: return f.read()
    except FileNotFoundError as e:
        raise ConfigError(f"missing config: {path}") from e
```

`from e`는 원인을 보존합니다. 도메인 의미를 덧붙이면서도 디버깅에 필요한 원래 예외를 잃지 않는 방식입니다.

### Step 4 — Retry + backoff

```python
# 4_retry.py
import time, random
def with_retry(fn, attempts=3):
    for i in range(attempts):
        try: return fn()
        except TimeoutError:
            if i == attempts - 1: raise
            time.sleep((2 ** i) + random.random())
```

재시도는 아무 데나 붙이는 장식이 아닙니다. 일시적 실패이면서, 같은 작업을 다시 해도 안전한 경우에만 써야 합니다.

### Step 5 — Catch only at boundaries

```python
# 5_boundary.py
def handle_request(req):
    try:
        return business_logic(req)
    except ValueError as e:
        return {"status": 400, "error": str(e)}
    except Exception:
        return {"status": 500, "error": "internal"}
```

넓은 except는 가장 바깥 경계에서만 허용하는 편이 좋습니다. 내부 로직까지 모두 삼켜 버리면 구조가 보이지 않게 됩니다.

## 검증 방법

```bash
python -m pytest -q tests/test_error_handling.py
python -m pytest -q tests/test_retry_idempotency.py
```

**기대 결과**

- 예외 타입과 HTTP 경계 매핑이 테스트로 고정됩니다.
- 재시도는 멱등한 호출에서만 통과해야 합니다.

## 실패하기 쉬운 지점

- `except Exception`이 내부 로직 깊숙한 곳에 남아 있습니다.
- 재시도가 중복 결제를 만들 수 있는 작업에도 붙어 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 검증과 처리 책임이 분리되어 있습니다.
- 도메인 예외 타입이 실패의 의미를 운반합니다.
- 재시도는 멱등한 작업에서만 안전합니다.

## 자주 하는 실수 5가지

1. **빈 except 블록 두기.** 정보가 모두 사라집니다.
2. **`Exception`을 무차별적으로 잡기.** 디버깅이 거의 불가능해집니다.
3. **로그만 찍고 계속 진행하기.** 나쁜 상태가 누적됩니다.
4. **무한 재시도 루프 만들기.** 시스템 전체를 더 불안정하게 만듭니다.
5. **예외를 흐름 제어로 사용하기.** 비싸고 읽기도 어렵습니다.

## 실무에서는 이렇게 보입니다

API 서버에서는 핸들러가 보통 경계가 됩니다. 도메인 로직은 타입이 있는 예외를 올리고, 핸들러는 그것을 HTTP 응답으로 바꿉니다. 외부 호출 재시도는 멱등성이 보장된 작업에만 제한적으로 붙입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 입력은 입구에서 검증합니다.
- 도메인 예외 타입을 분명히 만듭니다.
- 복구 가능한 실패와 불가능한 실패를 구분합니다.
- 재시도는 멱등성과 함께 설계합니다.
- 넓은 except는 경계에만 둡니다.

## 체크리스트

- [ ] 입력 검증이 함수 상단에 있는가?
- [ ] 도메인 예외 타입이 있는가?
- [ ] except 범위가 충분히 좁은가?
- [ ] `from e`로 원인을 보존했는가?
- [ ] 재시도가 멱등한 작업에만 적용되는가?

## 연습 문제

1. 코드에 있는 빈 except 하나를 의미 있는 처리로 바꿔 보세요.
2. 파싱 함수 하나를 Result 패턴으로 바꿔 보세요.
3. 외부 호출 하나에 백오프 재시도를 붙여 보세요.

## 정리 및 다음 단계

오류 처리는 일급 시민이어야 하지만, 주인공이 되어서는 안 됩니다. 다음 글에서는 자주 오해되고 남용되기 쉬운 주석과 문서화를 다룹니다.

## 처음 질문으로 돌아가기

- **예외를 던질지 값을 반환할지 어떻게 판단할까요?**
  - 본문의 기준은 오류 처리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Fail Fast는 어떤 상황에서 특히 중요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **"값으로서의 오류" 패턴은 언제 유용할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- [Clean Code 101 (4/10): 조건문 줄이기](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): 중복 제거](./05-removing-duplication.md)
- **오류 처리 (현재 글)**
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Clean Code (Ch. 7 Error Handling)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Joel Spolsky — Exceptions](https://www.joelonsoftware.com/2003/10/13/13/)
- [Google SRE — Handling Overload](https://sre.google/sre-book/handling-overload/)
- [AWS — Exponential Backoff and Jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Python exception hierarchy](https://docs.python.org/3/library/exceptions.html)
- [AWS Builders Library — timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
Tags: Computer Science, CleanCode, ErrorHandling, Exceptions, Robustness, Reliability
