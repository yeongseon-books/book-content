---
series: pytest-101
episode: 10
title: 테스트하기 쉬운 코드 구조 만들기
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
seo_description: 의존성 주입, 순수 함수, 관심사 분리로 테스트하기 쉬운 코드를 설계하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# 테스트하기 쉬운 코드 구조 만들기

이 글은 pytest 101 시리즈의 마지막 글입니다. 테스트가 어려운 이유는 종종 테스트 도구가 부족해서가 아니라 코드 설계가 외부 의존성과 부작용을 지나치게 안쪽에 끌어안고 있기 때문입니다. 이 글에서는 의존성 주입, 순수 함수, 관심사 분리를 통해 mock이 적게 필요한 구조를 만드는 방법을 설명합니다.

테스트하기 쉬운 코드는 단지 테스트 작성이 편한 코드가 아닙니다. 변경하기 쉽고, 재사용하기 쉽고, 문제 원인을 국소화하기 쉬운 코드이기도 합니다. 결국 테스트 용이성은 설계 품질을 보여 주는 신호에 가깝습니다.

---

## 이 글에서 다룰 문제

- 어떤 코드는 왜 mock이 여러 개 필요할 만큼 테스트하기 어려울까요?
- 의존성 주입은 테스트를 어떻게 단순하게 만들까요?
- 순수 함수와 관심사 분리는 왜 테스트 가능성과 직결될까요?
- 레거시 코드를 리팩터링할 때 무엇을 목표로 잡아야 할까요?

## 왜 이 글이 중요한가

테스트 하나를 작성하려고 할 때 mock이 다섯 개 이상 필요하다면, 문제는 대개 테스트가 아니라 코드 구조에 있습니다. 함수 하나가 DB 조회, API 호출, 메일 발송, 시간 조회까지 모두 맡고 있다면, 테스트가 복잡해지는 것은 자연스러운 결과입니다.

> “테스트하기 어렵다”는 말은 종종 “설계를 개선해야 한다”는 피드백입니다. 테스트는 품질 확인 도구이면서 동시에 설계 피드백 루프이기도 합니다.

테스트하기 쉬운 코드는 변화에 더 강합니다. 외부 의존성을 교체하기 쉽고, 비즈니스 로직을 독립적으로 검증할 수 있으며, 버그 원인을 더 작은 단위에서 찾을 수 있습니다.

## 핵심 개념 잡기

> testable code = clear inputs + predictable outputs

```text
[Hard to Test]                   [Easy to Test]
  DB call inside the function     DB passed as parameter
  Depends on global variables     Values passed as arguments
  Side effects hidden inside      Side effects separated out
  datetime.now() called directly  Time passed as parameter
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 의존성 주입 | 외부 의존성을 함수 인자나 생성자로 전달해 교체 가능하게 만드는 방식입니다 |
| 순수 함수 | 같은 입력에 항상 같은 출력을 반환하고 부작용이 없는 함수입니다 |
| 관심사 분리 | 비즈니스 로직과 인프라 코드를 분리하는 설계 원칙입니다 |
| 테스트 용이성 | 코드를 격리해 독립적으로 검증할 수 있는 정도입니다 |
| 포트와 어댑터 | 비즈니스 로직과 외부 시스템 연결부를 분리하는 패턴입니다 |

## Before / After

하드코딩된 의존성과 주입된 의존성을 비교해 보겠습니다.

```python
# before: dependencies hard-coded — untestable without mocks
import requests
from datetime import datetime

def create_order(user_id, items):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    order_date = datetime.now()
    payment = requests.post("https://pay.api/charge", json={...})
    send_email(user["email"], "Order confirmed")
    return {"order_id": 1, "status": "completed"}
```

```python
# after: dependencies injected — testable without mocks
def create_order(user, items, now, charge_fn, notify_fn):
    total = sum(item["price"] * item["qty"] for item in items)
    payment = charge_fn(user["id"], total)
    if payment["status"] != "success":
        return {"status": "payment_failed"}
    notify_fn(user["email"], "Order confirmed")
    return {
        "order_id": payment["order_id"],
        "total": total,
        "date": now,
        "status": "completed",
    }
```

## 단계별 실습

### Step 1: Isolate Business Logic with Pure Functions

```python
# pricing.py — pure functions: input → output, no side effects
def calculate_discount(total: float, membership: str) -> float:
    rates = {"gold": 0.15, "silver": 0.10, "bronze": 0.05}
    rate = rates.get(membership, 0.0)
    return round(total * rate, 2)

def calculate_shipping(total: float, country: str) -> float:
    if country == "KR":
        return 0.0 if total >= 50000 else 3000.0
    return 15000.0

def calculate_total(
    items: list[dict],
    membership: str,
    country: str,
) -> dict:
    subtotal = sum(item["price"] * item["qty"] for item in items)
    discount = calculate_discount(subtotal, membership)
    shipping = calculate_shipping(subtotal - discount, country)
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": subtotal - discount + shipping,
    }
```

```python
# test_pricing.py — no mocks needed
from pricing import calculate_discount, calculate_shipping, calculate_total

