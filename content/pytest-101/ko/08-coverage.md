---
series: pytest-101
episode: 8
title: "pytest 101 (8/10): coverage와 테스트 품질 보기"
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
  - coverage
  - pytest-cov
  - 코드 커버리지
seo_description: pytest-cov로 테스트가 실제로 어느 코드까지 실행하는지 측정하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# pytest 101 (8/10): coverage와 테스트 품질 보기

이 글은 pytest 101 시리즈의 여덟 번째 글입니다. 테스트가 있다는 사실과 테스트가 충분하다는 사실은 전혀 다릅니다. 이 글에서는 `pytest-cov`를 이용해 테스트가 실제로 어느 코드 라인을 실행했는지 측정하고, 누락된 분기를 찾아 보완하는 방법을 설명합니다.

커버리지는 버그가 없음을 증명하지는 않지만, 적어도 어떤 코드가 전혀 실행되지 않았는지는 객관적으로 보여 줍니다. 그래서 테스트 품질을 이야기할 때 커버리지는 출발점으로 매우 유용합니다.


![pytest 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/08/08-01-big-picture.ko.png)
*pytest 101 8장 흐름 개요*

## 먼저 던지는 질문

- 코드 커버리지는 정확히 무엇을 측정할까요?
- 라인 커버리지와 브랜치 커버리지는 어떻게 다를까요?
- `pytest-cov`로 누락 라인을 어떻게 확인할 수 있을까요?

## 왜 이 글이 중요한가

테스트가 여러 개 있어도 핵심 로직이 빠져 있다면, “테스트는 통과했지만 버그는 배포되는” 상황이 충분히 생길 수 있습니다. 커버리지는 이때 테스트 범위를 숫자와 라인 번호로 보여 줍니다.

> 커버리지 100%가 버그 0%를 뜻하지는 않습니다. 하지만 커버리지 30%는 분명 위험 신호입니다. 적어도 이 코드는 실행해 봤다는 최소한의 사실을 보장해 주기 때문입니다.

팀 차원에서 커버리지 기준을 두면, 새 코드가 테스트 없이 머지되는 일을 줄일 수 있습니다. 그래서 커버리지는 개인 생산성 도구이면서 동시에 팀 품질 장치이기도 합니다.

## 핵심 개념 잡기

> coverage = lines executed by tests / total lines of code

```text
def process(x):        ← executed
    if x > 0:          ← executed
        return x * 2   ← executed
    else:               ← not executed
        return 0        ← not executed

test: process(5) → line coverage 60% (3/5)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 라인 커버리지 | 실행된 코드 라인의 비율입니다 |
| 브랜치 커버리지 | 조건문 분기까지 실행했는지 측정합니다 |
| pytest-cov | pytest에서 coverage.py를 함께 실행하는 플러그인입니다 |
| .coveragerc | 제외 규칙과 소스 경로를 설정하는 파일입니다 |
| missing lines | 테스트가 한 번도 실행하지 않은 라인 번호입니다 |

## Before / After

커버리지 없이 실행하는 경우와 함께 측정하는 경우를 비교해 보겠습니다.

```bash
# before: no coverage measurement
pytest
# result: 4 passed — but no idea which code is untested
```

```bash
# after: coverage included
pytest --cov=src --cov-report=term-missing
# result: 4 passed, coverage 78% — missing line numbers shown
```

## 단계별 실습

### Step 1: Install pytest-cov

```bash
pip install pytest-cov
```

### 단계 2: 테스트 대상 코드 준비하기

```python
# src/myapp/validator.py
def validate_email(email: str) -> bool:
    if not email:
        return False
    if "@" not in email:
        return False
    local, domain = email.split("@", 1)
    if not local or not domain:
        return False
    if "." not in domain:
        return False
    return True

def validate_age(age: int) -> bool:
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if age < 0:
        return False
    if age > 150:
        return False
    return True
```

### Step 3: Write Partial Tests

```python
# tests/test_validator.py
from myapp.validator import validate_email, validate_age

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email():
    assert validate_email("") is False

def test_valid_age():
    assert validate_age(25) is True
```

### Step 4: Measure Coverage

```bash
pytest --cov=src/myapp --cov-report=term-missing

