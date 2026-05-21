---
series: pytest-101
episode: 10
title: "pytest 101 (10/10): 테스트하기 쉬운 코드 구조 만들기"
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
  - 테스트 가능한 코드
  - 의존성 주입
  - 소프트웨어 설계
seo_description: mock 벽을 줄이기 위해 순수 로직과 외부 의존성 경계를 나누고, 의존성 주입으로 테스트하기 쉬운 Python 코드를 설계합니다.
last_reviewed: '2026-05-17'
---

# pytest 101 (10/10): 테스트하기 쉬운 코드 구조 만들기

이 글은 pytest 101 시리즈의 마지막 글입니다.

테스트가 힘든 이유는 pytest 기능이 부족해서가 아니라 코드가 결제, 저장, 알림, 시간 조회 같은 바깥세상 의존성을 한 함수 안에 뒤섞어 놓았기 때문인 경우가 많습니다. 이 글에서는 mock이 많아지는 구조를 어떻게 읽어야 하는지, 그리고 어떤 경계에서 순수 로직과 부작용을 분리해야 테스트가 짧아지는지 구체적인 예제로 살펴봅니다.

## 먼저 던지는 질문

- 왜 어떤 함수는 테스트 하나에 patch와 mock이 여러 개씩 필요할까요?
- 의존성 주입은 어떤 지점에 적용해야 실제로 테스트가 단순해질까요?
- 순수 함수, Protocol, Fake 객체는 각각 어떤 역할을 맡으면 좋을까요?

## 큰 그림

![pytest 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/10/10-01-testable-code-boundary.ko.png)

*pytest 101 10장 흐름 개요*

## 왜 중요한가

테스트가 어렵다는 말은 대개 “이 코드는 경계가 흐리다”는 뜻입니다. 함수 하나가 DB를 읽고, 외부 API를 호출하고, 현재 시간을 찍고, 메일을 보내면 테스트도 그만큼 많은 가짜 환경을 꾸며야 합니다.

> mock이 많아질수록 테스트가 정교해진다는 뜻은 아닙니다. 종종 그 반대로, 코드가 외부 세계에 너무 강하게 묶여 있다는 신호입니다.

테스트하기 쉬운 구조는 테스트만 편하게 하지 않습니다. 변경 범위를 줄이고, 실패 원인을 좁히고, 비즈니스 규칙을 더 선명하게 드러내 줍니다.

## 핵심 개념 잡기

> 테스트하기 쉬운 코드는 “안쪽에는 순수 규칙, 바깥쪽에는 교체 가능한 부작용”이라는 경계를 분명히 둔 코드입니다.

```text
[Pure core]
  price calculation
  validation rules
  status transitions

[Boundary adapters]
  payment gateway
  repository
  notification sender
  clock / id factory
```

## 핵심 개념

| 용어 | 설명 |
| --- | --- |
| 순수 함수 | 같은 입력에 같은 결과를 돌려주고 숨은 부작용이 없는 함수입니다 |
| 의존성 주입 | 외부 시스템 접근 수단을 함수 인자나 생성자로 넘겨 교체 가능하게 만드는 방식입니다 |
| Protocol | 협력 객체가 어떤 메서드를 가져야 하는지 타입 수준에서 표현하는 인터페이스입니다 |
| Fake | 실제 DB나 API 대신 테스트 안에서 동작하는 가벼운 구현체입니다 |
| 경계(boundary) | 비즈니스 규칙과 외부 세계가 만나는 지점입니다 |

## Before / After

**Before — 결제, 시간, 저장, 알림이 한 함수 안에 섞여 있음:**

```python
import requests
from datetime import datetime, timezone

def create_order(user: dict, items: list[dict]) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    payload = {
        "customer_id": user["payment_customer_id"],
        "amount": subtotal,
        "currency": "KRW",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "line_items": [
            {
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            }
            for item in items
        ],
    }
    response = requests.post(
        "https://pay.example.com/v1/charges",
        json=payload,
        timeout=5,
    )
    response.raise_for_status()
    charge = response.json()
    save_order_to_db(user["id"], subtotal, charge["id"])
    send_email(user["email"], f"주문 {charge['id']}가 완료되었습니다.")
    return {
        "order_id": charge["id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
    }
```

**After — 순수 계산과 외부 호출 경계를 나눔:**

