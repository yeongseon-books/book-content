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

이 글은 Testing 101 시리즈의 두 번째 글입니다. 여기서는 단위 테스트의 범위, AAA 패턴, `pytest`의 기본 작성법, fixture와 parametrize 활용, 그리고 좋은 단위 테스트가 갖춰야 할 조건을 정리하겠습니다.

![Testing 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/02/02-01-diagram.ko.png)
*Testing 101 2장 흐름 개요*
> 단위 테스트는 한 가지 동작만 검증하고, 같은 동작을 여러 번 실행해도 같은 결과가 나와야 합니다.

## 이 글에서 다룰 문제

- 단위 테스트는 정확히 어디까지를 검증할까요?
- AAA 패턴은 왜 많이 쓰일까요?
- `pytest`의 fixture와 parametrize는 언제 도움이 될까요?
- 경계값 테스트는 왜 중요할까요?
- 단위 테스트를 도메인 설계 도구로 어떻게 활용할까요?

단위 테스트는 테스트 피라미드의 바닥을 이룹니다. 실행이 빠르기 때문에 수천 개가 있어도 몇 초 안에 돌릴 수 있고, 변경 직후에 가장 먼저 피드백을 줍니다. 그래서 상위 단계의 통합 테스트와 E2E 테스트를 무한히 늘리지 않고도 핵심 로직을 두껍게 보호할 수 있습니다.

가격 계산, 권한 판정, 상태 전이처럼 사고가 나기 쉬운 도메인 로직은 단위 테스트의 투자 대비 효과가 특히 큽니다.

## 단위 테스트와 통합 테스트 비교

| 항목 | 단위 테스트 | 통합 테스트 |
|---|---|---|
| 검증 범위 | 함수나 메서드 하나 | 여러 컴포넌트가 연결된 흐름 |
| 외부 의존 | 없음 (또는 mock/stub 사용) | 실제 DB, HTTP 등 포함 |
| 실행 속도 | 밀리초 단위 | 수백 밀리초 ~ 초 단위 |
| 실패 시 원인 파악 | 즉시 가능 (범위가 좁음) | 여러 계층 포함으로 범위가 넓음 |
| 테스트 수 | 수백~수천 개 | 수십~수백 개 |
| CI 실행 빈도 | 모든 PR, 모든 커밋 | 선택적 또는 병합 전 |

이 구분이 중요한 이유는 테스트 전략 때문입니다. 단위 테스트는 많고 빠르고 좁아야 하고, 통합 테스트는 적고 느리지만 경계를 확인해야 합니다. 두 계층의 성질을 섞으면 빠르지도 않고 범위도 애매한 테스트가 됩니다.

## 하나에 여러 동작을 몰아넣은 테스트 vs 작은 동작으로 분리

**나쁜 예 — 하나에 여러 동작을 몰아넣은 테스트**

```python
def test_user_flow():
    u = create_user("a@b.com")
    u.activate()
    u.upgrade()
    assert u.plan == "pro"
```

**좋은 예 — 작은 동작으로 분리한 테스트**

```python
def test_create_user_starts_inactive():
    user = create_user("a@b.com")
    assert user.active is False

def test_activate_sets_active_flag():
    user = create_user("a@b.com")
    user.activate()
    assert user.active is True

def test_upgrade_sets_plan_to_pro():
    user = create_user("a@b.com")
    user.activate()
    user.upgrade()
    assert user.plan == "pro"
```

작게 나누면 실패 원인을 즉시 알 수 있습니다. 반대로 한 테스트에 여러 단계를 몰아넣으면 어디가 깨졌는지 추적하는 시간이 길어집니다.

## 다섯 단계로 pytest 시작하기

### 1단계 — 검증할 함수 준비

```python
# src/discount.py
def apply_discount(price: int, percent: int) -> int:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be 0..100")
    return price - price * percent // 100
```

### 2단계 — AAA 패턴으로 기본 테스트 작성

```python
# tests/unit/test_discount.py
from src.discount import apply_discount
import pytest

def test_apply_10_percent_discount():
    # Arrange
    price, percent = 1000, 10
    # Act
    result = apply_discount(price, percent)
    # Assert
    assert result == 900, f"Expected 900, got {result}"
```

### 3단계 — 비슷한 케이스를 파라미터화로 묶기

```python
@pytest.mark.parametrize("price,percent,expected", [
    (1000, 0, 1000),    # 할인 없음
    (1000, 50, 500),    # 반값 할인
    (1000, 100, 0),     # 전액 할인
    (500, 20, 400),     # 일반 케이스
])
def test_apply_discount_table(price, percent, expected):
    assert apply_discount(price, percent) == expected
```

