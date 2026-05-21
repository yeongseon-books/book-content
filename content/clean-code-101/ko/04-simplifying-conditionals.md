---
series: clean-code-101
episode: 4
title: "Clean Code 101 (4/10): 조건문 줄이기"
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
  - Conditionals
  - GuardClauses
  - Refactoring
  - Readability
seo_description: 가드 절과 조기 반환으로 중첩 조건문을 평평하게 고칩니다. 다형성으로 분기를 분리하고 복잡한 분기를 단순화해 가독성을 높이는 기법을 익힙니다.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (4/10): 조건문 줄이기

조건문은 작은 기능을 빠르게 만들 때는 편하지만, 책임이 섞이기 시작하면 가장 먼저 복잡도를 폭발시키는 지점이 됩니다.

이 글은 Clean Code 101 시리즈의 4번째 글입니다.

여기서는 중첩된 if를 평평하게 만들고, 분기 자체를 다른 구조로 옮기는 방법을 정리하겠습니다.


![Clean Code 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/04/04-01-concept-at-a-glance.ko.png)
*Clean Code 101 4장 흐름 개요*
> 분기 깊이보다 분기 책임을 먼저 나누세요.

## 먼저 던지는 질문

- 가드 절과 조기 반환은 어떤 상황에서 가장 효과적일까요?
- 부정형 조건과 이중 부정은 왜 읽기 어렵게 만들까요?
- if/else 체인은 언제 다형성으로 바꾸는 편이 좋을까요?

## 왜 중요한가

깊은 조건문은 단순히 보기 불편한 수준에서 끝나지 않습니다. 예외 처리, 상태 확인, 타입 분기, 정책 분기가 한 함수 안에 쌓이면 어느 분기가 왜 필요한지 설명하기도 어려워집니다.

실무에서는 권한 처리, 가격 정책, 라우팅 규칙처럼 분기가 많은 영역에서 이런 문제가 자주 보입니다. 이때 핵심은 if를 예쁘게 쓰는 것이 아니라, 분기 책임을 더 적절한 구조로 옮기는 것입니다.

## 한눈에 보는 개념

도구가 늘어날수록 분기 수는 줄고, 흐름은 더 평평해집니다.

## 핵심 용어

- **Guard Clause**: 예외 상황을 함수 초반에 바로 반환하는 방식입니다.
- **Early Return**: 더 깊이 들어가지 않고 빠르게 함수를 종료하는 방식입니다.
- **Polymorphism**: 타입별 동작을 조건문 대신 각 클래스에 나누는 방식입니다.
- **Strategy Pattern**: 알고리즘 선택을 외부에서 주입하는 패턴입니다.
- **Table-driven**: 분기 규칙을 데이터 구조로 표현하는 방식입니다.

## 전/후 비교

**Before**

```python
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

**After**

```python
def price(user, item):
    if user is None or not user.is_active: return None
    if item is None or not item.in_stock: return None
    rate = 0.9 if user.is_member else 1.0
    return item.price * rate
```

깊이가 4에서 1로 줄면, 동일한 정책도 훨씬 덜 피곤하게 읽힙니다. 조건문 정리는 가독성을 가장 빠르게 끌어올리는 방법 중 하나입니다.

## 실전 적용: 분기를 줄이는 다섯 단계

### 단계 1 — Flatten with guard clauses

```python
# 1_guard.py
def total(items):
    if not items:
        return 0
    return sum(it.price for it in items)
```

비정상 입력이나 예외 케이스는 초반에 바로 반환하는 편이 좋습니다. 정상 흐름을 가운데에 남겨 두어야 본문이 읽힙니다.

### 단계 2 — Flip negative conditions

```python
# 2_positive.py
# Before: if not user.is_inactive: ...
# After:
def can_login(user):
    if not user.is_active:
        return False
    return user.email_verified
```

부정형 조건은 생각을 한 번 더 꺾게 만듭니다. 특히 이중 부정은 거의 항상 더 나쁜 이름이나 더 나쁜 구조의 신호입니다.

### 단계 3 — Remove branches with polymorphism

```python
# 3_poly.py
class Shape:
    def area(self): ...
