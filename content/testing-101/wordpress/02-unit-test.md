---
series: testing-101
episode: 2
title: "바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트"
status: content-ready
targets:
  wordpress: true
  tistory: false
  medium: false
  hashnode: false
  mkdocs: false
  ebook: false
language: ko
tags:
  - 바이브코딩
  - Testing
  - Unit Test
  - pytest
  - Python
  - Quality
seo_description: AI가 만든 코드를 함수 단위로 빠르게 검증하는 단위 테스트. AAA 패턴과 pytest 실습으로 바이브코딩 팀의 첫 번째 안전망을 만드는 방법.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트

이 글은 **바이브코딩을 위한 테스팅 기초** 시리즈의 두 번째 글입니다. AI가 만든 함수 하나를 빠르게 검증하는 단위 테스트를 처음부터 설명합니다.

---

AI에게 함수를 만들어 달라고 하면 보통 그럴듯한 코드가 나옵니다. 문제는 "그럴듯해 보임"과 "실제로 맞음" 사이의 간격입니다. 특히 할인 계산, 권한 판정, 상태 전이처럼 비즈니스 로직이 복잡한 함수는 AI가 엣지 케이스를 빠뜨리기 쉽습니다.

단위 테스트는 AI가 만든 함수 하나를 그 자리에서 검증하는 가장 빠른 방법입니다. 수십 밀리초면 충분합니다. 바이브코딩 팀에서 단위 테스트는 AI 코드를 믿기 위한 첫 번째 안전망입니다.

> 단위 테스트는 한 가지 동작만 검증하고, 같은 동작을 여러 번 실행해도 같은 결과가 나와야 합니다.

## 이 글에서 다룰 문제

- 단위 테스트는 정확히 어디까지를 검증할까요?
- AAA 패턴은 왜 많이 쓰일까요?
- `pytest`의 fixture와 parametrize는 언제 도움이 될까요?
- AI가 만든 코드의 단위 테스트에서 자주 빠지는 케이스는 무엇일까요?
- 바이브코딩 팀이 단위 테스트를 가장 빨리 습관화하는 방법은 무엇일까요?

단위 테스트는 테스트 피라미드의 바닥입니다. 빠르게 돌 수 있어서 AI가 코드를 고칠 때마다 즉각 피드백을 줍니다. 단위 테스트가 두꺼울수록 AI 코드를 더 자신 있게 사용할 수 있습니다.

## 한눈에 보는 구조

단위 테스트는 가장 많고 가장 빨라야 합니다. 빠른 테스트가 많아야 개발자가 자주 돌릴 수 있고, AI에게 코드를 수정 요청할 때마다 결과를 즉시 확인할 수 있습니다.

- **단위(unit)**: 함수, 메서드, 클래스 같은 작은 동작 단위입니다.
- **AAA 패턴**: Arrange(준비), Act(실행), Assert(검증) 순서로 테스트를 읽기 쉽게 나누는 방식입니다.
- **픽스처(fixture)**: 여러 테스트가 함께 쓰는 준비 데이터나 객체입니다.
- **파라미터화(parametrize)**: 입력만 달라지는 비슷한 테스트를 하나로 묶는 기법입니다.
- **경계값(edge case)**: 0, 빈 문자열, 음수, `None`처럼 AI가 자주 빠뜨리는 입력입니다.

## 단위 테스트 vs 통합 테스트

| 항목 | 단위 테스트 | 통합 테스트 |
|---|---|---|
| 검증 범위 | 함수나 메서드 하나 | 여러 컴포넌트가 연결된 흐름 |
| 외부 의존 | 없음 (또는 mock/stub 사용) | 실제 DB, HTTP 등 포함 |
| 실행 속도 | 밀리초 단위 | 수백 밀리초 ~ 초 단위 |
| AI 코드 검증 용도 | 함수 로직 즉시 확인 | 시스템 연동 확인 |
| 테스트 수 | 수백~수천 개 | 수십~수백 개 |

## 바꾸기 전과 후

**바꾸기 전 — AI 코드를 하나의 테스트로 몰아 확인**

```python
def test_user_flow():
    u = create_user("a")
    u.activate()
    u.upgrade()
    assert u.plan == "pro"
```

**바꾼 뒤 — 동작별로 분리해서 AI 코드의 어느 부분이 틀렸는지 바로 확인**

```python
def test_create_user_starts_inactive(): ...
def test_activate_sets_active(): ...
def test_upgrade_sets_pro(): ...
```

하나의 테스트에 여러 단계를 몰아넣으면 AI 코드의 어느 부분이 틀렸는지 알기 어렵습니다. 작게 나누면 실패 지점이 바로 보입니다.

## 다섯 단계로 pytest 시작하기

### 1단계 — AI가 만든 함수 준비

```python
# src/discount.py
def apply_discount(price: int, percent: int) -> int:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be 0..100")
    return price - price * percent // 100
```

### 2단계 — AAA 패턴으로 기본 테스트 작성

```python
# tests/test_discount.py
from src.discount import apply_discount

def test_apply_10_percent_discount():
    # Arrange (준비)
    price, percent = 1000, 10
    # Act (실행)
    result = apply_discount(price, percent)
    # Assert (검증)
    assert result == 900
```

### 3단계 — AI가 빠뜨리기 쉬운 경계값을 parametrize로 묶기

```python
import pytest

@pytest.mark.parametrize("price,percent,expected", [
    (1000, 0, 1000),    # AI가 종종 빠뜨리는 0% 케이스
    (1000, 50, 500),    # 중간값
    (1000, 100, 0),     # AI가 종종 빠뜨리는 100% 케이스
])
def test_apply_discount_table(price, percent, expected):
    assert apply_discount(price, percent) == expected
```

