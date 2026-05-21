---
series: clean-code-101
episode: 3
title: "Clean Code 101 (3/10): 함수 작게 만들기"
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
  - Functions
  - SRP
  - Refactoring
  - Readability
seo_description: 함수가 한 가지 일만 하도록 작게 쪼개는 원칙과 추출 방법을 배웁니다. 가독성을 높이고 테스트와 재사용이 쉬운 코드를 만드는 기법을 익힙니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (3/10): 함수 작게 만들기

긴 함수는 처음에는 편하지만 시간이 갈수록 설명과 예외 처리가 한데 뭉치면서 읽기 어려워집니다.

이 글은 Clean Code 101 시리즈의 3번째 글입니다.

여기서는 함수가 충분히 작다는 말이 실제로 무엇을 뜻하는지, 그리고 큰 함수를 어떻게 안전하게 쪼갤 수 있는지 살펴보겠습니다.

## 먼저 던지는 질문

- 작은 함수가 주는 효과는 무엇일까요?
- Extract Function은 어떤 순서로 적용해야 안전할까요?
- 부수 효과를 줄이는 대표 패턴은 무엇일까요?

## 큰 그림

![Clean Code 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/03/03-01-concept-at-a-glance.ko.png)

*Clean Code 101 3장 흐름 개요*

이 그림은 추출(Extract Function)이 이름을 가능하게 하고, 좋은 이름이 다시 재사용과 테스트를 쉽게 만드는 선순환을 보여 줍니다. 함수가 한 가지 일만 할 때 모든 것이 명확해집니다.

> 작은 함수는 설명의 필요성을 줄이고, 테스트 가능성을 높입니다.

## 왜 중요한가

작은 함수의 장점은 단순히 줄 수가 적다는 데 있지 않습니다. 핵심은 “이 함수가 한 가지 일만 한다”는 사실이 이름과 본문에서 동시에 드러난다는 점입니다. 그 상태가 되면 함수 본문은 설명문이 아니라 목차처럼 읽히기 시작합니다.

반대로 큰 함수는 계속 주석을 요구합니다. 그리고 주석이 많아질수록 코드와 설명이 어긋날 가능성도 커집니다. 그래서 작은 함수는 가독성 문제이면서 동시에 유지보수와 테스트 전략의 문제이기도 합니다.

## 한눈에 보는 개념

추출은 이름을 가능하게 만들고, 좋은 이름은 재사용과 테스트를 쉽게 만듭니다.

## 핵심 용어

- **SRP (Single Responsibility)**: 변경 이유가 하나인 상태입니다.
- **Extract Function**: 블록을 별도 함수로 뽑아내는 리팩토링입니다.
- **Command-Query Separation**: 함수는 하거나 답하거나 둘 중 하나만 해야 한다는 원칙입니다.
- **Pure function**: 같은 입력에 같은 출력을 내고, 부수 효과가 없는 함수입니다.
- **Parameter Object**: 여러 인자를 하나의 객체로 묶는 방식입니다.

## 전/후 비교

**Before**

```python
def checkout(cart, user, addr, coupon):
    # 60 lines: validate + price + tax + ship + log + email + save
    ...
```

**After**

```python
def checkout(cart, user, addr, coupon):
    items = validate_cart(cart, user)
    total = price_with_tax(items, addr)
    order = save_order(user, items, total, coupon)
    notify_user(user, order)
    return order
```

두 번째 버전의 본문은 구현 세부보다 흐름을 먼저 보여 줍니다. 좋은 함수 본문은 설명문이 아니라 목차처럼 읽혀야 합니다.

## 실전 적용: 안전하게 추출하기

### 단계 1 — Partial extraction

```python
# 1_extract.py
def total(items):
    s = 0
    for it in items:
        s += it.price * it.qty
    return s
```

반복문은 추출 후보가 되기 좋습니다. 계산이 하나의 의미 단위로 보이기 시작하면 별도 함수 이름을 붙일 수 있습니다.

### 단계 2 — Intent name

```python
# 2_intent.py
def line_total(item): return item.price * item.qty
def total(items): return sum(line_total(it) for it in items)
```

이름을 붙이는 순간 코드 길이는 비슷해도 이해 비용은 줄어듭니다. 좋은 추출은 줄 수보다 의미를 더 잘 드러내는 데 있습니다.

### 단계 3 — Command/Query split

```python
# 3_cqs.py
class Account:
    def withdraw(self, amount):  # command
        self.balance -= amount
    def is_overdrawn(self):      # query
        return self.balance < 0
```

질문하는 함수는 상태를 바꾸지 않는 편이 좋습니다. 읽는 쪽에서 예상 가능한 동작이 디버깅 시간을 줄입니다.

