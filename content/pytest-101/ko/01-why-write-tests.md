---
series: pytest-101
episode: 1
title: "pytest 101 (1/10): 왜 테스트를 작성해야 할까?"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - Testing
  - 소프트웨어 품질
  - 자동화 테스트
seo_description: 테스트가 개발 속도와 코드 품질에 어떤 차이를 만드는지 pytest 관점에서 설명합니다.
last_reviewed: '2026-05-12'
---

# pytest 101 (1/10): 왜 테스트를 작성해야 할까?

이 글은 pytest 101 시리즈의 첫 번째 글입니다. 테스트를 작성하면 개발이 느려진다고 느끼기 쉽지만, 실제로는 변경에 대한 두려움을 줄여서 개발 속도를 높이는 경우가 훨씬 많습니다. 이 글에서는 테스트가 왜 중요한지, 어떤 종류의 테스트가 있는지, 그리고 Python에서 왜 pytest가 사실상 기본 도구로 자리 잡았는지를 정리합니다.

코드를 고칠 때마다 “이 변경이 다른 기능을 깨뜨리지는 않을까?”라는 불안이 생긴다면, 이미 테스트가 필요한 상태일 가능성이 큽니다. 테스트는 단지 품질 관리 문서가 아니라, 변경 후에도 기존 동작이 유지되는지 몇 초 안에 확인하게 해 주는 자동화 장치입니다.


![pytest 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/01/01-01-big-picture.ko.png)
*pytest 101 1장 흐름 개요*

## 먼저 던지는 질문

- 테스트는 개발 속도를 늦추는 작업일까요, 아니면 오히려 속도를 높이는 투자일까요?
- 단위 테스트, 통합 테스트, E2E 테스트는 무엇이 다를까요?
- 수동 테스트와 자동화 테스트는 어떤 차이를 만들까요?

## 왜 이 글이 중요한가

테스트가 없는 상태에서의 변경은 늘 도박에 가깝습니다. 코드가 커질수록 “이 함수 하나만 바꿨는데 왜 전혀 다른 화면이 깨졌지?” 같은 상황이 자주 생기기 때문입니다. 반대로 테스트가 있으면, 변경 직후 기존 동작이 유지되는지 바로 확인할 수 있습니다.

> 테스트는 미래의 나를 위한 안전망입니다. 오늘 10분 투자하면 내일 3시간 디버깅을 줄일 수 있습니다.

실무에서는 이 차이가 더 크게 드러납니다. 테스트 없이 배포하면 장애 원인 분석이 길어지고, 어디서 어떤 입력이 실패했는지 파악하는 시간도 늘어납니다. 테스트는 “정상 동작을 기대한 계약”을 코드로 남기는 수단입니다.

## 핵심 개념 잡기

> 테스트 = 코드가 기대한 방식으로 동작하는지 자동으로 검증하는 코드

```text
[Manual Testing]           [Automated Testing]
  Human runs code            Code runs code
  Repetition cost ↑          Repetition cost ≈ 0
  Error-prone                Consistent results
  Coverage unclear           Coverage measurable
```

수동 테스트는 처음에는 간단해 보이지만, 같은 확인을 반복할수록 비용이 빠르게 커집니다. 자동화 테스트는 처음 작성 비용이 있지만, 이후 반복 실행 비용이 거의 0에 가깝습니다. 이 차이가 누적되면 팀 생산성의 격차로 이어집니다.

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 단위 테스트 | 함수 하나를 독립적으로 검증합니다 |
| 통합 테스트 | 여러 컴포넌트가 함께 동작하는 방식을 검증합니다 |
| E2E 테스트 | 사용자 관점에서 전체 흐름을 검증합니다 |
| 테스트 피라미드 | 단위 테스트를 많이, 통합/E2E 테스트를 상대적으로 적게 두는 전략입니다 |
| 회귀 테스트 | 변경 후에도 기존 기능이 계속 동작하는지 확인합니다 |

## Before / After

수동 확인과 pytest 자동 검증의 차이를 비교해 보겠습니다.

```python
# before: manually call functions and visually inspect output
def add(a, b):
    return a + b

print(add(1, 2))   # check if 3 appears
print(add(-1, 1))   # check if 0 appears
```

