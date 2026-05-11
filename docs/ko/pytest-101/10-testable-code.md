---
series: pytest-101
episode: 10
title: 테스트하기 쉬운 코드 구조 만들기
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - 테스트 가능한 코드
  - 의존성 주입
  - 소프트웨어 설계
seo_description: 의존성 주입과 순수 함수로 테스트 가능한 코드를 설계하는 방법을 배웁니다.
last_reviewed: '2026-05-04'
---

# 테스트하기 쉬운 코드 구조 만들기

> pytest 101 시리즈 (10/10)


## 이 글에서 다룰 문제

mock이 5개 이상 필요한 테스트는 테스트의 문제가 아니라 코드의 문제입니다. 함수 하나가 DB 조회, API 호출, 이메일 전송을 모두 하면 테스트가 어려운 것은 당연합니다.

> "테스트하기 어려운 코드"는 "설계를 개선하라"는 피드백입니다. 테스트가 설계를 이끕니다.

테스트 용이성이 높은 코드는 변경에 유연하고, 재사용이 쉬우며, 버그를 빠르게 찾을 수 있습니다.

## 핵심 개념 잡기

> 테스트 가능한 코드 = 입력이 명확하고 출력이 예측 가능한 코드

```
[테스트하기 어려운 코드]         [테스트하기 쉬운 코드]
  함수 안에서 DB 직접 호출        DB를 파라미터로 받음
  전역 변수에 의존                인자로 값을 전달
  부작용이 내부에 숨겨짐           부작용을 외부로 분리
  datetime.now() 직접 호출        시간을 파라미터로 받음
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 의존성 주입 | 의존 객체를 외부에서 전달하여 교체 가능하게 합니다 |
| 순수 함수 | 같은 입력에 항상 같은 출력을 반환하고, 부작용이 없습니다 |
| 관심사 분리 | 비즈니스 로직과 인프라 코드를 분리합니다 |
| 테스트 용이성 | 코드를 격리하여 독립적으로 테스트할 수 있는 정도입니다 |
| 포트와 어댑터 | 비즈니스 로직(포트)과 외부 시스템(어댑터)을 분리하는 패턴입니다 |

## Before / After

의존성이 내부에 결합된 코드와 주입된 코드를 비교합니다.

```python
# before: 의존성이 내부에 결합 — mock 없이 테스트 불가
import requests
from datetime import datetime

def create_order(user_id, items):
    # DB 직접 호출
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    # 현재 시간 직접 호출
    order_date = datetime.now()
    # 외부 API 직접 호출
    payment = requests.post("https://pay.api/charge", json={...})
    # 이메일 직접 전송
    send_email(user["email"], "주문 확인")
    return {"order_id": 1, "status": "completed"}
```

```python
# after: 의존성 주입 — mock 없이 테스트 가능
def create_order(user, items, now, charge_fn, notify_fn):
    total = sum(item["price"] * item["qty"] for item in items)
    payment = charge_fn(user["id"], total)
    if payment["status"] != "success":
        return {"status": "payment_failed"}
    notify_fn(user["email"], "주문 확인")
    return {
        "order_id": payment["order_id"],
        "total": total,
        "date": now,
        "status": "completed",
    }
```

## 단계별 실습

### Step 1: 순수 함수로 비즈니스 로직 분리

```python
# pricing.py — 순수 함수: 입력 → 출력, 부작용 없음
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
# test_pricing.py — mock 불필요
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

### Step 2: 의존성 주입 패턴

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
            raise ValueError(f"사용자 {user_id}을(를) 찾을 수 없습니다")
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

    with pytest.raises(ValueError, match="찾을 수 없습니다"):
        service.get_user(999)

def test_update_name():
    repo = FakeUserRepo()
    repo.users[1] = {"id": 1, "name": "Alice"}
    service = UserService(repo)

    updated = service.update_name(1, "Bob")
    assert updated["name"] == "Bob"
    assert len(repo.saved) == 1
```

### Step 3: 관심사 분리

```python
# report.py — 데이터 처리와 출력을 분리
def aggregate_sales(transactions: list[dict]) -> dict:
    """순수 함수: 데이터 집계만 담당합니다."""
    total = sum(t["amount"] for t in transactions)
    count = len(transactions)
    avg = total / count if count > 0 else 0
    return {"total": total, "count": count, "average": round(avg, 2)}

def format_report(stats: dict) -> str:
    """순수 함수: 포맷팅만 담당합니다."""
    return (
        f"매출 리포트\n"
        f"총 매출: {stats['total']:,.0f}원\n"
        f"거래 건수: {stats['count']}건\n"
        f"평균 거래액: {stats['average']:,.0f}원"
    )

def save_report(content: str, filepath: str) -> None:
    """인프라 함수: 파일 저장만 담당합니다."""
    with open(filepath, "w") as f:
        f.write(content)
