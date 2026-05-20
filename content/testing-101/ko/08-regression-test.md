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

이 글은 Testing 101 시리즈의 여덟 번째 글입니다. 여기서는 회귀 테스트의 의미, 버그를 테스트로 재현하고 수정으로 연결하는 흐름, 그리고 회귀 테스트를 어디 계층에 두는 편이 좋은지 정리하겠습니다.

## 먼저 던지는 질문

- 회귀 테스트는 무엇을 막는 테스트일까요?
- 버그를 재현하고 테스트로 남기는 순서는 어떻게 될까요?
- 최소 재현 케이스는 왜 중요할까요?

## 큰 그림

![Testing 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/08/08-01-diagram.ko.png)

*Testing 101 8장 흐름 개요*

이 그림에서는 한 번 고쳐진 버그가 같은 방식으로 다시 나타나는 것을 방지하는 테스트를 보여줍니다. 버그 수정 후 테스트를 추가하면 그 문제가 반복되지 않도록 막습니다.

> 회귀 테스트는 과거의 고통을 재무보험입니다. 한 번 깨진 부분이 다시 깨지지 않도록 합니다.

## 왜 중요한가

버그를 말로만 기억하면 사람과 함께 사라집니다. 이슈 트래커에 기록이 남아 있어도, 코드가 그 맥락을 스스로 막아 주지는 못합니다. 회귀 테스트는 팀의 기억을 실행 가능한 형태로 남깁니다.

특히 반복해서 사고가 나는 모듈에서는 회귀 테스트의 가치가 큽니다. 같은 버그가 돌아오는 이유는 우연이 아니라, 취약한 경계나 복잡한 설계가 남아 있다는 뜻일 때가 많기 때문입니다.

## 한눈에 보는 구조

좋은 회귀 테스트 흐름은 버그 보고에서 끝나지 않습니다. 먼저 실패하는 재현 테스트를 만들고, 그 테스트를 통과하도록 코드를 고친 뒤, CI에 넣어 다시는 조용히 돌아오지 못하게 만듭니다.

## 핵심 용어

- **회귀(regression)**: 한 번 고친 동작이 나중에 다시 깨지는 현상입니다.
- **재현 테스트(repro test)**: 버그를 최소한의 입력으로 다시 일으키는 테스트입니다.
- **버그 ID**: 이슈 트래커에서 쓰는 고유 식별자입니다.
- **골든 파일**: 기대 결과를 파일 형태로 고정해 비교하는 방식입니다.
- **스냅샷 테스트**: 전체 출력 결과를 한 번에 비교하는 테스트입니다.

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
```

**바꾼 뒤 — 회귀 테스트를 추가한 상태**

```python
def test_regression_PROJ_1234_negative_total():
    cart = Cart(); cart.add(Item(price=-1))
    with pytest.raises(ValueError):
        cart.total()
```

차이는 기억 방식입니다. 사람의 설명 대신 테스트가 버그의 경계를 코드 안에 남깁니다.

## 다섯 단계로 회귀 테스트 만들기

### 1단계 — 버그를 재현하기

```python
# tests/test_regression.py
def test_repro_negative_price_breaks_total():
    cart = Cart(); cart.add(Item(price=-1))
    assert cart.total() >= 0   # 현재는 실패함
```

### 2단계 — 실패를 먼저 확인하기

```bash
pytest tests/test_regression.py -v
# FAILED ... assert -1 >= 0
```

### 3단계 — 코드 수정하기

```python
class Cart:
    def add(self, item):
        if item.price < 0:
            raise ValueError("price must be >= 0")
        self._items.append(item)
```

### 4단계 — 의도를 담아 테스트 다듬기

```python
def test_regression_PROJ_1234_negative_price_rejected():
    """Adding an item with a negative price raises ValueError. (PROJ-1234)"""
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add(Item(price=-1))
```

### 5단계 — CI에 넣어 다시 돌아오지 못하게 하기

```bash
git add tests/test_regression.py src/cart.py
git commit -m "fix(cart): reject negative price (PROJ-1234)"
```

## 이 코드에서 먼저 볼 점

- 테스트 이름에 버그 ID를 넣어 추적 가능성을 남겼습니다.
- 재현 케이스는 작고 분명합니다. 한 가지 버그만 겨냥합니다.
- 회귀 테스트는 모든 버그에 기계적으로 추가하는 것이 아니라, 재발 위험이 큰 문제에 우선 적용합니다.

실패를 먼저 확인하는 과정도 중요합니다. 테스트가 실제로 버그를 잡는지 보지 않고 바로 초록색 테스트만 남기면, 그 테스트는 재현력이 없는 장식일 수 있습니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 버그를 고치고 테스트를 쓰지 않는 일입니다. 그 순간부터 같은 회귀가 다시 시작될 가능성이 생깁니다.

또 다른 실수는 재현 테스트를 지나치게 크게 만드는 일입니다. 화면 전체를 띄우거나 거대한 시나리오를 태우지 않아도 되는 문제라면, 가장 낮은 계층으로 내려 작은 케이스로 고정하는 편이 유지비가 훨씬 낮습니다.

## 버그 리포트를 회귀 테스트로 바꾸는 전체 예시

실제 버그 수정 시나리오를 pytest 전체 코드로 보겠습니다. 이 예시는 버그 발견부터 테스트 추가, 수정, 검증까지 전체 흐름을 보여줍니다.

**버그 리포트 — PROJ-1234**

```text
제목: 장바구니에 음수 가격 상품 추가 시 total이 음수가 됨
재현 단계:
1. Item(price=-100) 생성
2. cart.add(item)
3. cart.total() 호출
예상: 예외 발생 또는 거부
실제: -100 반환
```

**1단계 — 실패하는 재현 테스트 작성**

```python
# tests/test_regression.py
import pytest
from src.cart import Cart, Item

