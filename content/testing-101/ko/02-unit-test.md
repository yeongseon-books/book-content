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

![Testing 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/02/02-01-diagram.ko.png)
*Testing 101 2장 흐름 개요*
> 단위 테스트는 한 가지 동작만 검증하고, 같은 동작을 여러 번 실행해도 같은 결과가 나와야 합니다.

## 먼저 던지는 질문

- 단위 테스트는 정확히 어디까지를 검증할까요?
- AAA 패턴은 왜 많이 쓰일까요?
- `pytest`의 fixture와 parametrize는 언제 도움이 될까요?

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

## 단위 테스트와 통합 테스트 비교

단위 테스트를 처음 배울 때 가장 헷갈리는 지점은 통합 테스트와의 경계입니다. 다음 표는 두 테스트 계층의 차이를 보여 줍니다.

| 항목 | 단위 테스트 | 통합 테스트 |
|---|---|---|
| 검증 범위 | 함수나 메서드 하나 | 여러 컴포넌트가 연결된 흐름 |
| 외부 의존 | 없음 (또는 mock/stub 사용) | 실제 DB, HTTP 등 포함 |
| 실행 속도 | 밀리초 단위 | 수백 밀리초 ~ 초 단위 |
| 실패 시 원인 파악 | 즉시 가능 (범위가 좁음) | 조금 더 넓음 (여러 계층 포함) |
| 테스트 수 | 수백~수천 개 | 수십~수백 개 |
| CI 실행 빈도 | 모든 PR, 모든 커밋 | 선택적 또는 병합 전 |

이 구분이 중요한 이유는 테스트 전략 때문입니다. 단위 테스트는 많고 빠르고 좁아야 하고, 통합 테스트는 적고 느리지만 경계를 확인해야 합니다. 두 계층의 성질을 섞으면 빠르지도 않고 범위도 애매한 테스트가 됩니다.

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

## 다섯 단계로 파이테스트 시작하기

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

실무 프로젝트에서는 단위 테스트가 수백 개를 넘기는 일이 흔합니다. 이때 각 테스트가 독립적이고 빠르게 실행되어야 CI 파이프라인에서 피드백 시간을 짧게 유지할 수 있습니다. 느린 테스트 하나가 전체 스위트를 지연시키면, 팀원들이 테스트를 건너뛰는 습관으로 이어질 수 있습니다.

## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 실제 데이터베이스나 네트워크를 붙인 채 단위 테스트라고 부르는 경우입니다. 외부 의존이 붙으면 그 시점부터는 단위 테스트보다 통합 테스트에 가까워집니다.

또 하나는 테스트끼리 상태를 공유하는 경우입니다. 이전 테스트가 남긴 값을 다음 테스트가 기대하면 실행 순서가 바뀌는 순간 깨집니다. 단위 테스트는 어떤 순서로 돌려도 같은 결과가 나와야 합니다.

이름을 대충 붙이는 문제도 자주 보입니다. `test_1`, `test_2` 같은 이름은 실패했을 때 아무 설명을 주지 못합니다. 테스트 이름은 동작 설명서라고 생각하는 편이 좋습니다.

## 좋은 단위 테스트의 조건

좋은 단위 테스트는 다음 다섯 가지 성질을 만족합니다.

### 1. 빠르다 (Fast)

수백 개가 있어도 몇 초 안에 끝나야 합니다. 외부 네트워크나 디스크 IO가 들어가면 빠르지 않습니다.

### 2. 독립적이다 (Independent)

테스트 순서를 바꿔도, 병렬로 돌려도 결과가 같아야 합니다. 이전 테스트의 상태에 의존하면 안 됩니다.

### 3. 반복 가능하다 (Repeatable)

같은 코드를 백 번 실행해도 같은 결과가 나와야 합니다. 시간, 랜덤, 네트워크에 의존하면 반복성이 무너집니다.

### 4. 스스로 검증한다 (Self-validating)

테스트 결과를 사람이 판단하지 않습니다. 통과와 실패가 자동으로 판정되어야 합니다.

### 5. 적시에 작성한다 (Timely)

코드를 작성한 직후, 또는 코드 작성 전에 테스트를 씁니다. 배포 전날 급하게 쓰는 테스트는 형식적입니다.

이 다섯 가지는 Robert C. Martin의 FIRST 원칙으로도 알려져 있습니다. 이 원칙을 어기는 테스트는 느리고, 불안정하고, 신뢰받지 못합니다.
## 테스트 함수 이름 짓기

