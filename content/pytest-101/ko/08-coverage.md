---
series: pytest-101
episode: 8
title: coverage와 테스트 품질 보기
status: publish-ready
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
  - coverage
  - pytest-cov
  - 코드 커버리지
seo_description: pytest-cov로 테스트가 실제로 어느 코드까지 실행하는지 측정하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# coverage와 테스트 품질 보기

이 글은 pytest 101 시리즈의 여덟 번째 글입니다. 테스트가 있다는 사실과 테스트가 충분하다는 사실은 전혀 다릅니다. 이 글에서는 `pytest-cov`를 이용해 테스트가 실제로 어느 코드 라인을 실행했는지 측정하고, 누락된 분기를 찾아 보완하는 방법을 설명합니다.

커버리지는 버그가 없음을 증명하지는 않지만, 적어도 어떤 코드가 전혀 실행되지 않았는지는 객관적으로 보여 줍니다. 그래서 테스트 품질을 이야기할 때 커버리지는 출발점으로 매우 유용합니다.

---

## 이 글에서 다룰 문제

- 코드 커버리지는 정확히 무엇을 측정할까요?
- 라인 커버리지와 브랜치 커버리지는 어떻게 다를까요?
- `pytest-cov`로 누락 라인을 어떻게 확인할 수 있을까요?
- CI에서 최소 커버리지를 강제하려면 어떻게 해야 할까요?

## 왜 이 글이 중요한가

테스트가 여러 개 있어도 핵심 로직이 빠져 있다면, “테스트는 통과했지만 버그는 배포되는” 상황이 충분히 생길 수 있습니다. 커버리지는 이때 테스트 범위를 숫자와 라인 번호로 보여 줍니다.

> 커버리지 100%가 버그 0%를 뜻하지는 않습니다. 하지만 커버리지 30%는 분명 위험 신호입니다. 적어도 이 코드는 실행해 봤다는 최소한의 사실을 보장해 주기 때문입니다.

팀 차원에서 커버리지 기준을 두면, 새 코드가 테스트 없이 머지되는 일을 줄일 수 있습니다. 그래서 커버리지는 개인 생산성 도구이면서 동시에 팀 품질 장치이기도 합니다.

## 핵심 개념 잡기

> coverage = lines executed by tests / total lines of code

```text
def process(x):        ← executed
    if x > 0:          ← executed
        return x * 2   ← executed
    else:               ← not executed
        return 0        ← not executed

test: process(5) → line coverage 60% (3/5)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 라인 커버리지 | 실행된 코드 라인의 비율입니다 |
| 브랜치 커버리지 | 조건문 분기까지 실행했는지 측정합니다 |
| pytest-cov | pytest에서 coverage.py를 함께 실행하는 플러그인입니다 |
| .coveragerc | 제외 규칙과 소스 경로를 설정하는 파일입니다 |
| missing lines | 테스트가 한 번도 실행하지 않은 라인 번호입니다 |

## Before / After

커버리지 없이 실행하는 경우와 함께 측정하는 경우를 비교해 보겠습니다.

```bash
# before: no coverage measurement
pytest
# result: 4 passed — but no idea which code is untested
```

```bash
# after: coverage included
pytest --cov=src --cov-report=term-missing
# result: 4 passed, coverage 78% — missing line numbers shown
```

## 단계별 실습

### Step 1: Install pytest-cov

```bash
pip install pytest-cov
```

### Step 2: Prepare the Code Under Test

```python
# src/myapp/validator.py
def validate_email(email: str) -> bool:
    if not email:
        return False
    if "@" not in email:
        return False
    local, domain = email.split("@", 1)
    if not local or not domain:
        return False
    if "." not in domain:
        return False
    return True

def validate_age(age: int) -> bool:
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if age < 0:
        return False
    if age > 150:
        return False
    return True
```

### Step 3: Write Partial Tests

```python
# tests/test_validator.py
from myapp.validator import validate_email, validate_age

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email():
    assert validate_email("") is False

def test_valid_age():
    assert validate_age(25) is True
```

### Step 4: Measure Coverage

```bash
pytest --cov=src/myapp --cov-report=term-missing

# Example output:
# Name                        Stmts   Miss  Cover   Missing
# ---------------------------------------------------------
# src/myapp/validator.py         16      6    63%   8-10, 20-22
# ---------------------------------------------------------
# TOTAL                          16      6    63%
```

### Step 5: Fill the Gaps

```python
# tests/test_validator.py — additional tests
import pytest
from myapp.validator import validate_email, validate_age

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email():
    assert validate_email("") is False

def test_no_at_sign():
    assert validate_email("userexample.com") is False

def test_no_local_part():
    assert validate_email("@example.com") is False

def test_no_domain_dot():
    assert validate_email("user@localhost") is False

def test_valid_age():
    assert validate_age(25) is True

def test_negative_age():
    assert validate_age(-1) is False

def test_too_old():
    assert validate_age(200) is False