def test_regression_PROJ_1234_negative_price_rejected():
    """Adding item with negative price should raise ValueError. (PROJ-1234)"""
    cart = Cart()
    # 버그 수정 전에는 이 테스트가 통과하지 않아야 합니다.
    with pytest.raises(ValueError, match="price must be >= 0"):
        cart.add(Item(price=-100))
```

**2단계 — 실패 확인**

```bash
pytest tests/test_regression.py::test_regression_PROJ_1234_negative_price_rejected -v
# FAILED ... ValueError not raised
```

**3단계 — 코드 수정**

```python
# src/cart.py
class Cart:
    def __init__(self):
        self._items = []

    def add(self, item):
        if item.price < 0:
            raise ValueError("price must be >= 0")
        self._items.append(item)

    def total(self):
        return sum(item.price for item in self._items)
```

**4단계 — 테스트 재실행**

```bash
pytest tests/test_regression.py::test_regression_PROJ_1234_negative_price_rejected -v
# PASSED
```

**5단계 — 커밋**

```bash
git add tests/test_regression.py src/cart.py
git commit -m "fix(cart): reject negative price (PROJ-1234)"
```

이 전체 흐름은 버그를 고치기 전에 반드시 재현 테스트가 먼저 실패하는 것을 확인하는 습관을 보여줍니다.
스냅샷을 아무 생각 없이 갱신하는 문제도 자주 보입니다. 변경 이유를 이해하지 못한 채 갱신하면 테스트는 문서 작업만 남고 신뢰는 사라집니다.

## 직접 검증해 볼 것

1. 수정 전 코드에서 재현 테스트를 먼저 실행해 진짜로 빨간색이 되는지 확인합니다. 이 단계가 없으면 회귀 테스트가 장식으로 끝날 수 있습니다.
2. 버그 ID를 테스트 이름과 주석 중 한 곳에는 남겨 두어, 나중에 왜 이 테스트가 존재하는지 바로 추적할 수 있게 합니다.
3. 같은 버그를 E2E와 단위 테스트 중 어디에 두는 편이 더 싼지 비교합니다. 가능한 한 낮은 계층으로 내리는 편이 유지비가 낮습니다.

**예상 결과:** 수정 전에는 재현 테스트가 실패하고, 수정 후에는 같은 테스트가 안정적으로 통과해야 합니다.

## 실패 신호와 첫 점검

- 버그를 고친 뒤 초록색 테스트만 추가하면 실제 회귀 방지력이 없습니다.
- 재현 테스트가 너무 크면 다른 원인까지 섞여 실패 이유가 흐려집니다.
- 스냅샷을 무심코 갱신하는 습관이 생기면 회귀 테스트가 기억 장치가 아니라 승인 절차로 변합니다.

## 회귀 테스트가 느려지면?

회귀 테스트가 계속 쌓이면 결국 실행 시간이 문제가 됩니다. 다음은 속도를 관리하는 세 가지 전략입니다.

### 병렬 실행

```bash
pip install pytest-xdist
pytest tests/test_regression.py -n auto  # CPU 코어 수만큼 병렬 실행
```

병렬 실행은 테스트 간 의존이 없을 때 가장 효과적입니다. 공유 상태나 파일 의존이 있으면 간헐적 실패를 일으킬 수 있습니다.

### 선택적 실행

```bash
pytest -m regression  # 회귀 테스트만 실행
pytest tests/test_regression.py -k "PROJ_123"  # 특정 버그만
```

마커를 활용하면 전체 테스트 스위트 중 회귀 테스트만 분리해서 돌릴 수 있습니다.

### 핵심 경로 우선 실행

```bash
# PR에서는 핵심 경로만
pytest tests/test_regression.py -m critical

