---
title: "바이브코딩을 위한 클린 코드 (4/10): AI가 중첩 if를 5단계로 만들었다"
series: clean-code-101
episode: 4
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
- 조건문단순화
- GuardClause
- 리팩토링
seo_description: "바이브코딩 시대, AI가 생성한 5단계 중첩 if문을 가드 절과 전략 패턴으로 평탄화하는 실용적인 방법을 설명합니다."
---

# 바이브코딩을 위한 클린 코드 (4/10): AI가 중첩 if를 5단계로 만들었다

이 글은 바이브코딩을 위한 클린 코드 시리즈의 4번째 글입니다.

환불 승인 로직을 AI에게 맡겼더니 이런 코드가 나왔습니다.

```python
def approve_refund(user, order, amount):
    if user is not None:
        if user.is_active:
            if order is not None:
                if order.is_paid:
                    if amount > 0:
                        return amount <= order.total_amount
    return False
```

동작합니다. 하지만 이 코드를 처음 읽는 사람은 피라미드를 만날 준비가 되어 있어야 합니다. 실제 정책인 마지막 줄 `return amount <= order.total_amount`에 도달하기 위해 들여쓰기를 4단 내려가야 합니다. 만약 "로그인하지 않은 사용자가 환불 요청하면 특정 메시지를 반환해야 한다"는 요구사항이 추가된다면 어디를 수정해야 할지 즉시 보이지 않습니다.

AI는 조건을 순서대로 쌓아가는 방식으로 if 체인을 만듭니다. "A이면 B를 확인하고, B이면 C를 확인하고..." 라는 흐름이 그대로 들여쓰기로 표현됩니다. 작은 기능에서는 문제가 없지만, 조건이 3개를 넘기 시작하면 읽는 비용이 급격히 올라갑니다.

조건문 단순화의 핵심은 분기 깊이를 줄이는 것이 아니라 분기 책임을 적절한 위치로 옮기는 것입니다. 예외 케이스를 초반에 걷어내면 정상 흐름이 선명하게 드러납니다.

> 깊은 if 체인은 조건이 많다는 신호가 아니라 예외 케이스와 정상 흐름이 뒤섞였다는 신호입니다.

---

## 이 글에서 다룰 문제
- 가드 절(Guard Clause)로 중첩 if를 어떻게 평탄화할 수 있나요?
- 정책이 자주 바뀌는 분기는 어떻게 구조화해야 할까요?
- 부정형 조건이 왜 읽기 어려운가요?
- AI에게 if 중첩을 피하도록 요청하는 방법은 무엇인가요?
- 분기를 데이터 구조로 옮기면 무엇이 달라지나요?

---

## AI가 중첩 if를 만드는 이유

AI는 각 조건을 중첩해서 확인하는 "방어적 프로그래밍" 패턴을 선호하는 경향이 있습니다. 각 단계에서 null 확인을 하고 들어가는 방식입니다. 작은 예제에서는 이 방식이 명확해 보이기 때문에 AI 학습 데이터에도 많이 포함되어 있을 것입니다.

하지만 실제 코드에서 조건이 4~5단계가 되면 읽는 사람이 "어느 조건이 충족됐을 때 실제 로직이 실행되는가"를 파악하는 데만 상당한 인지 비용이 들어갑니다.

### 가드 절로 평탄화

예외 케이스를 함수 초반에 처리하고 일찍 반환하는 방식입니다.

```python
# AI가 생성한 중첩 패턴
def approve_refund(user, order, amount):
    if user is not None:
        if user.is_active:
            if order is not None:
                if order.is_paid:
                    if amount > 0:
                        return amount <= order.total_amount
    return False

# 가드 절 적용
def approve_refund(user, order, amount):
    if user is None or not user.is_active:
        return False
    if order is None or not order.is_paid:
        return False
    if amount <= 0:
        return False
    return amount <= order.total_amount
```

정상 흐름인 마지막 줄이 이제 선명하게 보입니다. 각 예외 케이스도 독립적으로 확인할 수 있습니다.

### 정책을 데이터 구조로

같은 패턴의 조건이 반복될 때는 데이터로 표현할 수 있습니다.

```python
# AI가 자주 만드는 패턴 - if/elif 체인
def shipping_fee(country, amount_cents):
    if country == "KR":
        if amount_cents >= 50000:
            return 0
        return 3000
    elif country == "JP":
        if amount_cents >= 80000:
            return 0
        return 5000
    elif country == "US":
        if amount_cents >= 100000:
            return 0
        return 9000
    return 15000

# 정책 테이블로 전환
FREE_SHIPPING_POLICY = {
    "KR": (50000, 3000),
    "JP": (80000, 5000),
    "US": (100000, 9000),
}

def shipping_fee(country, amount_cents):
    threshold, fee = FREE_SHIPPING_POLICY.get(country, (10**12, 15000))
    return 0 if amount_cents >= threshold else fee
```

