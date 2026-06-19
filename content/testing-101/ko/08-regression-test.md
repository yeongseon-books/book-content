---
series: testing-101
episode: 8
title: "Testing 101 (8/10): 회귀 테스트"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Testing
  - Regression
  - Bugfix
  - Quality
  - pytest
seo_description: 동일한 버그가 다시 발생하지 않도록 고정하는 회귀 테스트의 개념과 작성 절차를 알아봅니다.
last_reviewed: '2026-05-12'
---

# Testing 101 (8/10): 회귀 테스트

버그를 한 번 고친 뒤에도 몇 달 뒤 같은 문제가 다시 돌아오는 경우가 있습니다. 코드는 바뀌고 사람도 바뀌기 때문입니다. 누군가 예전 맥락을 모른 채 같은 경로를 다시 깨뜨리면, 팀은 이미 고친 문제를 다시 조사하고 다시 수정하게 됩니다.

소프트웨어는 스스로 기억하지 않습니다. 그래서 버그 수정을 코드로 얼려 두는 장치가 필요합니다. 그 역할을 하는 것이 회귀 테스트입니다.

이 글은 Testing 101 시리즈의 여덟 번째 글입니다. 여기서는 회귀 테스트의 의미, 버그를 테스트로 재현하고 수정으로 연결하는 흐름, git bisect로 원인 커밋을 좁히는 방법, 그리고 회귀 테스트를 어느 계층에 두는 편이 좋은지 정리하겠습니다.

![Testing 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/08/08-01-diagram.ko.png)
*Testing 101 8장 흐름 개요*
> 회귀 테스트는 과거의 고통을 재무보험입니다. 한 번 깨진 부분이 다시 깨지지 않도록 합니다.

## 이 글에서 다룰 문제

- 회귀 테스트는 무엇을 막는 테스트일까요?
- 버그를 재현하고 테스트로 남기는 순서는 어떻게 될까요?
- 최소 재현 케이스는 왜 중요할까요?
- git bisect로 어떻게 원인 커밋을 추적할까요?
- 회귀 테스트가 쌓일 때 속도를 어떻게 유지할까요?

버그를 말로만 기억하면 사람과 함께 사라집니다. 이슈 트래커에 기록이 남아 있어도, 코드가 그 맥락을 스스로 막아 주지는 못합니다. 회귀 테스트는 팀의 기억을 실행 가능한 형태로 남깁니다.

특히 반복해서 사고가 나는 모듈에서는 회귀 테스트의 가치가 큽니다. 같은 버그가 돌아오는 이유는 우연이 아니라, 취약한 경계나 복잡한 설계가 남아 있다는 뜻일 때가 많기 때문입니다.

## 한눈에 보는 구조

좋은 회귀 테스트 흐름은 버그 보고에서 끝나지 않습니다. 먼저 실패하는 재현 테스트를 만들고, 그 테스트를 통과하도록 코드를 고친 뒤, CI에 넣어 다시는 조용히 돌아오지 못하게 만듭니다.

- **회귀(regression)**: 한 번 고친 동작이 나중에 다시 깨지는 현상입니다.
- **재현 테스트(repro test)**: 버그를 최소한의 입력으로 다시 일으키는 테스트입니다.
- **버그 ID**: 이슈 트래커에서 쓰는 고유 식별자입니다.
- **골든 파일**: 기대 결과를 파일 형태로 고정해 비교하는 방식입니다.
- **스냅샷 테스트**: 전체 출력 결과를 한 번에 비교하는 테스트입니다.
- **git bisect**: 이진 탐색으로 회귀가 처음 발생한 커밋을 찾는 Git 명령입니다.

## 회귀 테스트 트리거 시점

회귀 테스트를 작성할 타이밍은 단순히 버그 수정 후만이 아닙니다. 다음 표는 팀이 회귀 테스트를 고려해야 하는 주요 시점을 정리한 것입니다.