# 야간 빌드에서는 전체
pytest tests/
```

팀이 회귀 테스트를 계층화하면 빠른 피드백과 전체 검증을 동시에 운영할 수 있습니다.
## 실무에서는 이렇게 생각합니다

강한 팀은 버그 수정 PR에 회귀 테스트를 거의 기본으로 요구합니다. 특히 재발 가능성이 높은 문제, 고객 영향이 큰 문제, 경계 조건과 예외 처리 문제는 더 그렇습니다.

경험 많은 엔지니어는 회귀 테스트가 반복해서 쌓이는 모듈을 보면 구조를 의심합니다. 같은 영역에서 같은 류의 버그가 계속 나온다면 테스트를 더 붙이는 것만으로는 부족하고, 설계 단순화나 리팩터링이 필요할 수 있습니다.

## Git bisect 활용

회귀가 발견되었는데 어느 커밋에서 문제가 시작되었는지 모를 때 `git bisect`를 사용할 수 있습니다.

```bash
git bisect start
git bisect bad HEAD              # 현재 커밋은 실패
git bisect good v1.2.0           # v1.2.0에서는 통과했음
# Git이 중간 커밋으로 체크아웃
pytest tests/test_regression.py
git bisect good  # 또는 git bisect bad
# 반복하면 문제 커밋을 찾아냄
git bisect reset
```

이 과정은 자동화할 수도 있습니다.

```bash
git bisect start HEAD v1.2.0
git bisect run pytest tests/test_regression.py
```

bisect는 회귀 테스트가 명확히 실패할 때 가장 유용합니다. 플래키 테스트는 bisect 결과를 신뢰하기 어렵게 만듭니다.
## 체크리스트

- [ ] 최근 버그 수정에 회귀 테스트를 함께 추가했습니다.
- [ ] 테스트 이름에 이슈 ID나 이유를 남겼습니다.
- [ ] 재현 테스트를 작고 결정적으로 유지했습니다.
- [ ] 가능한 한 낮은 테스트 계층에 회귀 테스트를 두었습니다.

## 연습 문제

1. 최근에 고친 버그 하나를 골라 회귀 테스트를 추가해 보세요.
2. 수정 전 코드에서 그 테스트가 실제로 실패하는지 확인해 보세요.
3. 같은 모듈에서 회귀가 세 번 이상 있었다면 어떤 리팩터링이 필요한지 적어 보세요.

## 정리

회귀 테스트는 팀의 기억을 코드로 남기는 방법입니다. 버그를 고치는 일로 끝내지 않고, 다시 오지 못하게 막는 일까지 해야 수정이 완성됩니다. 다음 글에서는 이런 테스트들을 모든 커밋마다 자동으로 실행하는 CI 흐름을 보겠습니다.

## 회귀 테스트 유지 보수

회귀 테스트를 추가하는 것도 중요하지만, 시간이 지나면서 관리하는 방법도 필요합니다.

**삭제 기준**

- 테스트가 참조하는 기능이 완전히 삭제된 경우: 테스트도 함께 삭제합니다.
- 분기 전체에서 한 번도 실패하지 않은 경우: 가치를 재평가합니다.
- 코드보다 테스트 수정 비용이 큰 경우: 테스트를 더 낮은 계층으로 내립니다.

**재작성 기준**

- 테스트 의도가 불분명하거나 이름에서 버그 ID를 찾을 수 없는 경우: 더메이트를 보강합니다.
- 같은 회귀를 여러 계층에서 중복 확인하는 경우: 가장 빠른 계층 하나만 남깁니다.
- 긴 실행 시간으로 인해 CI가 느려지는 경우: 부분 테스트로 쪼개거나 병렬화합니다.

회귀 테스트는 한 번 추가하면 끝이 아니라 지속적으로 가치를 재평가하는 대상입니다.
## 처음 질문으로 돌아가기

- **회귀 테스트는 무엇을 막는 테스트일까요?**
  - 회귀 테스트는 버그 리포트를 받으면 그 버그를 재현하는 테스트를 먼저 작성합니다.
- **버그를 재현하고 테스트로 남기는 순서는 어떻게 될까요?**
  - 버그를 고친 후에도 회귀 테스트는 계속 실행되어 같은 문제가 다시 나타나지 않도록 감시합니다.
- **최소 재현 케이스는 왜 중요할까요?**
  - 프로젝트 나이가 길수록 회귀 테스트의 누적이 중요하므로 버그 고침 = 테스트 추가로 습관화합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- **회귀 테스트 (현재 글)**
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [pytest documentation](https://docs.pytest.org/)
- [GitHub Issues documentation](https://docs.github.com/en/issues)

### 실무 참고
- [Martin Fowler — The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [The Pragmatic Programmer — Bug fixing chapter](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)

Tags: Testing, Regression, Bugfix, Quality, pytest
