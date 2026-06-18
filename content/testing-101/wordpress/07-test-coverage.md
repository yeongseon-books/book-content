---
series: testing-101
episode: 7
title: "바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지"
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
  - Coverage
  - pytest-cov
  - Quality
  - Metrics
seo_description: AI가 만든 코드 중 테스트가 닿지 않은 부분을 찾는 커버리지 측정법. 100% 커버리지의 함정과 바이브코딩 팀의 현실적인 커버리지 전략.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지

이 글은 **바이브코딩을 위한 테스팅 기초** 시리즈의 일곱 번째 글입니다. AI가 만든 코드에서 테스트가 닿지 않은 위험한 부분을 찾는 방법과 커버리지를 올바르게 해석하는 방법을 설명합니다.

---

AI가 코드를 만들면 테스트도 같이 만들어 달라고 요청할 수 있습니다. 그런데 AI가 만든 테스트가 높은 커버리지를 보여줘도 실제로 배포 후 터지는 경우가 있습니다. 코드가 실행되었다는 사실과 올바르게 검증되었다는 사실은 다르기 때문입니다.

커버리지는 AI가 만든 코드에서 테스트가 닿지 않은 위험한 구간을 찾는 진단 도구입니다. 숫자를 올리는 것이 목적이 아니라, 어디가 비었는지 파악하는 것이 목적입니다.

> 커버리지는 지표일 뿐 목표가 아닙니다. AI가 만든 테스트의 100% 커버리지도 모든 버그를 잡지는 못합니다.

## 이 글에서 다룰 문제

- 라인, 브랜치, 함수 커버리지는 무엇이 다를까요?
- `pytest-cov`로 커버리지를 어떻게 측정할까요?
- AI가 만든 테스트에서 자주 빠지는 코드는 어디일까요?
- 커버리지 100%인데도 버그가 있는 이유는 무엇일까요?
- 바이브코딩 팀의 현실적인 커버리지 목표는 무엇일까요?

AI가 만든 테스트는 정상 케이스는 잘 커버하지만 예외 경로나 경계값을 빠뜨리는 경우가 많습니다. 커버리지 보고서를 통해 이 공백을 찾아 보강하는 것이 바이브코딩 팀의 핵심 습관입니다.

## 한눈에 보는 구조

코드를 실행하면 커버리지 도구가 어떤 줄과 분기가 실행됐는지 기록합니다. 보고서를 읽고 비어 있는 지점을 확인한 뒤, AI에게 추가 테스트를 요청하거나 직접 보강합니다.

- **라인 커버리지**: 전체 줄 가운데 실제로 실행된 줄의 비율입니다.
- **브랜치 커버리지**: `if/else`처럼 갈라지는 분기의 양쪽이 모두 실행됐는지 보는 지표입니다.
- **함수 커버리지**: 함수가 한 번이라도 호출됐는지 보는 지표입니다.
- **미검증 코드(uncovered code)**: 테스트 실행 중 한 번도 지나가지 않은 코드입니다.
- **커버리지 게이트**: 최소 기준 아래로 떨어지면 CI를 실패시키는 설정입니다.

## 커버리지 종류

| 종류 | 설명 | AI 코드에서의 의미 |
|---|---|---|
| **라인 커버리지** | 전체 코드 줄 중 실행된 줄의 비율 | AI가 만든 코드 중 한 번도 실행 안 된 줄 |
| **브랜치 커버리지** | `if/else` 분기의 양쪽 경로 실행 비율 | AI가 빠뜨린 else 분기나 예외 경로 |
| **함수 커버리지** | 함수가 한 번이라도 호출된 비율 | AI가 만들었지만 한 번도 테스트 안 된 함수 |

AI가 만든 코드에서 브랜치 커버리지는 특히 중요합니다. AI는 정상 경로(happy path)는 잘 테스트하지만 else 분기나 예외 처리는 빠뜨리는 경향이 있습니다.

## 바꾸기 전과 후

**바꾸기 전 — 커버리지 없이 감으로 판단**

```text
- AI가 테스트를 만들었음
- "테스트가 있으니 괜찮겠지"
- 어떤 줄이 한 번도 실행되지 않았는지 알 수 없음
- 배포 후 예외 처리 코드에서 버그 발견
```

**바꾼 뒤 — 커버리지 보고서로 AI 코드 공백 파악**

```text
src/payment.py: 78% (line 42, 57 uncovered)
  → 42번째 줄: 결제 실패 처리 분기 (AI가 빠뜨린 케이스)
  → 57번째 줄: 환불 로직 (AI가 테스트 작성 안 함)
```

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
src/calc.py    24    2    92%   18-19
src/auth.py    50   10    80%   34, 41-49
TOTAL         200   18    91%
```

### 3단계 — HTML 보고서 열기

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

빨간 줄이 AI 코드에서 테스트가 닿지 않은 부분입니다.

### 4단계 — 브랜치 커버리지까지 보기

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```

AI가 만든 `if/else` 분기에서 한쪽만 테스트됐는지 확인할 수 있습니다.

### 5단계 — CI 기준선 만들기

```toml
# pyproject.toml
[tool.coverage.report]
fail_under = 80
```

## AI 코드의 커버리지 100% 함정

AI가 만든 테스트가 커버리지 100%를 달성해도 버그가 있을 수 있습니다. 코드를 실행했다고 해서 올바르게 검증된 것은 아니기 때문입니다.

**AI가 만들 수 있는 커버리지 100% 버그 테스트**