테스트 이름은 실패했을 때 읽는 첫 번째 설명서입니다. 다음은 좋은 테스트 이름과 나쁜 테스트 이름의 비교입니다.

**나쁜 예:**

```python
def test_1(): ...
def test_discount(): ...
def test_user(): ...
```

**좋은 예:**

```python
def test_apply_discount_with_zero_percent_returns_original_price(): ...
def test_create_user_with_duplicate_email_raises_value_error(): ...
def test_calculate_total_with_empty_cart_returns_zero(): ...
```

좋은 테스트 이름은 다음 세 가지 정보를 담습니다.

1. **무엇을 하는가** (동작, 함수명)
2. **어떤 조건에서** (입력, 상태)
3. **무엇을 기대하는가** (결과, 예외)

이름이 길어지는 것은 문제가 아닙니다. 실패 로그에서 어떤 시나리오가 깨졌는지 바로 알 수 있다면 길이는 부차적입니다. 테스트 이름을 줄이려다 의미를 잃는 것이 더 큰 손해입니다.

실무에서는 `test_<action>_<condition>_<result>` 형식을 자주 씁니다. 예를 들어 `test_login_with_invalid_password_returns_401`처럼 쓰면 테스트 목록만 봐도 검증 범위가 드러납니다.
## 경계값 테스트 — 버그가 숨는 곳

경계값은 정상 케이스보다 버그를 더 잘 드러냅니다. `0`, `None`, 빈 문자열, 음수, 최대값 같은 입력은 조건문과 반복문의 경계에서 예상 밖의 동작을 일으킵니다.

다음은 경계값 테스트를 추가한 예시입니다.

```python
import pytest

@pytest.mark.parametrize("price,percent,expected", [
    (1000, 0, 1000),       # 경계: 할인 없음
    (1000, 100, 0),        # 경계: 전액 할인
    (0, 50, 0),            # 경계: 가격 0
    (1, 1, 0),             # 경계: 최소 단위
])
def test_apply_discount_edge_cases(price, percent, expected):
    assert apply_discount(price, percent) == expected

@pytest.mark.parametrize("price,percent", [
    (1000, -1),            # 경계: 음수 퍼센트
    (1000, 101),           # 경계: 범위 초과
])
def test_apply_discount_rejects_invalid_percent(price, percent):
    with pytest.raises(ValueError):
        apply_discount(price, percent)
```

경계값 테스트는 코드 리뷰에서 자주 등장하는 질문입니다. `0`일 때는? `None`일 때는? 빈 배열일 때는? 이 질문에 코드로 답하는 것이 경계값 테스트의 역할입니다.
## 단위 테스트를 도메인 규칙에 맞추는 확장 패턴

단위 테스트를 충분히 작성했는데도 운영 버그가 계속 나오는 팀은 대체로 같은 문제를 겪습니다. 함수 단위 분기는 많이 테스트했지만, 비즈니스 규칙의 조합을 충분히 다루지 못한 경우입니다. 예를 들어 할인 정책은 "회원 등급"과 "쿠폰"과 "최대 할인 상한"이 함께 작동합니다. 이때 조합 테스트를 설계하지 않으면 단일 케이스가 모두 통과해도 실제 시나리오에서 실패할 수 있습니다.

```python
import pytest

@pytest.mark.parametrize(
    'tier,coupon,amount,expected',
    [
        ('bronze', None, 10000, 10000),
        ('silver', None, 10000, 9500),
        ('gold', 'WELCOME10', 10000, 8500),
        ('gold', 'VIP30', 10000, 7000),   # 상한 적용
    ],
)
def test_calculate_price_by_tier_and_coupon(tier, coupon, amount, expected):
    assert calculate_final_price(tier=tier, coupon=coupon, amount=amount) == expected
```

이 방식은 단순히 케이스 수를 늘리는 것이 아니라, 규칙 표를 테스트로 고정한다는 의미가 있습니다. 정책 문서가 바뀌면 표를 먼저 업데이트하고 테스트를 실패시켜 수정 범위를 드러내는 흐름이 효과적입니다.

## 픽스처 계층화로 준비 비용 줄이기

단위 테스트가 늘어날수록 fixture를 한 단계로만 운영하면 재사용성과 가독성이 동시에 떨어집니다. 실무에서는 "기본 객체"와 "상태 변형"을 분리해 계층화하면 유지보수가 쉬워집니다.

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

def test_refund_only_for_paid_order(paid_order):
    assert can_refund(paid_order) is True

def test_refund_rejected_for_pending_order(base_order):
    assert can_refund(base_order) is False