```python
# after: automated verification with pytest
def add(a, b):
    return a + b

def test_add_positive():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, 1) == 0
```

두 방식의 핵심 차이는 사람이 눈으로 확인하느냐, 도구가 조건을 자동으로 확인하느냐입니다. 테스트는 단순히 편의 기능이 아니라, 변경을 반복할 수 있게 만드는 기반입니다.

## 단계별 실습

### Step 1: Check Python Environment

```bash
python3 --version
# Python 3.10 or higher is fine
```

### Step 2: Install pytest

```bash
pip install pytest
pytest --version
```

### Step 3: Write the Function Under Test

Create `calculator.py`:

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Step 4: Write the Test File

Create `test_calculator.py`:

```python
# test_calculator.py
import pytest
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)
```

### Step 5: Run the Tests

```bash
pytest test_calculator.py -v
```

Output:

```text
test_calculator.py::test_add PASSED
test_calculator.py::test_add_negative PASSED
test_calculator.py::test_divide PASSED
test_calculator.py::test_divide_by_zero PASSED
========================= 4 passed =========================
```

## 이 코드에서 주목할 점

- `test_`로 시작하는 함수는 pytest가 자동으로 발견합니다.
- `assert` 하나만으로 기대값을 간결하게 표현할 수 있습니다.
- `pytest.raises`는 예외가 반드시 발생해야 하는 경우를 검증할 때 사용합니다.
- `-v` 옵션은 어떤 테스트가 통과하거나 실패했는지 개별적으로 보여 줍니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 테스트 파일 이름이 `test_`로 시작하지 않음 | pytest가 파일을 자동 탐색하지 못합니다 | `test_*.py` 또는 `*_test.py` 규칙을 따릅니다 |
| 테스트 함수 이름이 `test_`로 시작하지 않음 | 테스트로 인식되지 않습니다 | 함수명에 `test_` 접두사를 붙입니다 |
| `print()`로 결과를 확인함 | 자동화할 수 없고 회귀를 잡지 못합니다 | 기대값을 `assert`로 명시합니다 |
| 하나의 테스트에 assert를 너무 많이 넣음 | 첫 실패 이후 나머지 검증이 중단됩니다 | 테스트 하나당 한 가지 행위를 검증합니다 |
| 테스트가 실행 순서에 의존함 | 독립 실행 시 실패할 수 있습니다 | 각 테스트를 자기완결적으로 설계합니다 |

## 실무에서 이렇게 쓰입니다

- CI/CD 파이프라인에서 `pytest`를 실행해 머지 전에 자동 검증합니다.
- 리팩터링 전에 테스트를 먼저 추가해 안전망을 확보합니다.
- 버그 리포트가 오면 재현 테스트를 먼저 작성한 뒤 수정합니다.
- 코드 리뷰에서 테스트 커버리지를 함께 확인합니다.
- 새 팀원이 프로젝트 동작을 이해할 때 테스트가 가장 빠른 문서 역할을 합니다.

## 현업 개발자는 이렇게 생각합니다

경험이 쌓인 개발자일수록 테스트를 “추가 작업”이 아니라 “개발의 일부”로 봅니다. 테스트 없이 코드를 바꾸는 것은 컴파일하지 않고 배포하는 것과 비슷한 감각입니다.

실제로 많은 팀은 전체 개발 시간의 일부를 테스트 작성에 꾸준히 투자합니다. 그 비용은 디버깅 감소, 더 안전한 리팩터링, 더 빠른 리뷰로 돌아옵니다.

## 체크리스트

- [ ] `pytest --version`으로 설치를 확인했다
- [ ] `test_` 접두사 규칙을 이해했다
- [ ] `assert`로 기대값을 검증하는 테스트를 작성했다
- [ ] `pytest.raises`로 예외 테스트를 작성했다
- [ ] `pytest -v`로 실행 결과를 확인했다

## 연습 문제

1. `multiply(a, b)` 함수를 만들고, 양수·음수·0 입력을 검증하는 테스트 세 개를 작성해 보세요.
2. `is_even(n)` 함수를 만들고, 짝수·홀수·음수 케이스를 테스트해 보세요.
3. 잘못된 문자열 입력에서 `ValueError`를 발생시키는 `parse_int(s)` 함수를 만들고 테스트해 보세요.