| 트리거 상황 | 왜 회귀 테스트가 필요한가 | 예시 |
|---|---|---|
| 버그 수정 | 같은 버그가 다시 발생하지 않도록 고정합니다. | PROJ-1234 음수 가격 입력 허용 |
| 리팩터링 | 동작 보존을 확인합니다. | 결제 모듈 분리 후 동작 검증 |
| 의존 업데이트 | 외부 라이브러리 변경이 기존 동작을 깨지 않는지 확인합니다. | requests 2.x → 3.x 업그레이드 |
| 설정 변경 | 환경 설정이 의도하지 않은 동작을 일으키지 않는지 확인합니다. | DB 풀 크기 조정 후 검증 |

팀이 변경의 영향 범위를 측정하려면 회귀 테스트가 필요한 시점을 미리 명시해 두는 편이 좋습니다.

## 바꾸기 전과 후

**바꾸기 전 — 구두 약속만 있는 상태**

```text
- "이 버그 고쳤습니다"라고 말하고 머지한다
- 몇 달 뒤 같은 버그가 다시 발견된다
- 팀은 이미 본 문제를 처음부터 다시 조사한다
```

**바꾼 뒤 — 회귀 테스트를 추가한 상태**

```python
# pytest.mark.regression 마커로 분류
@pytest.mark.regression
def test_regression_PROJ_1234_negative_total():
    cart = Cart()
    with pytest.raises(ValueError, match="price must be >= 0"):
        cart.add(Item(price=-1))
```

차이는 기억 방식입니다. 사람의 설명 대신 테스트가 버그의 경계를 코드 안에 남깁니다. 다음 번에 같은 경로가 깨지면 CI가 먼저 알려줍니다.

## 다섯 단계로 회귀 테스트 만들기

### 1단계 — 버그를 재현하는 실패 테스트 작성하기

버그를 수정하기 전에 먼저 실패하는 테스트를 작성합니다. 이것이 회귀 테스트의 핵심입니다.

```python
# tests/test_regression.py
import pytest
from src.cart import Cart, Item

@pytest.mark.regression
def test_regression_PROJ_1234_negative_price_rejected():
    """Adding item with negative price should raise ValueError. (PROJ-1234)"""
    cart = Cart()
    # 버그 수정 전에는 이 테스트가 반드시 실패해야 합니다.
    with pytest.raises(ValueError, match="price must be >= 0"):
        cart.add(Item(price=-100))
```

### 2단계 — 실패를 먼저 확인하기

```bash
pytest tests/test_regression.py::test_regression_PROJ_1234_negative_price_rejected -v
# FAILED ... ValueError not raised
```

이 단계를 건너뛰면 테스트가 실제로 버그를 잡는지 알 수 없습니다. 처음부터 초록색인 테스트는 재현력이 없는 장식일 수 있습니다.

### 3단계 — 코드 수정하기

```python
# src/cart.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class Item:
    name: str = ""
    price: float = 0.0

class Cart:
    def __init__(self):
        self._items: List[Item] = []

    def add(self, item: Item) -> None:
        if item.price < 0:
            raise ValueError("price must be >= 0")
        self._items.append(item)

    def total(self) -> float:
        return sum(item.price for item in self._items)
```

### 4단계 — 테스트가 통과하는지 확인하기

```bash
pytest tests/test_regression.py::test_regression_PROJ_1234_negative_price_rejected -v
# PASSED
```

### 5단계 — CI에 넣어 다시 돌아오지 못하게 하기

```bash
git add tests/test_regression.py src/cart.py
git commit -m "fix(cart): reject negative price (PROJ-1234)"
```

이 전체 흐름은 버그를 고치기 전에 반드시 재현 테스트가 먼저 실패하는 것을 확인하는 습관을 보여줍니다.

## 마커로 회귀 테스트 분류하기

회귀 테스트가 쌓일수록 분류가 중요합니다. pytest 마커를 사용하면 회귀 테스트만 선택적으로 실행할 수 있습니다.

