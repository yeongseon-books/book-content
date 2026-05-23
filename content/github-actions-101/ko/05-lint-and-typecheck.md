---
series: github-actions-101
episode: 5
title: "GitHub Actions 101 (5/10): Lint와 Type Check"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - GitHubActions
  - Lint
  - Ruff
  - Mypy
  - QualityGate
seo_description: ruff, mypy, pre-commit으로 코드 품질 게이트를 자동화하는 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (5/10): Lint와 Type Check

코드 리뷰가 늘 비슷한 지적에서 시작된다면 팀의 시간이 아깝게 쓰이고 있다는 뜻입니다. import 정렬, 줄 길이, 포매팅, 명백한 타입 오류까지 사람이 반복해서 잡고 있다면 리뷰어는 더 중요한 설계와 위험 신호에 집중하기 어렵습니다. 이런 일은 가능한 한 기계에게 넘기는 편이 맞습니다.

이 글은 GitHub Actions 101 시리즈의 5번째 글입니다. 여기서는 Ruff와 Mypy, pre-commit을 이용해 코드 품질 게이트를 만들고, PR 리뷰가 스타일 교정이 아니라 로직 검토에 집중되도록 하는 방법을 설명하겠습니다.

![GitHub Actions 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/05/05-01-diagram.ko.png)
*GitHub Actions 101 5장 흐름 개요*

## 먼저 던지는 질문

- Ruff는 왜 여러 도구를 하나로 줄이는 데 유용할까요?
- Mypy는 어느 시점부터 엄격 모드로 가져가는 편이 좋을까요?
- pre-commit은 왜 CI와 짝을 이뤄야 할까요?

## 왜 중요한가

린트와 타입 검사는 리뷰어가 가장 먼저 발견하는 항목입니다. 그런데 이 검사는 대부분 기계가 훨씬 더 빠르고 일관되게 할 수 있습니다. 품질 게이트를 자동화하면 리뷰어는 아키텍처, 예외 흐름, 성능, 운영 영향처럼 더 비싼 판단에 시간을 쓸 수 있습니다.

또 하나 중요한 점은 팀 기준의 통일입니다. 로컬에서는 통과했는데 CI에서는 실패하는 상황이 반복되면 개발자는 자동화를 귀찮은 장벽으로 느낍니다. 같은 명령을 로컬과 CI에서 똑같이 실행하게 만드는 것이 오래 가는 구조입니다.

## 한눈에 보는 품질 게이트

이 구조에서 핵심은 분명합니다. 코드가 들어오면 먼저 기계가 스타일과 정적 타입을 확인하고, 그 결과가 CI 게이트로 이어집니다. 사람의 리뷰는 그 다음입니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| 린터 | 스타일과 패턴 위반을 잡는 도구 | 반복적인 리뷰 지적을 줄여 줍니다 |
| 포매터 | 코드를 자동으로 정렬하고 맞추는 도구 | 팀 내 스타일 논쟁을 줄입니다 |
| 타입 체커 | 정적 타입 오류를 미리 찾는 도구 | 실행 전 경계 오류를 줄이는 데 유용합니다 |
| pre-commit | 커밋 전에 실행하는 훅 | CI에 가기 전 빠른 피드백을 줍니다 |
| 품질 게이트 | 실패 시 머지를 막는 규칙 | 기준을 문서가 아니라 동작으로 만듭니다 |

Ruff가 특히 매력적인 이유는 여러 도구를 단순화해 준다는 데 있습니다. flake8, isort, black을 따로 관리하던 복잡도를 줄여 주면 팀 전체 유지비가 확실히 낮아집니다.

## 자동화 전과 후를 비교해 보겠습니다

품질 게이트가 없으면 리뷰어는 같은 피드백을 반복합니다. import 순서, 사용하지 않는 변수, 줄 길이, 타입 누락 같은 항목이 매 PR마다 다시 등장합니다. 이 과정은 지치기 쉽고, 팀이 커질수록 기준이 사람마다 흔들립니다.

반대로 PR에 `Lint passed`, `Type-check passed`가 자동으로 붙으면 리뷰 대화의 초점이 달라집니다. 이제 관심사는 “형식이 맞는가”보다 “이 설계가 맞는가”, “이 예외 처리가 충분한가”로 옮겨 갑니다. 저는 품질 게이트의 진짜 가치를 여기에 둡니다.

## 품질 게이트를 5단계로 구성해 보겠습니다

### 1단계 — Ruff로 기본 규칙 만들기

```yaml
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
  with:
    python-version: "3.11"
- run: pip install ruff
- run: ruff check .
- run: ruff format --check .
```