def test_age_type_error():
    with pytest.raises(TypeError):
        validate_age("twenty")
```

```bash
pytest --cov=src/myapp --cov-report=term-missing
# result: coverage 100%
```

## 이 코드에서 주목할 점

- `--cov=src/myapp`는 측정 대상을 명확히 지정합니다.
- `term-missing`은 누락 라인을 터미널에서 바로 보여 줍니다.
- 빠진 라인을 보면 어떤 분기 테스트가 부족한지 바로 알 수 있습니다.
- 커버리지 100%가 곧 충분한 테스트를 의미하지는 않는다는 점도 함께 기억해야 합니다.

## 흔한 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 무조건 100%만 목표로 삼음 | 유지보수 비용이 커질 수 있습니다 | 핵심 로직 중심으로 현실적인 기준을 둡니다 |
| 브랜치 커버리지를 무시함 | 라인은 지나가도 분기를 놓칠 수 있습니다 | `--cov-branch`를 함께 검토합니다 |
| 테스트 코드까지 측정함 | 의미 없는 숫자가 섞입니다 | `--cov=src`처럼 소스만 측정합니다 |
| 숫자만 보고 리포트를 읽지 않음 | 어떤 로직이 빠졌는지 모릅니다 | HTML 또는 `term-missing`으로 누락 라인을 확인합니다 |
| `# pragma: no cover`를 남용함 | 위험한 코드가 측정에서 빠질 수 있습니다 | 근거가 있는 경우에만 제외합니다 |

## 실무에서 이렇게 쓰입니다

- CI에서 `--cov-fail-under=80`으로 최소 기준을 강제합니다.
- PR마다 커버리지 변화를 자동으로 보여 줍니다.
- HTML 리포트를 아티팩트로 저장해 팀이 브라우저로 확인하게 합니다.
- `pyproject.toml`에 커버리지 설정을 넣어 팀 전체가 같은 기준을 사용합니다.
- 신규 코드 커버리지를 별도 추적해 레거시보다 나빠지지 않게 관리합니다.

## 현업 개발자는 이렇게 생각합니다

커버리지는 “테스트가 부족한 곳”을 찾는 도구이지, “테스트가 충분한 곳”을 증명하는 도구는 아닙니다. 숫자가 높아도 assert가 약하면 품질은 높지 않을 수 있습니다.

그래서 실무에서는 전체를 한 번에 100%로 끌어올리기보다, 변경되는 코드의 커버리지를 지속적으로 높이는 전략이 더 현실적입니다. 중요한 것은 숫자 자체보다, 숫자가 보여 주는 빈 구간을 실제 테스트 개선으로 연결하는 일입니다.

## 체크리스트

- [ ] pytest-cov를 설치하고 커버리지를 측정했다
- [ ] `term-missing`으로 누락 라인을 확인했다
- [ ] HTML 리포트를 만들어 시각적으로 확인했다
- [ ] `--cov-fail-under`로 최소 기준을 설정했다
- [ ] `pyproject.toml`에 커버리지 설정을 넣었다

## 연습 문제

1. `--cov-branch`를 켜고 line coverage와 branch coverage 차이를 비교해 보세요.
2. `pyproject.toml`에 커버리지 설정을 추가하고 `--cov-fail-under=90`으로 실패를 재현해 보세요.
3. HTML 리포트를 생성해 브라우저에서 누락 라인을 직접 확인해 보세요.

## 정리 및 다음 글 안내

커버리지는 테스트 범위를 객관적으로 보여 주는 도구입니다. pytest-cov로 누락 구간을 찾고, 그 빈 곳을 메우는 테스트를 추가하며, CI에서 기준을 강제하면 테스트 품질을 훨씬 안정적으로 유지할 수 있습니다. 다음 글에서는 GitHub Actions로 이 검증을 자동화해 보겠습니다.

<!-- toc:begin -->
- [왜 테스트를 작성해야 할까?](./01-why-write-tests.md)
- [첫 번째 pytest 테스트 작성하기](./02-first-pytest-test.md)
- [assert와 예외 테스트](./03-assert-and-exceptions.md)
- [fixture 이해하기](./04-fixtures.md)
- [parametrization으로 테스트 케이스 늘리기](./05-parametrization.md)
- [mock과 monkeypatch](./06-mock-and-monkeypatch.md)
- [파일, 환경변수, 시간 테스트하기](./07-testing-files-env-time.md)
- **coverage와 테스트 품질 보기 (현재 글)**
- GitHub Actions에서 테스트 자동화하기 (예정)
- 테스트하기 쉬운 코드 구조 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [pytest-cov — Documentation](https://pytest-cov.readthedocs.io/)
- [coverage.py — Documentation](https://coverage.readthedocs.io/)
- [Real Python — Python Code Coverage](https://realpython.com/python-testing/#testing-for-code-coverage)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)

Tags: Python, pytest, coverage, pytest-cov, 코드 커버리지