**pytest.ini 설정**

```ini
[pytest]
markers =
    regression: marks tests as regression tests (deselect with '-m "not regression"')
    critical: marks tests covering critical user paths
```

**conftest.py — 버그 ID 메타데이터 추가**

```python
# tests/conftest.py
import pytest

def pytest_collection_modifyitems(items):
    for item in items:
        if "regression" in item.keywords:
            # 버그 ID를 이름에서 파싱해 출력에 포함
            if "PROJ_" in item.name:
                bug_id = next(
                    (part for part in item.name.split("_") if part.startswith("PROJ")),
                    None
                )
                if bug_id:
                    item.add_marker(pytest.mark.usefixtures())
```

**선택적 실행**

```bash
# 회귀 테스트만 실행
pytest -m regression -v

# 특정 버그 ID로 필터링
pytest tests/test_regression.py -k "PROJ_1234"

# 회귀 테스트 제외
pytest -m "not regression"
```

## 여러 경계 조건을 parametrize로 고정하기

한 버그가 여러 입력에서 발생했다면 parametrize로 모두 고정합니다.

```python
import pytest
from src.cart import Cart, Item

@pytest.mark.regression
@pytest.mark.parametrize("price,expected_error", [
    (-1, "price must be >= 0"),
    (-100, "price must be >= 0"),
    (-0.01, "price must be >= 0"),
])
def test_regression_PROJ_1234_various_negative_prices(price, expected_error):
    """PROJ-1234: Any negative price must be rejected."""
    cart = Cart()
    with pytest.raises(ValueError, match=expected_error):
        cart.add(Item(price=price))

@pytest.mark.regression
@pytest.mark.parametrize("price", [0, 0.01, 1, 9999.99])
def test_regression_PROJ_1234_valid_prices_accepted(price):
    """PROJ-1234: Non-negative prices must be accepted."""
    cart = Cart()
    cart.add(Item(price=price))
    assert cart.total() == price
```

이 방식은 버그 수정 범위를 명확히 하고, 경계 조건이 모두 테스트됨을 보장합니다.

## 재현 케이스를 가능한 한 낮은 계층에 두기

버그를 최소 계층에서 재현하면 유지비가 낮습니다.

| 상황 | 권장 계층 | 이유 |
|---|---|---|
| 순수 도메인 로직 버그 | 단위 테스트 | 빠르고 결정적, 의존 없음 |
| DB 저장 오류 | 통합 테스트 | 실제 DB 경계에서 발생 |
| 화면 흐름 오류 | E2E | 브라우저 상호작용 필요 |
| API 응답 형식 오류 | 통합 테스트 | HTTP 경계에서 검증 |

E2E 계층에서만 재현되는 버그도 가능한 한 아래 계층으로 내려 검증합니다. E2E 회귀 테스트는 속도가 느리고 유지비가 높습니다.

## git bisect로 원인 커밋 추적하기

회귀가 발견되었는데 어느 커밋에서 문제가 시작되었는지 모를 때 `git bisect`를 사용합니다. 이진 탐색으로 원인 커밋을 빠르게 찾습니다.

**수동 bisect**

```bash
git bisect start
git bisect bad HEAD              # 현재 커밋은 실패
git bisect good v1.2.0           # v1.2.0에서는 통과했음

# Git이 중간 커밋으로 자동 체크아웃
pytest tests/test_regression.py
# 통과하면:
git bisect good
# 실패하면:
git bisect bad
# 반복하면 문제 커밋을 찾아냄

git bisect reset                 # 원래 HEAD로 복귀
```

**자동 bisect — 테스트 스크립트 연결**

```bash
# 재현 테스트가 명확하면 완전 자동화가 가능합니다
git bisect start HEAD v1.2.0
git bisect run pytest tests/test_regression.py::test_regression_PROJ_1234_negative_price_rejected -x
```