이 구성만으로도 상당수 스타일 문제를 자동으로 걸러낼 수 있습니다. 포매팅까지 검사하면 “이건 취향 아닌가요?”라는 논쟁도 크게 줄어듭니다.

### 2단계 — Mypy 추가하기

```yaml
- run: pip install mypy
- run: mypy src/
```

정적 타입 검사는 실행 전에 드러낼 수 있는 오류를 앞당겨 보여 줍니다. 특히 함수 경계와 데이터 구조가 많아질수록 효과가 커집니다.

### 3단계 — 설정을 한곳에 모으기

```toml
[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP"]

[tool.mypy]
strict = true
```

설정 파일이 여러 곳에 흩어지면 어느 값이 기준인지 불분명해집니다. 저는 `pyproject.toml` 한곳을 중심으로 맞추는 방식을 선호합니다.

### 4단계 — pre-commit으로 로컬과 CI를 맞추기

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks: [{id: ruff}, {id: ruff-format}]
```

로컬에서 먼저 잡히는 오류는 CI 시간도 아껴 줍니다. 팀원이 커밋 전에 같은 규칙을 돌리면 PR에서 보는 실패 수도 자연스럽게 줄어듭니다.

### 5단계 — 변경분만 검사하기

```yaml
- run: |
    git fetch origin ${{ github.base_ref }}
    ruff check $(git diff --name-only origin/${{ github.base_ref }} | grep '\.py$') || true
```

전체 저장소를 한 번에 엄격하게 바꾸기 어려운 레거시 프로젝트에서는 이 방식이 유용할 수 있습니다. 다만 임시 전략인지 장기 전략인지 팀 안에서 분명히 정하는 편이 좋습니다.

## 이 코드에서 먼저 봐야 할 점

- Ruff 하나로 여러 품질 도구를 단순화할 수 있습니다.
- Mypy는 가능하면 초기에 엄격하게 가져가는 편이 전환 비용이 낮습니다.
- pre-commit은 CI 전에 문제를 줄여 주는 빠른 방파제 역할을 합니다.

도구 수를 늘리는 일은 본질이 아닙니다. 기준을 선명하게 만드는 편이 훨씬 중요합니다. 기준이 선명하면 실패도 덜 억울하고 수정도 더 빨라집니다.

## 자주 하는 실수 다섯 가지

1. CI에서만 돌리고 로컬에는 같은 도구를 설치하지 않습니다.
2. 규칙을 자꾸 완화하다가 사실상 의미 없는 수준으로 만듭니다.
3. Mypy를 일부 모듈에만 어정쩡하게 적용합니다.
4. `ruff format` 결과를 PR마다 자동 커밋하게 만들어 충돌을 늘립니다.
5. 설정 파일을 여러 곳에 흩어 놓습니다.

특히 두 번째 실수는 흔합니다. 경고를 줄이는 대신 기준을 낮추면 단기적으로는 편하지만, 장기적으로는 품질 게이트 자체를 신뢰하지 않게 됩니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 Ruff, Mypy, pre-commit 조합을 표준 템플릿으로 묶습니다. 저장소마다 제각각 다른 규칙을 두기보다, 템플릿 저장소나 공통 설정으로 팀의 기준을 일관되게 만드는 편이 유지보수에 유리합니다.

또한 자동 수정과 자동 커밋을 구분해서 봐야 합니다. 자동 수정 자체는 좋지만, CI가 PR마다 코드를 다시 커밋하기 시작하면 리뷰와 충돌 관리가 오히려 복잡해질 수 있습니다. 저는 보통 로컬 자동 수정, CI 검증 분리를 선호합니다.

## 체크리스트

- [ ] `ruff check`와 `ruff format --check`가 CI에서 돈다.
- [ ] `mypy strict` 기준이 켜져 있다.
- [ ] 팀이 pre-commit을 설치해 사용한다.
- [ ] 설정이 `pyproject.toml`에 모여 있다.

## 연습 문제

1. Ruff와 Mypy를 함께 실행하는 워크플로우를 추가해 보세요.
2. 세 개 이상의 훅으로 pre-commit 구성을 만들어 보세요.
3. strict mypy를 켠 뒤 나타나는 오류를 범주별로 분류해 보세요.

## Ruff 설정을 실무 수준으로 잡아 보겠습니다

Ruff는 Python 린터와 포매터를 하나로 합친 도구입니다. Flake8, isort, pycodestyle, pyflakes 등 여러 도구의 규칙을 하나의 바이너리에서 실행하므로, CI 설정이 간단해지고 실행 속도도 빠릅니다.

### pyproject.toml 설정

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "S",    # flake8-bandit (보안)
    "A",    # flake8-builtins
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # ruff-specific rules
]
ignore = [
    "E501",   # line-length (formatter가 처리)
    "S101",   # assert 사용 (테스트에서 필요)
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "S106"]  # 테스트에서는 assert, 하드코딩 패스워드 허용

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

이 설정의 설계 의도를 짚어 보겠습니다.

- `select`에 규칙 그룹을 명시적으로 나열해서, 어떤 검사가 활성화돼 있는지 한눈에 보이게 합니다.
- `per-file-ignores`로 테스트 코드에서는 불필요한 규칙을 비활성화합니다.
- `line-length`는 formatter에 위임하고 린터에서는 무시합니다.

### CI 워크플로우 설정

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Ruff 린트
        uses: astral-sh/ruff-action@v3
        with:
          args: "check --output-format github"

      - name: Ruff 포맷 확인
        uses: astral-sh/ruff-action@v3
        with:
          args: "format --check --diff"
```

