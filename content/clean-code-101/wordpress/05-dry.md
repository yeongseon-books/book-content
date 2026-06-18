---
title: "바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다"
series: clean-code-101
episode: 5
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
- DRY
- 중복제거
- 리팩토링
seo_description: "바이브코딩 시대, AI가 같은 코드를 여러 곳에 복사한 경우를 DRY 원칙으로 안전하게 정리하는 방법과 주의할 점을 설명합니다."
---

# 바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다

이 글은 바이브코딩을 위한 클린 코드 시리즈의 5번째 글입니다.

API 서버를 AI로 만들다 보니 세금 계산 로직이 세 곳에 있었습니다. 주문 생성 API에도, 견적 계산 API에도, 환불 계산 API에도 `amount * 0.1`이라는 코드가 각각 들어 있었습니다. AI는 각 엔드포인트를 독립적으로 구현하면서 같은 로직을 복사한 것입니다.

어느 날 세율이 10%에서 12%로 바뀌었습니다. 그래서 코드를 검색해서 고쳤는데, 환불 계산 API의 것을 하나 놓쳤습니다. 주문은 12%로 계산되는데 환불은 10%로 계산되는 버그가 생겼습니다. 코드 리뷰에서도 잡히지 않았습니다. 배포 후 며칠이 지나 고객 민원으로 발견됐습니다.

이것이 중복의 진짜 위험입니다. 중복은 "코드가 길어진다"는 미학적 문제가 아닙니다. 한 곳을 고치고 다른 곳을 놓치는 순간, 시스템에 서로 다른 진실이 생깁니다.

AI는 각 요청을 독립적으로 처리하기 때문에 이전 대화에서 만든 코드를 재사용하기보다 비슷한 코드를 다시 만드는 경향이 있습니다. 특히 여러 번의 대화를 통해 코드를 만들면 중복이 자연스럽게 쌓입니다.