class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14 * self.r * self.r
class Square(Shape):
    def __init__(self, a): self.a = a
    def area(self): return self.a * self.a

def total_area(shapes): return sum(s.area() for s in shapes)
```

타입 분기가 반복되면, 각 타입이 자기 동작을 맡아야 할 때가 많습니다.

### 단계 4 — Strategy pattern

```python
# 4_strategy.py
def percent_off(price, rate): return price * (1 - rate)
def fixed_off(price, amount): return max(0, price - amount)

DISCOUNTS = {"member": lambda p: percent_off(p, 0.1),
             "coupon10": lambda p: fixed_off(p, 10)}

def apply(price, kind): return DISCOUNTS[kind](price)
```

정책의 종류가 외부 입력에 따라 바뀐다면, 전략이나 딕셔너리 조회가 if/elif보다 더 단순하고 확장에도 유리합니다.

### 단계 5 — Table-driven

```python
# 5_table.py
GRADES = [(90, "A"), (80, "B"), (70, "C"), (0, "F")]
def grade(score):
    return next(g for s, g in GRADES if score >= s)
```

분기가 사실상 데이터라면, 데이터 구조로 올리는 편이 맞습니다. 정책 테이블은 코드보다 변경이 덜 위험한 경우가 많습니다.

## 검증 방법

```bash
radon cc app/pricing.py -s
python -m pytest -q tests/test_pricing.py
```

**기대 결과**

- 중첩을 줄인 뒤 복잡도와 테스트 안정성이 함께 확인됩니다.
- 분기 정책을 테이블로 옮겨도 결과가 같아야 합니다.

## 실패하기 쉬운 지점

- 가드 절로 바꾸면서 예외 순서가 달라집니다.
- 타입 분기를 감춘 채 이름만 더 예쁘게 바꿉니다.

## 이 코드에서 먼저 봐야 할 점

- 가드 절은 들여쓰기를 줄입니다.
- 다형성은 조건문 자체를 없애 줍니다.
- 테이블은 정책을 데이터로 표현하게 만듭니다.

## 자주 하는 실수 5가지

1. **가드 절 없이 계속 중첩하기.** else 블록만 쌓입니다.
2. **부정형 조건을 유지하기.** 이중 부정이 쉽게 스며듭니다.
3. **타입마다 분기하기.** `isinstance`가 코드 전체에 퍼집니다.
4. **상태를 가진 전략 만들기.** 테스트가 어려워집니다.
5. **순서 의존 테이블 만들기.** 우선순위가 깨지기 쉽습니다.

## 실무에서는 이렇게 보입니다

가격 정책, 권한 체크, 라우팅 규칙처럼 분기가 사실상 데이터에 가까운 영역은 전략과 테이블로 옮길수록 관리가 쉬워집니다. 새로운 규칙을 추가할 때 기존 조건문을 뜯어고치지 않아도 되기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 깊이가 3을 넘으면 설계 냄새로 봅니다.
- if/elif가 5개 이상이면 다형성이나 테이블을 의심합니다.
- 외부 입력에 따라 바뀌는 정책은 데이터로 옮깁니다.
- 부정형 조건은 한 번에 긍정형으로 뒤집습니다.
- 전략은 가능한 한 상태 없이 유지합니다.

## 체크리스트

- [ ] 함수 깊이가 3 이하인가?
- [ ] 가드 절이 먼저 배치되어 있는가?
- [ ] 부정형 조건을 뒤집었는가?
- [ ] 타입 분기를 다형성으로 바꿀 수 있는가?
- [ ] 정책 분기를 테이블/전략으로 표현할 수 있는가?

## 연습 문제

1. 깊이 4 이상의 분기를 하나 찾아 평평하게 만들어 보세요.
2. 5개 이상 분기가 있는 if/elif 체인을 테이블로 바꿔 보세요.
3. `isinstance` 기반 분기 하나를 다형성으로 바꿔 보세요.

## 정리 및 다음 단계

조건문이 줄어들수록 코드의 핵심 흐름은 더 또렷해집니다. 다음 글에서는 또 하나의 큰 적인 중복을 어떻게 다뤄야 하는지 살펴보겠습니다.


## 조건문 단순화 패턴을 체계적으로 고르는 법

조건문을 단순화할 때는 한 가지 기법만 고집하지 않는 편이 좋습니다. 분기의 성격에 따라 패턴을 골라야 합니다.

| 패턴 | 적용 상황 | 장점 | 주의점 |
| --- | --- | --- | --- |
| Guard Clause | 비정상 입력을 초기에 걸러야 할 때 | 들여쓰기 감소, 본 흐름 강조 | 반환 순서 변경 주의 |
| Early Return | 조건 충족 시 즉시 종료 가능 | 가독성 향상 | 종료 경로 과다 주의 |
| Lookup Table | 정책이 데이터로 표현 가능 | 확장 용이, if 감소 | 키 누락 검증 필요 |
| Strategy | 알고리즘 선택이 잦을 때 | OCP 친화, 테스트 용이 | 클래스 과도 분할 주의 |
| Polymorphism | 타입 분기가 반복될 때 | `isinstance` 제거 | 모델링 비용 고려 |

핵심은 분기 수를 줄이는 것이 아니라 분기 책임을 올바른 위치로 옮기는 것입니다.

## 가드 절 전후 비교

```python
# before

