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

## 먼저 던지는 질문

- 테스트는 개발 속도를 늦추는 작업일까요, 아니면 오히려 속도를 높이는 투자일까요?
- 단위 테스트, 통합 테스트, E2E 테스트는 무엇이 다를까요?
- 수동 테스트와 자동화 테스트는 어떤 차이를 만들까요?

## 큰 그림

![pytest 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/01/01-01-big-picture.ko.png)

*pytest 101 1장 흐름 개요*

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

Tags: Python, pytest, Testing, 소프트웨어 품질, 자동화 테스트