### 4단계 — 예외 케이스 분리

```python
@pytest.mark.parametrize("price,percent", [
    (1000, -1),    # 음수 퍼센트
    (1000, 101),   # 범위 초과
    (1000, 200),   # 크게 초과
])
def test_apply_discount_invalid_percent_raises(price, percent):
    with pytest.raises(ValueError, match="percent must be 0..100"):
        apply_discount(price, percent)
```

### 5단계 — 픽스처로 준비 코드 줄이기

```python
@pytest.fixture
def base_price() -> int:
    return 10_000

@pytest.fixture
def premium_price() -> int:
    return 50_000

def test_discount_on_base_price(base_price: int):
    assert apply_discount(base_price, 10) == 9_000

def test_full_discount_on_premium(premium_price: int):
    assert apply_discount(premium_price, 100) == 0
```

## 테스트 함수 이름 짓기

테스트 이름은 실패했을 때 읽는 첫 번째 설명서입니다. CI 로그에서 어떤 시나리오가 깨졌는지 바로 알 수 있어야 합니다.

**나쁜 예:**

```python
def test_1(): ...
def test_discount(): ...
def test_user(): ...
```

**좋은 예:**

```python
def test_apply_discount_with_zero_percent_returns_original_price(): ...
def test_apply_discount_with_100_percent_returns_zero(): ...
def test_apply_discount_with_negative_percent_raises_value_error(): ...
def test_create_user_with_duplicate_email_raises_value_error(): ...
```

좋은 테스트 이름은 세 가지 정보를 담습니다.

1. **무엇을 하는가** — 동작, 함수명
2. **어떤 조건에서** — 입력, 상태
3. **무엇을 기대하는가** — 결과, 예외

실무에서는 `test_<action>_<condition>_<result>` 형식을 자주 씁니다. 이름이 길어지는 것은 문제가 아닙니다. 실패 로그에서 어떤 시나리오가 깨졌는지 바로 알 수 있다면 길이는 부차적입니다.

## 경계값 테스트 — 버그가 숨는 곳

경계값은 정상 케이스보다 버그를 더 잘 드러냅니다. `0`, `None`, 빈 문자열, 음수, 최대값 같은 입력은 조건문과 반복문의 경계에서 예상 밖의 동작을 일으킵니다.

```python
@pytest.mark.parametrize("price,percent,expected", [
    (1000, 0, 1000),    # 경계: 할인 없음
    (1000, 100, 0),     # 경계: 전액 할인
    (0, 50, 0),         # 경계: 가격 0
    (1, 1, 0),          # 경계: 최소 단위 (정수 나누기)
    (9999, 99, 9900),   # 경계: 큰 숫자
])
def test_apply_discount_edge_cases(price, percent, expected):
    assert apply_discount(price, percent) == expected
```

경계값 테스트는 코드 리뷰에서 자주 등장하는 질문에 코드로 답하는 것입니다. `0`일 때는? `None`일 때는? 빈 배열일 때는?

## 도메인 규칙 조합 테스트

단위 테스트를 충분히 작성했는데도 운영 버그가 계속 나오는 팀은 대체로 같은 문제를 겪습니다. 함수 단위 분기는 많이 테스트했지만, 비즈니스 규칙의 조합을 충분히 다루지 못한 경우입니다.

예를 들어 할인 정책은 "회원 등급"과 "쿠폰"과 "최대 할인 상한"이 함께 작동합니다. 이때 조합 테스트를 설계하지 않으면 단일 케이스가 모두 통과해도 실제 시나리오에서 실패할 수 있습니다.

```python
@pytest.mark.parametrize(
    'tier,coupon,amount,expected',
    [
        ('bronze', None, 10000, 10000),         # 할인 없음
        ('silver', None, 10000, 9500),          # 5% 할인
        ('gold', None, 10000, 9000),            # 10% 할인
        ('gold', 'WELCOME10', 10000, 8500),     # 10% + 쿠폰 5%
        ('gold', 'VIP30', 10000, 7000),         # 상한 30% 적용
    ],
)
def test_calculate_price_by_tier_and_coupon(tier, coupon, amount, expected):
    result = calculate_final_price(tier=tier, coupon=coupon, amount=amount)
    assert result == expected, f"tier={tier}, coupon={coupon}, amount={amount}: expected {expected}, got {result}"
```

이 방식은 단순히 케이스 수를 늘리는 것이 아니라, 규칙 표를 테스트로 고정한다는 의미가 있습니다. 정책 문서가 바뀌면 표를 먼저 업데이트하고 테스트를 실패시켜 수정 범위를 드러내는 흐름이 효과적입니다.