def approve_refund(user, order, amount):
    if user is not None:
        if user.is_active:
            if order is not None:
                if order.is_paid:
                    if amount > 0:
                        return amount <= order.total_amount
    return False
```

```python
# after

def approve_refund(user, order, amount):
    if user is None or not user.is_active:
        return False
    if order is None or not order.is_paid:
        return False
    if amount <= 0:
        return False
    return amount <= order.total_amount
```

후자는 정상 흐름을 마지막 한 줄로 모아 놓았기 때문에 리뷰어가 정책을 더 빠르게 검증할 수 있습니다.

## 정책 테이블과 전략 객체 예시

```python
class MemberPolicy:
    def discount(self, amount: int) -> int:
        return int(amount * 0.9)


class GuestPolicy:
    def discount(self, amount: int) -> int:
        return amount


POLICIES = {
    "member": MemberPolicy(),
    "guest": GuestPolicy(),
}


def apply_discount(amount: int, user_type: str) -> int:
    policy = POLICIES[user_type]
    return policy.discount(amount)
```

위 구조는 if/elif 체인을 제거하고 정책 추가를 국소화합니다. 새 사용자 타입이 생겨도 기존 함수 본문을 수정하지 않고 정책 클래스만 추가하면 됩니다.

## 분기 단순화 검증 포인트

1. 예외 케이스가 초반에 배치되는가
2. 들여쓰기 깊이가 감소했는가
3. 정책 추가 시 기존 코드 변경량이 줄었는가
4. 테스트 케이스가 조건 단위로 명확해졌는가

```python
def max_indentation_depth(lines: list[str]) -> int:
    depth = 0
    max_depth = 0
    for line in lines:
        leading_spaces = len(line) - len(line.lstrip(" "))
        depth = leading_spaces // 4
        max_depth = max(max_depth, depth)
    return max_depth
```

수치를 함께 보면 조건문 개선이 실제로 효과를 냈는지 더 명확하게 판단할 수 있습니다.


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


## 조건문 단순화 패턴 카탈로그

분기 단순화는 코드 스타일 문제가 아니라 결함률을 낮추는 구조 개선입니다. 아래 카탈로그를 기준으로 현재 분기 형태를 분류하면 대응 전략을 빠르게 고를 수 있습니다.

| 패턴 | 징후 | 추천 리팩토링 |
| --- | --- | --- |
| 깊은 중첩 if | 들여쓰기 3단 이상 | 가드 절 도입 |
| 타입 분기 | `if type ==` 반복 | 다형성/전략 패턴 |
| 조건 중복 | 파일마다 같은 조건식 | 판정 함수 추출 |
| 부정형 과다 | `if not ... and not ...` | 긍정형 함수로 전환 |
| 정책 하드코딩 | 지역 변수로 규칙 고정 | 정책 테이블 분리 |

## 전/후 데모: 정책 테이블로 분기 축소

```python
# before
def shipping_fee(country: str, amount_cents: int) -> int:
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


