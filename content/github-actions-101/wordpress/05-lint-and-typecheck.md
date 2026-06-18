---
title: "바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화"
series: github-actions-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- Lint
- Ruff
- QualityGate
seo_description: "바이브코딩으로 만든 AI 코드의 스타일 오류와 타입 문제를 GitHub Actions에서 자동으로 잡는 방법을 설명합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 5번째 글입니다.

AI에게 코드를 만들어 달라고 하면 동작은 하지만 스타일이 제각각인 코드가 나올 수 있습니다. import 순서가 엉망이거나, 줄 길이가 넘치거나, 타입 힌트가 빠져 있거나, 심지어 보안상 위험한 패턴이 쓰일 수도 있습니다. 팀에서 리뷰를 하다 보면 "이거 ruff 돌려봤어요?"라는 말을 반복하게 됩니다. 같은 지적이 반복되면 리뷰어는 지치고, 실제로 중요한 설계 문제에 집중하기 어려워집니다.

린트와 타입 체크를 CI에 넣으면 이 문제가 사라집니다. PR이 열리는 순간 Ruff가 스타일을 검사하고, Mypy가 타입을 확인합니다. 사람이 "형식적인 문제"를 지적하는 대신, 기계가 먼저 잡아 줍니다. 리뷰어는 로직과 설계에만 집중할 수 있게 됩니다. 바이브코딩에서 AI가 만든 코드를 팀이 함께 관리하려면 이 자동화 게이트가 필수입니다.

> 린트와 타입 체크를 CI에 넣는 목적은 스타일 통제가 아닙니다. 리뷰어가 설계와 로직에 집중할 수 있도록, 기계가 잡을 수 있는 문제는 기계에게 맡기는 것입니다.

---

## 이 글에서 다룰 문제
- Ruff 하나로 여러 린트 도구를 대체할 수 있는 이유는 무엇일까요?
- Mypy 타입 체크는 어느 시점부터 시작하는 것이 현실적일까요?
- pre-commit과 CI 린트는 어떻게 역할을 나눠야 할까요?
- AI가 만든 코드에서 린트가 가장 자주 잡는 문제 유형은 무엇일까요?
- 린트 규칙을 너무 엄격하게 잡으면 어떤 역효과가 생길까요?

---

## AI 코드에서 린트가 잡는 대표 문제들

AI가 생성한 Python 코드에서 Ruff가 자주 잡는 패턴입니다.

```python
# AI가 자주 생성하는 패턴들

import os, sys  # E401: 여러 import를 한 줄에
from typing import *  # F401/F403: 와일드카드 import

def process(d, t, r):  # 이름이 짧아 의도 불명확 (린트 외 클린코드 문제)
    if d != None:  # E711: None 비교는 is/is not으로
        pass

password = "hardcoded"  # S105: 하드코딩된 비밀번호 패턴
```

이런 패턴들이 PR마다 자동으로 잡히면 리뷰어가 같은 지적을 반복할 필요가 없습니다.

### 핵심 용어 정리

| 용어 | 뜻 | 실무 포인트 |
|------|------|------|
| Ruff | 빠른 Python 린터+포매터 | flake8, isort, black을 하나로 대체합니다 |
| Mypy | 정적 타입 체커 | 실행 전에 타입 오류를 잡습니다 |
| pre-commit | 커밋 전 로컬 훅 | CI 전에 빠른 피드백을 줍니다 |
| `--output-format github` | PR diff에 인라인 어노테이션 표시 | 어디를 고쳐야 하는지 바로 보입니다 |
| 품질 게이트 | 통과하지 못하면 머지를 막는 규칙 | 기준을 문서가 아닌 동작으로 만듭니다 |

---

## Before / After

**AI가 만든 스타일 문제가 있는 코드**

```python
import os,json,sys
from typing import *

def f(d,t):
    if d!=None:
        return d*t
    return None
```

Ruff를 돌리면 `E401`, `F403`, `E711`, `E225` 등 여러 오류가 나옵니다.

