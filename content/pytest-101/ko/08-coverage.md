---
series: pytest-101
episode: 8
title: coverage와 테스트 품질 보기
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
  - coverage
  - pytest-cov
  - 코드 커버리지
seo_description: pytest-cov로 코드 커버리지를 측정하고 분석하는 방법을 실습합니다.
last_reviewed: '2026-05-11'
---

# coverage와 테스트 품질 보기

> pytest 101 시리즈 (8/10)


## 이 글에서 다룰 문제

테스트가 있다고 해서 충분한 것은 아닙니다. 핵심 로직이 테스트에 포함되지 않으면 "테스트를 통과했지만 버그가 있는" 상황이 발생합니다. 커버리지는 테스트의 범위를 객관적으로 측정합니다.

> 커버리지 100%가 버그 0%를 의미하지는 않습니다. 하지만 커버리지 30%는 확실히 위험합니다. 커버리지는 "최소한 이 코드는 실행해봤다"는 보장입니다.

팀에서 커버리지 임계값을 설정하면, 새 코드가 테스트 없이 머지되는 것을 방지합니다.

## 핵심 개념 잡기

> coverage = 테스트가 실행한 코드 라인 수 / 전체 코드 라인 수

```text
def process(x):        ← 실행됨 ✓
    if x > 0:          ← 실행됨 ✓
        return x * 2   ← 실행됨 ✓
    else:               ← 실행 안 됨 ✗
        return 0        ← 실행 안 됨 ✗

test: process(5) → 라인 커버리지 60% (3/5)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 라인 커버리지 | 실행된 코드 라인의 비율입니다 |
| 브랜치 커버리지 | 조건문의 모든 분기를 실행한 비율입니다 |
| pytest-cov | pytest에서 coverage.py를 실행하는 플러그인입니다 |
| .coveragerc | 커버리지 측정의 제외 패턴, 소스 경로를 설정합니다 |
| missing lines | 테스트가 실행하지 않은 코드 라인 번호입니다 |

## Before / After

커버리지 없이 테스트하는 경우와 커버리지를 측정하는 경우를 비교합니다.

```bash
# 이전 방식: 커버리지를 측정하지 않고 실행합니다
pytest
# 결과: 4 passed — 어떤 코드가 테스트되지 않았는지는 알 수 없습니다
```

```bash
# 개선 방식: 커버리지와 함께 실행합니다
pytest --cov=src --cov-report=term-missing
# 결과: 4 passed, coverage 78% — 누락 라인 번호까지 표시합니다
```

## 단계별 실습

### Step 1: pytest-cov 설치

```bash
pip install pytest-cov
```

### Step 2: 테스트 대상 코드 준비

```python
# src/myapp/validator.py 파일
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
        raise TypeError("나이는 정수여야 합니다")
    if age < 0:
        return False
    if age > 150:
        return False
    return True
```

### Step 3: 부분 테스트 작성

```python
# tests/test_validator.py 파일
from myapp.validator import validate_email, validate_age

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email():
    assert validate_email("") is False

def test_valid_age():
    assert validate_age(25) is True
```

### Step 4: 커버리지 측정

```bash
pytest --cov=src/myapp --cov-report=term-missing

# 출력 예시입니다:
# 열 제목: Name                        Stmts   Miss  Cover   Missing
# ---------------------------------------------------------
# 파일: src/myapp/validator.py         16      6    63%   8-10, 20-22
# ---------------------------------------------------------
# 합계: TOTAL                       16      6    63%
```

### Step 5: 누락 라인 보완

```python
# tests/test_validator.py 파일 — 추가 테스트
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
# 결과: coverage 100%입니다
```

## 이 코드에서 주목할 점

- `--cov=src/myapp`으로 측정 대상 디렉터리를 지정합니다
- `term-missing`으로 누락 라인 번호를 터미널에서 바로 확인합니다
- 누락 라인을 보고 해당 분기를 커버하는 테스트를 추가합니다
- 커버리지 100%를 달성해도 모든 엣지 케이스를 커버한 것은 아닙니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 커버리지 100%를 목표로 삼음 | 불필요한 테스트가 늘어나고 유지보수 비용이 증가합니다 | 핵심 비즈니스 로직 80% 이상을 목표로 합니다 |
| 브랜치 커버리지를 무시 | 라인 커버리지 100%여도 else 분기를 놓칠 수 있습니다 | `--cov-branch`를 함께 사용합니다 |
| 테스트 코드의 커버리지를 측정 | 테스트 코드 자체는 커버리지 대상이 아닙니다 | `--cov=src`로 소스 코드만 측정합니다 |
| 커버리지 리포트를 확인하지 않음 | 숫자만 보고 어떤 라인이 누락인지 모릅니다 | HTML 리포트를 생성하여 시각적으로 확인합니다 |
| `# pragma: no cover`를 남용 | 측정 대상에서 제외하면 숨겨진 버그가 됩니다 | 정당한 이유가 있는 코드만 제외합니다 |

## 실무에서 이렇게 쓰입니다

- CI에서 `--cov-fail-under=80`으로 커버리지 하락 시 빌드를 실패시킵니다
- PR마다 커버리지 변화를 댓글로 보여주는 봇을 연동합니다
- HTML 리포트를 아티팩트로 저장하여 팀원이 브라우저에서 확인합니다
- `pyproject.toml`에 커버리지 설정을 팀 전체가 공유합니다
- 신규 코드의 커버리지를 별도로 측정하여 "기존 코드 대비 개선"을 추적합니다

## 현업 개발자는 이렇게 생각합니다

커버리지는 "테스트가 부족한 곳"을 찾는 도구이지, "테스트가 충분한 곳"을 증명하는 도구가 아닙니다. 커버리지가 높아도 assertion이 부실하면 의미가 없습니다.

실무에서는 새 코드의 커버리지를 기존 코드보다 높게 유지하는 전략이 효과적입니다. 레거시 코드를 한 번에 100%로 올리는 것보다, 변경되는 코드부터 테스트를 추가하는 것이 현실적입니다.

## 체크리스트

- [ ] pytest-cov를 설치하고 커버리지를 측정했다
- [ ] `term-missing`으로 누락 라인을 확인했다
- [ ] HTML 리포트를 생성하여 시각적으로 확인했다
- [ ] `--cov-fail-under`로 최소 커버리지를 설정했다
- [ ] `pyproject.toml`에 커버리지 설정을 추가했다

## 정리 및 다음 글 안내

커버리지는 테스트의 범위를 객관적으로 측정하는 도구입니다. pytest-cov로 측정하고, 누락 라인을 보완하며, CI에서 임계값을 강제하면 테스트 품질을 유지할 수 있습니다. 다음 글에서는 GitHub Actions에서 테스트를 자동화하는 방법을 배웁니다.

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

- [pytest-cov — 공식 문서](https://pytest-cov.readthedocs.io/)
- [coverage.py — 공식 문서](https://coverage.readthedocs.io/)
- [Real Python — Python Code Coverage](https://realpython.com/python-testing/#testing-for-code-coverage)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)

Tags: Python, pytest, coverage, pytest-cov, 코드 커버리지
