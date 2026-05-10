---
series: type-hints-python-101
episode: 8
title: mypy와 pyright 사용하기
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
  - Type Hints
  - mypy
  - pyright
  - 정적 분석
  - CI
seo_description: mypy와 pyright를 설정하고 프로젝트에 점진적으로 도입하여 타입 오류를 자동 검출하는 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# mypy와 pyright 사용하기

> Type Hints in Python 101 시리즈 (8/10)


## 이 글에서 다룰 문제

타입 힌트를 아무리 꼼꼼하게 작성해도 검증 도구 없이는 오류가 누적됩니다. 함수 시그니처를 변경했는데 호출부를 놓치거나, Optional인 값을 None 체크 없이 사용하는 실수가 대표적입니다. 정적 분석 도구는 이런 문제를 코드 실행 전에 발견합니다.

> 타입 검사 = 테스트를 실행하지 않아도 잡히는 버그

mypy와 pyright는 Python 생태계에서 가장 널리 쓰이는 두 가지 타입 검사 도구입니다.

## 개념 한눈에 보기

> 정적 타입 검사 도구는 코드를 실행하지 않고 타입 힌트를 분석하여 타입 불일치를 찾습니다.

```text
소스 코드 (.py)
     │
     ├─── mypy ──── 타입 오류 리포트
     │
     └─── pyright ── 타입 오류 리포트
              │
         VS Code 실시간 표시
```

## Before / After

**Before — 타입 검사 없이 실행:**

```python
def get_user_name(user_id: int) -> str:
    return None  # 런타임까지 오류를 모릅니다


name = get_user_name(1)
print(name.upper())  # AttributeError: NoneType
```

**After — mypy로 사전 검출:**

```python
def get_user_name(user_id: int) -> str:
    return None  # mypy: error: Incompatible return value type
    # (got "None", expected "str")
```

## 실습: 단계별로 따라하기

### 1단계: mypy 설치와 첫 실행

```bash
pip install mypy
mypy app.py
```

```python
# app.py
def greet(name: str) -> str:
    return "Hello, " + name


greet(42)  # mypy: error: Argument 1 has incompatible type "int"
```

mypy는 파일 단위 또는 디렉터리 단위로 실행할 수 있습니다. `mypy .`으로 프로젝트 전체를 검사합니다.

### 2단계: pyproject.toml로 mypy 설정

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

주요 옵션 설명입니다.

- `disallow_untyped_defs`: 타입 힌트 없는 함수를 오류로 처리합니다
- `warn_return_any`: Any를 반환하면 경고합니다
- `overrides`: 모듈별로 다른 설정을 적용합니다

### 3단계: pyright 설치와 설정

```bash
pip install pyright
pyright app.py
```

```json
// pyrightconfig.json
{
    "pythonVersion": "3.11",
    "typeCheckingMode": "basic",
    "reportMissingImports": true,
    "reportMissingTypeStubs": false,
    "include": ["src"],
    "exclude": ["tests"]
}
```

pyright는 VS Code의 Pylance 확장에 내장되어 있어 에디터에서 실시간으로 타입 오류를 표시합니다.

### 4단계: strict 모드와 점진적 도입

```toml
# 전체 strict 대신 점진적 도입
[tool.mypy]
# 1단계: 기본 검사
check_untyped_defs = true

# 2단계: 새 코드에 타입 힌트 요구
disallow_untyped_defs = true

# 3단계: strict 모드
strict = true
```

기존 프로젝트에 strict 모드를 한 번에 적용하면 수백 개의 오류가 발생할 수 있습니다. 모듈 단위로 점진적으로 도입하는 것이 현실적입니다.

```toml
# 특정 모듈만 strict
[[tool.mypy.overrides]]
module = "src.core.*"
strict = true

[[tool.mypy.overrides]]
module = "src.legacy.*"
ignore_errors = true
```

### 5단계: CI 파이프라인에 통합

```yaml
# .github/workflows/type-check.yml
name: Type Check

on: [push, pull_request]

jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pip install mypy
      - run: mypy src/
```

CI에 타입 검사를 추가하면 타입 오류가 있는 코드가 병합되지 않습니다.

## 이 코드에서 주목할 점

- mypy는 `pyproject.toml`에서, pyright는 `pyrightconfig.json`에서 설정합니다
- strict 모드는 점진적으로 모듈 단위로 도입합니다
- CI에 타입 검사를 추가하여 팀 전체에 적용합니다
- `type: ignore` 주석은 최후의 수단으로만 사용합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| type: ignore 남발 | 타입 검사 효과가 사라집니다 | 근본 원인을 해결하고 ignore는 최소화합니다 |
| stub 파일 미설치 | 서드파티 라이브러리에서 오류가 납니다 | `pip install types-requests` 등 stub을 설치합니다 |
| strict 모드 일괄 적용 | 수백 개 오류에 좌절합니다 | 모듈 단위로 점진 도입합니다 |
| mypy 캐시 무시 | 느린 실행 속도에 불편합니다 | `.mypy_cache/`를 `.gitignore`에 추가하되 삭제하지 않습니다 |
| pyright와 mypy 결과 차이 무시 | 도구마다 판단이 다를 수 있습니다 | 팀에서 하나를 기준으로 통일합니다 |

## 실무에서는 이렇게 쓰입니다

- CI/CD 파이프라인에서 mypy를 필수 게이트로 설정하여 타입 오류가 있는 PR을 차단
- VS Code + Pylance(pyright)로 개발 중 실시간 타입 피드백 확인
- pre-commit 훅에 mypy를 추가하여 커밋 전 자동 검사
- monorepo에서 모듈별로 다른 strict 수준을 적용하여 점진 마이그레이션
- stub 파일을 자체 작성하여 내부 C 확장 모듈의 타입 정보 제공

## 체크리스트

- [ ] mypy 또는 pyright를 설치하고 실행했는가
- [ ] pyproject.toml 또는 pyrightconfig.json에 설정을 추가했는가
- [ ] 점진적 도입 전략을 수립했는가
- [ ] CI 파이프라인에 타입 검사를 추가했는가
- [ ] type: ignore를 최소한으로 사용했는가

## 정리 및 다음 단계

mypy와 pyright는 타입 힌트를 실제로 검증하는 정적 분석 도구입니다. pyproject.toml로 프로젝트에 맞게 설정하고, CI에 통합하면 타입 오류를 코드 리뷰 전에 자동으로 잡을 수 있습니다. 점진적 도입 전략으로 기존 프로젝트에도 무리 없이 적용할 수 있습니다.

다음 글에서는 타입 힌트를 런타임에서 적극 활용하는 Pydantic 라이브러리를 다룹니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- **mypy와 pyright 사용하기 (현재 글)**
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [mypy 공식 문서](https://mypy.readthedocs.io/en/stable/)
- [pyright 공식 문서](https://github.com/microsoft/pyright)
- [mypy 설정 레퍼런스](https://mypy.readthedocs.io/en/stable/config_file.html)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

Tags: Python, Type Hints, mypy, pyright, 정적 분석, CI
