---
title: "바이브코딩을 위한 클린 코드 (3/10): AI가 100줄짜리 함수를 만들었다"
series: clean-code-101
episode: 3
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
- 함수쪼개기
- SRP
- 리팩토링
seo_description: "바이브코딩 시대, AI가 생성한 100줄짜리 거대 함수를 작은 함수로 쪼개는 방법과 단일 책임 원칙을 적용하는 실용적인 기법을 설명합니다."
---

# 바이브코딩을 위한 클린 코드 (3/10): AI가 100줄짜리 함수를 만들었다

이 글은 바이브코딩을 위한 클린 코드 시리즈의 3번째 글입니다.

"결제 처리 전체 흐름을 구현해줘"라고 AI에게 요청했더니 `process_payment`라는 함수 하나에 120줄이 들어왔습니다. 입력 검증, 금액 계산, 멤버십 할인 적용, 쿠폰 처리, 결제 게이트웨이 호출, 재고 차감, 이메일 발송, 로깅이 전부 하나의 함수 안에 있었습니다. 동작은 했습니다.

일주일 뒤에 "멤버십 할인 규칙을 바꿔달라"는 요청이 왔습니다. 할인 로직이 어디 있는지 찾는 데 15분이 걸렸습니다. 120줄 중간 어딘가에 변수 하나가 그 역할을 하고 있었고, 건드리면 다른 계산에도 영향이 갈 것 같아 조심스러웠습니다. 결국 AI에게 다시 전체 함수를 새로 만들어달라고 했고, 그 결과가 또 다른 거대 함수였습니다.

AI는 "전체를 한 번에" 요청하면 "전체를 한 함수에" 담으려는 경향이 있습니다. 요청 단위가 함수 크기 단위가 되기 때문입니다. 작은 함수로 나누는 것은 사람이 명시적으로 요청하거나, 받은 코드를 직접 정리해야 합니다.

작은 함수의 장점은 줄 수가 줄어드는 것이 아닙니다. "이 함수가 한 가지 일만 한다"는 사실이 이름과 본문에서 동시에 드러나는 것입니다. 그 상태가 되면 멤버십 할인 규칙을 바꾸려고 할 때 `apply_membership_discount`라는 함수를 찾으면 됩니다.

> 작은 함수는 코드를 짧게 만드는 것이 아니라, 다음에 어디를 바꿔야 하는지 즉시 알 수 있게 만드는 것입니다.

---

## 이 글에서 다룰 문제
- AI가 만든 거대 함수를 어떤 기준으로 쪼개야 할까요?
- 함수를 나눌 때 안전하게 진행하는 순서는 무엇일까요?
- 함수를 너무 작게 쪼개면 어떤 문제가 생길까요?
- 순수 함수와 부수 효과를 분리하면 왜 테스트가 쉬워질까요?
- AI에게 작은 함수를 만들도록 요청하는 방법은 무엇일까요?

---

## AI가 큰 함수를 만드는 이유

AI는 하나의 요청("결제 처리를 구현해줘")을 하나의 답(함수 하나)으로 매핑하는 경향이 있습니다. 요청이 넓으면 함수가 커집니다. 또한 AI는 "이 코드가 나중에 수정될 때 어떤 부분이 독립적으로 바뀔 것인가"를 고려하지 않습니다.

그 결과 검증, 계산, 저장, 알림이 한 함수에 뒤섞입니다.

### 함수 분리의 기준

함수를 분리해야 하는 신호들이 있습니다.

**이름에 "and"가 들어가면 두 함수입니다**
```python
# "validate_and_calculate" → 두 개의 책임
def validate_order_and_calculate_total(order):
    ...

# 분리 후
def validate_order(order):
    ...

def calculate_order_total(order):
    ...
```

**주석 블록이 있으면 함수 후보입니다**
```python
# AI가 자주 만드는 패턴
def checkout(order, user, mailer, repo):
    # 1. 검증
    if not order.items:
        raise ValueError("empty order")

    # 2. 가격 계산
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity

    # 3. 저장
    repo.save(order)

    # 4. 알림
    mailer.send(user.email, f"paid={subtotal}")
```

각 주석 블록이 함수 이름이 됩니다.

## Before / After

```python
# AI가 생성한 코드
def checkout(order, user, mailer, repository):
    if not order.items:
        raise ValueError("empty order")

    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity

    if user.is_member:
        subtotal = int(subtotal * 0.9)

    if order.coupon_code:
        subtotal -= 1000

    repository.save(order.id, subtotal)
    mailer.send(user.email, f"paid={subtotal}")
    return subtotal
```