`--output-format github`는 린트 오류를 PR의 파일 diff 위에 인라인 어노테이션으로 표시합니다. 개발자가 로그를 뒤지지 않아도 어디를 고쳐야 하는지 바로 보입니다.

`format --check --diff`는 포매팅이 맞지 않는 부분을 diff로 보여주되, 파일을 수정하지는 않습니다. CI에서는 검증만 하고, 실제 수정은 개발자의 로컬 `ruff format`이나 pre-commit에서 처리하는 구조입니다.

---

## Mypy 타입 검사를 단계적으로 도입하기

Mypy를 프로젝트에 처음 도입할 때 가장 큰 실수는 즉시 `--strict`를 켜는 것입니다. 기존 코드에 타입 어노테이션이 없으면 수백 개의 에러가 쏟아져 나오고, 팀이 의욕을 잃습니다.

### 단계적 도입 전략

```toml
# pyproject.toml - 1단계: 기본 검사만
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

# 새 모듈은 strict
[[tool.mypy.overrides]]
module = "src.new_module.*"
strict = true

# 레거시 모듈은 느슨하게
[[tool.mypy.overrides]]
module = "src.legacy.*"
ignore_errors = true
```

이 전략의 핵심은 새 코드에는 엄격한 기준을 적용하면서, 레거시 코드는 점진적으로 마이그레이션하는 것입니다.

### CI에서 Mypy 실행

```yaml
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"

      - name: Mypy 타입 검사
        run: mypy src --output-format=github-actions
```

`--output-format=github-actions`는 Ruff처럼 PR diff에 인라인 어노테이션을 표시합니다. Mypy 0.900 이상에서 사용 가능합니다.

### Mypy 캐시 활용

```yaml
      - name: Mypy 캐시 복원
        uses: actions/cache@v4
        with:
          path: .mypy_cache
          key: mypy-${{ hashFiles('pyproject.toml') }}-${{ hashFiles('src/**/*.py') }}
          restore-keys: |
            mypy-${{ hashFiles('pyproject.toml') }}-
            mypy-
      
      - run: mypy src
```

Mypy는 증분 검사를 지원하므로 캐시를 활용하면 실행 시간을 크게 줄일 수 있습니다. 소스 파일 해시를 캐시 키에 포함하면 코드가 바뀔 때만 캐시가 갱신됩니다.

---

## pre-commit과 CI의 관계

pre-commit은 로컬 커밋 시점에 검사를 실행하는 도구입니다. "로컬에서 이미 검사했으니 CI에서는 필요 없지 않나?"라고 생각할 수 있지만, 두 가지 이유로 CI에서도 반드시 실행해야 합니다.

1. **로컬 훅은 건너뛸 수 있습니다.** `git commit --no-verify`로 훅을 우회하거나, pre-commit을 설치하지 않은 개발자가 있을 수 있습니다.
2. **CI가 최종 게이트입니다.** PR 체크에서 실패해야 머지를 막을 수 있습니다. 로컬 훅은 "빠른 피드백"이고, CI는 "강제 게이트"입니다.

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-pyyaml
```

### CI에서 pre-commit 실행

```yaml
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - uses: pre-commit/action@v3.0.1
```

`pre-commit/action`은 변경된 파일에 대해서만 훅을 실행하므로 전체 검사보다 빠릅니다. 캐시도 자동으로 처리합니다.

---

## 린트와 타입체크를 잡 구조에 배치하기

린트와 타입체크를 다른 검증과 어떻게 조합하는지가 실무의 핵심입니다.

```yaml
name: quality-gate