```python
def build_charge_request(user: dict, items: list[dict], requested_at: str) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    return {
        "customer_id": user["payment_customer_id"],
        "amount": subtotal,
        "currency": "KRW",
        "requested_at": requested_at,
        "line_items": [
            {
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            }
            for item in items
        ],
    }

def finalize_order(charge: dict) -> dict:
    return {
        "order_id": charge["id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
    }
```

After 버전의 핵심은 “무엇을 계산할지”와 “어디에 요청을 보낼지”를 분리했다는 점입니다. 이제 테스트는 대부분 `dict` 입력과 출력만 검증하면 됩니다.

## 단계별 실습

### Step 1: 먼저 순수 로직을 밖으로 끄집어낸다

```python
# pricing.py
def calculate_subtotal(items: list[dict]) -> int:
    return sum(item["unit_price"] * item["quantity"] for item in items)

def membership_discount_rate(membership: str) -> float:
    rates = {"gold": 0.15, "silver": 0.10, "bronze": 0.05}
    return rates.get(membership, 0.0)

def calculate_discount(subtotal: int, membership: str) -> int:
    return int(subtotal * membership_discount_rate(membership))

def calculate_shipping(amount_after_discount: int, country: str) -> int:
    if country == "KR":
        return 0 if amount_after_discount >= 50000 else 3000
    return 15000

def calculate_order_totals(items: list[dict], membership: str, country: str) -> dict:
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, membership)
    shipping = calculate_shipping(subtotal - discount, country)
    total = subtotal - discount + shipping
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": total,
    }
```

```python
# test_pricing.py
from pricing import calculate_order_totals, calculate_shipping, calculate_discount

def test_gold_discount():
    assert calculate_discount(100000, "gold") == 15000

def test_shipping_for_small_domestic_order():
    assert calculate_shipping(42000, "KR") == 3000

def test_order_totals_for_silver_member():
    items = [
        {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
        {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
    ]
    result = calculate_order_totals(items, membership="silver", country="KR")

    assert result == {
        "subtotal": 40000,
        "discount": 4000,
        "shipping": 3000,
        "total": 39000,
    }
```

여기서는 네트워크도, DB도, 현재 시간도 없습니다. 그래서 테스트가 짧고 실패 이유도 바로 보입니다.

### Step 2: 외부 협력 객체는 Protocol과 Fake로 분리한다

```python
# order_service.py
from typing import Protocol

class PaymentGateway(Protocol):
    def charge(self, payload: dict) -> dict:
        pass

class OrderRepository(Protocol):
    def save(self, order: dict) -> dict:
        pass

class Notifier(Protocol):
    def send(self, email: str, message: str) -> None:
        pass

class OrderService:
    def __init__(
        self,
        gateway: PaymentGateway,
        repository: OrderRepository,
        notifier: Notifier,
    ):
        self.gateway = gateway
        self.repository = repository
        self.notifier = notifier

    def create(self, user: dict, payload: dict) -> dict:
        charge = self.gateway.charge(payload)
        order = {
            "user_id": user["id"],
            "email": user["email"],
            "charge_id": charge["id"],
            "status": charge["status"],
            "charged_amount": charge["amount"],
        }
        saved = self.repository.save(order)
        self.notifier.send(user["email"], f"주문 {saved['charge_id']}가 완료되었습니다.")
        return saved
```

```python
# test_order_service.py
from order_service import OrderService

class FakeGateway:
    def __init__(self):
        self.payloads = []

    def charge(self, payload: dict) -> dict:
        self.payloads.append(payload)
        return {
            "id": "ch_1001",
            "status": "paid",
            "amount": payload["amount"],
        }

class FakeRepository:
    def __init__(self):
        self.saved_orders = []

    def save(self, order: dict) -> dict:
        persisted = {**order, "id": 101}
        self.saved_orders.append(persisted)
        return persisted

class FakeNotifier:
    def __init__(self):
        self.messages = []

    def send(self, email: str, message: str) -> None:
        self.messages.append((email, message))

def test_create_order_with_fakes():
    service = OrderService(FakeGateway(), FakeRepository(), FakeNotifier())
    user = {"id": 7, "email": "buyer@example.com"}
    payload = {
        "customer_id": "cus_777",
        "amount": 39000,
        "currency": "KRW",
        "requested_at": "2026-05-17T09:00:00+00:00",
        "line_items": [
            {"sku": "keyboard", "quantity": 1, "unit_price": 30000},
            {"sku": "switch-pack", "quantity": 2, "unit_price": 5000},
        ],
    }

    result = service.create(user, payload)

    assert result["id"] == 101
    assert result["charge_id"] == "ch_1001"
    assert result["charged_amount"] == 39000
```