## 정리 및 다음 글 안내

테스트는 코드 변경에 대한 안전망입니다. pytest는 `assert` 하나로도 충분히 읽기 좋은 테스트를 만들 수 있게 해 줍니다. 다음 글에서는 pytest가 테스트 파일과 함수를 어떻게 자동으로 찾는지부터, 첫 번째 테스트를 실제로 작성하는 과정까지 살펴보겠습니다.

## 실전 패턴 추가: fixture, parametrization, mock을 함께 설계하기

테스트 파일이 커질수록 중요한 것은 개별 문법보다 테스트 경계를 일정하게 유지하는 일입니다. 특히 fixture로 상태를 준비하고, `@pytest.mark.parametrize`로 입력 집합을 확장하고, mock으로 외부 의존성을 분리하는 세 가지를 한 흐름으로 묶으면 테스트 유지보수 비용이 크게 줄어듭니다.

```python
# tests/test_order_service.py
from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

import pytest


@dataclass
class Order:
    item: str
    qty: int


class InventoryClient:
    def reserve(self, item: str, qty: int) -> bool:  # pragma: no cover
        raise NotImplementedError


class OrderService:
    def __init__(self, client: InventoryClient) -> None:
        self.client = client

    def place(self, order: Order) -> str:
        if order.qty <= 0:
            raise ValueError("qty must be positive")
        ok = self.client.reserve(order.item, order.qty)
        return "confirmed" if ok else "rejected"


@pytest.fixture
def inventory_client() -> Mock:
    return Mock(spec=InventoryClient)


@pytest.fixture
def order_service(inventory_client: Mock) -> OrderService:
    return OrderService(client=inventory_client)


@pytest.mark.parametrize(
    "order,expected",
    [
        (Order("book", 1), "confirmed"),
        (Order("book", 3), "confirmed"),
        (Order("book", 5), "rejected"),
    ],
)
def test_place_orders(order_service: OrderService, inventory_client: Mock, order: Order, expected: str) -> None:
    inventory_client.reserve.return_value = expected == "confirmed"
    assert order_service.place(order) == expected


def test_place_rejects_invalid_quantity(order_service: OrderService) -> None:
    with pytest.raises(ValueError, match="qty must be positive"):
        order_service.place(Order("book", 0))
```

위 구조의 핵심은 테스트 목적별 분리입니다. fixture는 준비, parametrization은 입력 공간, mock은 외부 의존성 제어를 담당합니다. 팀 단위에서는 이 분리를 지켜야 테스트를 고칠 때 영향 범위를 빠르게 읽을 수 있습니다.

또한 fixture scope를 무조건 넓히지 않는 편이 안전합니다. DB 연결이나 임시 디렉터리처럼 생성 비용이 큰 자원만 `module` 또는 `session`으로 올리고, 나머지는 `function` scope로 두어 테스트 독립성을 유지하는 것이 좋습니다.

## 추가 실무 메모: 실패 재현 테스트를 먼저 고정하기

버그 수정에서는 구현보다 재현 테스트를 먼저 고정하는 순서가 중요합니다. 예를 들어 시간대나 경계값 입력처럼 운영에서만 드러나는 문제는 아래처럼 실패 케이스를 테스트로 먼저 기록한 뒤 수정해야 재발을 막을 수 있습니다.

```python
import pytest

def normalize_hour(hour: int) -> int:
    if not 0 <= hour <= 23:
        raise ValueError("hour out of range")
    return hour

@pytest.mark.parametrize("bad", [-1, 24, 100])
def test_normalize_hour_rejects_invalid_values(bad: int) -> None:
    with pytest.raises(ValueError):
        normalize_hour(bad)
```

이 방식은 회고 문서보다 강한 운영 기록을 남깁니다. 다음 변경에서도 같은 실패가 자동으로 잡히기 때문입니다.

## 실전 시나리오: 테스트가 비용을 줄이는 순간

아래는 장바구니 할인 계산 로직을 수동 확인에서 자동 테스트로 전환하는 사례입니다.

