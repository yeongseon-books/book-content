---
series: testing-101
episode: 2
title: "Testing 101 (2/10): 단위 테스트"
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
  - Unit Test
  - pytest
  - Python
  - Quality
seo_description: 단위 테스트의 정의, 좋은 단위 테스트의 조건, AAA 패턴과 pytest 실습으로 입문하는 글.
last_reviewed: '2026-05-12'
---

# Testing 101 (2/10): 단위 테스트

테스트를 처음 배우면 가장 먼저 드는 질문이 있습니다. 어디까지를 하나의 테스트 단위로 봐야 할까요? 함수 하나일 수도 있고, 메서드 하나일 수도 있고, 클래스의 특정 동작 하나일 수도 있습니다. 범위를 너무 넓게 잡으면 원인을 찾기 어려워지고, 너무 모호하게 잡으면 테스트가 금방 무거워집니다.

그래서 단위 테스트는 크기를 줄이는 연습이기도 합니다. 외부 의존을 걷어 내고, 작은 동작 하나를 빠르게 확인하는 방식으로 신뢰를 쌓습니다.

이 글은 Testing 101 시리즈의 두 번째 글입니다. 여기서는 단위 테스트의 범위, AAA 패턴, `pytest`의 기본 작성법, 그리고 좋은 단위 테스트가 갖춰야 할 조건을 정리하겠습니다.

## 먼저 던지는 질문

- 단위 테스트는 정확히 어디까지를 검증할까요?
- AAA 패턴은 왜 많이 쓰일까요?
- `pytest`의 fixture와 parametrize는 언제 도움이 될까요?

## 큰 그림

![Testing 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/02/02-01-diagram.ko.png)

*Testing 101 2장 흐름 개요*

이 그림에서는 단위 테스트를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 단위 테스트의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

단위 테스트는 테스트 피라미드의 바닥을 이룹니다. 실행이 빠르기 때문에 수천 개가 있어도 몇 초 안에 돌릴 수 있고, 변경 직후에 가장 먼저 피드백을 줍니다. 그래서 상위 단계의 통합 테스트와 E2E 테스트를 무한히 늘리지 않고도 핵심 로직을 두껍게 보호할 수 있습니다.

가격 계산, 권한 판정, 상태 전이처럼 사고가 나기 쉬운 도메인 로직은 단위 테스트의 투자 대비 효과가 특히 큽니다. 화면이나 데이터베이스까지 다 붙이지 않아도, 위험한 계산과 분기 자체를 촘촘하게 검증할 수 있기 때문입니다.

## 한눈에 보는 구조

단위 테스트는 가장 많고 가장 빨라야 합니다. 통합 테스트는 그보다 적고, E2E 테스트는 더 적어야 합니다. 이 분포가 중요한 이유는 속도 때문입니다. 빠른 테스트가 많아야 개발자가 자주 돌릴 수 있고, 자주 돌려야 테스트가 실제 습관이 됩니다.

## 핵심 용어

- **단위(unit)**: 함수, 메서드, 클래스 같은 작은 동작 단위입니다.
- **AAA 패턴**: Arrange, Act, Assert 순서로 테스트를 읽기 쉽게 나누는 방식입니다.
- **픽스처(fixture)**: 여러 테스트가 함께 쓰는 준비 데이터나 객체입니다.
- **파라미터화(parametrize)**: 입력만 달라지는 비슷한 테스트를 하나로 묶는 기법입니다.
- **경계값(edge case)**: 0, 빈 문자열, 음수, `None`처럼 분기와 오류를 자주 드러내는 입력입니다.

## 바꾸기 전과 후

**바꾸기 전 — 하나에 여러 동작을 몰아넣은 테스트**

```python
def test_user_flow():
    u = create_user("a")
    u.activate()
    u.upgrade()
    assert u.plan == "pro"
```

**바꾼 뒤 — 작은 동작으로 분리한 테스트**

```python
def test_create_user_starts_inactive(): ...
def test_activate_sets_active(): ...
def test_upgrade_sets_pro(): ...
```

작게 나누면 실패 원인을 즉시 알 수 있습니다. 반대로 한 테스트에 여러 단계를 몰아넣으면 어디가 깨졌는지 추적하는 시간이 길어집니다. 단위 테스트의 장점은 작은 크기에서 나옵니다.

## 다섯 단계로 `pytest` 시작하기

### 1단계 — 검증할 함수 준비

```python
# src/discount.py
def apply_discount(price: int, percent: int) -> int:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be 0..100")
    return price - price * percent // 100
```

### 2단계 — 기본 테스트 작성

```python
# tests/test_discount.py
from src.discount import apply_discount

def test_apply_10_percent_discount():
    # Arrange
    price, percent = 1000, 10
    # Act
    result = apply_discount(price, percent)
    # Assert
    assert result == 900
```

### 3단계 — 비슷한 케이스를 묶기

```python
import pytest

@pytest.mark.parametrize("price,percent,expected", [
    (1000, 0, 1000),
    (1000, 50, 500),
    (1000, 100, 0),
])
def test_apply_discount_table(price, percent, expected):
    assert apply_discount(price, percent) == expected
```

### 4단계 — 예외 케이스 분리

```python
def test_apply_discount_invalid_percent_raises():
    with pytest.raises(ValueError):
        apply_discount(1000, 150)
```