### 단계 4 — Parameter object

```python
# 4_param_obj.py
from dataclasses import dataclass
@dataclass
class Range: lo: int; hi: int
def in_range(value, r: Range): return r.lo <= value <= r.hi
```

인자가 많아질수록 호출 지점의 소음도 커집니다. 묶을 수 있는 인자는 객체로 올려서 문맥을 보존하는 편이 낫습니다.

### 단계 5 — Make it pure

```python
# 5_pure.py
def discount(price: int, rate: float) -> int:
    return int(price * (1 - rate))
```

순수 함수는 테스트가 가장 쉽습니다. 작은 함수와 순수 함수는 함께 갈수록 효과가 커집니다.

## 검증 방법

```bash
radon cc app/ -a -s
python -m pytest -q tests/test_checkout.py
```

**기대 결과**

- 추출 전후 복잡도와 테스트 안정성이 함께 비교됩니다.
- 함수 본문이 목차처럼 읽히는지 바로 확인할 수 있습니다.

## 실패하기 쉬운 지점

- 추출 뒤 인자 수가 급격히 늘어납니다.
- 질문 함수가 여전히 상태를 바꿉니다.

## 이 코드에서 먼저 봐야 할 점

- 함수 본문은 목차처럼 읽혀야 합니다.
- 이름이 주석을 대신해야 합니다.
- Command/Query를 분리하면 버그 추적이 쉬워집니다.

## 자주 하는 실수 5가지

1. **거대 함수를 변수만 늘려서 정리하기.** 새로운 의미 단위가 생기지 않습니다.
2. **추출 뒤 인자가 폭발하기.** 객체로 묶을 시점인지 봐야 합니다.
3. **질문 함수가 상태를 바꾸기.** 버그의 주요 원인입니다.
4. **테스트 없이 추출하기.** 회귀 위험이 커집니다.
5. **과도하게 잘게 쪼개기.** 한 줄 함수가 너무 많아지면 오히려 흐름이 끊깁니다.

## 실무에서는 이렇게 보입니다

좋은 팀은 함수 길이, 인자 수, 복잡도를 lint와 PR 가이드로 함께 관리합니다. 큰 함수는 자동으로 경고를 띄우고, 리뷰에서는 “한 가지 일만 하는가”를 별도의 질문으로 다룹니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 함수 본문이 목차처럼 읽혀야 합니다.
- 이름이 주석을 대신해야 합니다.
- Query는 상태를 바꾸면 안 됩니다.
- 인자가 셋을 넘으면 냄새일 수 있습니다.
- 순수 함수는 테스트의 가장 좋은 친구입니다.

## 체크리스트

- [ ] 함수가 정확히 한 가지 일만 하는가?
- [ ] 본문이 목차처럼 읽히는가?
- [ ] 인자가 3개 이하인가?
- [ ] Query가 부수 효과를 만들지 않는가?
- [ ] 추출 전후를 지키는 테스트가 있는가?

## 연습 문제

1. 함수 본문이 목차처럼 읽히도록 하나를 다시 써 보세요.
2. 인자가 4개 이상인 함수를 객체 하나로 묶어 보세요.
3. CQS를 어기는 함수 하나를 찾아 고쳐 보세요.

## 정리 및 다음 단계

작은 함수는 좋은 이름과 테스트를 가능하게 만듭니다. 다음 글에서는 큰 함수를 키우는 가장 흔한 원인인 조건문을 어떻게 단순화할지 다룹니다.


## 함수 분리 원칙: 어디까지 쪼개야 충분한가

함수 분리는 "짧게 만들기" 자체가 목적이 아닙니다. 핵심은 변경 이유를 분리하는 것입니다. 아래 표는 함수를 분리할지 판단할 때 사용하는 기준입니다.

| 기준 | 분리 신호 | 유지 가능 신호 | 권장 액션 |
| --- | --- | --- | --- |
| 변경 이유 | 서로 다른 정책이 함께 존재 | 한 정책만 수행 | 정책 단위 추출 |
| 입력/출력 | 인자 의미가 섞여 있음 | 인자 의미가 단일 | Parameter Object 검토 |
| 부수 효과 | 저장/로그/알림이 섞임 | 계산만 수행 | IO 경계 분리 |
| 테스트 난이도 | 테스트 준비가 과도함 | 입력-출력 검증이 단순 | 순수 로직 먼저 추출 |
| 네이밍 | 함수명에 and가 들어감 | 동사 하나로 설명 가능 | 두 함수로 분해 |

분리 원칙은 코드 길이보다 책임 경계에 집중합니다. 30줄이어도 한 책임이면 유지할 수 있고, 10줄이어도 책임이 둘이면 분해하는 편이 낫습니다.

