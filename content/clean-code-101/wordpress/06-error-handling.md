---
title: "바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다"
series: clean-code-101
episode: 6
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
- 에러처리
- Exceptions
- 안정성
seo_description: "바이브코딩 시대, AI가 생성한 except: pass, except Exception 패턴이 왜 위험한지, 올바른 에러 처리 구조를 만드는 방법을 설명합니다."
---

# 바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다

이 글은 바이브코딩을 위한 클린 코드 시리즈의 6번째 글입니다.

AI가 만들어준 API 서버를 배포했습니다. 처음 며칠은 잘 동작했습니다. 그런데 특정 사용자들의 주문이 실패하는데 로그에 아무것도 없었습니다. 코드를 열어보니 이런 패턴이 있었습니다.

```python
def process_payment(order_data):
    try:
        result = payment_gateway.charge(order_data)
        return result
    except:
        pass
    return None
```

`except: pass`였습니다. 결제 게이트웨이에서 어떤 에러가 발생해도 조용히 `None`을 반환하고 있었습니다. 사용자 입장에서는 주문이 처리됐는지 실패했는지 알 수 없었고, 개발자 입장에서는 무슨 문제인지 전혀 알 수 없었습니다. 결국 며칠치 실패 로그가 없어서 어떤 종류의 에러가 얼마나 발생했는지도 파악이 불가능했습니다.

AI는 "에러가 나도 프로그램이 멈추지 않게" 하는 방어적 코드를 자주 생성합니다. 겉보기에 안전해 보이는 이 패턴이 실제로는 가장 위험합니다. 에러를 숨기기 때문입니다. 숨겨진 에러는 시스템을 나쁜 상태로 조용히 계속 실행시킵니다.

좋은 에러 처리는 "모든 에러를 막는다"가 아닙니다. "어디서 어떤 실패를 처리할지 경계를 분명히 나눈다"는 것입니다.

> 에러를 숨기는 코드는 존재하지 않는 버그처럼 보이게 만들 뿐, 버그를 없애지 않습니다.

---

## 이 글에서 다룰 문제
- `except: pass`가 왜 시스템 전체에 위험한가요?
- 예외를 던질지 값으로 반환할지 어떻게 결정하나요?
- 에러가 발생했을 때 원인 정보를 어떻게 보존하나요?
- AI에게 올바른 에러 처리를 요청하는 방법은 무엇인가요?
- 재시도 로직을 잘못 붙이면 어떤 문제가 생기나요?

---

## AI가 나쁜 에러 처리를 만드는 이유

AI는 "프로그램이 죽지 않게" 하는 방어적 코드를 선호합니다. 예외를 잡아서 `None`을 반환하거나 `pass`로 넘어가는 패턴이 학습 데이터에 많이 있기 때문이기도 합니다. 또한 AI는 에러가 발생했을 때 어떤 에러 메시지가 운영에 중요한지, 어떤 에러가 사용자에게 전달되어야 하는지를 컨텍스트 없이 판단하기 어렵습니다.

### except: pass가 위험한 이유

```python
# AI가 자주 만드는 패턴
def fetch_user(user_id):
    try:
        return db.query(f"SELECT * FROM users WHERE id={user_id}")
    except:
        pass  # 무엇이 실패했는지 알 수 없음
```

이 코드는:
- 데이터베이스 연결 실패도 `None`을 반환합니다
- SQL 인젝션 에러도 `None`을 반환합니다
- 네트워크 타임아웃도 `None`을 반환합니다
- 모든 에러가 같은 결과처럼 보입니다

### 좋은 에러 처리의 구조

```python
# 에러를 의미 있게 처리하는 버전
class UserFetchError(Exception):
    """사용자 조회 실패"""

def fetch_user(user_id: str) -> dict:
    try:
        return db.query("SELECT * FROM users WHERE id = %s", (user_id,))
    except TimeoutError as e:
        raise UserFetchError(f"DB timeout for user {user_id}") from e
    except DatabaseError as e:
        raise UserFetchError(f"DB error for user {user_id}") from e
```

이제 어떤 종류의 에러인지, 어떤 user_id에서 발생했는지 알 수 있습니다. `from e`는 원인 에러를 보존합니다.

### Fail Fast: 입력을 초반에 검증

```python
# 나쁜 패턴 - 나중에 실패
def transfer_money(amount, from_account, to_account):
    # 복잡한 로직 실행...
    # 100줄 뒤에 금액이 음수인 것을 발견

# 좋은 패턴 - 초반에 실패
def transfer_money(amount: int, from_account: str, to_account: str):
    if amount <= 0:
        raise ValueError(f"amount must be positive, got {amount}")
    if not from_account or not to_account:
        raise ValueError("accounts cannot be empty")
    # 이제 정상 로직 실행
```