on:
  pull_request:
    paths: ["src/**", "tests/**", "pyproject.toml"]

concurrency:
  group: quality-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/ruff-action@v3
        with:
          args: "check --output-format github"
      - uses: astral-sh/ruff-action@v3
        with:
          args: "format --check"

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: mypy src

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest -q

  build:
    needs: [lint, typecheck, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

세 검증 잡이 병렬로 실행되고, 모두 통과해야 빌드가 시작됩니다. 린트는 가장 빠르게 끝나고(보통 10초 이내), 타입체크는 30초-1분, 테스트는 가장 오래 걸립니다. 이 구조에서 린트 실패는 즉시 피드백으로 돌아오고, 나머지 잡이 끝날 때까지 기다릴 필요가 없습니다.

---

## 점진적 엄격화 전략

팀에 린트와 타입체크를 도입할 때 가장 현실적인 접근은 점진적 엄격화입니다.

| 단계 | 린트 | 타입체크 | 기간 |
| --- | --- | --- | --- |
| 1단계 | 기본 규칙만 (E, F) | ignore_missing_imports | 2주 |
| 2단계 | 확장 규칙 추가 (B, UP, SIM) | 새 모듈 strict | 1개월 |
| 3단계 | 보안 규칙 포함 (S) | 전체 strict | 점진적 |

각 단계에서 CI 실패가 0이 되면 다음 단계로 넘어갑니다. 기존 코드의 문제는 별도 PR로 일괄 수정하고, 새 코드부터 엄격한 기준을 적용하는 방식이 팀 합의를 얻기 가장 쉽습니다.

`ruff check --statistics`로 현재 위반 현황을 파악하면 어떤 규칙을 먼저 활성화할지 판단하기 좋습니다.

```bash
$ ruff check --statistics src/
  128  F841  local variable is assigned but never used
   45  E501  line too long
   23  B006  mutable argument default
```

이 출력에서 가장 많은 위반부터 수정하면 효과가 큽니다.

---

## 자동 수정과 수동 검증의 균형

린트 도구의 `--fix` 옵션은 편리하지만, CI에서 자동 수정을 적용해 커밋까지 만들면 의도하지 않은 변경이 PR에 섞일 수 있습니다. 실무에서는 다음 원칙을 따릅니다.

- **로컬**: `ruff check --fix`와 `ruff format`으로 자동 수정 적용
- **CI**: `ruff check`(fix 없이)와 `ruff format --check`로 검증만 수행

만약 CI에서 자동 수정 후 커밋을 원한다면 다음 패턴을 사용할 수 있습니다.

```yaml
jobs:
  auto-fix:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ github.head_ref }}
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - run: pip install ruff
      - run: ruff check --fix .
      - run: ruff format .

      - name: 변경사항 커밋
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git diff --quiet || (git add -A && git commit -m "style: auto-fix lint issues")
          git push
```

이 패턴은 편리하지만 주의점이 있습니다. 자동 커밋이 들어오면 워크플로우가 다시 트리거될 수 있어 무한 루프가 생길 수 있습니다. `github-actions[bot]`의 토큰으로 만든 커밋은 기본적으로 워크플로우를 트리거하지 않으므로 보통 안전하지만, PAT를 사용하면 주의가 필요합니다.

---

## 커스텀 Ruff 규칙과 팀 표준

팀 고유의 코딩 규칙이 있다면 Ruff의 설정으로 표현할 수 있습니다.

```toml
[tool.ruff.lint]
# 팀 표준: 모든 public 함수에 docstring 필요
select = ["D"]  # pydocstyle

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.isort]
known-first-party = ["myapp"]
force-single-line = true
```

또한 `ruff.toml`을 별도 파일로 관리하면 CI와 로컬에서 동일한 설정을 보장합니다. 설정 파일이 변경되면 CI에서 전체 검사를 다시 실행해야 하므로, paths 필터에 설정 파일도 포함하는 것을 잊지 마세요.

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "pyproject.toml"
      - "ruff.toml"  # 설정 변경도 검증 대상
```

---

## 타입 검사 결과를 활용한 리팩토링

Mypy는 단순한 검사 도구를 넘어, 리팩토링 안전망으로도 활용할 수 있습니다.

```python
# Before: Any 타입으로 숨겨진 버그
def process_data(data):  # type: ignore
    return data["key"]["nested"]  # KeyError 위험

# After: 타입으로 계약을 명시
from typing import TypedDict

class NestedData(TypedDict):
    nested: str

class InputData(TypedDict):
    key: NestedData

def process_data(data: InputData) -> str:
    return data["key"]["nested"]  # Mypy가 구조를 검증
```

타입 어노테이션을 추가하면 Mypy가 호출부에서의 타입 불일치를 잡아냅니다. 이는 테스트로는 발견하기 어려운 종류의 버그를 정적으로 차단합니다.

### Mypy 엄격도 보고서

현재 프로젝트의 타입 커버리지를 파악하려면 다음 명령을 사용합니다.

```bash
$ mypy src --txt-report mypy-report
$ cat mypy-report/index.txt
Module              Stmts   Miss  Cover
--------------------------------------
src.api.routes        45      3    93%
src.core.models       80      0   100%
src.legacy.utils     120     95    21%
```

이 보고서를 CI 아티팩트로 저장하면 시간에 따른 타입 커버리지 추세를 추적할 수 있습니다.

---

## 보안 린트 (Bandit/Ruff S 규칙)

코드 보안 검사도 린트의 일부로 처리할 수 있습니다. Ruff의 `S` 규칙 그룹은 flake8-bandit의 규칙을 포함합니다.

```toml
[tool.ruff.lint]
select = ["S"]  # 보안 규칙 활성화
```

자주 잡히는 보안 문제 예시입니다.

| 규칙 | 내용 | 예시 |
| --- | --- | --- |
| S101 | assert 사용 | 프로덕션에서 -O 옵션으로 제거될 수 있음 |
| S104 | 0.0.0.0 바인딩 | 의도하지 않은 외부 노출 |
| S105 | 하드코딩된 비밀번호 | 변수명에 password 포함 |
| S108 | /tmp 사용 | 심볼릭 링크 공격 가능 |
| S301 | pickle 사용 | 역직렬화 공격 가능 |
| S603 | subprocess 호출 | 커맨드 인젝션 위험 |

보안 린트는 모든 문제를 잡아주지는 않지만, 가장 흔한 실수를 자동으로 방지합니다. 보안 팀의 코드 리뷰 부담을 줄이는 첫 단계입니다.

## 정리

린트와 타입 검사는 사람이 반복해서 볼 가치가 낮은 오류를 미리 걷어 내는 게이트입니다. Ruff로 스타일과 포맷을 통일하고, Mypy로 타입 경계를 점검하고, pre-commit으로 로컬과 CI의 기준을 맞추면 리뷰의 밀도가 높아집니다.

다음 글에서는 빌드 아티팩트를 다룹니다. 코드 품질을 검증했다면, 이제 그 결과물인 빌드 산출물을 어떻게 저장하고 다음 단계로 넘길지 살펴볼 차례입니다.

---

## 처음 질문으로 돌아가기

- **Ruff는 왜 여러 도구를 하나로 줄이는 데 유용할까요?**
  - Ruff는 Flake8, isort, pycodestyle, pyflakes, flake8-bugbear 등 10개 이상의 도구 규칙을 하나의 Rust 바이너리에서 실행합니다. CI 설정이 `ruff check`와 `ruff format` 두 명령으로 단순해지고, 실행 속도는 기존 도구 대비 10-100배 빠릅니다. `--output-format github`로 PR diff에 인라인 어노테이션까지 표시할 수 있어, 별도 리포터 도구도 필요 없습니다.
- **Mypy는 어느 시점부터 엄격 모드로 가져가는 편이 좋을까요?**
  - 새 모듈은 처음부터 `strict`로 시작하고, 레거시 모듈은 `ignore_errors = true`에서 시작해 점진적으로 타입을 추가합니다. 전체 프로젝트에 즉시 strict를 거는 것은 수백 개의 에러와 팀의 의욕 저하를 동시에 만듭니다. `per-file-ignores`와 module overrides를 활용해 "새 코드는 엄격, 레거시는 점진적"이라는 현실적 전략을 써야 합니다.
- **pre-commit은 왜 CI와 짝을 이뤄야 할까요?**
  - pre-commit은 로컬에서 빠른 피드백을 주는 도구이고, CI는 강제 게이트입니다. 로컬 훅은 `--no-verify`로 건너뛸 수 있고, 설치하지 않은 개발자도 있을 수 있으므로, CI에서 동일한 검사를 한 번 더 실행해야 "통과하지 않으면 머지 불가"라는 규칙이 확실히 지켜집니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- **Lint와 Type Check (현재 글)**
- 빌드 아티팩트 (예정)
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Mypy documentation](https://mypy.readthedocs.io/)
- [pre-commit](https://pre-commit.com/)
- [astral-sh/ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Lint, Ruff, Mypy, QualityGate
