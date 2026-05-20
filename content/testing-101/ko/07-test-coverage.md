---
series: testing-101
episode: 7
title: "Testing 101 (7/10): 테스트 커버리지"
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
  - Coverage
  - pytest-cov
  - Quality
  - Metrics
seo_description: 라인/브랜치 커버리지의 의미, 측정법, 그리고 100% 커버리지가 위험한 이유까지 한 번에 정리.
last_reviewed: '2026-05-12'
---

# Testing 101 (7/10): 테스트 커버리지

테스트를 어느 정도 썼는지 물으면 많은 팀이 숫자부터 말합니다. 80퍼센트인지, 90퍼센트인지, 아니면 100퍼센트를 목표로 하는지 같은 이야기입니다. 그런데 숫자만 보면 금방 착시가 생깁니다. 코드가 실행되었다는 사실과, 올바르게 검증되었다는 사실은 다르기 때문입니다.

커버리지는 유용합니다. 다만 목표가 아니라 진단 도구로 다룰 때만 유용합니다. 숫자를 올리기 위해 의미 없는 테스트를 추가하는 순간 지표는 남고 신뢰는 빠집니다.

이 글은 Testing 101 시리즈의 일곱 번째 글입니다. 여기서는 라인, 브랜치, 함수 커버리지의 차이, `pytest-cov`로 측정하는 기본 흐름, 그리고 100퍼센트 숫자에 집착할 때 생기는 문제를 정리하겠습니다.

## 먼저 던지는 질문

- 라인, 브랜치, 함수 커버리지는 무엇이 다를까요?
- `pytest-cov`로 커버리지를 어떻게 측정할까요?
- 테스트가 닿지 않은 코드는 어떻게 찾을까요?

## 큰 그림

![Testing 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/07/07-01-diagram.ko.png)

*Testing 101 7장 흐름 개요*

이 그림에서는 라인 커버리지, 브랜치 커버리지, 경로 커버리지의 차이와 각각의 한계를 보여줍니다. 높은 커버리지 수치가 반드시 높은 품질을 보장하지는 않습니다.

> 커버리지는 지표일 뿐 목표가 아닙니다. 100% 커버리지도 모든 버그를 잡지는 못합니다.

## 왜 중요한가

테스트가 어디까지 닿았는지 모르면 공백 구간에서 사고가 납니다. 어떤 파일이 한 번도 실행되지 않았는지, 어떤 분기가 한쪽만 검증됐는지 모르는 상태에서는 팀이 눈가림으로 안전하다고 느끼기 쉽습니다.

반대로 숫자만 올리려는 테스트도 문제입니다. 코드가 실행됐다는 이유만으로 안전하다고 판단하면, 단언문이 빈약한 테스트가 대량으로 쌓입니다. 그래서 커버리지는 방향을 잡는 도구로만 써야 합니다.

## 한눈에 보는 구조

프로덕션 코드를 실행하면 커버리지 도구가 어떤 줄과 분기가 실행됐는지 기록합니다. 보고서를 읽고 비어 있는 지점을 확인한 뒤, 필요한 테스트를 보강하는 흐름입니다. 그래서 커버리지는 테스트 작성의 출발점이 아니라 점검 단계에 가깝습니다.

## 핵심 용어

- **라인 커버리지**: 전체 줄 가운데 실제로 실행된 줄의 비율입니다.
- **브랜치 커버리지**: `if/else`처럼 갈라지는 분기의 양쪽이 모두 실행됐는지 보는 지표입니다.
- **함수 커버리지**: 함수가 한 번이라도 호출됐는지 보는 지표입니다.
- **미검증 코드(uncovered code)**: 테스트 실행 중 한 번도 지나가지 않은 코드입니다.
- **커버리지 게이트**: 최소 기준 아래로 떨어지면 CI를 실패시키는 설정입니다.

## 커버리지 종류

pytest-cov가 측정할 수 있는 커버리지 종류는 여러 가지입니다. 각각이 보여 주는 관점이 다릅니다.

| 종류 | 설명 | 예시 |
|---|---|---|
| **라인 커버리지** | 전체 코드 줄 중 실행된 줄의 비율 | `result = a + b` 줄이 실행되면 카운트 |
| **브랜치 커버리지** | `if/else` 분기의 양쪽 경로가 모두 실행된 비율 | `if x > 0:` 의 True와 False 두 경로 |
| **조건 커버리지** | 복합 조건 내 각 하위 조건이 모두 평가된 비율 | `if a > 0 and b < 10:` 에서 a와 b의 True/False 조합 |
| **경로 커버리지** | 모든 가능한 실행 경로를 지나간 비율 | 여러 분기점 조합 |