Protocol은 “무슨 메서드가 필요하냐”를 드러내고, Fake는 “테스트에서 그 메서드를 어떻게 흉내 내느냐”를 담당합니다. 둘을 나누면 mock 프레임워크 없이도 협력 객체 테스트가 가능합니다.

### Step 3: 요청 조립과 반환값 정리를 별도 함수로 둔다

```python
# checkout.py
def build_charge_request(user: dict, items: list[dict], requested_at: str) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    return {
        "customer_id": user["payment_customer_id"],
        "amount": subtotal,
        "currency": "KRW",
        "requested_at": requested_at,
        "line_items": [
            {
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            }
            for item in items
        ],
    }

def present_checkout_result(charge: dict) -> dict:
    return {
        "order_id": charge["id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
    }
```

```python
# test_checkout.py
from checkout import build_charge_request, present_checkout_result

def test_build_charge_request_uses_explicit_fields():
    payload = build_charge_request(
        user={"payment_customer_id": "cus_777"},
        items=[
            {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
            {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
        ],
        requested_at="2026-05-17T09:00:00+00:00",
    )

    assert payload == {
        "customer_id": "cus_777",
        "amount": 40000,
        "currency": "KRW",
        "requested_at": "2026-05-17T09:00:00+00:00",
        "line_items": [
            {"sku": "keyboard", "quantity": 1, "unit_price": 30000},
            {"sku": "switch-pack", "quantity": 2, "unit_price": 5000},
        ],
    }

def test_present_checkout_result():
    charge = {"id": "ch_1001", "status": "paid", "amount": 40000}
    assert present_checkout_result(charge) == {
        "order_id": "ch_1001",
        "status": "paid",
        "charged_amount": 40000,
    }
```

이렇게 payload를 조립하는 코드도 별도 함수가 되면 `json={...}` 같은 빈칸 예제가 아니라, 실제로 어떤 필드가 오가는지 테스트와 문서에서 모두 분명해집니다.

### Step 4: 시간과 ID 생성도 경계 밖으로 뺀다

```python
from collections.abc import Callable

from pricing import calculate_order_totals

def create_checkout_payload(
    user: dict,
    items: list[dict],
    now_iso: str,
    order_id_factory: Callable[[], str],
) -> dict:
    totals = calculate_order_totals(items, membership=user["membership"], country=user["country"])
    return {
        "order_id": order_id_factory(),
        "customer_id": user["payment_customer_id"],
        "requested_at": now_iso,
        "amount": totals["total"],
        "currency": "KRW",
        "line_items": items,
    }
```

```python
from checkout import create_checkout_payload

def test_create_checkout_payload_with_fixed_clock_and_id():
    user = {
        "membership": "gold",
        "country": "KR",
        "payment_customer_id": "cus_777",
    }
    items = [{"sku": "keyboard", "unit_price": 30000, "quantity": 2}]

    payload = create_checkout_payload(
        user=user,
        items=items,
        now_iso="2026-05-17T09:00:00+00:00",
        order_id_factory=lambda: "order_9001",
    )

    assert payload["order_id"] == "order_9001"
    assert payload["requested_at"] == "2026-05-17T09:00:00+00:00"
    assert payload["amount"] == 51000
```

`datetime.now()`와 `uuid4()`를 함수 안에서 바로 호출하면 테스트가 그 시점과 랜덤 값에 묶입니다. 시간을 문자열이나 `datetime` 인자로 넘기고, ID 생성 함수를 주입하면 테스트는 즉시 결정적(deterministic)으로 바뀝니다.

### Step 5: patch 벽을 실제 before/after로 비교한다

먼저 리팩터링 전 코드와 테스트를 보겠습니다.

```python
# before_checkout.py
import requests
from datetime import datetime, timezone

from mailer import send_email
from repository import save_order_to_db

def checkout(user: dict, items: list[dict]) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    response = requests.post(
        "https://pay.example.com/v1/charges",
        json={
            "customer_id": user["payment_customer_id"],
            "amount": subtotal,
            "currency": "KRW",
            "requested_at": datetime.now(timezone.utc).isoformat(),
        },
        timeout=5,
    )
    response.raise_for_status()
    charge = response.json()
    save_order_to_db(user["id"], subtotal, charge["id"])
    send_email(user["email"], f"주문 {charge['id']}가 완료되었습니다.")
    return {"order_id": charge["id"], "status": charge["status"]}
```