bisect는 회귀 테스트가 명확히 실패할 때 가장 유용합니다. 플래키 테스트는 bisect 결과를 신뢰하기 어렵게 만듭니다. 재현 테스트가 결정적이어야 하는 또 다른 이유입니다.

**bisect 결과 예시**

```text
Bisecting: 3 revisions left to test after this (roughly 2 steps)
[a3f8b2c] refactor(cart): simplify item validation

...

a3f8b2c is the first bad commit
Author: Developer <dev@example.com>
Date:   Mon Jun 2 14:23:11 2026

    refactor(cart): simplify item validation
```

## 회귀 테스트가 느려지면? 병렬화와 선택적 실행

회귀 테스트가 계속 쌓이면 실행 시간이 문제가 됩니다. 다음은 속도를 관리하는 전략입니다.

**pytest-xdist로 병렬 실행**

```bash
pip install pytest-xdist
pytest tests/test_regression.py -n auto  # CPU 코어 수만큼 병렬 실행
pytest tests/test_regression.py -n 4    # 워커 4개 고정
```

병렬 실행은 테스트 간 의존이 없을 때 가장 효과적입니다. 공유 상태나 파일 의존이 있으면 간헐적 실패를 일으킬 수 있습니다.

**마커로 선택적 실행**

```bash
# PR에서는 critical 마커만
pytest -m "regression and critical" -n auto

# 야간 빌드에서는 전체
pytest tests/ -n auto
```

**비용이 높은 회귀 테스트 분리**

```python
@pytest.mark.regression
@pytest.mark.slow          # 3초 이상 걸리는 테스트
def test_regression_PROJ_5678_large_cart_performance():
    """PROJ-5678: Cart with 10,000 items must total in under 1 second."""
    import time
    cart = Cart()
    for i in range(10_000):
        cart.add(Item(price=1.0))
    start = time.perf_counter()
    total = cart.total()
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0
    assert total == 10_000.0
```

```bash
# 빠른 회귀 테스트만 PR에서 실행
pytest -m "regression and not slow"

# 느린 테스트는 야간 또는 머지 후
pytest -m "regression and slow"
```

## CI 연동