## 리팩토링 전후 Python 예시

```python
# before

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
# after

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

후자에서는 계산 규칙과 외부 부수 효과가 분리되어 테스트 전략이 즉시 달라집니다. `calculate_subtotal`, `apply_membership_discount`, `apply_coupon`은 빠른 단위 테스트 대상으로 떨어지고, `checkout`은 통합 경계를 검증하는 테스트로 좁힐 수 있습니다.

## 함수 분해 체크 시나리오

```python
from dataclasses import dataclass

@dataclass
class FunctionSplitDecision:
    has_multiple_policies: bool
    has_side_effects: bool
    argument_count: int


def should_split_function(decision: FunctionSplitDecision) -> bool:
    if decision.has_multiple_policies:
        return True
    if decision.has_side_effects:
        return True
    return decision.argument_count >= 4
```

이런 식의 단순한 규칙만 있어도 리뷰 기준이 선명해집니다. "왜 나누는가"를 설명할 때 감정이 아니라 기준으로 대화할 수 있기 때문입니다.


## 실무 적용 메모

아래 메모는 팀 내 합의 문서에 그대로 옮겨 적어도 되는 수준의 운영 규칙입니다.

1. 리뷰는 코드 스타일보다 변경 위험을 먼저 다룹니다.
2. 규칙 위반은 사람 지적보다 자동화 전환을 우선합니다.
3. 반복되는 설계 결함은 교육 과제가 아니라 구조 개선 과제로 등록합니다.
4. 모든 개선은 테스트와 함께 진행하며, 동작 변경 여부를 PR 설명에 명시합니다.
5. 다음 분기 목표에는 "새 기능 수"와 함께 "변경 비용 감소 지표"를 반드시 포함합니다.

```python
from dataclasses import dataclass

@dataclass
class QualityGate:
    has_tests: bool
    has_clear_names: bool
    has_boundary_error_handling: bool
    has_small_functions: bool
    has_review_notes: bool


def evaluate_gate(gate: QualityGate) -> tuple[bool, list[str]]:
    missing = []
    if not gate.has_tests:
        missing.append("tests")
    if not gate.has_clear_names:
        missing.append("naming")
    if not gate.has_boundary_error_handling:
        missing.append("error-boundary")
    if not gate.has_small_functions:
        missing.append("function-size")
    if not gate.has_review_notes:
        missing.append("review-notes")
    return len(missing) == 0, missing
```

이 체크 함수는 단순하지만, 품질 기준을 코드로 표현하는 출발점이 됩니다. 팀이 기준을 말로만 합의하면 시간이 지나며 흐려집니다. 반대로 코드와 템플릿과 자동화 규칙으로 남기면 신규 멤버가 들어와도 동일한 기준이 유지됩니다.

또한 개선 활동은 단발성 이벤트가 아니라 루프여야 합니다. 한 번의 대청소보다 매 PR마다 작은 개선을 추가하는 편이 장기적으로 더 강합니다. 이름 하나, 함수 하나, 분기 하나를 매번 더 낫게 만드는 습관이 쌓이면 코드베이스의 평균 품질이 올라가고, 장애 대응 속도도 실제로 빨라집니다.


## 함수 추출 기준: 분리 시점 판단표

함수를 작게 만드는 일은 길이를 줄이는 작업이 아니라 책임 경계를 분명히 하는 작업입니다. 아래 기준표는 추출 시점을 빠르게 결정하는 데 도움을 줍니다.

| 신호 | 현재 상태 | 분리 기준 | 분리 후 기대 효과 |
| --- | --- | --- | --- |
| 이름 붙이기 어려움 | 본문이 여러 역할 혼합 | 문장으로 요약 가능한 덩어리 단위 추출 | 호출 흐름 가독성 향상 |
| 테스트 케이스 폭증 | 한 함수에서 조합 분기 과다 | 순수 계산과 I/O 분리 | 테스트 수 감소 |
| 파라미터 과다 | 5개 이상 인자 반복 전달 | 파라미터 객체 도입 | 호출부 단순화 |
| 재사용 애매함 | 유사 코드 복붙 증가 | 공통 의도 함수 추출 | 중복 감소 |

## 함수 분해 데모: 단일 책임으로 나누기

```python
# before
def checkout(order, payment_gateway, inventory, notifier):
    if not order["items"]:
        raise ValueError("empty_order")
    total = 0
    for item in order["items"]:
        total += item["unit_price_cents"] * item["quantity"]
    payment_gateway.charge(order["user_id"], total)
    inventory.reserve(order["items"])
    notifier.send(order["user_id"], "checkout-complete")
    return {"total": total}