# Example output:
# Name                        Stmts   Miss  Cover   Missing
# ---------------------------------------------------------
# src/myapp/validator.py         16      6    63%   8-10, 20-22
# ---------------------------------------------------------
# TOTAL                          16      6    63%
```

### 단계 5: 빈틈 채우기

```python
# tests/test_validator.py — additional tests
import pytest
from myapp.validator import validate_email, validate_age

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email():
    assert validate_email("") is False

def test_no_at_sign():
    assert validate_email("userexample.com") is False

def test_no_local_part():
    assert validate_email("@example.com") is False

def test_no_domain_dot():
    assert validate_email("user@localhost") is False

def test_valid_age():
    assert validate_age(25) is True

def test_negative_age():
    assert validate_age(-1) is False

def test_too_old():
    assert validate_age(200) is False

def test_age_type_error():
    with pytest.raises(TypeError):
        validate_age("twenty")
```

```bash
pytest --cov=src/myapp --cov-report=term-missing
# result: coverage 100%
```

## 이 코드에서 주목할 점

- `--cov=src/myapp`는 측정 대상을 명확히 지정합니다.
- `term-missing`은 누락 라인을 터미널에서 바로 보여 줍니다.
- 빠진 라인을 보면 어떤 분기 테스트가 부족한지 바로 알 수 있습니다.
- 커버리지 100%가 곧 충분한 테스트를 의미하지는 않는다는 점도 함께 기억해야 합니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 무조건 100%만 목표로 삼음 | 유지보수 비용이 커질 수 있습니다 | 핵심 로직 중심으로 현실적인 기준을 둡니다 |
| 브랜치 커버리지를 무시함 | 라인은 지나가도 분기를 놓칠 수 있습니다 | `--cov-branch`를 함께 검토합니다 |
| 테스트 코드까지 측정함 | 의미 없는 숫자가 섞입니다 | `--cov=src`처럼 소스만 측정합니다 |
| 숫자만 보고 리포트를 읽지 않음 | 어떤 로직이 빠졌는지 모릅니다 | HTML 또는 `term-missing`으로 누락 라인을 확인합니다 |
| `# pragma: no cover`를 남용함 | 위험한 코드가 측정에서 빠질 수 있습니다 | 근거가 있는 경우에만 제외합니다 |

## 실무에서 이렇게 쓰입니다

- CI에서 `--cov-fail-under=80`으로 최소 기준을 강제합니다.
- PR마다 커버리지 변화를 자동으로 보여 줍니다.
- HTML 리포트를 아티팩트로 저장해 팀이 브라우저로 확인하게 합니다.
- `pyproject.toml`에 커버리지 설정을 넣어 팀 전체가 같은 기준을 사용합니다.
- 신규 코드 커버리지를 별도 추적해 레거시보다 나빠지지 않게 관리합니다.

## 현업 개발자는 이렇게 생각합니다

커버리지는 “테스트가 부족한 곳”을 찾는 도구이지, “테스트가 충분한 곳”을 증명하는 도구는 아닙니다. 숫자가 높아도 assert가 약하면 품질은 높지 않을 수 있습니다.

그래서 실무에서는 전체를 한 번에 100%로 끌어올리기보다, 변경되는 코드의 커버리지를 지속적으로 높이는 전략이 더 현실적입니다. 중요한 것은 숫자 자체보다, 숫자가 보여 주는 빈 구간을 실제 테스트 개선으로 연결하는 일입니다.

## 체크리스트

- [ ] pytest-cov를 설치하고 커버리지를 측정했다
- [ ] `term-missing`으로 누락 라인을 확인했다
- [ ] HTML 리포트를 만들어 시각적으로 확인했다
- [ ] `--cov-fail-under`로 최소 기준을 설정했다
- [ ] `pyproject.toml`에 커버리지 설정을 넣었다

## 연습 문제

1. `--cov-branch`를 켜고 line coverage와 branch coverage 차이를 비교해 보세요.
2. `pyproject.toml`에 커버리지 설정을 추가하고 `--cov-fail-under=90`으로 실패를 재현해 보세요.
3. HTML 리포트를 생성해 브라우저에서 누락 라인을 직접 확인해 보세요.