def test_gold_discount():
    assert calculate_discount(100000, "gold") == 15000.0

def test_no_discount():
    assert calculate_discount(100000, "none") == 0.0

def test_free_shipping_kr():
    assert calculate_shipping(60000, "KR") == 0.0

def test_paid_shipping_kr():
    assert calculate_shipping(30000, "KR") == 3000.0

def test_total_calculation():
    items = [{"price": 10000, "qty": 3}, {"price": 5000, "qty": 2}]
    result = calculate_total(items, "silver", "KR")
    assert result["subtotal"] == 40000
    assert result["discount"] == 4000.0
    assert result["shipping"] == 3000.0
    assert result["total"] == 39000.0
```

### Step 2: Dependency Injection Pattern

```python
# user_service.py
from typing import Protocol

class UserRepository(Protocol):
    def find_by_id(self, user_id: int) -> dict | None: ...
    def save(self, user: dict) -> None: ...

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user(self, user_id: int) -> dict:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

    def update_name(self, user_id: int, new_name: str) -> dict:
        user = self.get_user(user_id)
        user["name"] = new_name
        self.repo.save(user)
        return user
```

```python
# test_user_service.py
import pytest
from user_service import UserService

class FakeUserRepo:
    def __init__(self):
        self.users = {}
        self.saved = []

    def find_by_id(self, user_id):
        return self.users.get(user_id)

    def save(self, user):
        self.saved.append(user)

def test_get_user():
    repo = FakeUserRepo()
    repo.users[1] = {"id": 1, "name": "Alice"}
    service = UserService(repo)

    user = service.get_user(1)
    assert user["name"] == "Alice"

def test_get_missing_user():
    repo = FakeUserRepo()
    service = UserService(repo)

    with pytest.raises(ValueError, match="not found"):
        service.get_user(999)

def test_update_name():
    repo = FakeUserRepo()
    repo.users[1] = {"id": 1, "name": "Alice"}
    service = UserService(repo)

    updated = service.update_name(1, "Bob")
    assert updated["name"] == "Bob"
    assert len(repo.saved) == 1
```

### Step 3: Separation of Concerns

```python
# report.py — separate data processing from output
def aggregate_sales(transactions: list[dict]) -> dict:
    """Pure function: handles data aggregation only."""
    total = sum(t["amount"] for t in transactions)
    count = len(transactions)
    avg = total / count if count > 0 else 0
    return {"total": total, "count": count, "average": round(avg, 2)}

def format_report(stats: dict) -> str:
    """Pure function: handles formatting only."""
    return (
        f"Sales Report\n"
        f"Total Sales: ${stats['total']:,.0f}\n"
        f"Transactions: {stats['count']}\n"
        f"Average: ${stats['average']:,.0f}"
    )

def save_report(content: str, filepath: str) -> None:
    """Infrastructure function: handles file I/O only."""
    with open(filepath, "w") as f:
        f.write(content)
```

```python
# test_report.py — test each concern independently
from report import aggregate_sales, format_report

def test_aggregate_sales():
    transactions = [
        {"amount": 10000},
        {"amount": 20000},
        {"amount": 30000},
    ]
    result = aggregate_sales(transactions)
    assert result == {"total": 60000, "count": 3, "average": 20000.0}

def test_aggregate_empty():
    result = aggregate_sales([])
    assert result == {"total": 0, "count": 0, "average": 0}

def test_format_report():
    stats = {"total": 60000, "count": 3, "average": 20000.0}
    report = format_report(stats)
    assert "$60,000" in report
    assert "3" in report
```

### Step 4: Separating Side Effects via Function Parameters

```python
# notification.py
from typing import Callable

def process_order(
    order: dict,
    save_fn: Callable[[dict], None],
    notify_fn: Callable[[str, str], None],
) -> dict:
    """Business logic only. Injected functions handle side effects."""
    if order["total"] <= 0:
        raise ValueError("Order total must be greater than 0")

    order["status"] = "confirmed"
    save_fn(order)
    notify_fn(order["email"], f"Order {order['id']} confirmed")
    return order
```

```python
# test_notification.py
import pytest
from notification import process_order

def test_process_order():
    saved = []
    notifications = []

    result = process_order(
        order={"id": 1, "total": 10000, "email": "a@test.com"},
        save_fn=lambda o: saved.append(o),
        notify_fn=lambda email, msg: notifications.append((email, msg)),
    )

    assert result["status"] == "confirmed"
    assert len(saved) == 1
    assert len(notifications) == 1
    assert notifications[0][0] == "a@test.com"

def test_invalid_order():
    with pytest.raises(ValueError, match="greater than 0"):
        process_order(
            order={"id": 1, "total": 0, "email": "a@test.com"},
            save_fn=lambda o: None,
            notify_fn=lambda e, m: None,
        )
```

### Step 5: Before and After Refactoring

```python
# before refactoring: needs 5 mocks
# def test_create_order():
#     with patch("module.db") as mock_db, \
#          patch("module.requests") as mock_req, \
#          patch("module.send_email") as mock_email, \
#          patch("module.datetime") as mock_dt, \
#          patch("module.logger") as mock_log:
#         ...  # 30 lines of setup

