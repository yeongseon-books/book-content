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

이 글은 Testing 101 시리즈의 일곱 번째 글입니다. 여기서는 라인, 브랜치, 함수 커버리지의 차이, `pytest-cov`로 측정하는 기본 흐름, 위험 기반 우선순위 설정, 그리고 100퍼센트 숫자에 집착할 때 생기는 문제를 정리하겠습니다.

![Testing 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/07/07-01-diagram.ko.png)
*Testing 101 7장 흐름 개요*
> 커버리지는 지표일 뿐 목표가 아닙니다. 100% 커버리지도 모든 버그를 잡지는 못합니다.

## 이 글에서 다룰 문제

- 라인, 브랜치, 함수 커버리지는 무엇이 다를까요?
- `pytest-cov`로 커버리지를 어떻게 측정할까요?
- 테스트가 닿지 않은 코드는 어떻게 찾을까요?
- 100% 커버리지가 왜 위험한 착각을 만들까요?
- 위험 기반으로 커버리지 우선순위를 어떻게 정할까요?

테스트가 어디까지 닿았는지 모르면 공백 구간에서 사고가 납니다. 어떤 파일이 한 번도 실행되지 않았는지, 어떤 분기가 한쪽만 검증됐는지 모르는 상태에서는 팀이 눈가림으로 안전하다고 느끼기 쉽습니다.

반대로 숫자만 올리려는 테스트도 문제입니다. 코드가 실행됐다는 이유만으로 안전하다고 판단하면, 단언문이 빈약한 테스트가 대량으로 쌓입니다. 그래서 커버리지는 방향을 잡는 도구로만 써야 합니다.

## 커버리지 종류 비교

| 종류 | 설명 | 예시 |
|---|---|---|
| 라인 커버리지 | 전체 코드 줄 중 실행된 줄의 비율 | `result = a + b` 줄이 실행되면 카운트 |
| 브랜치 커버리지 | `if/else` 분기의 양쪽 경로가 모두 실행된 비율 | `if x > 0:` 의 True와 False 두 경로 |
| 조건 커버리지 | 복합 조건 내 각 하위 조건이 모두 평가된 비율 | `if a > 0 and b < 10:` 에서 a와 b의 조합 |
| 경로 커버리지 | 모든 가능한 실행 경로를 지나간 비율 | 여러 분기점 조합 |
| 함수 커버리지 | 정의된 함수가 한 번이라도 호출된 비율 | `def process():` 함수 호출 여부 |

라인 커버리지는 가장 기본이지만, `if/else`에서 한쪽만 지나가도 수치가 높게 나올 수 있습니다. 그래서 **브랜치 커버리지**를 함께 보는 편이 더 정직합니다. 경로 커버리지는 이론상 가장 꼼꼼하지만, 분기가 많아지면 경로 수가 폭발적으로 늘어나서 현실적으로 모두 커버하기 어렵습니다.

## 숫자 없이 감으로 판단 vs 보고서로 공백 파악

**숫자 없이 판단**

```text
- "테스트가 많다"는 말만 있다
- 어떤 줄이 한 번도 실행되지 않았는지 알 수 없다
- 결제 모듈의 음수 처리가 빠진 것을 배포 후 발견
```

**보고서로 공백 파악**

```text
src/payment.py: 78% (line 42, 57 uncovered → 음수 금액 처리 누락)
src/auth.py: 92% (line 11 uncovered → 비밀번호 재설정 만료 처리)
TOTAL: 84%
```

보고서가 있으면 적어도 어디가 비었는지는 알 수 있습니다. 그 다음 질문은 숫자가 낮은 이유가 무엇인지, 위험한 코드인지, 우선 보강할 가치가 있는지입니다.

## 다섯 단계로 pytest-cov 사용하기

### 1단계 — 설치

```bash
pip install pytest-cov
```

### 2단계 — 기본 보고서 보기

```bash
pytest --cov=src --cov-report=term-missing
```

```text
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/auth.py                45      8    82%   34, 41-49
src/order.py               92     12    87%   105, 118-128
src/payment.py             38      2    95%   67-68
src/utils.py               25      5    80%   15, 22-25
-----------------------------------------------------
TOTAL                     200     27    86%
```

### 3단계 — HTML 보고서 열기

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

빨간 줄이 테스트가 닿지 않은 부분입니다. HTML 보고서는 누락된 줄을 파일별로 직관적으로 확인할 수 있어 우선순위를 정할 때 유용합니다.

