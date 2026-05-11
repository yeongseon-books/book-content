---
series: pytest-101
episode: 1
title: 왜 테스트를 작성해야 할까?
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - pytest
  - Testing
  - 소프트웨어 품질
  - 자동화 테스트
seo_description: 테스트 작성이 개발 생산성과 코드 품질에 미치는 영향을 설명합니다.
last_reviewed: '2026-05-04'
---

# 왜 테스트를 작성해야 할까?

> pytest 101 시리즈 (1/10)


## 이 글에서 다룰 문제

코드를 수정할 때 "이거 고치면 다른 데 안 깨지겠지?"라는 불안감을 느낀 적이 있을 것입니다. 테스트가 없으면 모든 변경이 도박입니다. 테스트가 있으면 변경 후 몇 초 만에 기존 기능이 정상인지 확인할 수 있습니다.

> 테스트는 미래의 나를 위한 안전망입니다. 오늘 10분 투자하면 내일 3시간 디버깅을 절약합니다.

실무에서 테스트 없이 배포하면, 장애 발생 시 원인을 찾는 데 평균 3~5배의 시간이 소요됩니다. 테스트가 있으면 어떤 입력에서 실패하는지 즉시 파악할 수 있습니다.

## 핵심 개념 잡기

> 테스트 = 코드가 기대대로 동작하는지 자동으로 검증하는 코드

```
[수동 테스트]          [자동화 테스트]
  사람이 직접 실행       코드가 자동으로 실행
  반복할 때 비용 ↑      반복 비용 ≈ 0
  실수 가능             일관된 결과
  커버리지 불명확        커버리지 측정 가능
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 단위 테스트 | 함수 하나를 독립적으로 검증합니다 |
| 통합 테스트 | 여러 컴포넌트의 상호작용을 검증합니다 |
| E2E 테스트 | 사용자 관점에서 전체 흐름을 검증합니다 |
| 테스트 피라미드 | 단위 > 통합 > E2E 순으로 많이 작성하는 전략입니다 |
| 회귀 테스트 | 기존 기능이 변경 후에도 정상인지 확인합니다 |

## Before / After

테스트 없이 검증하는 방식과 pytest로 자동화하는 방식을 비교합니다.

```python
# before: 수동으로 함수를 호출하여 눈으로 확인
def add(a, b):
    return a + b

print(add(1, 2))   # 3이 나오는지 눈으로 확인
print(add(-1, 1))   # 0이 나오는지 눈으로 확인
```

```python
# after: pytest로 자동 검증
def add(a, b):
    return a + b

def test_add_positive():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, 1) == 0
```

## 단계별 실습

### Step 1: Python 환경 확인

```bash
python3 --version
# Python 3.10 이상이면 OK
```

### Step 2: pytest 설치

```bash
pip install pytest
pytest --version
```

### Step 3: 테스트 대상 함수 작성

`calculator.py` 파일을 만듭니다.

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다")
    return a / b
```

### Step 4: 테스트 파일 작성

`test_calculator.py` 파일을 만듭니다.

```python
# test_calculator.py
import pytest
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
        divide(1, 0)
```

### Step 5: 테스트 실행

```bash
pytest test_calculator.py -v
```

출력 결과:

```
test_calculator.py::test_add PASSED
test_calculator.py::test_add_negative PASSED
test_calculator.py::test_divide PASSED
test_calculator.py::test_divide_by_zero PASSED
========================= 4 passed =========================
```

## 이 코드에서 주목할 점

- `test_`로 시작하는 함수는 pytest가 자동으로 발견합니다
- `assert` 문 하나로 기대값을 검증합니다 — unittest의 `assertEqual`보다 간결합니다
- `pytest.raises`로 예외 발생을 검증합니다
- `-v` 플래그로 각 테스트의 통과/실패를 개별 확인합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 테스트 파일명이 `test_`로 시작하지 않음 | pytest가 테스트를 발견하지 못합니다 | `test_*.py` 또는 `*_test.py` 규칙을 따릅니다 |
| 테스트 함수명이 `test_`로 시작하지 않음 | 함수가 테스트로 인식되지 않습니다 | 함수명을 `test_`로 시작합니다 |
| `print()`로 결과를 눈으로 확인 | 자동화가 불가능하고 회귀를 잡지 못합니다 | `assert`로 기대값을 명시합니다 |
| 하나의 테스트에 너무 많은 assert | 첫 번째 실패 이후 나머지를 검증하지 못합니다 | 테스트 하나당 하나의 행위를 검증합니다 |
| 테스트 간 실행 순서에 의존 | 독립 실행 시 실패합니다 | 각 테스트가 독립적으로 동작하도록 설계합니다 |

## 실무에서 이렇게 쓰입니다

- CI/CD 파이프라인에서 `pytest`를 실행하여 머지 전 자동 검증합니다
- 리팩터링 전에 테스트를 먼저 작성하여 안전망을 확보합니다
- 버그 리포트를 받으면 재현 테스트를 먼저 작성한 뒤 수정합니다
- 코드 리뷰 시 테스트 커버리지를 기준으로 변경 범위를 확인합니다
- 새 팀원 온보딩 시 테스트를 실행하여 프로젝트 동작을 빠르게 이해합니다

## 현업 개발자는 이렇게 생각합니다

테스트 작성을 "추가 작업"으로 보는 시각이 있지만, 경험 있는 개발자는 테스트를 "개발의 일부"로 봅니다. 테스트 없이 코드를 작성하는 것은 컴파일하지 않고 배포하는 것과 같습니다.

실무에서는 테스트 작성에 전체 개발 시간의 20~30%를 투자하는 것이 일반적입니다. 이 투자는 디버깅 시간 감소, 안전한 리팩터링, 빠른 코드 리뷰로 회수됩니다.

## 체크리스트

- [ ] pytest를 설치하고 `pytest --version`으로 확인했다
- [ ] `test_` 접두사 규칙을 이해했다
- [ ] `assert`로 기대값을 검증하는 테스트를 작성했다
- [ ] `pytest.raises`로 예외 테스트를 작성했다
- [ ] `pytest -v`로 테스트를 실행하고 결과를 확인했다

## 정리 및 다음 글 안내

테스트는 코드 변경에 대한 안전망입니다. pytest는 `assert` 하나로 테스트를 작성할 수 있는 간결한 도구입니다. 다음 글에서는 실제 pytest 테스트를 처음부터 작성하는 방법을 실습합니다.

<!-- toc:begin -->
- **왜 테스트를 작성해야 할까? (현재 글)**
- 첫 번째 pytest 테스트 작성하기 (예정)
- assert와 예외 테스트 (예정)
- fixture 이해하기 (예정)
- parametrization으로 테스트 케이스 늘리기 (예정)
- mock과 monkeypatch (예정)
- 파일, 환경변수, 시간 테스트하기 (예정)
- coverage와 테스트 품질 보기 (예정)
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [Python Testing with pytest (Brian Okken)](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)
- [테스트 피라미드 — Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Real Python — Getting Started With Testing in Python](https://realpython.com/python-testing/)