# after refactoring: zero mocks
def test_calculate_order_total():
    items = [{"price": 10000, "qty": 2}]
    total = calculate_total(items, "gold", "KR")
    assert total["total"] == 17000.0  # 20000 - 3000(15%) + 0(shipping)
```

## 이 코드에서 주목할 점

- 순수 함수는 입력과 출력만 검증하면 되므로 테스트가 짧고 명확합니다.
- Protocol 기반 의존성 주입은 Fake 구현체를 만들기 쉽게 합니다.
- 관심사를 분리하면 데이터 처리, 포맷팅, I/O를 각각 독립적으로 테스트할 수 있습니다.
- 부작용을 함수 인자로 주입하면 단순한 lambda만으로도 테스트가 가능합니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 비즈니스 로직과 I/O를 한 함수에 섞음 | mock 없이 테스트하기 어려워집니다 | 로직과 인프라를 분리합니다 |
| 전역 객체에 직접 의존함 | 상태가 새어 나가 테스트가 불안정해집니다 | 의존성을 외부에서 주입합니다 |
| mock을 지나치게 많이 씀 | 구현 세부사항에 테스트가 묶입니다 | mock 수를 줄이도록 설계를 바꿉니다 |
| 테스트 가능성을 위해 코드를 바꾸지 않으려 함 | 설계 개선 기회를 놓칩니다 | 테스트 피드백을 설계 입력으로 받아들입니다 |
| 모든 것을 클래스로 만듦 | 불필요한 상태가 테스트를 복잡하게 합니다 | 가능한 곳은 순수 함수로 단순화합니다 |

## 실무에서 이렇게 쓰입니다

- 핵심 비즈니스 로직을 순수 함수로 빼서 빠른 도메인 테스트를 만듭니다.
- Repository 패턴으로 DB 접근을 감싸 Fake 구현으로 검증합니다.
- FastAPI의 의존성 주입 구조와도 자연스럽게 연결됩니다.
- 이벤트 발행과 데이터 처리 로직을 분리해 각각 테스트합니다.
- 레거시 리팩터링의 목표를 “더 예쁜 코드”가 아니라 “더 테스트하기 쉬운 구조”로 잡습니다.

## 현업 개발자는 이렇게 생각합니다

경험이 많은 개발자는 테스트하기 어려운 코드를 보면 먼저 “이걸 어떻게 mock하지?”보다 “이 설계를 어떻게 바꾸면 되지?”를 생각합니다. mock은 일시적 우회책일 수 있지만, 설계 개선은 반복 비용 자체를 낮춥니다.

TDD의 진짜 가치를 “테스트를 먼저 쓰는 절차”에만 두면 반쪽짜리 이해가 됩니다. 더 중요한 가치는 테스트를 통해 자연스럽게 테스트하기 쉬운 구조로 끌려가게 된다는 점입니다.

## 체크리스트

- [ ] 비즈니스 로직을 순수 함수로 분리했다
- [ ] 외부 의존성을 의존성 주입으로 교체 가능하게 했다
- [ ] Protocol과 Fake 구현으로 협력 객체를 테스트했다
- [ ] 관심사를 나누어 각 레이어를 독립적으로 검증했다
- [ ] 핵심 로직을 mock 없이 테스트했다

## 연습 문제

1. DB를 직접 조회하는 함수를 Repository 패턴으로 바꾸고 Fake Repository로 테스트해 보세요.
2. `datetime.now()`를 직접 호출하는 함수를 시간 인자를 받도록 바꾼 뒤 테스트해 보세요.
3. 파일 읽기 → 데이터 처리 → 파일 쓰기 함수를 세 단계로 나누고 각각을 독립 테스트해 보세요.

## 정리 및 시리즈 마무리

이 시리즈는 pytest 입문부터 테스트하기 쉬운 설계까지 한 흐름으로 다뤘습니다. 결국 테스트는 “코드가 맞는지 확인하는 도구”이면서 동시에 “좋은 설계로 밀어 주는 피드백 장치”이기도 합니다. 테스트를 먼저 생각하는 습관은 더 안전한 코드와 더 다루기 쉬운 구조로 자연스럽게 이어집니다.

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [assert와 예외 테스트](./03-assert-and-exceptions.md)
- [fixture 이해하기](./04-fixtures.md)
- [parametrization으로 테스트 케이스 늘리기](./05-parametrization.md)
- [mock과 monkeypatch](./06-mock-and-monkeypatch.md)
- [파일, 환경변수, 시간 테스트하기](./07-testing-files-env-time.md)
- [coverage와 테스트 품질 보기](./08-coverage.md)
- [GitHub Actions에서 테스트 자동화하기](./09-ci-with-github-actions.md)
- **테스트하기 쉬운 코드 구조 만들기 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [pytest — Documentation](https://docs.pytest.org/)
- [Cosmic Python — Architecture Patterns with Python](https://www.cosmicpython.com/)
- [Martin Fowler — Dependency Injection](https://martinfowler.com/articles/injection.html)

Tags: Python, pytest, 테스트 가능한 코드, 의존성 주입, 소프트웨어 설계