새 나라를 추가할 때 함수 본문을 건드리지 않고 테이블에 항목만 추가하면 됩니다.

## Before / After

```python
# AI가 생성한 코드
def price(user, item):
    if user is not None:
        if user.is_active:
            if item is not None:
                if item.in_stock:
                    return item.price * (0.9 if user.is_member else 1.0)
                else:
                    return None
            else:
                return None
        else:
            return None
    else:
        return None
```

```python
# 가드 절 적용 버전
def price(user, item):
    if user is None or not user.is_active:
        return None
    if item is None or not item.in_stock:
        return None
    discount_rate = 0.9 if user.is_member else 1.0
    return item.price * discount_rate
```

들여쓰기 깊이가 4에서 1로 줄었습니다. 같은 정책인데 읽기 피로도가 완전히 다릅니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 중첩 if를 그대로 유지 | 각 조건의 의미를 파악하기 어려움 | 가드 절로 예외 케이스 분리 |
| 이중 부정 조건 사용 | `if not is_not_empty(x)` 읽기 고통 | 긍정형 함수로 전환 |
| elif 체인에 새 정책 계속 추가 | 기존 코드를 건드려야 함 | 정책 테이블 또는 전략 패턴 |
| 같은 조건이 여러 파일에 중복 | 정책 불일치 위험 | 판정 함수 추출 후 공유 |
| 타입마다 isinstance 분기 | 코드 전체에 분기가 퍼짐 | 다형성으로 대체 |

## AI에게 클린 코드 요청하는 팁

```
프롬프트 예시:
"환불 승인 로직을 구현해줘.
조건문 규칙:
- 예외 케이스(null, 비활성 등)는 함수 초반에 가드 절로 처리할 것
- 들여쓰기는 최대 2단으로 제한
- 같은 패턴의 정책이 반복되면 딕셔너리나 테이블로 표현할 것
- elif 체인이 4개 이상이면 다른 방식을 먼저 고려할 것"
```

## 운영 체크리스트
- [ ] 함수 깊이가 3 이하인가?
- [ ] 가드 절이 함수 상단에 배치되어 있는가?
- [ ] 부정형 조건을 긍정형으로 바꿀 수 있는가?
- [ ] 같은 패턴의 정책을 테이블로 표현할 수 있는가?
- [ ] elif가 4개 이상이면 전략 패턴을 고려했는가?

## 처음 질문으로 돌아가기

- **가드 절로 중첩 if를 어떻게 평탄화하나요?**
  예외 케이스를 함수 초반에 조기 반환으로 처리하면 정상 흐름이 함수 끝에 남습니다. 중첩 구조가 평탄해집니다.

- **정책이 자주 바뀌는 분기는 어떻게 구조화해야 할까요?**
  `FREE_SHIPPING_POLICY` 같은 딕셔너리나 전략 객체로 정책을 분리하면 새 정책을 추가할 때 기존 함수 본문을 건드리지 않아도 됩니다.

- **부정형 조건이 왜 읽기 어렵나요?**
  `if not is_not_empty(x)` 같은 표현은 독자가 조건을 머릿속에서 두 번 뒤집어야 합니다. 이중 부정은 항상 더 나쁜 이름이나 구조의 신호입니다.

## 정리

AI가 만든 중첩 if는 동작하지만 읽기 비용이 숨어 있습니다. 가드 절로 예외 케이스를 초반에 걷어내면 정상 흐름이 명확해집니다. 정책이 자주 바뀌는 영역은 테이블이나 전략 패턴으로 옮겨야 새 정책 추가 시 기존 코드를 최소한으로 건드릴 수 있습니다. 다음 글에서는 AI가 같은 코드를 3곳에 복사한 경우를 다룹니다.

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
- **바이브코딩을 위한 클린 코드 (4/10): AI가 중첩 if를 5단계로 만들었다 (현재 글)**
- [바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다](./05-dry.md)
- [바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다](./06-error-handling.md)
- [바이브코딩을 위한 클린 코드 (7/10): AI가 주석을 잔뜩 넣었는데 코드와 안 맞다](./07-comments.md)
- [바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다](./08-testable-code.md)
- [바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법](./09-refactoring.md)
- [바이브코딩을 위한 클린 코드 (10/10): AI 코드를 리뷰하는 방법](./10-code-review.md)
<!-- toc:end -->
Tags: 바이브코딩, CleanCode, AI코딩, 조건문단순화, GuardClause, 리팩토링