## 픽스처 계층화로 준비 비용 줄이기

단위 테스트가 늘어날수록 fixture를 한 단계로만 운영하면 재사용성과 가독성이 동시에 떨어집니다. "기본 객체"와 "상태 변형"을 분리해 계층화하면 유지보수가 쉬워집니다.

```python
import pytest

@pytest.fixture
def base_order():
    return Order(id='o-1', total=20000, status='pending', paid=False)

@pytest.fixture
def paid_order(base_order):
    base_order.paid = True
    base_order.status = 'paid'
    return base_order

@pytest.fixture
def cancelled_order(base_order):
    base_order.status = 'cancelled'
    return base_order

def test_refund_only_for_paid_order(paid_order):
    assert can_refund(paid_order) is True

def test_refund_rejected_for_pending_order(base_order):
    assert can_refund(base_order) is False

def test_refund_rejected_for_cancelled_order(cancelled_order):
    assert can_refund(cancelled_order) is False
```

fixture를 이렇게 쪼개면 테스트 본문은 의도만 남고, 준비 로직은 한곳에서 관리됩니다. 특히 도메인 객체 필드가 바뀔 때 수정 지점이 명확해집니다.

## Mock으로 외부 의존 격리하기

단위 테스트에서 외부 의존을 제거할 때 `unittest.mock`은 매우 실용적입니다. 핵심은 "외부 호출 결과를 흉내" 내는 것보다 "호출 계약이 지켜졌는지"를 확인하는 데 있습니다.

```python
from unittest.mock import Mock, patch

def test_send_invoice_calls_mailer_with_expected_payload():
    mailer = Mock()
    service = BillingService(mailer=mailer)

    service.send_invoice(user_id='u-1', amount=39000)

    mailer.send.assert_called_once_with(
        to='u-1',
        subject='청구서가 발행되었습니다',
        body='결제 금액: 39,000원',
    )

def test_payment_retries_once_on_timeout():
    with patch('src.payment.client.charge') as charge:
        charge.side_effect = [TimeoutError(), {'status': 'ok'}]
        service = PaymentService()
        result = service.pay(user_id='u-1', amount=10000)

    assert result['status'] == 'ok'
    assert charge.call_count == 2
```

이 테스트는 네트워크 없이도 서비스 계층의 행위를 검증합니다. 다만 호출 인자 검증이 구현 세부사항에 과하게 묶이지 않도록, 비즈니스적으로 의미 있는 필드만 확인하는 균형이 필요합니다.

## 커버리지로 단위 테스트 공백 찾기

`pytest-cov`를 단위 테스트 루프에 연결하면 누락 분기를 빠르게 발견할 수 있습니다.

```bash
pytest tests/unit -q --cov=src/domain --cov-report=term-missing
```

```text
Name                     Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/domain/coupon.py        48      7    85%   33-36, 58-60
src/domain/tax.py           29      0   100%
src/domain/discount.py      35      3    91%   44-46
-------------------------------------------------------
TOTAL                      112     10    91%
```

`coupon.py`의 누락 라인이 "만료 쿠폰" 처리라면, 곧바로 회귀 버그로 이어질 가능성이 큽니다. 이런 경우에는 커버리지 임계값을 높이는 것보다, 누락된 규칙 케이스를 먼저 추가하는 편이 맞습니다.

## 단위 테스트를 CI 기본 계약으로 두기

단위 테스트는 가장 빠르기 때문에 CI에서 반드시 실행해야 합니다.

```yaml
name: unit-test
on:
  pull_request:

jobs:
  run-unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/unit -q --maxfail=1 --cov=src/domain --cov-report=term-missing
```

테스트 전략에서 가장 먼저 자동화해야 할 계층이 단위 테스트인 이유가 여기에 있습니다. 빠르고 싸고, 실패 원인이 선명하기 때문입니다.

## FIRST 원칙

좋은 단위 테스트는 다음 다섯 가지 성질을 만족합니다. Robert C. Martin의 FIRST 원칙으로도 알려져 있습니다.