```

fixture를 이렇게 쪼개면 테스트 본문은 의도만 남고, 준비 로직은 한곳에서 관리됩니다. 특히 도메인 객체 필드가 바뀔 때 수정 지점이 명확해집니다.

## 유닛테스트 목 객체로 단위 경계 고정하기

단위 테스트에서 외부 의존을 제거할 때 `unittest.mock`은 매우 실용적입니다. 핵심은 "외부 호출 결과를 흉내" 내는 것보다 "호출 계약이 지켜졌는지"를 확인하는 데 있습니다.

```python
from unittest.mock import Mock

def test_send_invoice_calls_mailer_with_expected_payload():
    mailer = Mock()
    service = BillingService(mailer=mailer)

    service.send_invoice(user_id='u-1', amount=39000)

    mailer.send.assert_called_once_with(
        to='u-1',
        subject='청구서가 발행되었습니다',
        body='결제 금액: 39000원',
    )
```

이 테스트는 네트워크 없이도 서비스 계층의 행위를 검증합니다. 다만 호출 인자 검증이 구현 세부사항에 과하게 묶이지 않도록, 비즈니스적으로 의미 있는 필드만 확인하는 균형이 필요합니다.

## 커버리지 리포트로 단위 테스트 공백 찾기

`pytest-cov`를 단위 테스트 루프에 연결하면 누락 분기를 빠르게 발견할 수 있습니다.

```bash
pytest tests/unit -q --cov=src/domain --cov-report=term-missing
```

```text
Name                     Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/domain/coupon.py        48      7    85%   33-36, 58-60
src/domain/tax.py           29      0   100%
-------------------------------------------------------
TOTAL                       77      7    90%
```

`coupon.py`의 누락 라인이 "만료 쿠폰" 처리라면, 곧바로 회귀 버그로 이어질 가능성이 큽니다. 이런 경우에는 커버리지 임계값을 높이는 것보다, 누락된 규칙 케이스를 먼저 추가하는 편이 맞습니다.

## 단위 테스트를 지속적 통합 기본 계약으로 두기

단위 테스트는 가장 빠르기 때문에 CI에서 반드시 실행해야 합니다. 다음 구성은 최소 기준으로 충분합니다.

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
      - run: pytest tests/unit -q --maxfail=1
```

테스트 전략에서 가장 먼저 자동화해야 할 계층이 단위 테스트인 이유가 여기에 있습니다. 빠르고 싸고, 실패 원인이 선명하기 때문입니다.

## 직접 검증해 볼 것

1. `apply_discount(1000, 100)`과 `apply_discount(1000, 0)`이 모두 기대값을 반환하는지 확인해 경계값 테스트가 실제로 작동하는지 봅니다.
2. `apply_discount(1000, 150)`처럼 예외 입력을 넣고 실패 메시지가 함수 계약을 분명하게 설명하는지 확인합니다.
3. 같은 테스트 파일에서 DB 연결이나 HTTP 호출이 끼어들지 않는지 살펴봅니다. 단위 테스트에 외부 의존이 붙는 순간 피드백 속도가 급격히 떨어집니다.

**예상 결과:** 정상 입력은 즉시 초록색으로 끝나고, 잘못된 퍼센트 입력은 `ValueError`를 분명하게 보여 줘야 합니다.

## 심화 실습: 운영 관점 테스트 점검

실무에서 테스트를 확장할 때 가장 먼저 해야 할 일은 실패 원인을 사람이 추측하지 않도록 로그와 단언문을 정리하는 것입니다. 테스트 실패 메시지에는 입력값, 기대값, 실제값이 함께 남아야 하며, 그래야 CI 로그만으로도 원인을 좁힐 수 있습니다.

또한 테스트는 코드와 함께 진화해야 합니다. 기능이 바뀌었는데 테스트가 그대로라면 테스트는 안전장치가 아니라 오경보 장치가 됩니다. 그래서 팀에서는 요구사항 변경 PR에 테스트 변경이 함께 포함되는지를 리뷰 기준으로 두는 편이 좋습니다.

fixture는 단순 편의 기능이 아니라 설계 도구입니다. 어떤 객체를 기본 상태로 두는지, 어떤 상태 변형을 허용하는지 fixture 레이어에서 명확히 정의하면 테스트 의도가 깔끔해집니다. 특히 도메인 객체가 복잡할수록 fixture 설계 품질이 테스트 유지보수 비용을 좌우합니다.