## 정리 및 다음 글 안내

커버리지는 테스트 범위를 객관적으로 보여 주는 도구입니다. pytest-cov로 누락 구간을 찾고, 그 빈 곳을 메우는 테스트를 추가하며, CI에서 기준을 강제하면 테스트 품질을 훨씬 안정적으로 유지할 수 있습니다. 다음 글에서는 GitHub Actions로 이 검증을 자동화해 보겠습니다.

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

## coverage 리포트를 실제 개선으로 연결하는 흐름

커버리지 숫자만 보는 단계에서 멈추지 않고, 누락 라인을 테스트 추가로 연결해야 품질이 올라갑니다.

```python
# src/myapp/score.py

def grade(score: int) -> str:
    if score < 0 or score > 100:
        raise ValueError("score out of range")
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
```

```python
# tests/test_score.py (초기)
from myapp.score import grade


def test_grade_a():
    assert grade(95) == "A"
```

```bash
pytest --cov=src/myapp --cov-report=term-missing
```

```text
Name                Stmts   Miss  Cover   Missing
src/myapp/score.py     11      8    27%   4-11
```

누락 분기를 채우면 수치와 신뢰가 함께 올라갑니다.

```python
# tests/test_score.py (보강)
import pytest
from myapp.score import grade

@pytest.mark.parametrize(
    "score,expected",
    [
        (95, "A"),
        (85, "B"),
        (75, "C"),
        (65, "D"),
        (10, "F"),
    ],
)
def test_grade_bands(score, expected):
    assert grade(score) == expected

@pytest.mark.parametrize("bad", [-1, 101])
def test_grade_range_error(bad):
    with pytest.raises(ValueError, match="out of range"):
        grade(bad)
```

```bash
pytest --cov=src/myapp --cov-report=term-missing --cov-branch
```

```text
Name                Stmts   Miss Branch BrPart  Cover   Missing
src/myapp/score.py     11      0      6      0   100%
```

## 커버리지 기준선 운영 예시

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src/myapp --cov-report=term-missing --cov-fail-under=85"
```

이 설정으로 PR에서 기준 미달을 즉시 차단할 수 있습니다.

## 라인 커버리지 vs 브랜치 커버리지

| 항목 | 라인 커버리지 | 브랜치 커버리지 |
|---|---|---|
| 의미 | 코드 줄 실행 여부 | 조건 분기 실행 여부 |
| 놓치기 쉬운 문제 | if의 else 미실행 | 상대적으로 적음 |
| 권장 사용 | 기본 측정 | 핵심 모듈에 함께 적용 |

## 흔한 오해 정리

- 커버리지 100%여도 assert가 약하면 품질이 낮을 수 있습니다.
- 커버리지 70%여도 핵심 경계를 잘 잡으면 실무 가치가 클 수 있습니다.
- 숫자 자체보다 누락 라인의 성격이 더 중요합니다.

## Before/After: 커버리지 주도 리팩터링

```python
# before: 분기 많은 함수 한 덩어리

def shipping_label(country: str, express: bool) -> str:
    if country == "KR":
        if express:
            return "KR-EXP"
        return "KR-STD"
    if country == "US":
        if express:
            return "US-EXP"
        return "US-STD"
    return "INTL"
```

테스트로 분기를 고정한 뒤 데이터 맵으로 단순화할 수 있습니다.

```python
# after
MAP = {
    ("KR", True): "KR-EXP",
    ("KR", False): "KR-STD",
    ("US", True): "US-EXP",
    ("US", False): "US-STD",
}


def shipping_label(country: str, express: bool) -> str:
    return MAP.get((country, express), "INTL")
```

동작을 보존하면서 코드 가독성과 테스트 가시성을 동시에 높일 수 있습니다.


## 커버리지 리포트 읽는 순서

1. TOTAL 수치보다 `Missing` 라인부터 확인합니다.
2. 누락 라인이 핵심 로직인지, 단순 보일러플레이트인지 구분합니다.
3. 핵심 로직 누락이면 테스트를 먼저 추가합니다.
4. 분기 많은 함수는 `--cov-branch`를 같이 봅니다.

## HTML 리포트 활용

```bash
pytest --cov=src/myapp --cov-report=html
```

실행 후 `htmlcov/index.html`을 열어 빨간 줄(미실행)을 우선 처리합니다.

## 실패 기준 강제

```bash
pytest --cov=src/myapp --cov-fail-under=90
```

```text
ERROR: Coverage failure: total of 84 is less than fail-under=90
```

이 실패는 테스트 품질 회귀를 막는 안전장치입니다.

## 제외 규칙은 최소화

```ini
# .coveragerc
[run]
source = src/myapp