| 원칙 | 의미 | 위반 신호 |
|------|------|-----------|
| Fast | 수백 개가 몇 초 안에 끝나야 합니다 | DB 연결, 파일 I/O, HTTP 호출 포함 |
| Independent | 테스트 순서를 바꿔도 결과가 같아야 합니다 | 전역 상태, 파일 공유, 테스트 간 의존 |
| Repeatable | 같은 코드를 몇 번 돌려도 같은 결과가 나와야 합니다 | 시간, 랜덤, 네트워크에 의존 |
| Self-validating | 통과/실패가 자동으로 판정되어야 합니다 | 사람이 로그를 직접 확인해야 하는 구조 |
| Timely | 코드 작성 직후 또는 직전에 씁니다 | 배포 전날 급조된 형식적 테스트 |

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|------|------|------------|
| DB나 네트워크를 붙이고 단위 테스트라 부름 | 느리고 환경에 따라 결과가 달라짐 | 외부 의존을 mock/stub으로 교체하거나 통합 테스트로 분류 |
| 테스트끼리 상태 공유 | 순서를 바꾸면 실패하는 불안정한 테스트 | 각 테스트에서 독립적으로 상태를 초기화 |
| 이름을 `test_1`, `test_case` 처럼 모호하게 지음 | 실패 메시지에서 원인을 바로 읽기 어려움 | `test_<행동>_<조건>_<기대결과>` 형식 사용 |
| 단언문 없이 실행만 확인 | 커버리지는 높지만 버그를 잡지 못함 | 의미 있는 `assert`로 결과를 명시적 검증 |
| 하나의 테스트에 여러 동작을 몰아넣음 | 실패 시 어느 단계가 문제인지 불분명 | 동작 하나당 테스트 하나 원칙 |
| 경계값을 빠뜨림 | 0, None, 음수, 최대값에서 런타임 오류 | 경계값을 파라미터화 테스트로 체계적으로 커버 |

## 단위 테스트를 설계 도구로 쓰기

시니어 엔지니어는 보통 단위 테스트를 도메인 설계 점검 도구로도 씁니다. 테스트를 쓰기 지나치게 어렵다면 함수 책임이 너무 많거나 의존이 과하게 얽혀 있을 가능성이 큽니다.

- Mock 설정이 테스트보다 길어진다면 의존이 과하게 퍼져 있는 신호입니다.
- 픽스처 없이 테스트 준비 코드가 50줄을 넘는다면 객체 생성이 복잡하다는 뜻입니다.
- 같은 모듈에서 테스트가 계속 깨진다면 설계 단순화가 필요할 수 있습니다.

테스트의 불편함이 설계의 불편함을 드러내는 경우가 많습니다. 테스트를 억지로 통과시키기 전에 코드 구조를 먼저 살펴보는 편이 낫습니다.

## 직접 검증해 볼 것

1. `apply_discount(1000, 100)`과 `apply_discount(1000, 0)`이 모두 기대값을 반환하는지 확인해 경계값 테스트가 실제로 작동하는지 봅니다.
2. `apply_discount(1000, 150)`처럼 예외 입력을 넣고 실패 메시지가 함수 계약을 분명하게 설명하는지 확인합니다.
3. 같은 테스트 파일에서 DB 연결이나 HTTP 호출이 끼어들지 않는지 살펴봅니다. 단위 테스트에 외부 의존이 붙는 순간 피드백 속도가 급격히 떨어집니다.

**예상 결과:** 정상 입력은 즉시 초록색으로 끝나고, 잘못된 퍼센트 입력은 `ValueError`를 분명하게 보여 줘야 합니다.

## 운영 체크리스트

- [ ] 함수 하나에 대해 테스트 세 개 이상을 작성했습니다.
- [ ] 경계값과 예외 케이스를 함께 다뤘습니다.
- [ ] AAA 구조로 읽히게 작성했습니다.
- [ ] `parametrize`를 한 번 이상 사용했습니다.
- [ ] 테스트 이름에 행동, 조건, 기대 결과가 담겨 있습니다.
- [ ] 외부 의존 없이 밀리초 단위로 실행됩니다.

## 연습 문제

1. `is_palindrome(s)` 함수를 만들고 다섯 입력으로 파라미터화 테스트를 작성해 보세요.
2. 빈 문자열, 한 글자, 공백 문자열 같은 경계값을 추가해 보세요.
3. 일부러 버그를 넣고 어떤 테스트가 잡는지 기록해 보세요.
4. fixture를 사용해 기본 사용자 객체를 만들고 role별 권한 테스트를 작성해 보세요.

## 정리

단위 테스트는 작고, 빠르고, 외부 의존이 없어야 합니다. 이 성질이 지켜질 때 테스트 피라미드의 바닥이 단단해집니다. 다음 글에서는 여러 부품을 실제로 연결했을 때 무엇이 깨지는지 확인하는 통합 테스트를 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- **Testing 101 (2/10): 단위 테스트 (현재 글)**
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [pytest — parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Martin Fowler — Unit Test](https://martinfowler.com/bliki/UnitTest.html)
- [Google Testing Blog](https://testing.googleblog.com/)

Tags: Testing, Unit Test, pytest, Python, Quality