```python
def calculate_discount(price: float, user_tier: str) -> float:
    discount = 0.0
    if user_tier == "gold":
        discount = price * 0.2
    elif user_tier == "silver":
        discount = price * 0.1
    return price - discount

# AI가 생성한 테스트 (커버리지 100%지만 단언문 없음)
def test_calculate_discount():
    result = calculate_discount(100, "gold")
    # 실행만 하고 검증하지 않음!
    result2 = calculate_discount(100, "silver")
    # 역시 검증 없음!
```

**올바른 테스트**

```python
def test_calculate_discount_with_assertions():
    assert calculate_discount(100, "gold") == 80.0
    assert calculate_discount(100, "silver") == 90.0
    assert calculate_discount(100, "bronze") == 100.0  # AI가 빠뜨리는 케이스
    assert calculate_discount(0, "gold") == 0.0         # 경계값
```

AI가 만든 테스트를 검토할 때 단언문이 실제 값을 검증하는지 반드시 확인하세요.

## 바이브코딩 팀의 위험 기반 커버리지 전략

AI가 만든 모든 코드에 같은 커버리지 기준을 요구하면 비효율적입니다. 위험도에 따라 우선순위를 정하세요.

| 영역 | 위험도 | 목표 커버리지 | 이유 |
|---|---|---|---|
| 핵심 도메인 로직 (결제, 할인, 권한) | High | 90%+ | AI 실수가 가장 큰 피해를 줌 |
| API 엔드포인트 | Medium | 70~80% | 계약 변경 빠르게 감지 필요 |
| 유틸리티 함수 | Low | 50~60% | 단순하고 위험도 낮음 |
| AI 생성 보일러플레이트 | Very Low | 30~50% | 테스트 가치 낮음 |

## 커버리지 보고서로 AI에게 추가 테스트 요청하기

```bash
# 커버리지 보고서 실행
pytest --cov=src --cov-report=term-missing
```

```text
Name                       Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/payment.py                82     19    77%   45-52, 71-79
```

```text
AI 프롬프트 예시:
"src/payment.py의 45-52번째 줄이 테스트에 닿지 않았어.
이 줄들은 결제 실패 처리 로직이야.
이 부분을 커버하는 pytest 테스트를 작성해 줘."
```

## 자주 하는 실수

첫 번째 실수는 AI가 만든 테스트의 커버리지 숫자만 보고 안심하는 일입니다. 단언문 없이 코드만 실행하는 테스트도 커버리지를 높입니다.

두 번째 실수는 라인 커버리지만 보는 경우입니다. AI가 만든 `if/else`에서 한쪽만 테스트됐는지 확인하려면 브랜치 커버리지를 함께 봐야 합니다.

세 번째 실수는 커버리지 100%를 목표로 삼아 AI에게 의미 없는 테스트를 양산하게 하는 것입니다.

## AI 팁: 커버리지 기반 테스트 보강 프롬프트

```text
프롬프트 예시:
"pytest --cov=src --cov-report=term-missing 결과를 첨부할게.
커버리지가 낮은 파일에서 빠진 분기를 파악하고
각 분기를 커버하는 테스트를 추가로 작성해 줘.
단순히 코드를 실행하는 테스트가 아니라 실제 값을 검증하는 단언문을 포함해 줘."
```

## 운영 체크리스트

- [ ] `pytest --cov` 보고서를 한 번 이상 읽었습니다.
- [ ] AI가 만든 테스트의 단언문이 실제 값을 검증하는지 확인했습니다.
- [ ] 브랜치 커버리지를 켜 보았습니다.
- [ ] 핵심 도메인 코드의 커버리지를 우선 보강했습니다.
- [ ] CI에 최소 커버리지 기준을 설정했습니다.

## 처음 질문으로 돌아가기

- **라인, 브랜치, 함수 커버리지는 무엇이 다를까요?**
  라인은 줄 실행 여부, 브랜치는 분기 양쪽 실행 여부, 함수는 함수 호출 여부입니다. AI가 만든 코드에서는 브랜치 커버리지가 예외 경로 누락을 가장 잘 드러냅니다.

- **커버리지 100%인데도 버그가 있는 이유는 무엇일까요?**
  커버리지는 코드 실행 여부만 봅니다. AI가 단언문 없이 코드만 실행하는 테스트를 만들면 커버리지는 100%지만 버그는 그대로입니다.

- **바이브코딩 팀의 현실적인 커버리지 목표는?**
  핵심 도메인(결제, 할인, 권한)은 90%+, 전체 평균은 70-80%가 현실적입니다. 숫자보다 어디가 비었는지가 더 중요합니다.

## 정리

커버리지는 AI가 만든 테스트의 공백을 찾는 진단 도구입니다. 보고서를 읽고 위험한 구간을 찾아 보강하는 습관이 바이브코딩 팀의 품질을 높입니다. 다음 글에서는 AI가 수정한 코드에서 이전 버그가 다시 돌아오지 않게 만드는 회귀 테스트를 보겠습니다.

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [pytest-cov docs](https://pytest-cov.readthedocs.io/)
- [coverage.py docs](https://coverage.readthedocs.io/)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 테스팅 기초 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트](./02-unit-test.md)
- [바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트](./03-integration-test.md)
- [바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트](./04-e2e-test.md)
- [바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블](./05-test-double.md)
- [바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- **바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지 (현재 글)**
- [바이브코딩을 위한 테스팅 기초 (8/10): 회귀 테스트](./08-regression-test.md)
- [바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [바이브코딩을 위한 테스팅 기초 (10/10): 테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

Tags: 바이브코딩, Testing, Coverage, pytest-cov, Quality, Metrics