라인 커버리지는 가장 기본이지만, `if/else`에서 한쪽만 지나가도 수치가 높게 나올 수 있습니다. 그래서 **브랜치 커버리지**를 함께 보는 편이 더 정직합니다.

경로 커버리지는 이론상 가장 꼼꼼하지만, 분기가 많아지면 경로 수가 폭발적으로 늘어나서 현실적으로 모두 커버하기 어렵습니다. 대부분의 팀은 라인과 브랜치 커버리지 두 가지를 함께 봅니다.

## 바꾸기 전과 후

**바꾸기 전 — 숫자 없이 감으로 판단**

```text
- "테스트가 많다"는 말만 있다
- 어떤 줄이 한 번도 실행되지 않았는지 알 수 없다
```

**바꾼 뒤 — 보고서로 공백 파악**

```text
src/payment.py: 78% (line 42, 57 uncovered)
src/auth.py: 92% (line 11 uncovered)
TOTAL: 84%
```

보고서가 있으면 적어도 어디가 비었는지는 알 수 있습니다. 그 다음 질문은 숫자가 낮은 이유가 무엇인지, 위험한 코드인지, 우선 보강할 가치가 있는지입니다.

## 다섯 단계로 `pytest-cov` 사용하기

### 1단계 — 설치

```bash
pip install pytest-cov
```

### 2단계 — 기본 보고서 보기

```bash
pytest --cov=src --cov-report=term-missing
```

```text
src/calc.py    24    2    92%   18-19
src/auth.py    50   10    80%   34, 41-49
TOTAL         200   18    91%
```

### 3단계 — HTML 보고서 열기

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

빨간 줄이 테스트가 닿지 않은 부분입니다.

### 4단계 — 브랜치 커버리지까지 보기

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```

이 설정을 켜면 `if x > 0:`의 참 경로와 거짓 경로를 모두 지났는지도 확인할 수 있습니다.

### 5단계 — CI 기준선 만들기

```toml
# pyproject.toml
[tool.coverage.report]
fail_under = 80
```

```bash
pytest --cov=src
# Coverage failure: total of 78 is less than fail_under=80
```

### pytest-cov 터미널 출력 예시

실제 `pytest --cov` 명령을 실행하면 다음과 같은 텍스트 형식의 보고서가 나옵니다.

```text
========================= test session starts ==========================
platform linux -- Python 3.11.5, pytest-7.4.3, pluggy-1.3.0
rootdir: /home/user/project
plugins: cov-4.1.0
collected 42 items

tests/test_auth.py .......                                        [ 16%]
tests/test_payment.py ............                                [ 45%]
tests/test_order.py .......................                       [100%]

---------- coverage: platform linux, python 3.11.5 -----------
Name                    Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/__init__.py             0      0   100%
src/auth.py                45      8    82%   34, 41-49
src/order.py               92     12    87%   105, 118-128
src/payment.py             38      2    95%   67-68
src/utils.py               25      5    80%   15, 22-25
-------------------------------------------------------
TOTAL                     200     27    86%

========================= 42 passed in 2.34s ===========================
```

이 보고서에서 볼 점은 다음과 같습니다.

- **Stmts**: 전체 실행 가능한 줄 수
- **Miss**: 테스트가 닿지 않은 줄 수
- **Cover**: 커버리지 비율 `(Stmts - Miss) / Stmts * 100`
- **Missing**: 테스트가 빠진 구체적인 줄 번호

`--cov-report=term-missing` 옵션을 추가하면 Missing 열이 표시되고, 어느 파일의 어느 줄이 비었는지 바로 볼 수 있습니다. 이 정보로 다음 테스트를 어디에 추가할지 판단합니다.

## 이 코드에서 먼저 볼 점

- 라인 커버리지는 실행 여부만 보여 줍니다. 값이 맞는지는 단언문이 따로 보장해야 합니다.
- 브랜치 커버리지는 분기 누락을 더 정직하게 드러냅니다.
- HTML 보고서는 비어 있는 줄을 빠르게 찾는 데 유용합니다.

그래서 숫자 하나보다 보고서의 빈칸이 더 중요합니다. 어떤 분기가 빠졌는지, 예외 경로가 비어 있는지, 핵심 도메인 코드가 낮은지부터 봐야 합니다.

## 커버리지 100%의 함정

커버리지 100%는 모든 코드가 실행됐다는 의미이지, 모든 코드가 **올바르게 검증됐다**는 의미가 아닙니다. 코드가 실행되었지만 단언문이 없으면 버그는 그대로 남습니다.

**100% 커버리지인데 버그가 있는 코드**

```python
def calculate_discount(price: float, user_tier: str) -> float:
    """Calculate discount based on user tier."""
    discount = 0.0
    if user_tier == "gold":
        discount = price * 0.2
    elif user_tier == "silver":
        discount = price * 0.1
    return price - discount