### 4단계 — 브랜치 커버리지까지 보기

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```

이 설정을 켜면 `if x > 0:`의 참 경로와 거짓 경로를 모두 지났는지도 확인할 수 있습니다. 라인 커버리지가 90%여도 브랜치 커버리지는 70%에 불과한 경우가 많습니다.

### 5단계 — CI 기준선 만들기

```toml
# pyproject.toml
[tool.coverage.report]
fail_under = 80
omit = [
    "src/migrations/*",
    "src/settings/*",
    "tests/*",
]
```

```bash
pytest --cov=src
# Coverage failure: total of 78 is less than fail_under=80
```

생성 코드, 마이그레이션 파일, 설정 파일은 측정 대상에서 제외하는 편이 의미 있는 수치를 유지하는 데 도움이 됩니다.

## 커버리지 100%의 함정

커버리지 100%는 모든 코드가 실행됐다는 의미이지, 모든 코드가 **올바르게 검증됐다**는 의미가 아닙니다.

**100% 커버리지인데 버그가 있는 코드**

```python
def calculate_discount(price: float, user_tier: str) -> float:
    discount = 0.0
    if user_tier == "gold":
        discount = price * 0.2
    elif user_tier == "silver":
        discount = price * 0.1
    return price - discount

def test_calculate_discount():
    # 모든 분기를 지나가므로 커버리지 100%
    result = calculate_discount(100, "gold")    # 실행만 하고
    result2 = calculate_discount(100, "silver") # 검증 없음
    result3 = calculate_discount(100, "bronze") # 검증 없음
```

이 테스트는 모든 분기를 지나가므로 커버리지는 100%입니다. 하지만 단언문이 없으므로 금액 계산이 틀려도 통과합니다.

**수정된 테스트**

```python
import pytest

@pytest.mark.parametrize("tier,price,expected", [
    ("gold", 100, 80.0),     # 20% 할인
    ("silver", 100, 90.0),   # 10% 할인
    ("bronze", 100, 100.0),  # 할인 없음
    ("gold", 0, 0.0),        # 가격 0
    ("gold", 1000, 800.0),   # 큰 금액
])
def test_calculate_discount_with_assertions(tier, price, expected):
    result = calculate_discount(price, tier)
    assert result == expected, f"tier={tier}, price={price}: expected {expected}, got {result}"
```

이제 테스트가 결과를 실제로 확인합니다. 커버리지 수치는 같지만 의미는 완전히 달라졌습니다.

## 위험 기반 커버리지 우선순위

만약 커버리지 80%를 목표로 한다면, 그 80%를 어떻게 채울지가 중요합니다. 모든 코드를 균등하게 볼 필요는 없습니다.

| 영역 | 위험도 | 목표 커버리지 | 이유 |
|---|---|---|---|
| 핵심 도메인 로직 | High | 90%+ | 비즈니스 규칙, 금액 계산, 상태 전이 |
| 외부 통합 계층 | Medium | 70~80% | API 호출, 결제, 네트워크 실패 처리 |
| 유틸리티 함수 | Low | 50~60% | 로깅, 포매팅, 단순 변환 |
| UI/화면 계층 | Very Low | 30~50% | 표시 로직, 레이아웃 분기 |
| 생성 코드/마이그레이션 | 제외 | — | 도구가 생성한 코드 |

**핵심 로직 집중 테스트 예시**

```python
# src/order.py — 핵심 도메인
def calculate_order_total(items: list, user: dict) -> float:
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    discount = apply_user_discount(subtotal, user["tier"])
    tax = calculate_tax(subtotal - discount, user["region"])
    return subtotal - discount + tax

# tests/unit/test_order.py — 90%+ 커버리지 목표
@pytest.mark.parametrize("tier,region,subtotal,expected", [
    ("gold", "KR", 200, 186.0),   # 200 - 20(할인) + 6(세금)
    ("basic", "KR", 200, 206.0),  # 할인 없음 + 6(세금)
    ("gold", "US", 200, 188.0),   # 다른 세율
    ("gold", "KR", 0, 0.0),       # 빈 장바구니
])
def test_calculate_order_total(tier, region, subtotal, expected):
    user = {"tier": tier, "region": region}
    items = [{"price": subtotal, "quantity": 1}]
    assert calculate_order_total(items, user) == pytest.approx(expected)
```

```python
# src/utils/formatting.py — 유틸리티 (50% 커버리지로 충분)
def format_currency(amount: float, currency: str = "USD") -> str:
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "KRW":
        return f"₩{int(amount):,}"
    return f"{amount:.2f} {currency}"