```

```python
# test_report.py — 각 관심사를 독립적으로 테스트
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
    assert "60,000원" in report
    assert "3건" in report
```

### Step 4: 함수 파라미터로 부작용 분리

```python
# notification.py
from typing import Callable

def process_order(
    order: dict,
    save_fn: Callable[[dict], None],
    notify_fn: Callable[[str, str], None],
) -> dict:
    """비즈니스 로직만 담당합니다. 부작용은 주입된 함수가 처리합니다."""
    if order["total"] <= 0:
        raise ValueError("주문 금액은 0보다 커야 합니다")

    order["status"] = "confirmed"
    save_fn(order)
    notify_fn(order["email"], f"주문 {order['id']} 확인")
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
    with pytest.raises(ValueError, match="0보다 커야"):
        process_order(
            order={"id": 1, "total": 0, "email": "a@test.com"},
            save_fn=lambda o: None,
            notify_fn=lambda e, m: None,
        )
```

### Step 5: 리팩터링 전후 테스트 비교

```python
# 리팩터링 전: mock 5개 필요
# def test_create_order():
#     with patch("module.db") as mock_db, \
#          patch("module.requests") as mock_req, \
#          patch("module.send_email") as mock_email, \
#          patch("module.datetime") as mock_dt, \
#          patch("module.logger") as mock_log:
#         ...  # 설정 코드 30줄

# 리팩터링 후: mock 0개
def test_calculate_order_total():
    items = [{"price": 10000, "qty": 2}]
    total = calculate_total(items, "gold", "KR")
    assert total["total"] == 17000.0  # 20000 - 3000(15%) + 0(배송)
```

## 이 코드에서 주목할 점

- 순수 함수는 입력과 출력만 검증하면 되므로 테스트가 간결합니다
- Protocol을 사용한 의존성 주입으로 Fake 구현체를 쉽게 만듭니다
- 관심사 분리로 데이터 처리, 포맷팅, I/O를 독립적으로 테스트합니다
- 함수 파라미터로 부작용을 주입하면 lambda로 간단히 테스트합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 하나의 함수에 비즈니스 로직과 I/O를 혼합 | mock 없이 테스트할 수 없습니다 | 로직과 I/O를 분리합니다 |
| 전역 객체에 직접 의존 | 테스트 간 상태 오염이 발생합니다 | 의존성을 파라미터로 주입합니다 |
| mock을 과도하게 사용 | 구현 세부사항에 테스트가 결합됩니다 | 설계를 개선하여 mock 필요성을 줄입니다 |
| 테스트를 위한 코드 변경을 거부 | 테스트 용이성은 좋은 설계의 지표입니다 | 테스트가 설계를 이끌도록 합니다 |
| 모든 것을 클래스로 만듦 | 불필요한 상태가 테스트를 복잡하게 합니다 | 가능하면 순수 함수를 우선 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 비즈니스 로직을 순수 함수로 작성하여 도메인 테스트를 빠르게 실행합니다
- Repository 패턴으로 DB 접근을 분리하여 Fake 구현체로 테스트합니다
- FastAPI의 Depends로 의존성을 주입하고 테스트에서 override합니다
- 이벤트 핸들러를 분리하여 이벤트 발행과 처리를 독립적으로 테스트합니다
- 레거시 코드를 리팩터링할 때 "테스트하기 쉬운 구조"를 목표로 삼습니다

## 현업 개발자는 이렇게 생각합니다

테스트하기 어려운 코드를 만나면 "어떻게 mock할까?"가 아니라 "어떻게 설계를 바꿀까?"를 먼저 생각합니다. mock은 임시 해결책이고, 좋은 설계는 근본 해결책입니다.

TDD(Test-Driven Development)의 진정한 가치는 "테스트를 먼저 작성하는 것"이 아니라, "테스트하기 쉬운 설계를 강제하는 것"입니다.

## 체크리스트

- [ ] 순수 함수로 비즈니스 로직을 분리했다
- [ ] 의존성 주입으로 외부 의존성을 교체 가능하게 했다
- [ ] Protocol로 인터페이스를 정의하고 Fake를 만들었다
- [ ] 관심사 분리로 각 레이어를 독립적으로 테스트했다
- [ ] mock 없이 핵심 비즈니스 로직을 테스트했다

## 정리 및 시리즈 마무리

이 시리즈에서 pytest의 기본부터 테스트 가능한 설계까지 배웠습니다. 테스트는 단순히 "코드가 동작하는지 확인하는 도구"가 아니라, "좋은 설계를 이끄는 피드백 루프"입니다. 테스트를 먼저 생각하면 자연스럽게 좋은 코드가 나옵니다.

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
- [pytest — 공식 문서](https://docs.pytest.org/)
- [Cosmic Python — Architecture Patterns with Python](https://www.cosmicpython.com/)
- [Martin Fowler — Dependency Injection](https://martinfowler.com/articles/injection.html)