# after
FREE_SHIPPING_POLICY = {
    "KR": (50000, 3000),
    "JP": (80000, 5000),
    "US": (100000, 9000),
}


def shipping_fee(country: str, amount_cents: int) -> int:
    threshold, fee = FREE_SHIPPING_POLICY.get(country, (10**12, 15000))
    return 0 if amount_cents >= threshold else fee
```

## SOLID 샘플: 개방-폐쇄 원칙 기반 전략 객체

```python
from dataclasses import dataclass

@dataclass
class DiscountRule:
    min_total_cents: int
    rate: float

    def apply(self, total_cents: int) -> int:
        if total_cents < self.min_total_cents:
            return total_cents
        return int(total_cents * (1 - self.rate))
```

정책이 늘어날수록 기존 분기문을 수정하는 대신 규칙 객체를 추가하는 구조가 유지보수 비용을 더 안정적으로 제어합니다.

## 린터 예시: 복잡도 경고로 분기 폭발 예방

```toml
[tool.ruff.lint]
select = ["C90", "PLR", "B", "E", "F"]

[tool.ruff.lint.mccabe]
max-complexity = 7
```

복잡도 한도를 낮추면 분기 폭발이 기능 출시 전에 드러납니다. 나중에 대청소하는 방식보다 예방 비용이 훨씬 작습니다.


## 심화 실습: 분기 폭발을 예방하는 설계 루틴

분기가 늘어나는 근본 원인은 정책이 코드 안쪽에 하드코딩되기 때문입니다. 정책을 데이터 또는 객체로 분리하면 if/elif 체인이 자연스럽게 줄어듭니다.

```python
RISK_POLICY = {
    "new": 0.03,
    "silver": 0.02,
    "gold": 0.01,
}


def calculate_fee_by_tier(tier: str, amount_cents: int) -> int:
    rate = RISK_POLICY.get(tier, 0.05)
    return int(amount_cents * rate)
```

## 분기 리팩토링 체크표

| 질문 | 예 | 조치 |
| --- | --- | --- |
| 같은 조건이 반복되는가 | 국가별 배송 조건 중복 | 정책 테이블 추출 |
| 분기마다 같은 후처리가 있는가 | 로깅/메트릭 중복 | 공통 후처리 함수 |
| 새로운 정책 추가가 어려운가 | `elif` 추가 시 기존 코드 수정 다수 | 전략 객체 도입 |

분기 코드는 기능이 늘수록 기하급수적으로 복잡해집니다. 먼저 줄이는 습관이 비용을 크게 절감합니다.


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

- **가드 절과 조기 반환은 어떤 상황에서 가장 효과적일까요?**
  - 본문의 기준은 조건문 줄이기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **부정형 조건과 이중 부정은 왜 읽기 어렵게 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **if/else 체인은 언제 다형성으로 바꾸는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Clean Code 101 (1/10): Clean Code란 무엇인가?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): 이름 짓기](./02-naming.md)
- [Clean Code 101 (3/10): 함수 작게 만들기](./03-small-functions.md)
- **조건문 줄이기 (현재 글)**
- 중복 제거 (예정)
- 오류 처리 (예정)
- 주석과 문서화 (예정)
- 테스트 가능한 코드 (예정)
- 리팩토링 기초 (예정)
- 좋은 코드 리뷰 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Refactoring — Replace Nested Conditional with Guard Clauses](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html)
- [Refactoring — Replace Conditional with Polymorphism](https://refactoring.com/catalog/replaceConditionalWithPolymorphism.html)
- [Strategy Pattern (Refactoring Guru)](https://refactoring.guru/design-patterns/strategy)
- [Clean Code (Ch. 3 Functions, Ch. 6 Objects)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/clean-code-101/ko)
Tags: Computer Science, CleanCode, Conditionals, GuardClauses, Refactoring, Readability