```python
# test_before_checkout.py
from datetime import datetime, timezone
from unittest.mock import patch

from before_checkout import checkout

@patch("before_checkout.send_email")
@patch("before_checkout.save_order_to_db")
@patch("before_checkout.requests.post")
@patch("before_checkout.datetime")
def test_checkout_before(mock_datetime, mock_post, mock_save, mock_email):
    mock_datetime.now.return_value = datetime(2026, 5, 17, 9, 0, tzinfo=timezone.utc)
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {
        "id": "ch_1001",
        "status": "paid",
        "amount": 40000,
    }

    result = checkout(
        user={"id": 7, "email": "buyer@example.com", "payment_customer_id": "cus_777"},
        items=[
            {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
            {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
        ],
    )

    assert result == {"order_id": "ch_1001", "status": "paid"}
    mock_save.assert_called_once()
    mock_email.assert_called_once()
```

테스트가 길어진 이유는 검증하려는 비즈니스 규칙보다 외부 환경 흉내 내기에 더 많은 줄을 쓰고 있기 때문입니다.

이제 같은 요구사항을 경계를 나눈 구조로 바꾸겠습니다.

```python
# after_checkout.py
from collections.abc import Callable

from checkout import create_checkout_payload

def plan_checkout(user: dict, items: list[dict], now_iso: str, order_id_factory: Callable[[], str]) -> dict:
    payload = create_checkout_payload(user, items, now_iso=now_iso, order_id_factory=order_id_factory)
    return {
        "order_id": payload["order_id"],
        "charge_request": payload,
        "email": user["email"],
    }

def complete_checkout(plan: dict, charge: dict) -> dict:
    return {
        "order_id": plan["order_id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
        "email": plan["email"],
    }
```

```python
# test_after_checkout.py
from after_checkout import complete_checkout, plan_checkout

def test_checkout_after_refactoring():
    user = {
        "email": "buyer@example.com",
        "membership": "silver",
        "country": "KR",
        "payment_customer_id": "cus_777",
    }
    items = [
        {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
        {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
    ]

    plan = plan_checkout(
        user=user,
        items=items,
        now_iso="2026-05-17T09:00:00+00:00",
        order_id_factory=lambda: "order_9001",
    )
    result = complete_checkout(
        plan,
        charge={"id": "ch_1001", "status": "paid", "amount": 39000},
    )

    assert plan["charge_request"]["amount"] == 39000
    assert result == {
        "order_id": "order_9001",
        "status": "paid",
        "charged_amount": 39000,
        "email": "buyer@example.com",
    }
```

리팩터링 후 테스트는 외부 네트워크도, 현재 시간 patch도, DB patch도 필요 없습니다. 핵심 규칙만 남았기 때문입니다.

## 이 코드에서 주목할 점

- 순수 계산 함수는 입력과 출력만 보면 되므로 테스트 의도가 선명합니다.
- Protocol과 Fake를 쓰면 협력 객체 검증도 `patch()` 중심이 아니라 상태 확인 중심으로 바뀝니다.
- payload 조립을 별도 함수로 두면 외부 API 요청 필드가 코드와 테스트에서 동시에 문서화됩니다.
- 시간과 ID 생성 함수를 주입하면 테스트가 결정적이고 재현 가능해집니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
| --- | --- | --- |
| 비즈니스 로직과 외부 호출을 한 함수에 섞음 | 테스트가 네트워크, DB, 시간에 동시에 묶입니다 | 계산과 I/O 경계를 먼저 나눕니다 |
| Protocol 예제를 `...` 같은 빈칸으로만 남김 | 독자가 바로 복사해 실행하기 어렵습니다 | 최소한 `pass`와 구체적 메서드 이름으로 완성합니다 |
| payload 예제를 `json={...}`로 뭉개서 보여 줌 | 무엇을 검증해야 하는지 흐려집니다 | 필드를 명시한 실제 예제를 씁니다 |
| 리팩터링 후에도 patch 개수만 줄이는 데 집중함 | 설계 문제는 그대로 남을 수 있습니다 | 순수 로직을 더 안쪽으로 밀어 넣습니다 |
| 무조건 클래스로만 분리함 | 불필요한 상태가 다시 테스트를 복잡하게 만듭니다 | 가능한 부분은 함수로 남깁니다 |