# 주요 케이스만 테스트
def test_format_currency_common_cases():
    assert format_currency(100.5, "USD") == "$100.50"
    assert format_currency(10000, "KRW") == "₩10,000"
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|------|------|------------|
| 100% 커버리지를 KPI로 관리 | 단언문 없는 테스트 양산, 형식적 실행 | 커버리지를 방향 지표로만 사용 |
| 라인 커버리지만 보고 안심 | `if/else` 한쪽만 검증해도 수치가 높게 나옴 | 브랜치 커버리지를 함께 활성화 |
| 생성 코드/마이그레이션 포함 측정 | 전체 수치는 높지만 의미 없음 | `omit` 설정으로 제외 |
| 신규/레거시 코드를 같은 기준으로 강제 | 팀이 게이트를 우회하기 시작 | 변경 라인 기준 또는 신규 코드 기준 별도 설정 |
| 커버리지 숫자만 보고 전략 판단 | 핵심 도메인 낮아도 유틸리티 높으면 평균 높음 | 파일별 누락 라인을 함께 확인 |
| 브랜치 커버리지 없이 분기 검증 | 예외 처리, else 경로 누락 | `--cov-branch` 항상 활성화 |

## 커버리지 CI 통합 예시

```yaml
# .github/workflows/coverage.yml
name: coverage-check
on:
  pull_request:

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements-dev.txt
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-branch \
                 --cov-report=term-missing \
                 --cov-report=html \
                 --cov-fail-under=80
      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-html
          path: htmlcov/
```

`--cov-fail-under=80`은 커버리지가 80% 미만이면 CI를 실패시킵니다. 처음 도입할 때는 현재 수치보다 조금 낮게 설정하고, 팀이 익숙해지면 점진적으로 올리는 편이 현실적입니다.

## 직접 검증해 볼 것

1. `pytest --cov=src --cov-report=term-missing` 결과에서 빠진 줄 두세 개를 실제 코드와 함께 읽어 봅니다. 숫자보다 빈칸 위치가 더 중요한지 금방 감이 옵니다.
2. 같은 테스트 묶음에 `--cov-branch`를 추가해 라인 수치와 브랜치 수치가 얼마나 달라지는지 비교합니다.
3. 새로 추가한 예외 처리 한 줄이 커버리지 보고서에 바로 반영되는지 확인해, CI 게이트가 실제 변경을 감시하는지 검증합니다.

**예상 결과:** 단순 총합 퍼센트보다 어떤 분기와 예외 경로가 비었는지가 더 선명하게 드러나야 합니다.

## 운영 관점에서 생각하기

많은 팀이 프로덕션 코드 기준 70퍼센트에서 85퍼센트 사이를 현실적인 범위로 잡습니다. 핵심 도메인 로직은 더 높게 유지하고, 어댑터나 화면 계층은 상대적으로 낮게 두기도 합니다.

경험 많은 엔지니어는 커버리지를 성과 지표보다 진단 지표로 씁니다. 숫자가 낮은 파일을 보면 먼저 왜 낮은지, 테스트가 어려운 구조인지, 위험한 경로가 빠졌는지 묻습니다. 숫자는 질문을 시작하게 만드는 재료이지, 질문을 끝내는 답이 아닙니다.

커버리지 보고서는 주간 회고에서 매우 유용합니다. 숫자만 보는 대신 누락 라인이 핵심 도메인인지 확인하고, 다음 스프린트에서 보강할 테스트를 합의하면 테스트 투자가 산발적으로 흩어지지 않습니다.

## 운영 체크리스트

- [ ] `pytest --cov` 보고서를 한 번 이상 읽었습니다.
- [ ] HTML 보고서의 빨간 줄을 확인했습니다.
- [ ] 브랜치 커버리지를 켜 보았습니다.
- [ ] CI에 최소 커버리지 기준을 설정했습니다.
- [ ] 생성 코드와 마이그레이션 파일을 측정에서 제외했습니다.
- [ ] 핵심 도메인과 유틸리티에 다른 목표 수치를 적용했습니다.

## 연습 문제

1. 프로젝트에서 커버리지가 가장 낮은 파일 하나를 찾아보세요.
2. 왜 낮은지 한 줄로 적고 추가할 테스트 세 개를 제안해 보세요.
3. 라인 커버리지와 브랜치 커버리지의 수치 차이를 비교해 보세요.
4. 단언문이 없는 테스트를 하나 만들어 커버리지 100%가 되는지 확인하고, 버그를 삽입해도 통과하는지 관찰해 보세요.

## 정리

커버리지는 건강 자체가 아니라 건강 신호입니다. 보고서를 읽으면 어디가 비었는지 알 수 있고, 그 공백을 메우는 우선순위를 정할 수 있습니다. 다음 글에서는 한 번 고친 버그가 다시 돌아오지 않게 만드는 회귀 테스트를 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- [Testing 101 (3/10): 통합 테스트](./03-integration-test.md)
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- **Testing 101 (7/10): 테스트 커버리지 (현재 글)**
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [pytest-cov docs](https://pytest-cov.readthedocs.io/)
- [coverage.py docs](https://coverage.readthedocs.io/)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
- [Google Testing Blog — Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)

Tags: Testing, Coverage, pytest-cov, Quality, Metrics