def test_calculate_discount():
    result = calculate_discount(100, "gold")
    # 실행만 하고 검증하지 않음
    
    result2 = calculate_discount(100, "silver")
    # 역시 검증 없음
```

이 테스트는 모든 분기를 지나가므로 커버리지는 100%입니다. 하지만 단언문이 없으므로 다음 버그를 잡지 못합니다.

```python
# 버그: 할인을 빼면 음수가 될 수 있음
result = calculate_discount(10, "gold")  # 10 - 2 = 8 (OK)
result = calculate_discount(5, "gold")   # 5 - 1 = 4 (OK)
# 그런데 비즈니스 로직상 할인은 최대 50%여야 하는데, 테스트가 이를 확인하지 않음
```

**수정한 테스트**

```python
def test_calculate_discount_with_assertions():
    # gold tier: 20% discount
    assert calculate_discount(100, "gold") == 80
    
    # silver tier: 10% discount
    assert calculate_discount(100, "silver") == 90
    
    # unknown tier: no discount
    assert calculate_discount(100, "bronze") == 100
    
    # edge case: zero price
    assert calculate_discount(0, "gold") == 0
```

이제 테스트가 결과를 실제로 확인합니다. 커버리지 수치는 같지만 의미는 완전히 달라졌습니다. 커버리지는 테스트 **범위**를 보여 주지만, 테스트 **품질**까지 보장하지는 못합니다.
## 어디서 자주 헷갈릴까요?

가장 흔한 실수는 100퍼센트를 KPI처럼 다루는 일입니다. 그러면 의미 없는 호출 테스트나 단언문 없는 테스트가 늘어납니다.

둘째, 라인 커버리지만 보고 안심하는 경우입니다. `if/else`에서 한쪽만 지나가도 라인 수치가 높게 나올 수 있으므로 브랜치 커버리지를 함께 봐야 합니다.

셋째, 새 코드와 레거시 코드를 같은 기준으로 묶는 경우입니다. 오래된 코드베이스에서는 전체 평균보다 변경 라인 기준이나 신규 코드 기준을 따로 두는 편이 현실적일 때가 많습니다.

## 위험 기반 커버리지 — 어디에 투자할까

만약 커버리지 80%를 목표로 한다면, 그 80%를 어떻게 채울지가 중요합니다. 모든 코드를 균등하게 볼 필요는 없습니다.

**위험도별 커버리지 우선순위**

| 영역 | 위험도 | 목표 커버리지 | 이유 |
|---|---|---|---|
| 핵심 도메인 로직 | High | 90%+ | 비즈니스 규칙, 금액 계산, 상태 전이 |
| 외부 통합 | Medium | 70~80% | API 호출, 결제, 네트워크 실패 처리 |
| 유틸리티 함수 | Low | 50~60% | 로깅, 포매팅, 단순 변환 |
| UI/화면 계층 | Very Low | 30~50% | 표시 로직, 레이아웃 분기 |

**예시: 핵심 로직 집중 테스트**

```python
# src/order.py — 핵심 도메인
def calculate_order_total(items: list[Item], user: User) -> Money:
    """Calculate order total with discounts and tax."""
    subtotal = sum(item.price * item.quantity for item in items)
    discount = apply_user_discount(subtotal, user.tier)
    tax = calculate_tax(subtotal - discount, user.region)
    return Money(subtotal - discount + tax)


# tests/test_order.py — 90%+ 커버리지 목표
def test_calculate_order_total_all_paths():
    # normal case
    items = [Item(price=100, quantity=2)]
    user = User(tier="gold", region="KR")
    total = calculate_order_total(items, user)
    assert total.amount == 186  # 200 - 20 (discount) + 6 (tax)
    
    # no discount
    user_basic = User(tier="basic", region="KR")
    total_basic = calculate_order_total(items, user_basic)
    assert total_basic.amount == 206
    
    # zero items
    assert calculate_order_total([], user).amount == 0
    
    # different region
    user_us = User(tier="gold", region="US")
    total_us = calculate_order_total(items, user_us)
    assert total_us.amount == 188  # different tax rate
```

```python
# src/utils/formatting.py — 유틸리티
def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "KRW":
        return f"₩{int(amount):,}"
    return f"{amount:.2f} {currency}"