```python
# pricing.py
from dataclasses import dataclass

@dataclass
class CartItem:
    name: str
    price: int
    qty: int


def calc_total(items: list[CartItem], coupon_rate: float = 0.0) -> int:
    if not 0.0 <= coupon_rate <= 1.0:
        raise ValueError("coupon_rate must be between 0 and 1")
    subtotal = sum(i.price * i.qty for i in items)
    discounted = int(subtotal * (1 - coupon_rate))
    return max(0, discounted)
```

```python
# test_pricing.py
import pytest
from pricing import CartItem, calc_total


def test_calc_total_without_coupon():
    items = [CartItem("book", 10000, 2), CartItem("pen", 1000, 3)]
    assert calc_total(items) == 23000


def test_calc_total_with_coupon():
    items = [CartItem("book", 10000, 2), CartItem("pen", 1000, 3)]
    assert calc_total(items, 0.1) == 20700


@pytest.mark.parametrize("bad_rate", [-0.1, 1.1])
def test_calc_total_rejects_bad_coupon_rate(bad_rate):
    with pytest.raises(ValueError, match="between 0 and 1"):
        calc_total([], bad_rate)
```

```bash
pytest test_pricing.py -v
```

```text
test_pricing.py::test_calc_total_without_coupon PASSED
test_pricing.py::test_calc_total_with_coupon PASSED
test_pricing.py::test_calc_total_rejects_bad_coupon_rate[-0.1] PASSED
test_pricing.py::test_calc_total_rejects_bad_coupon_rate[1.1] PASSED
========================= 4 passed =========================
```

버그가 들어간 코드를 일부러 넣어 보면 테스트의 의미가 더 분명해집니다.

```python
# 잘못된 코드 예시
# discounted = int(subtotal * (1 + coupon_rate))
```

```bash
pytest test_pricing.py -v
```

```text
test_pricing.py::test_calc_total_without_coupon PASSED
test_pricing.py::test_calc_total_with_coupon FAILED
E       assert 25300 == 20700
```

이 실패 한 줄이 운영 장애를 막아 주는 신호입니다.

## 테스트 우선순위 정하는 법

테스트를 어디부터 써야 할지 모를 때는 아래 기준이 실용적입니다.

| 우선순위 | 영역 | 이유 | 예시 |
|---|---|---|---|
| 1 | 금액, 권한, 재고 | 실패 비용이 큼 | 결제 합계, 관리자 권한 |
| 2 | 외부 연동 경계 | 장애 전파 위험이 큼 | API 응답 변환, DB 저장 |
| 3 | 순수 계산 함수 | 빠르게 넓게 커버 가능 | 파싱, 포맷팅, 검증 |
| 4 | 단순 getter/setter | ROI가 낮을 수 있음 | 얇은 래퍼 함수 |

핵심은 중요한 경계를 먼저 자동화하는 것입니다. 모든 코드를 같은 밀도로 테스트하려고 하면 유지보수 비용이 먼저 올라갑니다.

## 흔한 반론과 대응

| 반론 | 실제 문제 | 대응 |
|---|---|---|
| "테스트 쓸 시간 없음" | 디버깅 시간이 더 커짐 | 버그 재현 테스트부터 작성 |
| "UI가 자주 바뀜" | 단위 테스트 범위 오해 | 도메인 로직을 분리해 테스트 |
| "이미 수동 QA 있음" | 회귀 탐지 속도 느림 | PR 단계 자동 테스트 추가 |
| "커버리지가 낮아 의미 없음" | 측정 시작 자체가 없음 | 핵심 모듈부터 기준선 설정 |

## 리팩터링 전후 비교: 테스트 없는 코드 vs 테스트 있는 코드

```python
# before_refactor.py
def shipping_fee(country: str, total: int) -> int:
    if country == "KR":
        if total >= 50000:
            return 0
        return 3000
    if country == "US":
        if total >= 100:
            return 0
        return 10
    return 999999
```

```python
# test_shipping_fee.py
import pytest
from before_refactor import shipping_fee

@pytest.mark.parametrize(
    "country,total,expected",
    [
        ("KR", 10000, 3000),
        ("KR", 50000, 0),
        ("US", 50, 10),
        ("US", 100, 0),
        ("JP", 1, 999999),
    ],
)
def test_shipping_fee(country, total, expected):
    assert shipping_fee(country, total) == expected
```

