---
series: type-hints-python-101
episode: 8
title: mypy와 pyright 사용하기
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
last_reviewed: '2026-05-12'
---

# mypy와 pyright 사용하기

타입 힌트를 열심히 붙여도 검사기를 돌리지 않으면 효과는 절반입니다. 함수 시그니처는 그럴듯하게 적혀 있지만 실제 구현이 다른 값을 반환해도, 아무 도구도 읽지 않으면 그 계약은 그냥 주석처럼 남습니다.

이 글은 Type Hints (Python) 101 시리즈의 8번째 글입니다. 여기서는 mypy와 pyright를 설치하고 설정하는 법, strict 모드를 점진적으로 도입하는 전략, CI에 연결하는 방식까지 정리합니다.

## 이 글에서 다룰 문제

- 타입 힌트를 코드 실행 없이 어떻게 검증할까요?
- mypy와 pyright는 무엇이 다르고 어떻게 고를까요?
- strict 모드는 언제 켜고, 기존 프로젝트에는 어떻게 도입할까요?
- 팀 단위로 타입 검사를 강제하려면 어디에 넣어야 할까요?

> 타입 힌트의 실제 가치는 검사기를 돌릴 때 완성됩니다.

## 왜 이 주제가 중요한가

타입 힌트가 런타임에 강제되지 않는다는 점은 이미 봤습니다. 즉, 검증 도구가 없으면 잘못된 반환 타입, Optional 체크 누락, 잘못된 콜백 시그니처가 그대로 저장소에 들어갈 수 있습니다. 이 간극을 메우는 것이 정적 타입 검사기입니다.

mypy와 pyright는 Python 생태계에서 가장 널리 쓰이는 두 도구입니다. 둘 다 소스 코드를 실행하지 않고 읽으면서 타입 불일치를 보고합니다. 차이는 속도, 에디터 통합, 일부 규칙 해석 정도에 있고, 중요한 것은 팀이 하나의 기준을 정하는 일입니다.

## 한눈에 보는 개념

```text
소스 코드 (.py)
     │
     ├── mypy    ── 타입 오류 리포트
     │
     └── pyright ── 타입 오류 리포트
              │
         VS Code 실시간 표시
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| mypy | Python 진영에서 가장 널리 쓰이는 정적 타입 검사기입니다 |
| pyright | Microsoft가 만든 빠른 타입 검사기이며 Pylance의 기반입니다 |
| strict mode | 타입 힌트 누락까지 적극적으로 오류로 보는 엄격 모드입니다 |
| stub file | 타입 정보가 없는 라이브러리를 위한 `.pyi` 파일입니다 |
| `type: ignore` | 특정 줄의 타입 오류를 억제하는 주석입니다 |

## 바꾸기 전과 후

```python
def get_user_name(user_id: int) -> str:
    return None  # 런타임 전에는 조용합니다


name = get_user_name(1)
print(name.upper())  # AttributeError
```

```python
def get_user_name(user_id: int) -> str:
    return None  # mypy: error: Incompatible return value type
```

이 한 줄 차이가 테스트 전, 리뷰 전, 배포 전 오류를 잡아내는 출발점입니다.

## 단계별로 익히기

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

mypy는 파일 하나만 볼 수도 있고, `mypy .`처럼 프로젝트 전체를 검사할 수도 있습니다.

### 2단계: `pyproject.toml`로 mypy 설정하기

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

대표 옵션은 다음과 같습니다.

- `disallow_untyped_defs`: 타입 힌트 없는 함수를 오류로 봅니다.
- `warn_return_any`: 반환 타입이 `Any`로 새는 지점을 경고합니다.
- `overrides`: 모듈별로 다른 규칙을 적용합니다.

### 3단계: pyright 설치와 설정하기

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

pyright는 VS Code의 Pylance와 연결되어 에디터 안에서 실시간 피드백을 주는 점이 강점입니다.

### 4단계: 점진적으로 엄격하게 만들기

```toml
# 1단계: 기본 검사
[tool.mypy]
check_untyped_defs = true

# 2단계: 새 코드에 타입 요구
# disallow_untyped_defs = true