# tests/test_formatting.py — 50% 커버리지로 충분
def test_format_currency_common_cases():
    assert format_currency(100.5, "USD") == "$100.50"
    assert format_currency(10000, "KRW") == "₩10,000"
    # 소수 통화는 테스트하지 않아도 됨 (실무에서 거의 안 쓰임)
```

위험 기반 접근을 쓰면 제한된 시간을 가장 중요한 곳에 집중할 수 있습니다. 평균 80% 커버리지라도, 핵심 로직은 90%+, 유틸리티는 50%로 분산하는 것이 순수 전체 평균보다 훬씬 효과적입니다.

## 직접 검증해 볼 것

1. `pytest --cov=src --cov-report=term-missing` 결과에서 빠진 줄 두세 개를 실제 코드와 함께 읽어 봅니다. 숫자보다 빈칸 위치가 더 중요한지 금방 감이 옵니다.
2. 같은 테스트 묶음에 `--cov-branch`를 추가해 라인 수치와 브랜치 수치가 얼마나 달라지는지 비교합니다.
3. 새로 추가한 예외 처리 한 줄이 커버리지 보고서에 바로 반영되는지 확인해, CI 게이트가 실제 변경을 감시하는지 검증합니다.

**예상 결과:** 단순 총합 퍼센트보다 어떤 분기와 예외 경로가 비었는지가 더 선명하게 드러나야 합니다.

## 실패 신호와 첫 점검

- 높은 라인 커버리지인데도 장애가 반복되면 단언문이 약하거나 브랜치 검증이 빠졌을 가능성이 큽니다.
- 생성 코드나 마이그레이션 파일까지 한데 묶어 측정하면 숫자는 올라가도 의사결정 품질은 떨어집니다.
- 신규 코드와 레거시 코드를 같은 기준으로 강제하다가 팀이 아예 게이트를 우회하기 시작하면 전략을 다시 잡아야 합니다.

## 실무에서는 이렇게 생각합니다

많은 팀이 프로덕션 코드 기준 70퍼센트에서 85퍼센트 사이를 현실적인 범위로 잡습니다. 핵심 도메인 로직은 더 높게 유지하고, 어댑터나 화면 계층은 상대적으로 낮게 두기도 합니다.

경험 많은 엔지니어는 커버리지를 성과 지표보다 진단 지표로 씁니다. 숫자가 낮은 파일을 보면 먼저 왜 낮은지, 테스트가 어려운 구조인지, 위험한 경로가 빠졌는지 묻습니다. 숫자는 질문을 시작하게 만드는 재료이지, 질문을 끝내는 답이 아닙니다.

## 체크리스트

- [ ] `pytest --cov` 보고서를 한 번 이상 읽었습니다.
- [ ] HTML 보고서의 빨간 줄을 확인했습니다.
- [ ] 브랜치 커버리지를 켜 보았습니다.
- [ ] CI에 최소 커버리지 기준을 설정했습니다.

## 연습 문제

1. 프로젝트에서 커버리지가 가장 낮은 파일 하나를 찾아보세요.
2. 왜 낮은지 한 줄로 적고 추가할 테스트 세 개를 제안해 보세요.
3. 라인 커버리지와 브랜치 커버리지의 수치 차이를 비교해 보세요.

## 정리

커버리지는 건강 자체가 아니라 건강 신호입니다. 보고서를 읽으면 어디가 비었는지 알 수 있고, 그 공백을 메우는 우선순위를 정할 수 있습니다. 다음 글에서는 한 번 고친 버그가 다시 돌아오지 않게 만드는 회귀 테스트를 보겠습니다.

## 처음 질문으로 돌아가기

- **라인, 브랜치, 함수 커버리지는 무엇이 다를까요?**
  - 커버리지 도구는 테스트가 코드의 어느 부분을 실행했는지 측정하는 수단입니다.
- **`pytest-cov`로 커버리지를 어떻게 측정할까요?**
  - 같은 커버리지 수치라도 라인 커버리지, 브랜치 커버리지, 경로 커버리지는 다른 결과를 줄 수 있습니다.
- **테스트가 닿지 않은 코드는 어떻게 찾을까요?**
  - 무리해서 100% 커버리지를 쫓기보다는 위험한 로직부터 촘촘히 검증하는 것이 비용 효율이 좋습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- **테스트 커버리지 (현재 글)**
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)

<!-- toc:end -->

## 참고 자료

- [pytest-cov docs](https://pytest-cov.readthedocs.io/)
- [coverage.py docs](https://coverage.readthedocs.io/)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
- [Google Testing Blog — Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)

Tags: Testing, Coverage, pytest-cov, Quality, Metrics