테스트를 먼저 고정하면 함수 내부를 안전하게 정리할 수 있습니다.

```python
# after_refactor.py
FEES = {
    "KR": {"free_over": 50000, "fee": 3000},
    "US": {"free_over": 100, "fee": 10},
}


def shipping_fee(country: str, total: int) -> int:
    policy = FEES.get(country)
    if policy is None:
        return 999999
    return 0 if total >= policy["free_over"] else policy["fee"]
```

같은 테스트를 실행해 모두 통과하면, 동작 계약을 지키면서 구조 개선이 끝난 것입니다.


## 팀 도입 로드맵: 테스트 문화를 실제로 시작하는 순서

테스트의 필요성에 동의해도, 팀에서 시작점을 못 잡으면 문서만 남고 실행이 멈춥니다. 아래 순서는 소규모 팀에서도 바로 적용 가능합니다.

### 1단계: 버그 재현 테스트 우선

운영에서 한 번이라도 장애가 난 코드부터 재현 테스트를 추가합니다.

```python
# bugfix_test_example.py

def normalize_phone(raw: str) -> str:
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) not in (10, 11):
        raise ValueError("invalid phone length")
    return digits
```

```python
import pytest
from bugfix_test_example import normalize_phone

@pytest.mark.parametrize("bad", ["123", "abc", "010-1234-12345"])
def test_normalize_phone_rejects_invalid_input(bad):
    with pytest.raises(ValueError):
        normalize_phone(bad)
```

### 2단계: 핵심 경계 자동화

입력 검증, 결제 금액, 권한 체크처럼 실패 비용이 큰 경계부터 테스트를 추가합니다.

### 3단계: PR 기본 규칙

- 기능 코드 수정 시 관련 테스트 1개 이상 포함
- 버그 수정 시 재현 테스트 먼저 작성
- CI에서 `pytest -q` 실패 시 머지 금지

## 수동 QA와 자동 테스트의 역할 분리

| 구분 | 자동 테스트 | 수동 QA |
|---|---|---|
| 목적 | 회귀 빠른 탐지 | 사용자 관점 검증 |
| 실행 빈도 | PR마다 | 릴리스 전/후 |
| 속도 | 초~분 | 분~시간 |
| 재현성 | 높음 | 상대적으로 낮음 |

두 방식은 대체 관계가 아니라 상호 보완 관계입니다.

## 실패 출력을 운영 지식으로 전환하기

테스트 실패는 개발자 개인 이벤트가 아니라 팀 지식 축적 이벤트입니다.

- 실패한 입력값을 parametrize 목록에 남깁니다.
- 에러 메시지를 구체화해 재현 시간을 줄입니다.
- 회고 문서 링크를 테스트 코드 주석으로 연결합니다.

```python
# regression_cases.py
import pytest


def parse_currency(value: str) -> int:
    cleaned = value.replace(",", "").strip()
    if not cleaned.isdigit():
        raise ValueError("invalid currency string")
    return int(cleaned)


@pytest.mark.parametrize(
    "raw",
    ["1,2,3", "12a00", "-100", ""],
)
def test_parse_currency_regressions(raw):
    with pytest.raises(ValueError):
        parse_currency(raw)
```

## 최소 운영 지표

테스트를 시작했다면 아래 지표를 월 단위로 추적하면 개선 방향이 명확해집니다.

| 지표 | 의미 | 목표 |
|---|---|---|
| 실패 후 복구 시간 | 테스트 실패 원인 파악/수정 시간 | 감소 추세 |
| 회귀 버그 수 | 같은 유형 재발 횟수 | 분기별 감소 |
| PR 테스트 실행률 | 테스트 포함 PR 비율 | 90% 이상 |
| 테스트 실행 시간 | 피드백 지연 정도 | 팀 합의선 유지 |


## 심화 실습 세트: 실패를 빠르게 재현하고 고정하는 루틴

아래 실습은 글 주제와 무관하게 pytest 프로젝트에서 반복적으로 쓰는 루틴입니다. 핵심은 실패를 의도적으로 만들고, 실패 메시지를 읽고, 테스트를 보강하고, 다시 통과시키는 사이클을 짧게 반복하는 것입니다.

### 실습 A: 입력 검증 함수