### 4단계 — 예외 케이스 별도 분리

```python
def test_apply_discount_invalid_percent_raises():
    with pytest.raises(ValueError):
        apply_discount(1000, 150)
```

### 5단계 — fixture로 준비 코드 재사용

```python
@pytest.fixture
def base_price() -> int:
    return 10_000

def test_with_fixture(base_price: int):
    assert apply_discount(base_price, 10) == 9_000
```

## AI 코드의 경계값 함정

경계값은 AI가 가장 자주 빠뜨리는 케이스입니다. AI는 정상 케이스는 잘 처리하지만 경계 조건에서 예상 밖의 동작을 만들기 쉽습니다.

```python
import pytest

@pytest.mark.parametrize("price,percent,expected", [
    (1000, 0, 1000),       # 경계: 할인 없음
    (1000, 100, 0),        # 경계: 전액 할인
    (0, 50, 0),            # 경계: 가격 0 (AI가 자주 빠뜨림)
    (1, 1, 0),             # 경계: 최소 단위
])
def test_apply_discount_edge_cases(price, percent, expected):
    assert apply_discount(price, percent) == expected

@pytest.mark.parametrize("price,percent", [
    (1000, -1),            # AI가 검증하지 않는 음수 퍼센트
    (1000, 101),           # 범위 초과
])
def test_apply_discount_rejects_invalid_percent(price, percent):
    with pytest.raises(ValueError):
        apply_discount(price, percent)
```

AI에게 "경계값 테스트를 추가해 줘"라고 요청할 때도 직접 케이스를 지정하는 편이 더 완전한 테스트를 얻을 수 있습니다.

## 자주 하는 실수

가장 흔한 실수는 실제 데이터베이스나 네트워크를 붙인 채 단위 테스트라고 부르는 경우입니다. 외부 의존이 붙으면 그 시점부터는 통합 테스트입니다.

또 하나는 테스트끼리 상태를 공유하는 경우입니다. AI가 만든 코드에 전역 변수가 있으면 이 문제가 자주 발생합니다. 단위 테스트는 어떤 순서로 돌려도 같은 결과가 나와야 합니다.

테스트 이름을 `test_1`, `test_2`처럼 붙이는 문제도 있습니다. AI 코드에서 테스트가 실패했을 때 이름이 모호하면 어떤 기능이 깨졌는지 알기 어렵습니다.

## 좋은 단위 테스트의 이름 짓기

```python
# 나쁜 예
def test_1(): ...
def test_discount(): ...

# 좋은 예 — AI 코드 실패 시 즉시 원인 파악 가능
def test_apply_discount_with_zero_percent_returns_original_price(): ...
def test_apply_discount_rejects_percent_over_100(): ...
```

## AI 팁: 테스트 작성 프롬프트

```text
프롬프트 예시:
"apply_discount(price, percent) 함수의 pytest 단위 테스트를 작성해 줘.
AAA 패턴을 사용하고, 경계값(0%, 100%, 음수, 100 초과)을 포함해 줘.
parametrize로 유사한 케이스를 묶어 줘."

확인 포인트:
1. 단언문이 실제 값을 검증하는지 확인 (실행만 하고 검증 없는 테스트 주의)
2. 경계값이 포함됐는지 확인
3. 예외 케이스가 pytest.raises로 작성됐는지 확인
```

## 운영 체크리스트

- [ ] 함수 하나에 대해 테스트 세 개 이상을 작성했습니다.
- [ ] 경계값과 예외 케이스를 함께 다뤘습니다.
- [ ] AAA 구조로 읽히게 작성했습니다.
- [ ] `parametrize`를 한 번 이상 사용했습니다.
- [ ] AI가 만든 테스트의 단언문이 실제 값을 검증하는지 확인했습니다.

## 처음 질문으로 돌아가기

- **단위 테스트는 정확히 어디까지를 검증할까요?**
  함수 하나, 메서드 하나의 로직을 외부 의존 없이 검증합니다. 데이터베이스나 네트워크를 붙이는 순간 통합 테스트가 됩니다.

- **AAA 패턴은 왜 많이 쓰일까요?**
  준비(Arrange), 실행(Act), 검증(Assert)이 분리되면 AI 코드의 어느 부분이 틀렸는지 읽기 쉬워집니다.

- **AI가 만든 코드의 단위 테스트에서 자주 빠지는 케이스는 무엇일까요?**
  경계값(0, None, 빈 문자열, 음수, 최대값)과 예외 경로입니다. AI에게 테스트를 요청할 때 이 케이스를 명시적으로 요구하세요.

## 정리

단위 테스트는 AI가 만든 코드를 함수 단위로 빠르게 검증하는 첫 번째 안전망입니다. 작고, 빠르고, 외부 의존이 없어야 합니다. 다음 글에서는 여러 컴포넌트가 실제로 연결됐을 때 무엇이 깨지는지 확인하는 통합 테스트를 보겠습니다.

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [pytest — parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Martin Fowler — Unit Test](https://martinfowler.com/bliki/UnitTest.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 테스팅 기초 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- **바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트 (현재 글)**
- [바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트](./03-integration-test.md)
- [바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트](./04-e2e-test.md)
- [바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블](./05-test-double.md)
- [바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [바이브코딩을 위한 테스팅 기초 (8/10): 회귀 테스트](./08-regression-test.md)
- [바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [바이브코딩을 위한 테스팅 기초 (10/10): 테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

Tags: 바이브코딩, Testing, Unit Test, pytest, Python, Quality