입력이 잘못됐다면 최대한 빨리 알려야 합니다. 나중에 발견할수록 원인을 찾기 어렵습니다.

## Before / After

```python
# AI가 생성한 코드
def fetch_order_data(url):
    try:
        ...
    except Exception:
        return None  # 모든 에러를 삼킴
```

```python
# 에러를 의미 있게 처리하는 버전
class OrderFetchError(Exception):
    """주문 데이터 조회 실패"""

def fetch_order_data(url: str) -> dict:
    try:
        return _http_get(url)
    except TimeoutError as e:
        raise OrderFetchError(f"timeout fetching order from {url}") from e
    except ConnectionError as e:
        raise OrderFetchError(f"connection failed: {url}") from e
```

에러가 발생하면 무엇이, 어디서 실패했는지 로그에 남습니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `except: pass` 또는 빈 except 블록 | 모든 에러 정보가 사라짐 | 최소한 로그는 남기고, 의미 있는 에러 타입으로 변환 |
| `except Exception`을 전체에서 사용 | 디버깅이 거의 불가능 | 넓은 except는 가장 바깥 경계에서만 |
| 멱등하지 않은 작업에 재시도 | 중복 결제, 중복 발송 발생 | 재시도는 네트워크 타임아웃처럼 안전한 경우에만 |
| 에러를 로그만 찍고 계속 진행 | 나쁜 상태가 누적됨 | 복구 불가능한 에러는 즉시 중단 |
| 입력 검증을 함수 중간에서 | 원인 찾기 어려움 | 함수 시작 부분에서 가드 절로 처리 |

## AI에게 클린 코드 요청하는 팁

```
프롬프트 예시:
"결제 처리 함수를 구현해줘.
에러 처리 규칙:
- except: pass나 빈 except 블록 금지
- 각 에러 타입에 맞는 도메인 예외 클래스 정의
- 원인 에러는 'from e'로 보존
- 입력 검증은 함수 시작 부분에서 처리
- 재시도는 네트워크 타임아웃에만, 결제 로직에는 절대 붙이지 말 것"
```

## 운영 체크리스트
- [ ] `except: pass`가 없는가?
- [ ] 입력 검증이 함수 상단에 있는가?
- [ ] 도메인 예외 타입이 정의되어 있는가?
- [ ] `from e`로 원인 에러를 보존했는가?
- [ ] 재시도가 멱등한 작업에만 적용되는가?

## 처음 질문으로 돌아가기

- **`except: pass`가 왜 위험한가요?**
  에러를 숨겨서 프로그램이 나쁜 상태로 계속 실행됩니다. 어떤 에러가 얼마나 발생했는지 알 수 없어 디버깅과 운영 대응이 불가능해집니다.

- **예외를 던질지 값으로 반환할지 어떻게 결정하나요?**
  호출자가 즉시 복구하기 어려운 상황이면 예외를, 파싱이나 검증처럼 실패가 예상 가능하고 호출자가 처리해야 하는 경우엔 `Result` 패턴으로 값을 반환합니다.

- **재시도 로직을 잘못 붙이면?**
  결제처럼 멱등하지 않은 작업에 재시도를 붙이면 같은 결제가 여러 번 발생합니다. 재시도는 네트워크 타임아웃처럼 다시 실행해도 안전한 경우에만 적용합니다.

## 정리

AI가 만드는 `except: pass`와 광범위한 `except Exception`은 겉으로는 안전해 보이지만 실제로는 에러를 숨기는 코드입니다. 좋은 에러 처리는 에러를 막는 것이 아니라 어디서 어떤 에러가 왜 발생했는지를 명확히 드러내는 것입니다. 입력을 초반에 검증하고, 에러 타입을 의미 있게 정의하고, 원인을 보존하는 습관이 운영 중 장애 대응 시간을 크게 줄여줍니다. 다음 글에서는 AI가 만든 주석이 코드와 맞지 않는 문제를 다룹니다.

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
- **바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다 (현재 글)**
- [바이브코딩을 위한 클린 코드 (7/10): AI가 주석을 잔뜩 넣었는데 코드와 안 맞다](./07-comments.md)
- [바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다](./08-testable-code.md)
- [바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법](./09-refactoring.md)
- [바이브코딩을 위한 클린 코드 (10/10): AI 코드를 리뷰하는 방법](./10-code-review.md)
<!-- toc:end -->
Tags: 바이브코딩, CleanCode, AI코딩, 에러처리, Exceptions, 안정성