## 실무에서 이렇게 씁니다

- FastAPI 서비스 계층에서 비즈니스 로직은 순수 함수로 두고, DB session과 외부 클라이언트는 경계 바깥에서 주입합니다.
- 결제, 메일, 메시지 큐 같은 연동부는 Adapter 객체로 감싸고 테스트에서는 Fake로 교체합니다.
- 레거시 코드 리팩터링은 “테스트가 돌아가게 하자”가 아니라 “순수 규칙을 분리하자”를 1차 목표로 잡습니다.
- 통합 테스트는 경계 바깥 어댑터를 검증하고, 단위 테스트는 경계 안쪽 규칙을 빠르게 검증합니다.

## 현업 개발자는 이렇게 생각합니다

숙련된 개발자는 테스트 작성이 막힐 때 pytest 기능을 더 찾기보다 “지금 이 함수가 너무 많은 일을 하는가?”를 먼저 봅니다. 테스트의 고통은 종종 설계가 내는 신호이기 때문입니다.

좋은 리팩터링은 mock 숫자를 줄이는 데서 끝나지 않습니다. 비즈니스 규칙이 코드 중심부에 남고, 바깥 연동부가 교체 가능해졌는지까지 봐야 합니다.

## 체크리스트

- [ ] 순수 계산 함수와 외부 호출 경계를 분리했다
- [ ] Protocol 또는 동등한 인터페이스로 협력 객체 계약을 드러냈다
- [ ] Fake 구현으로 핵심 서비스 테스트를 작성했다
- [ ] 시간, ID, 외부 API payload를 결정적으로 검증할 수 있게 만들었다
- [ ] 리팩터링 전 patch 벽을 리팩터링 후 순수 규칙 테스트로 바꿨다

## 연습 문제

1. 직접 `requests.post()`를 호출하는 함수를 `PaymentGateway` 어댑터로 감싸고 FakeGateway 테스트를 작성해 보세요.
2. `datetime.now()`를 직접 호출하는 기존 함수를 골라 시간 인자를 주입하는 형태로 바꿔 보세요.
3. 현재 프로젝트 코드에서 patch가 세 개 이상 필요한 테스트 하나를 골라, 어떤 경계를 분리하면 단순해질지 적어 보세요.

## 정리 및 시리즈 마무리

pytest를 잘 쓰는 것과 테스트하기 쉬운 코드를 만드는 일은 따로 떨어져 있지 않습니다. 순수 로직을 안쪽에 모으고, 외부 의존성을 경계 밖으로 밀어내면 테스트는 자연스럽게 짧아지고 설계는 더 분명해집니다. 이 시리즈의 마지막 메시지는 단순합니다. 좋은 테스트는 좋은 코드를 확인할 뿐 아니라, 좋은 코드 구조를 향해 계속 밀어 주는 설계 피드백이기도 합니다.

## 처음 질문으로 돌아가기

- **왜 어떤 함수는 테스트 하나에 patch와 mock이 여러 개씩 필요할까요?**
  - 본문의 기준은 테스트하기 쉬운 코드 구조 만들기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **의존성 주입은 어떤 지점에 적용해야 실제로 테스트가 단순해질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **순수 함수, Protocol, Fake 객체는 각각 어떤 역할을 맡으면 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [pytest 101 (1/10): 왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [pytest 101 (3/10): assert와 예외 테스트](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): fixture 이해하기](./04-fixtures.md)
- [pytest 101 (5/10): parametrization으로 테스트 케이스 늘리기](./05-parametrization.md)
- [pytest 101 (6/10): mock과 monkeypatch](./06-mock-and-monkeypatch.md)
- [pytest 101 (7/10): 파일, 환경변수, 시간 테스트하기](./07-testing-files-env-time.md)
- [pytest 101 (8/10): coverage와 테스트 품질 보기](./08-coverage.md)
- [pytest 101 (9/10): GitHub Actions에서 테스트 자동화하기](./09-ci-with-github-actions.md)
- **테스트하기 쉬운 코드 구조 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [pytest How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Dependency Injection](https://martinfowler.com/articles/injection.html)
- [Brian Okken — pytest for maintainable tests](https://pythontest.com/pytest-book/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, 테스트 가능한 코드, 의존성 주입, 소프트웨어 설계