# after
def checkout(order, payment_gateway, inventory, notifier):
    validate_order(order)
    total_cents = calculate_order_total(order["items"])
    charge_payment(order["user_id"], total_cents, payment_gateway)
    reserve_items(order["items"], inventory)
    send_checkout_notification(order["user_id"], notifier)
    return {"total": total_cents}
```

이 분해는 각 단계를 별도 테스트로 검증 가능하게 만들고, 실패 지점을 로그와 메트릭에서 더 명확히 식별하게 해 줍니다.

## SOLID 연결: 단일 책임과 의존 역전을 함수 수준에서 적용

- SRP 관점에서 함수는 "변경 이유"가 하나여야 합니다. 결제 정책 변경과 알림 채널 변경이 같은 함수를 수정하게 만들면 SRP 위반입니다.
- DIP 관점에서는 외부 의존을 인터페이스로 주입해야 테스트 더블 교체가 쉽습니다.

```python
from typing import Protocol

class PaymentGateway(Protocol):
    def charge(self, user_id: str, amount_cents: int) -> None: ...


def charge_payment(user_id: str, amount_cents: int, gateway: PaymentGateway) -> None:
    gateway.charge(user_id, amount_cents)
```

## 린터/정적분석 구성 예시

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "C90"]

[tool.ruff.lint.mccabe]
max-complexity = 8
```

복잡도 임계치를 낮추면 큰 함수가 자동으로 경고 대상이 됩니다. 작은 함수 문화는 교육보다 도구 설정에서 먼저 시작되는 경우가 많습니다.


## 심화 실습: 함수 추출 워크숍

함수 분해는 규칙 암기가 아니라 반복 훈련이 필요합니다. 아래 워크숍은 한 화면에서 끝나는 실습 흐름입니다.

1. 기존 함수의 입력/출력/부수효과를 색으로 표시합니다.
2. 색이 다른 덩어리를 함수 후보로 뽑습니다.
3. 후보마다 이름을 붙여 문장으로 읽어 봅니다.
4. 테스트를 먼저 고정하고 한 덩어리씩 추출합니다.

```python
def place_order(payload, repo, payment, notifier):
    validated = validate_payload(payload)
    amount_cents = calculate_amount(validated["line_items"])
    payment_result = payment.charge(validated["user_id"], amount_cents)
    order = persist_order(repo, validated, payment_result)
    notifier.send_order_created(order["id"])
    return order
```

위 구조처럼 한 줄이 한 책임을 나타내면 리뷰어는 흐름을 먼저 확인하고 세부 구현으로 내려갈 수 있습니다. 사고 비용이 크게 줄어듭니다.

## 함수 크기 정책 예시

| 항목 | 권장값 | 경고값 |
| --- | --- | --- |
| 함수 길이 | 5~20줄 | 30줄 이상 |
| 인자 수 | 0~3개 | 5개 이상 |
| 중첩 깊이 | 0~2단 | 3단 이상 |

정책은 절대 규칙이 아니라 경고 기준입니다. 다만 경고가 누적되면 구조를 다시 설계해야 한다는 신호로 받아야 합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.


### 심화 사례: 변경 전파 경로 점검

아래 체크는 변경 전파를 예측하기 위한 최소 루틴입니다.

- 변경 대상 함수의 호출자 수를 먼저 확인합니다.
- 입력/출력 계약이 바뀌는지 여부를 분리합니다.
- 예외 타입과 로그 이벤트 이름의 변경 여부를 기록합니다.
- 테스트 케이스가 입력 경계와 실패 경계를 모두 포함하는지 확인합니다.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| 점수 구간 | 권장 전략 |
| --- | --- |
| 0-5 | 단일 PR로 진행 |
| 6-12 | 리팩토링 PR과 기능 PR 분리 |
| 13+ | 단계별 배포와 롤백 계획 포함 |

점수를 수치로 남기면 리뷰 대화가 감각에서 근거 중심으로 이동합니다.

## 처음 질문으로 돌아가기

- **작은 함수가 주는 효과는 무엇일까요?**
  - 본문의 기준은 함수 작게 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Extract Function은 어떤 순서로 적용해야 안전할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **부수 효과를 줄이는 대표 패턴은 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- **함수 작게 만들기 (현재 글)**
- 조건문 줄이기 (예정)
- 중복 제거 (예정)
- 오류 처리 (예정)
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Clean Code (Ch. 3 Functions)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Refactoring — Extract Function](https://refactoring.com/catalog/extractFunction.html)
- [Martin Fowler — Command Query Separation](https://martinfowler.com/bliki/CommandQuerySeparation.html)
- [Refactoring — Introduce Parameter Object](https://refactoring.com/catalog/introduceParameterObject.html)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, Functions, SRP, Refactoring, Readability