회귀 버그를 줄이려면 버그 티켓이 닫힐 때 반드시 재현 테스트를 남겨야 합니다. 수정 코드만 머지하면 같은 원인의 버그가 다른 경로에서 재발합니다. 반대로 재현 테스트를 함께 남기면 팀 지식이 실행 가능한 형태로 축적됩니다.

커버리지 리포트는 주간 회고에서 매우 유용합니다. 숫자만 보는 대신 누락 라인이 핵심 도메인인지 확인하고, 다음 스프린트에서 보강할 테스트를 합의하면 테스트 투자가 산발적으로 흩어지지 않습니다.

CI에서는 실패를 빠르게 보여 주는 순서가 중요합니다. 일반적으로 단위 테스트를 먼저 실행하고, 그 다음 통합 테스트, 마지막으로 느린 E2E를 배치하면 평균 피드백 시간이 줄어듭니다. 파이프라인 설계도 테스트 전략의 일부로 다루어야 합니다.

실무에서 테스트를 확장할 때 가장 먼저 해야 할 일은 실패 원인을 사람이 추측하지 않도록 로그와 단언문을 정리하는 것입니다. 테스트 실패 메시지에는 입력값, 기대값, 실제값이 함께 남아야 하며, 그래야 CI 로그만으로도 원인을 좁힐 수 있습니다.

또한 테스트는 코드와 함께 진화해야 합니다. 기능이 바뀌었는데 테스트가 그대로라면 테스트는 안전장치가 아니라 오경보 장치가 됩니다. 그래서 팀에서는 요구사항 변경 PR에 테스트 변경이 함께 포함되는지를 리뷰 기준으로 두는 편이 좋습니다.

fixture는 단순 편의 기능이 아니라 설계 도구입니다. 어떤 객체를 기본 상태로 두는지, 어떤 상태 변형을 허용하는지 fixture 레이어에서 명확히 정의하면 테스트 의도가 깔끔해집니다. 특히 도메인 객체가 복잡할수록 fixture 설계 품질이 테스트 유지보수 비용을 좌우합니다.

회귀 버그를 줄이려면 버그 티켓이 닫힐 때 반드시 재현 테스트를 남겨야 합니다. 수정 코드만 머지하면 같은 원인의 버그가 다른 경로에서 재발합니다. 반대로 재현 테스트를 함께 남기면 팀 지식이 실행 가능한 형태로 축적됩니다.

커버리지 리포트는 주간 회고에서 매우 유용합니다. 숫자만 보는 대신 누락 라인이 핵심 도메인인지 확인하고, 다음 스프린트에서 보강할 테스트를 합의하면 테스트 투자가 산발적으로 흩어지지 않습니다.

CI에서는 실패를 빠르게 보여 주는 순서가 중요합니다. 일반적으로 단위 테스트를 먼저 실행하고, 그 다음 통합 테스트, 마지막으로 느린 E2E를 배치하면 평균 피드백 시간이 줄어듭니다. 파이프라인 설계도 테스트 전략의 일부로 다루어야 합니다.

```python
from unittest.mock import patch

def test_payment_service_retries_once_on_timeout():
    service = PaymentService()
    with patch('src.payment.client.charge') as charge:
        charge.side_effect = [TimeoutError(), {'status': 'ok'}]
        result = service.pay(user_id='u-1', amount=10000)

    assert result['status'] == 'ok'
    assert charge.call_count == 2
```

```bash
pytest -q --maxfail=1 --disable-warnings
pytest --cov=src --cov-report=term-missing
```

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
  - 단위 테스트는 가장 작은 검증 단위입니다. 한 함수나 메서드의 한 가지 경로만 검증하므로, 실패했을 때 정확히 어느 부분이 깨졌는지 바로 알 수 있습니다.
- **AAA 패턴은 왜 많이 쓰일까요?**
  - AAA 패턴은 준비, 실행, 검증의 세 단계를 명확히 분리해 테스트를 읽기 쉽게 만듭니다. 이 패턴을 따르면 테스트 의도가 코드로 드러나므로 유지보수가 편합니다.
- **`pytest`의 fixture와 parametrize는 언제 도움이 될까요?**
  - 픽스처와 파라미터화는 여러 테스트가 같은 데이터로 돌도록 준비를 줄이는 기법입니다. 빠른 단위 테스트를 유지하려면 외부 의존 없이 메모리상 데이터만 사용해야 합니다.

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

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [pytest — parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Martin Fowler — Unit Test](https://martinfowler.com/bliki/UnitTest.html)
- [Google Testing Blog](https://testing.googleblog.com/)

Tags: Testing, Unit Test, pytest, Python, Quality