> DRY(Don't Repeat Yourself)는 코드 줄 수를 줄이라는 것이 아닙니다. 같은 규칙의 출처를 하나로 유지하라는 원칙입니다.

---

## 이 글에서 다룰 문제
- AI가 만든 중복 코드를 어떻게 안전하게 통합할 수 있나요?
- 겉모양이 비슷한 중복과 실제 중복을 어떻게 구분하나요?
- 잘못된 추상화를 만들면 중복보다 더 나빠질 수 있다는 것은 무슨 뜻인가요?
- 데이터 중복이 코드 중복보다 더 위험한 이유는 무엇인가요?
- AI에게 중복을 피하도록 요청하는 방법은 무엇인가요?

---

## AI가 중복을 만드는 이유

AI는 각 대화를 독립적으로 처리합니다. "주문 API를 만들어줘"에서 세금 계산을 만들고, "환불 API를 만들어줘"에서 다시 세금 계산을 만듭니다. 이전에 만든 `calculate_tax` 함수를 참조하지 않습니다. 이것은 AI의 맥락 한계이기도 하지만, 요청이 각각 독립적이라면 자연스럽게 발생하는 패턴이기도 합니다.

### 진짜 중복 vs 우연한 유사성

중요한 것은 겉모양이 같다고 모두 합쳐야 한다는 것이 아닙니다.

```python
# 이 두 함수는 겉보기에 같지만 합치면 안 됩니다
def order_tax(amount_cents: int) -> int:
    return int(amount_cents * 0.1)

def salary_tax(income_cents: int) -> int:
    return int(income_cents * 0.1)
```

세율이 같아도 소비세와 소득세는 다른 정책입니다. 하나의 세율이 바뀌어도 다른 하나는 바뀌지 않을 수 있습니다. 이런 "우연한 유사성"을 억지로 합치면 나중에 하나를 바꿀 때 다른 하나도 영향을 받는 잘못된 결합이 생깁니다.

```python
# 이건 합쳐도 됩니다 - 같은 이유로 바뀌는 중복
def order_vat(amount_cents: int) -> int:
    return int(amount_cents * 0.1)

def refund_vat(amount_cents: int) -> int:
    return int(amount_cents * 0.1)

# 통합 후
VAT_RATE = 0.1

def calculate_vat(amount_cents: int) -> int:
    return int(amount_cents * VAT_RATE)
```

### 데이터 중복

코드 중복보다 더 위험한 것이 데이터 중복입니다.

```python
# AI가 자주 만드는 패턴 - 같은 정책이 여러 곳에
def get_free_plan_limit():
    return 100

def check_free_plan(usage):
    return usage < 100  # 100이 또 있음

def show_upgrade_prompt(usage):
    if usage >= 100:  # 여기도 100
        ...
```

```python
# 데이터를 단일 출처로 관리
PLAN_LIMITS = {
    "free": 100,
    "pro": 1000,
    "team": 10000,
}

def get_plan_limit(plan: str) -> int:
    return PLAN_LIMITS[plan]

def is_over_limit(plan: str, usage: int) -> bool:
    return usage >= PLAN_LIMITS[plan]
```

`PLAN_LIMITS`라는 단일 출처를 만들면 100을 바꿀 때 한 곳만 수정하면 됩니다.

## Before / After

```python
# AI가 생성한 코드 - 세 곳에 중복
# orders.py
def calculate_order_total(items):
    subtotal = sum(item.price * item.qty for item in items)
    return subtotal + int(subtotal * 0.1)  # 세금 10%

# refunds.py
def calculate_refund_amount(items):
    subtotal = sum(item.price * item.qty for item in items)
    return subtotal + int(subtotal * 0.1)  # 세금 10%

# quotes.py
def calculate_quote_total(items):
    subtotal = sum(item.price * item.qty for item in items)
    return subtotal + int(subtotal * 0.1)  # 세금 10%
```

```python
# 중복을 제거한 버전
# pricing.py
TAX_RATE = 0.1

def calculate_subtotal(items) -> int:
    return sum(item.price * item.qty for item in items)

def apply_tax(amount_cents: int, rate: float = TAX_RATE) -> int:
    return amount_cents + int(amount_cents * rate)

def calculate_total(items) -> int:
    return apply_tax(calculate_subtotal(items))

# orders.py, refunds.py, quotes.py 에서 calculate_total 사용
```

세율이 바뀌면 `TAX_RATE` 하나만 수정합니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 첫 번째 중복에서 바로 추상화 | 우연한 유사성일 수 있음 | 세 번 반복된 후에 통합 고려 |
| 겉모양만 보고 합치기 | 변경 이유가 다른 코드가 묶임 | 같은 이유로 바뀌는지 먼저 확인 |
| 공통 함수에 인자 6개 이상 | 실패한 추상화 신호 | 두 개의 단순한 함수로 분리 |
| 데이터 중복 무시 | 코드 중복보다 더 오래 숨음 | 상수와 정책을 단일 테이블로 관리 |
| 테스트 없이 통합 | 회귀 위험 | 통합 전 테스트 먼저 고정 |

## AI에게 클린 코드 요청하는 팁

```
프롬프트 예시:
"주문, 환불, 견적 API를 각각 구현해줘.
중복 방지 규칙:
- 세금, 할인, 수수료 같은 정책 상수는 한 파일에 모아서 관리
- 같은 계산 로직이 반복되면 공통 함수로 추출할 것
- 공통 함수의 인자는 5개를 넘지 않도록
- 각 API는 공통 모듈을 import해서 사용"
```

## 운영 체크리스트
- [ ] 이 중복은 같은 이유로 바뀌는 중복인가?
- [ ] 달라지는 부분이 명확한가?
- [ ] 공통 함수의 인자가 과하지 않은가?
- [ ] 정책 상수가 단일 출처로 관리되는가?
- [ ] 통합 후 호출 지점이 더 단순해졌는가?

## 처음 질문으로 돌아가기

- **겉모양이 비슷한 중복과 실제 중복을 어떻게 구분하나요?**
  같은 이유로 바뀌는지 물어보면 됩니다. 소비세와 소득세는 같은 비율이어도 독립적으로 변경됩니다. 주문 세금과 환불 세금은 항상 같이 바뀝니다.

- **잘못된 추상화가 중복보다 더 나쁠 수 있나요?**
  공통 함수 인자가 6개가 넘고, 호출하는 쪽이 대부분 더미 값을 넘기기 시작하면 잘못된 추상화입니다. 이 경우 다시 두 개의 단순한 함수로 나누는 것이 낫습니다.

- **데이터 중복이 코드 중복보다 위험한 이유는?**
  코드 중복은 IDE가 찾아주지만, 숫자 100이 여러 곳에 흩어져 있으면 정적 분석 도구가 잡기 어렵습니다. `PLAN_LIMITS` 같은 테이블로 단일 출처를 만들어야 합니다.

## 정리

AI는 각 요청을 독립적으로 처리하기 때문에 같은 로직이 여러 곳에 복사되는 것은 자연스러운 현상입니다. 중복을 발견했을 때 먼저 확인해야 할 것은 "같은 이유로 바뀌는가"입니다. 그렇다면 통합하고, 아니라면 우연한 유사성으로 남겨둬야 합니다. 특히 정책 상수가 여러 곳에 흩어지지 않도록 단일 테이블로 관리하는 습관이 중요합니다. 다음 글에서는 AI가 에러 처리를 어떻게 망치는지 다룹니다.

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
- **바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다 (현재 글)**
- [바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다](./06-error-handling.md)
- [바이브코딩을 위한 클린 코드 (7/10): AI가 주석을 잔뜩 넣었는데 코드와 안 맞다](./07-comments.md)
- [바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다](./08-testable-code.md)
- [바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법](./09-refactoring.md)
- [바이브코딩을 위한 클린 코드 (10/10): AI 코드를 리뷰하는 방법](./10-code-review.md)
<!-- toc:end -->
Tags: 바이브코딩, CleanCode, AI코딩, DRY, 중복제거, 리팩토링