# 3단계: 전체 strict 모드
# strict = true
```

기존 프로젝트에 strict를 한 번에 넣으면 수백 개 오류가 쏟아질 수 있습니다. 보통은 핵심 모듈부터 강화합니다.

```toml
[[tool.mypy.overrides]]
module = "src.core.*"
strict = true

[[tool.mypy.overrides]]
module = "src.legacy.*"
ignore_errors = true
```

### 5단계: CI에 연결하기

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

CI에 타입 검사를 걸어 두면 타입 오류가 있는 코드가 메인 브랜치로 들어가는 일을 크게 줄일 수 있습니다.

## 여기서 먼저 봐야 할 점

- mypy는 보통 `pyproject.toml`, pyright는 `pyrightconfig.json`으로 설정합니다.
- strict 모드는 한 번에 켜기보다 모듈 단위로 넓혀 가는 편이 현실적입니다.
- CI에 넣어야 팀 전체 규칙으로 자리잡습니다.
- `type: ignore`는 구조적 해결이 어려울 때만 쓰는 예외 수단입니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| `type: ignore`를 쉽게 붙임 | 타입 검사 자체를 무력화합니다 | 원인을 먼저 고치고, 꼭 필요한 줄에만 씁니다 |
| 스텁 패키지를 안 깔고 서드파티 오류를 방치함 | 타입 정보 부족으로 잡음이 많아집니다 | `types-requests` 같은 스텁을 설치합니다 |
| strict 모드를 한 번에 적용함 | 팀이 오류 양에 압도됩니다 | 모듈별로 점진 도입합니다 |
| 두 도구를 모두 CI 게이트로 강제함 | 엣지 케이스 차이로 마찰이 생깁니다 | 하나를 표준으로 정합니다 |
| 캐시와 설정을 무시하고 느리다고 느낌 | 반복 실행 비용이 커집니다 | 도구별 캐시와 설정 파일을 꾸준히 관리합니다 |

## 실무에서는 이렇게 연결됩니다

- 에디터 단계에서는 pyright/Pylance로 실시간 피드백을 받습니다.
- CI 단계에서는 mypy 또는 pyright 중 하나를 표준 게이트로 둡니다.
- 레거시 모듈은 완화 규칙을 두고, 새 코드에는 더 엄격한 기준을 적용합니다.
- pre-commit 훅이나 PR 검증 단계에 타입 체크를 넣는 팀도 많습니다.

## 실무 판단 기준

시니어 엔지니어는 타입 검사를 테스트, 린트, 포매터와 나란한 기본 인프라로 봅니다. 새 프로젝트라면 첫날부터 CI 게이트에 올리고, 기존 프로젝트라면 새 코드와 핵심 모듈부터 점진적으로 강화합니다. 완벽한 100% 도입보다 지속 가능한 도입이 더 중요합니다.

도구 선택 자체보다 중요한 것은 일관성입니다. 팀에서 mypy를 표준으로 정했다면 PR과 CI에서 같은 기준을 쓰고, pyright는 보조 에디터 도구로 활용하는 식이 현실적입니다.

## 체크리스트

- [ ] mypy 또는 pyright를 설치해 실행했습니다
- [ ] 설정 파일을 프로젝트에 추가했습니다
- [ ] strict 도입 계획을 단계적으로 세웠습니다
- [ ] CI 파이프라인에 타입 검사를 넣을 준비가 되어 있습니다
- [ ] `type: ignore` 사용을 최소화할 기준을 정했습니다

## 연습 문제

1. 타입 오류 세 개를 일부러 넣은 Python 파일을 만들고 mypy를 실행해 보세요.

2. `src/`는 엄격하게, `tests/`는 완화해서 검사하는 `pyproject.toml` 설정을 직접 작성해 보세요.

3. push와 pull request에서 mypy를 실행하는 GitHub Actions 워크플로를 만들어 보세요.

## 정리와 다음 글

mypy와 pyright는 타입 힌트를 실제로 검증하는 도구입니다. 설정 파일에서 규칙을 정하고, strict 모드는 점진적으로 넓히며, CI에 연결해 팀 규칙으로 만드는 것이 핵심입니다. 타입 힌트는 검사기가 돌아갈 때 비로소 코드 품질 장치로 완성됩니다.

다음 글에서는 타입 힌트를 런타임 검증으로 확장하는 Pydantic을 살펴보겠습니다.

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