**CI에서 Ruff가 자동으로 잡는 구조**

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

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: mypy src --output-format=github-actions
```

`--output-format github`와 `--output-format=github-actions` 옵션 덕분에 어떤 파일의 몇 번째 줄에 문제가 있는지 PR diff에 바로 표시됩니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| CI에서만 린트, 로컬에는 설치 안 함 | PR마다 CI에서 실패를 발견하게 됨 | pre-commit으로 로컬에서도 실행합니다 |
| 린트 규칙을 계속 완화함 | 결국 의미 없는 수준이 됨 | 처음부터 팀 합의로 규칙을 정합니다 |
| Mypy를 전체 코드에 한꺼번에 적용 | 수백 개 에러가 나서 팀이 의욕을 잃음 | 새 모듈부터 strict를 적용합니다 |
| 자동 수정 결과를 CI가 커밋 | PR에 bot 커밋이 섞여 리뷰가 복잡해짐 | CI는 검증만, 수정은 로컬에서 합니다 |
| 설정 파일을 여러 곳에 흩어 놓음 | 어느 설정이 실제 기준인지 불명확 | `pyproject.toml`에 모읍니다 |

## AI 팁: 린트 워크플로우 요청 프롬프트

```
프롬프트 예시:
"GitHub Actions에서 Ruff 린트와 Mypy 타입 체크를 실행하는 워크플로우를 만들어줘.
조건:
- Ruff는 astral-sh/ruff-action 사용, PR diff에 인라인 어노테이션 표시
- Ruff format도 검사 (--check)
- Mypy는 Python 3.12, pip 캐시 사용
- lint와 typecheck는 병렬 잡으로 분리
- 설정은 pyproject.toml에서 읽기"
```

받은 후에는 `--output-format github` 옵션이 포함됐는지, 두 잡이 병렬로 실행되는지 확인하세요.

## 운영 체크리스트
- [ ] `ruff check`와 `ruff format --check`가 CI에서 실행되는가?
- [ ] PR diff에 인라인 어노테이션이 표시되는가?
- [ ] Mypy가 적어도 새 모듈에는 적용됐는가?
- [ ] 린트 설정이 `pyproject.toml`에 모여 있는가?
- [ ] 로컬에서도 같은 규칙이 실행되는가?

## 처음 질문으로 돌아가기

- **Ruff가 여러 도구를 대체하는 이유는?**
  Ruff는 flake8, isort, pycodestyle, pyflakes의 규칙을 하나의 바이너리로 실행합니다. 도구 수가 줄어들면 CI 설정이 단순해지고 실행 속도도 빠릅니다.

- **Mypy를 처음부터 strict로 켜면?**
  기존 코드에 타입 어노테이션이 없으면 수백 개의 에러가 나옵니다. 팀의 의욕을 잃게 만드는 가장 빠른 방법입니다. 새로 작성하는 모듈부터 strict를 적용하고 점진적으로 확장하세요.

- **pre-commit과 CI 린트의 역할 차이는?**
  pre-commit은 커밋 전에 로컬에서 빠른 피드백을 주는 도구입니다. CI는 `--no-verify`로 우회할 수 있는 로컬 훅과 달리, 반드시 통과해야 머지되는 강제 게이트입니다. 둘은 함께 써야 합니다.

## 정리

Ruff와 Mypy를 CI에 넣으면 AI가 생성한 코드의 스타일 문제와 타입 오류가 PR 단계에서 자동으로 잡힙니다. 리뷰어는 반복적인 형식 지적 대신 설계와 로직에 집중할 수 있습니다. 다음 글에서는 빌드 결과물을 잡 사이에서 주고받고 릴리스까지 연결하는 아티팩트 관리를 다룹니다.

## 참고 자료
### 공식 문서
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Mypy documentation](https://mypy.readthedocs.io/)
### 관련 시리즈
- [Clean Code 101](../../clean-code-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기](./02-workflow-and-job.md)
- [바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기](./03-triggers.md)
- [바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- **바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화 (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리](./06-build-artifact.md)
- [바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드](./07-docker-build.md)
- [바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화](./08-deploy-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, Lint, Ruff, QualityGate