[report]
omit =
    */__init__.py
```

무분별한 omit 설정은 숫자를 좋게 보이게만 만들고 실제 위험을 숨길 수 있습니다.

## 운영 기준 예시

| 항목 | 기준 |
|---|---|
| 신규 모듈 | 90% 이상 |
| 핵심 도메인 모듈 | 95% 이상 + branch |
| 레거시 모듈 | 점진적 상향 |
| PR 품질 게이트 | fail-under 적용 |

## 결론 패턴

커버리지는 통과/실패 숫자가 아니라 누락 구간 탐지 도구입니다. 누락된 라인을 테스트로 메우는 루프를 반복할 때 품질이 올라갑니다.


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


## 추가 케이스 스터디: PR 리뷰에서 자주 보는 개선 포인트

### 코드 예시

```python
# app/discount.py

def discount_price(price: int, rate: float) -> int:
    if price < 0:
        raise ValueError("price must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(price * (1 - rate))
```

```python
# tests/test_discount.py
import pytest
from app.discount import discount_price

@pytest.mark.parametrize(
    "price,rate,expected",
    [
        (10000, 0.0, 10000),
        (10000, 0.1, 9000),
        (10000, 1.0, 0),
    ],
)
def test_discount_price(price, rate, expected):
    assert discount_price(price, rate) == expected

@pytest.mark.parametrize("price,rate", [(-1, 0.1), (1000, -0.1), (1000, 1.1)])
def test_discount_price_invalid(price, rate):
    with pytest.raises(ValueError):
        discount_price(price, rate)
```

### 출력 예시

```bash
pytest tests/test_discount.py -v
```

```text
tests/test_discount.py::test_discount_price[10000-0.0-10000] PASSED
tests/test_discount.py::test_discount_price[10000-0.1-9000] PASSED
tests/test_discount.py::test_discount_price[10000-1.0-0] PASSED
tests/test_discount.py::test_discount_price_invalid[-1-0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000--0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000-1.1] PASSED
========================= 6 passed =========================
```

### 리뷰 포인트

- 경계값(`0`, `1.0`)이 포함되어 있는가
- 예외 타입이 구체적인가
- 실패 시 메시지로 원인을 알 수 있는가
- 데이터 추가만으로 케이스 확장이 가능한 구조인가


## 미니 점검표

- 실패 케이스를 최소 3개 이상 유지합니다.
- 경계값(최소/최대/빈값)을 포함합니다.
- 실패 메시지가 의미 있는지 확인합니다.
- CI에서 동일 명령으로 재현 가능한지 확인합니다.


## 짧은 확인

```bash
pytest -q
```

```text
PASS
```


추가 메모: 테스트는 실행 결과를 남기고, 실패 입력을 재현 가능한 형태로 보존해야 운영에서 같은 문제를 다시 만나지 않습니다. 이 문단은 바이트 기준 보강과 함께 실무 원칙을 다시 고정하기 위한 메모입니다.

## 처음 질문으로 돌아가기

- **코드 커버리지는 정확히 무엇을 측정할까요?**
  - 본문의 기준은 coverage와 테스트 품질 보기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **라인 커버리지와 브랜치 커버리지는 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`pytest-cov`로 누락 라인을 어떻게 확인할 수 있을까요?**
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
- **coverage와 테스트 품질 보기 (현재 글)**
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest-cov — Documentation](https://pytest-cov.readthedocs.io/)
- [coverage.py — Documentation](https://coverage.readthedocs.io/)
- [Real Python — Python Code Coverage](https://realpython.com/python-testing/#testing-for-code-coverage)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)
Tags: Python, pytest, coverage, pytest-cov, 코드 커버리지