### 5단계 — 픽스처로 준비 코드 줄이기

```python
@pytest.fixture
def base_price() -> int:
    return 10_000

def test_with_fixture(base_price: int):
    assert apply_discount(base_price, 10) == 9_000
```

## 이 코드에서 먼저 볼 점

- 테스트 하나가 한 가지 사실만 검증합니다.
- 같은 모양의 테스트는 `parametrize`로 묶어 중복을 줄입니다.
- 예외 상황은 별도 테스트로 분리해 의도를 분명하게 남깁니다.

AAA 패턴이 좋은 이유도 여기에 있습니다. 준비, 실행, 검증이 눈에 보이면 테스트를 읽는 사람도 흐름을 빠르게 따라갈 수 있습니다. 단위 테스트는 작성자만 보는 코드가 아니라, 나중에 다른 사람이 설계를 이해할 때 읽는 코드이기도 합니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 실제 데이터베이스나 네트워크를 붙인 채 단위 테스트라고 부르는 경우입니다. 외부 의존이 붙으면 그 시점부터는 단위 테스트보다 통합 테스트에 가까워집니다.

또 하나는 테스트끼리 상태를 공유하는 경우입니다. 이전 테스트가 남긴 값을 다음 테스트가 기대하면 실행 순서가 바뀌는 순간 깨집니다. 단위 테스트는 어떤 순서로 돌려도 같은 결과가 나와야 합니다.

이름을 대충 붙이는 문제도 자주 보입니다. `test_1`, `test_2` 같은 이름은 실패했을 때 아무 설명을 주지 못합니다. 테스트 이름은 동작 설명서라고 생각하는 편이 좋습니다.

## 직접 검증해 볼 것

1. `apply_discount(1000, 100)`과 `apply_discount(1000, 0)`이 모두 기대값을 반환하는지 확인해 경계값 테스트가 실제로 작동하는지 봅니다.
2. `apply_discount(1000, 150)`처럼 예외 입력을 넣고 실패 메시지가 함수 계약을 분명하게 설명하는지 확인합니다.
3. 같은 테스트 파일에서 DB 연결이나 HTTP 호출이 끼어들지 않는지 살펴봅니다. 단위 테스트에 외부 의존이 붙는 순간 피드백 속도가 급격히 떨어집니다.

**예상 결과:** 정상 입력은 즉시 초록색으로 끝나고, 잘못된 퍼센트 입력은 `ValueError`를 분명하게 보여 줘야 합니다.

## 실패 신호와 첫 점검

- 예외 테스트가 `with pytest.raises(...)` 없이 작성되어 있으면 실패 원인이 흐려집니다.
- 픽스처가 전역 상태를 공유하면 순서를 바꿨을 때만 깨지는 테스트가 생깁니다.
- 단위 테스트 하나가 너무 많은 단계를 담고 있다면 함수 책임이 과한지부터 의심하는 편이 낫습니다.

## 실무에서는 이렇게 생각합니다

실무에서 단위 테스트는 양보다 성질이 더 중요합니다. 빠르게 돌고, 외부 환경에 흔들리지 않고, 실패했을 때 어느 동작이 깨졌는지 바로 말해 주어야 합니다.

시니어 엔지니어는 보통 단위 테스트를 도메인 설계 점검 도구로도 씁니다. 테스트를 쓰기 지나치게 어렵다면 함수 책임이 너무 많거나 의존이 과하게 얽혀 있을 가능성이 큽니다. 테스트의 불편함이 설계의 불편함을 드러내는 경우가 많습니다.

## 체크리스트

- [ ] 함수 하나에 대해 테스트 세 개 이상을 작성했습니다.
- [ ] 경계값과 예외 케이스를 함께 다뤘습니다.
- [ ] AAA 구조로 읽히게 작성했습니다.
- [ ] `parametrize`를 한 번 이상 사용했습니다.

## 연습 문제

1. `is_palindrome(s)` 함수를 만들고 다섯 입력으로 파라미터화 테스트를 작성해 보세요.
2. 빈 문자열, 한 글자, 공백 문자열 같은 경계값을 추가해 보세요.
3. 일부러 버그를 넣고 어떤 테스트가 잡는지 기록해 보세요.

## 정리

단위 테스트는 작고, 빠르고, 외부 의존이 없어야 합니다. 이 성질이 지켜질 때 테스트 피라미드의 바닥이 단단해집니다. 다음 글에서는 여러 부품을 실제로 연결했을 때 무엇이 깨지는지 확인하는 통합 테스트를 보겠습니다.

## 처음 질문으로 돌아가기

- **단위 테스트는 정확히 어디까지를 검증할까요?**
  - 본문의 기준은 단위 테스트를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **AAA 패턴은 왜 많이 쓰일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`pytest`의 fixture와 parametrize는 언제 도움이 될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- **단위 테스트 (현재 글)**
- 통합 테스트 (예정)
- E2E 테스트 (예정)
- 테스트 더블 (예정)
- Mock과 Stub (예정)
- 테스트 커버리지 (예정)
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest — parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Martin Fowler — Unit Test](https://martinfowler.com/bliki/UnitTest.html)
- [Google Testing Blog](https://testing.googleblog.com/)

Tags: Testing, Unit Test, pytest, Python, Quality