```yaml
# .github/workflows/regression.yml
name: Regression Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  regression:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-xdist

      - name: Run regression tests (PR fast path)
        run: |
          pytest -m "regression and not slow" -n auto -v \
            --tb=short \
            --junitxml=reports/regression-fast.xml

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: regression-report
          path: reports/

  regression-full:
    runs-on: ubuntu-latest
    # 야간 빌드에서만 전체 회귀 테스트 실행
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt pytest pytest-xdist

      - name: Run full regression suite
        run: pytest -m regression -n auto -v --tb=long
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|---|---|---|
| 버그 수정 후 테스트 없이 머지 | 같은 버그가 몇 달 뒤 재발 | 버그 수정 PR에 회귀 테스트를 필수로 포함 |
| 테스트를 먼저 통과시키고 실패 확인 생략 | 테스트가 실제로 버그를 잡지 못함 | 수정 전에 반드시 실패를 먼저 확인 |
| 재현 케이스를 E2E에만 작성 | 회귀 테스트가 느리고 유지비 높음 | 가능한 한 낮은 계층(단위/통합)으로 내림 |
| 버그 ID를 테스트 이름에 남기지 않음 | 왜 이 테스트가 존재하는지 추적 불가 | `test_regression_PROJ_1234_` 형식 유지 |
| 스냅샷을 이유 없이 갱신 | 테스트가 장식이 됨 | 변경 이유를 이해한 뒤 갱신, 리뷰어 확인 |
| 같은 영역에 회귀 테스트만 계속 추가 | 테스트 수는 늘지만 버그가 반복됨 | 반복 회귀는 설계 문제 신호, 리팩터링 고려 |

## 실무에서는 이렇게 생각합니다

강한 팀은 버그 수정 PR에 회귀 테스트를 거의 기본으로 요구합니다. 특히 재발 가능성이 높은 문제, 고객 영향이 큰 문제, 경계 조건과 예외 처리 문제는 더 그렇습니다.

경험 많은 엔지니어는 회귀 테스트가 반복해서 쌓이는 모듈을 보면 구조를 의심합니다. 같은 영역에서 같은 류의 버그가 계속 나온다면 테스트를 더 붙이는 것만으로는 부족하고, 설계 단순화나 리팩터링이 필요할 수 있습니다.

회귀 테스트가 쌓이는 속도도 하나의 신호입니다. 어떤 모듈에 회귀 테스트가 집중되는지 분기마다 확인하면 리팩터링 우선순위를 결정하는 데 도움이 됩니다.

## 회귀 테스트 유지 보수

회귀 테스트를 추가하는 것도 중요하지만, 시간이 지나면서 관리하는 방법도 필요합니다.

**삭제 기준**

- 테스트가 참조하는 기능이 완전히 삭제된 경우: 테스트도 함께 삭제합니다.
- 분기 전체에서 한 번도 의미 있게 실패하지 않은 경우: 가치를 재평가합니다.
- 코드보다 테스트 수정 비용이 큰 경우: 테스트를 더 낮은 계층으로 내립니다.

**재작성 기준**

- 테스트 의도가 불분명하거나 이름에서 버그 ID를 찾을 수 없는 경우: 명확성을 보강합니다.
- 같은 회귀를 여러 계층에서 중복 확인하는 경우: 가장 빠른 계층 하나만 남깁니다.
- 긴 실행 시간으로 인해 CI가 느려지는 경우: 부분 테스트로 쪼개거나 병렬화합니다.

회귀 테스트는 한 번 추가하면 끝이 아니라 지속적으로 가치를 재평가하는 대상입니다.

## 운영 체크리스트

- [ ] 최근 버그 수정에 회귀 테스트를 함께 추가했습니다.
- [ ] 테스트 이름에 이슈 ID를 남겼습니다(`test_regression_PROJ_XXXX_`).
- [ ] 수정 전에 재현 테스트가 실패하는 것을 확인했습니다.
- [ ] 재현 테스트를 작고 결정적으로 유지했습니다.
- [ ] 가능한 한 낮은 테스트 계층에 회귀 테스트를 두었습니다.
- [ ] CI 파이프라인에서 회귀 테스트가 자동으로 실행됩니다.

## 연습 문제

1. 최근에 고친 버그 하나를 골라 회귀 테스트를 추가해 보세요. 수정 전 코드에서 그 테스트가 실제로 실패하는지 확인해 보세요.
2. `pytest -m regression`으로 회귀 테스트만 모아 실행하는 환경을 만들어 보세요.
3. 같은 모듈에서 회귀가 세 번 이상 있었다면 어떤 리팩터링이 필요한지 적어 보세요.
4. `git bisect run`으로 회귀 원인 커밋을 자동으로 찾는 스크립트를 작성해 보세요.

## 정리

회귀 테스트는 팀의 기억을 코드로 남기는 방법입니다. 버그를 고치는 일로 끝내지 않고, 다시 오지 못하게 막는 일까지 해야 수정이 완성됩니다. 재현 테스트를 먼저 실패하게 만들고, 코드를 고쳐 통과시키고, CI에 넣는 흐름을 습관으로 만들면 팀의 버그 재발률이 눈에 띄게 줄어듭니다.

다음 글에서는 이런 테스트들을 모든 커밋마다 자동으로 실행하는 CI 흐름을 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- **Testing 101 (8/10): 회귀 테스트 (현재 글)**
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko

### 공식 문서

- [pytest documentation](https://docs.pytest.org/)
- [pytest markers](https://docs.pytest.org/en/stable/how-to/mark.html)
- [git bisect documentation](https://git-scm.com/docs/git-bisect)

### 실무 참고

- [Martin Fowler — The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [The Pragmatic Programmer — Bug fixing chapter](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)

Tags: Testing, Regression, Bugfix, Quality, pytest