```python
# app/input_guard.py

def require_non_empty(value: str) -> str:
    if value is None:
        raise TypeError("value cannot be None")
    if value.strip() == "":
        raise ValueError("value cannot be blank")
    return value.strip()
```

```python
# tests/test_input_guard.py
import pytest
from app.input_guard import require_non_empty


def test_require_non_empty_ok():
    assert require_non_empty("  hello  ") == "hello"


@pytest.mark.parametrize("bad", ["", "   ", "\n\t"])
def test_require_non_empty_blank(bad):
    with pytest.raises(ValueError, match="blank"):
        require_non_empty(bad)


def test_require_non_empty_none():
    with pytest.raises(TypeError, match="None"):
        require_non_empty(None)
```

```bash
pytest tests/test_input_guard.py -v
```

```text
tests/test_input_guard.py::test_require_non_empty_ok PASSED
tests/test_input_guard.py::test_require_non_empty_blank[] PASSED
tests/test_input_guard.py::test_require_non_empty_blank[   ] PASSED
tests/test_input_guard.py::test_require_non_empty_blank[\n\t] PASSED
tests/test_input_guard.py::test_require_non_empty_none PASSED
========================= 5 passed =========================
```

### 실습 B: 실패 유도 후 원인 파악

함수 구현을 일부러 아래처럼 바꿉니다.

```python
# 잘못된 구현 예시
# if value.strip() == "":
#     return value
```

다시 실행하면 실패가 즉시 재현됩니다.

```text
FAILED tests/test_input_guard.py::test_require_non_empty_blank[]
E   Failed: DID NOT RAISE <class 'ValueError'>
```

이 출력 하나로 계약 위반 지점을 바로 확인할 수 있습니다.

### 실습 C: 리팩터링 안정성 확인

```python
# app/input_guard.py (refactor)

def require_non_empty(value: str) -> str:
    if value is None:
        raise TypeError("value cannot be None")
    normalized = value.strip()
    if normalized == "":
        raise ValueError("value cannot be blank")
    return normalized
```

같은 테스트를 실행해 모두 통과하면, 구조를 바꿔도 계약은 유지된 것입니다.

## 터미널 옵션 조합

| 명령 | 목적 |
|---|---|
| `pytest -q` | 빠른 성공/실패 확인 |
| `pytest -v` | 케이스별 통과/실패 확인 |
| `pytest -x` | 첫 실패에서 즉시 중단 |
| `pytest -k "keyword"` | 특정 범위만 선택 실행 |
| `pytest --maxfail=3` | 최대 실패 수 제한 |

## 운영 회귀 테스트 템플릿

```python
import pytest

BUG_CASES = [
    ("", ValueError),
    ("   ", ValueError),
    (None, TypeError),
]

@pytest.mark.parametrize("raw,exc", BUG_CASES)
def test_regression_cases(raw, exc):
    with pytest.raises(exc):
        require_non_empty(raw)
```

이 템플릿은 버그 이슈를 테스트 코드로 영구 보존하는 가장 단순한 형태입니다.

## 품질 체크 질문

- 실패 메시지만 보고 원인을 추론할 수 있는가
- 테스트가 실행 순서에 의존하지 않는가
- 경계값 입력이 포함되어 있는가
- 정상/오류 경로를 모두 검증하는가
- 테스트 추가가 함수 복사 대신 데이터 추가로 끝나는가


## 처음 질문으로 돌아가기

- **테스트는 개발 속도를 늦추는 작업일까요, 아니면 오히려 속도를 높이는 투자일까요?**
  - 본문의 기준은 왜 테스트를 작성해야 할까?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **단위 테스트, 통합 테스트, E2E 테스트는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **수동 테스트와 자동화 테스트는 어떤 차이를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **왜 테스트를 작성해야 할까? (현재 글)**
- 첫 번째 pytest 테스트 작성하기 (예정)
- assert와 예외 테스트 (예정)
- fixture 이해하기 (예정)
- parametrization으로 테스트 케이스 늘리기 (예정)
- mock과 monkeypatch (예정)
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [Python Testing with pytest (Brian Okken)](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)
- [Test Pyramid — Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Real Python — Getting Started With Testing in Python](https://realpython.com/python-testing/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, Testing, 소프트웨어 품질, 자동화 테스트