```python
# 함수를 쪼갠 버전
def calculate_subtotal(items) -> int:
    return sum(item.price * item.quantity for item in items)

def apply_membership_discount(amount: int, is_member: bool) -> int:
    return int(amount * 0.9) if is_member else amount

def apply_coupon(amount: int, coupon_code: str | None) -> int:
    return amount - 1000 if coupon_code else amount

def checkout(order, user, mailer, repository) -> int:
    if not order.items:
        raise ValueError("empty order")

    subtotal = calculate_subtotal(order.items)
    subtotal = apply_membership_discount(subtotal, user.is_member)
    subtotal = apply_coupon(subtotal, order.coupon_code)

    repository.save(order.id, subtotal)
    mailer.send(user.email, f"paid={subtotal}")
    return subtotal
```

`checkout` 함수의 본문이 목차처럼 읽힙니다. 멤버십 할인 규칙을 바꾸려면 `apply_membership_discount`만 찾으면 됩니다. `calculate_subtotal`은 순수 함수가 되어 단위 테스트가 거의 공짜로 됩니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 거대 함수를 변수 정리로 해결 | 새로운 의미 단위가 생기지 않음 | 블록 단위로 함수 추출 |
| 추출 뒤 인자가 5개 이상 증가 | 잘못된 경계라는 신호 | 관련 인자를 객체로 묶기 |
| 순수 계산에 DB 호출 섞기 | 단위 테스트가 불가능 | 계산과 IO를 분리 |
| 한 줄짜리 함수를 너무 많이 만들기 | 흐름을 오히려 끊음 | 의미 단위로만 분리 |
| 테스트 없이 함수 추출 | 회귀 위험이 커짐 | 추출 전 테스트 먼저 고정 |

## AI에게 클린 코드 요청하는 팁

```
프롬프트 예시:
"결제 처리 함수를 구현해줘.
함수 규칙:
- 각 함수는 한 가지 일만 할 것
- 계산 로직(순수 함수)과 DB/이메일 같은 IO는 분리할 것
- 함수 본문이 5줄 이하면 이름을 붙일 가치가 있는지 먼저 검토
- checkout 함수의 본문은 목차처럼 읽혀야 함"
```

## 운영 체크리스트
- [ ] 함수가 정확히 한 가지 일만 하는가?
- [ ] 본문이 목차처럼 읽히는가?
- [ ] 인자가 3개 이하인가?
- [ ] 순수 계산 함수와 IO 함수가 분리되어 있는가?
- [ ] 추출 전후를 보장하는 테스트가 있는가?

## 처음 질문으로 돌아가기

- **AI가 만든 거대 함수를 어떤 기준으로 쪼개야 할까요?**
  주석 블록이 있는 곳, 함수 이름에 "and"가 들어가는 곳, 들여쓰기가 갑자기 깊어지는 곳이 분리 후보입니다.

- **함수를 나눌 때 안전하게 진행하는 순서는?**
  먼저 현재 동작을 테스트로 고정하고, 의미 단위 하나씩 추출하고, 추출 때마다 테스트를 다시 실행합니다.

- **순수 함수와 부수 효과를 분리하면 왜 테스트가 쉬워질까요?**
  `calculate_subtotal(items)` 같은 순수 함수는 데이터베이스나 네트워크 없이 단위 테스트할 수 있습니다. IO가 섞인 함수는 매번 환경을 설정해야 합니다.

## 정리

AI는 요청 단위로 함수를 만들기 때문에 "전체 흐름"을 요청하면 하나의 거대 함수가 나옵니다. 함수를 의미 단위로 나누는 것은 사람이 해야 하는 작업입니다. 작은 함수는 코드를 짧게 만드는 것이 아니라, 다음에 어디를 바꿔야 하는지 바로 알 수 있게 만드는 것입니다. 다음 글에서는 AI가 만든 5단계 중첩 if를 어떻게 평탄화하는지 다룹니다.

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
- **바이브코딩을 위한 클린 코드 (3/10): AI가 100줄짜리 함수를 만들었다 (현재 글)**
- [바이브코딩을 위한 클린 코드 (4/10): AI가 중첩 if를 5단계로 만들었다](./04-conditionals.md)
- [바이브코딩을 위한 클린 코드 (5/10): AI가 같은 코드를 3곳에 복붙했다](./05-dry.md)
- [바이브코딩을 위한 클린 코드 (6/10): AI가 except: pass를 넣었다](./06-error-handling.md)
- [바이브코딩을 위한 클린 코드 (7/10): AI가 주석을 잔뜩 넣었는데 코드와 안 맞다](./07-comments.md)
- [바이브코딩을 위한 클린 코드 (8/10): AI가 만든 코드를 테스트하기 어렵다](./08-testable-code.md)
- [바이브코딩을 위한 클린 코드 (9/10): AI 코드를 리팩터링하는 방법](./09-refactoring.md)
- [바이브코딩을 위한 클린 코드 (10/10): AI 코드를 리뷰하는 방법](./10-code-review.md)
<!-- toc:end -->
Tags: 바이브코딩, CleanCode, AI코딩, 함수쪼개기, SRP, 리팩토링
