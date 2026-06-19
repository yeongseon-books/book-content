---
series: open-source-101
episode: 10
title: "Open Source 101 (10/10): 내 첫 오픈소스 프로젝트"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - Project
  - Capstone
  - GitHub
  - Beginner
seo_description: 작은 도구를 첫 오픈소스 프로젝트로 공개하는 범위 설정부터 문서, 릴리스, 피드백 수집까지의 최소 절차를 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (10/10): 내 첫 오픈소스 프로젝트

시리즈를 따라오면서 오픈소스의 정의, 라이선스, 이슈, 풀 리퀘스트, README 문서, 릴리스, 커뮤니티, 메인테이너 역할, 포트폴리오까지 살펴봤습니다. 이제 마지막으로 남는 질문은 하나입니다. 그래서 실제로 무엇을 공개하면 될까 하는 질문입니다. 많은 사람이 여기서 멈춥니다. 아이디어는 있는데 너무 작아 보이거나, 반대로 완벽하지 않아서 공개하기 민망하다고 느끼기 때문입니다.

이 글은 오픈소스 101 시리즈의 마지막 글입니다.

여기서는 작은 도구 하나를 실제 오픈소스 프로젝트로 공개하기까지, 범위 설정부터 문서, 첫 릴리스, 피드백 수집까지 이어지는 최소 절차를 정리하겠습니다.

![Open Source 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/10/10-01-the-smallest-path-to-publication.ko.png)
*Open Source 101 10장 흐름 개요*

## 왜 이 글이 중요한가

오픈소스 학습은 공개될 때 비로소 닫힙니다. 로컬에서 돌아가는 코드와 다른 사람이 써 볼 수 있는 프로젝트 사이에는 생각보다 큰 차이가 있습니다. README, LICENSE, CHANGELOG, 피드백 채널, 릴리스 태그가 붙어야 비로소 다른 사람이 접근 가능한 산출물이 됩니다.

이 과정은 작아 보여도 실무 감각을 크게 길러 줍니다. 범위를 자르는 법, 문서 우선순위를 정하는 법, 첫 사용자 반응을 수집하는 법을 한 번에 연습할 수 있기 때문입니다. 그래서 첫 프로젝트는 크기보다 끝까지 가 보는 경험이 더 중요합니다.

## 이 글에서 다룰 문제

- 첫 오픈소스 프로젝트는 어느 정도 크기여야 할까요?
- 아이디어, 범위, MVP, 문서, 릴리스는 어떤 순서로 준비하면 좋을까요?
- 코드보다 문서와 라이선스가 왜 공개 직전에 더 중요해질까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 핵심 관점

> 첫 오픈소스 프로젝트는 완벽한 기능보다 **명확한 목적, 따라오기 쉬운 진입 경로, 응답 있는 커뮤니티**를 우선합니다.

첫 프로젝트는 대작일 필요가 없습니다. 오히려 작은 MVP라도 문서와 릴리스가 갖춰지면 충분히 첫 오픈소스 프로젝트가 됩니다. 핵심은 대단해 보이는 결과물이 아니라, 다른 사람이 실제로 써 볼 수 있는 상태까지 끝내는 것입니다.

## 핵심 개념 다섯 가지

| 개념 | 정의 | 첫 프로젝트에서의 역할 |
|---|---|---|
| **MVP** | 최소 기능을 갖춘 첫 공개 가능 버전 | 범위를 잘라 끝낼 수 있게 만드는 기준 |
| **Scope** | 이번 릴리스에 들어갈 것과 넣지 않을 것의 경계 | 완벽주의 함정에서 벗어나는 장치 |
| **Roadmap** | 이번 버전에 없는 것을 이후 계획으로 미루는 문서 | non-goals를 공개적으로 선언하는 수단 |
| **Announcement** | 프로젝트를 세상에 알리는 공개 메시지 | 첫 사용자를 만드는 시작점 |
| **Feedback loop** | 사용자 반응을 받아 다음 수정으로 연결하는 반복 구조 | 프로젝트를 살아있게 만드는 엔진 |

이 다섯 가지를 이해하면 완벽주의 때문에 공개를 미루는 패턴에서 벗어날 수 있습니다. 처음부터 모든 것을 해결하는 대신, 작게 내고 배우는 구조를 만들 수 있기 때문입니다.

## 공개까지 가는 최소 경로

공개가 맨 마지막에 한 번 일어나는 이벤트가 아니라는 사실이 중요합니다. 문서를 정리하는 순간부터 이미 외부 사용자를 상정하게 되고, 릴리스와 공지는 그 준비의 자연스러운 결과가 됩니다.

| 단계 | 작업 | 산출물 |
|---|---|---|
| 1 — 아이디어 정의 | 한 줄 목표 + non-goals 작성 | `SCOPE.md` 또는 이슈 #1 |
| 2 — MVP 구현 | 로컬에서 최소 기능 동작 확인 | 코드 + 로컬 테스트 |
| 3 — 문서 5종 준비 | README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG | 저장소 루트 파일 |
| 4 — CI 설정 | 자동 린트·테스트·빌드 | `.github/workflows/ci.yml` |
| 5 — 첫 릴리스 | `v0.1.0` 태그 + 릴리스 노트 | GitHub Releases |
| 6 — 공지 | SNS·커뮤니티 포스팅 | 첫 사용자 |
| 7 — 피드백 수집 | 이슈·댓글·이메일 모니터링 | `v0.1.1` 방향 |

작은 프로젝트일수록 이 순서를 지키는 편이 좋습니다. 기능을 과하게 늘리기 시작하면 끝내기 어려워지고, 끝내지 못한 프로젝트는 공개 경험을 남기지 못합니다.

## 직접 따라해 보기: 첫 프로젝트 공개 전체 흐름

### 1단계 — 아이디어와 범위 정하기

처음에는 무엇을 만들지보다 무엇을 이번 버전에 넣지 않을지 먼저 정하는 편이 좋습니다. 범위가 작아야 끝낼 수 있습니다.

```markdown
# tinytool — 프로젝트 범위 정의

## 목표
로컬 파일의 빈 줄을 한 명령으로 정리하는 CLI 도구

## 이번 버전 (v0.1.0)에 포함
- stdin 또는 파일 경로 입력
- 연속 빈 줄을 하나로 압축
- stdout 출력 또는 파일 덮어쓰기 옵션

## Non-goals (이번 버전에 넣지 않음)
- GUI
- 다국어 지원 (i18n)
- 플러그인 시스템
- Windows 바이너리 배포

## 다음 버전 후보
- 재귀 디렉터리 처리
- 설정 파일 지원 (.tinytoolrc)
```

이 문서를 저장소 첫 번째 이슈로 올려 두면, 외부 기여자가 기능을 요청할 때 "이미 non-goal로 선언되어 있다"고 링크를 걸 수 있습니다.

### 2단계 — MVP 코드와 저장소 골격 만들기

```bash
# 저장소 초기화
mkdir tinytool && cd tinytool
git init
python -m venv .venv && source .venv/bin/activate

# 기본 골격 생성
mkdir -p src/tinytool tests .github/workflows

# pyproject.toml 작성 (최소 구성)
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "tinytool"
version = "0.1.0"
description = "Collapse consecutive blank lines in text files"
requires-python = ">=3.9"
license = { text = "MIT" }

[project.scripts]
tinytool = "tinytool.cli:main"
EOF

# 메인 모듈 작성
cat > src/tinytool/__init__.py << 'EOF'
"""tinytool — collapse consecutive blank lines."""
__version__ = "0.1.0"
EOF

cat > src/tinytool/core.py << 'EOF'
import re

def collapse_blank_lines(text: str) -> str:
    """Replace 2+ consecutive blank lines with a single blank line."""
    return re.sub(r"\n{3,}", "\n\n", text)
EOF

cat > src/tinytool/cli.py << 'EOF'
import sys
import argparse
from .core import collapse_blank_lines

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collapse consecutive blank lines in text files."
    )
    parser.add_argument("file", nargs="?", help="Input file (default: stdin)")
    parser.add_argument("-i", "--inplace", action="store_true",
                        help="Edit file in place")
    args = parser.parse_args()

    if args.file:
        text = open(args.file).read()
        result = collapse_blank_lines(text)
        if args.inplace:
            open(args.file, "w").write(result)
        else:
            print(result, end="")
    else:
        text = sys.stdin.read()
        print(collapse_blank_lines(text), end="")

if __name__ == "__main__":
    main()
EOF

# 테스트 작성
cat > tests/test_core.py << 'EOF'
from tinytool.core import collapse_blank_lines

def test_no_change_single_blank():
    assert collapse_blank_lines("a\n\nb") == "a\n\nb"

def test_collapses_triple_blank():
    assert collapse_blank_lines("a\n\n\nb") == "a\n\nb"

def test_collapses_many_blanks():
    assert collapse_blank_lines("a\n\n\n\n\nb") == "a\n\nb"

def test_empty_string():
    assert collapse_blank_lines("") == ""
EOF

# 패키지 설치 및 테스트 실행
pip install -e ".[dev]" 2>/dev/null || pip install -e .
python -m pytest tests/ -v
```

### 3단계 — 기본 문서 5종 준비하기

문서가 없는 프로젝트는 써 볼 수 없는 프로젝트입니다. 최소 5종을 공개 전에 반드시 채워야 합니다.

```bash
# LICENSE 생성 (MIT 예시)
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

**README.md 최소 구성:**

```markdown
# tinytool

[![CI](https://github.com/yourname/tinytool/actions/workflows/ci.yml/badge.svg)](https://github.com/yourname/tinytool/actions)
[![PyPI](https://img.shields.io/pypi/v/tinytool)](https://pypi.org/project/tinytool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

로컬 파일의 연속 빈 줄을 한 명령으로 정리하는 CLI 도구입니다.

## 설치

```bash
pip install tinytool
```

## 사용법

```bash
# 결과를 stdout으로 출력
tinytool myfile.txt

# 파일 직접 수정
tinytool -i myfile.txt

# stdin 파이프
cat myfile.txt | tinytool
```

## 기여

[CONTRIBUTING.md](CONTRIBUTING.md)를 먼저 읽어 주세요.

## 라이선스

[MIT License](LICENSE)
```

**CHANGELOG.md (Keep a Changelog 형식):**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-20

### Added
- `collapse_blank_lines()` core function
- CLI entry point: `tinytool [file] [-i]`
- stdin piping support
- MIT license
- Initial test suite

[0.1.0]: https://github.com/yourname/tinytool/releases/tag/v0.1.0
```

### 4단계 — CI 설정하기

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Lint
        run: ruff check src/ tests/

      - name: Type check
        run: mypy src/

      - name: Test
        run: pytest tests/ -v --tb=short
```

PR이 열릴 때마다 이 워크플로가 돌아가면, 기여자가 코드를 올리기 전에 로컬에서 테스트를 돌려야 한다는 신호를 줍니다.

### 5단계 — 첫 릴리스 만들기

버전이 붙어야 사용자가 어디서부터 써야 하는지 분명해집니다. 첫 릴리스는 기능 규모보다 기준점 역할이 더 중요합니다.

```bash
# 변경사항 최종 커밋
git add .
git commit -m "feat: initial release v0.1.0"

# 원격 저장소에 푸시
git remote add origin https://github.com/yourname/tinytool.git
git push -u origin main

# 릴리스 태그 생성
git tag v0.1.0
git push origin v0.1.0

# GitHub CLI로 릴리스 생성 (CHANGELOG 기반 노트 자동 생성)
gh release create v0.1.0 \
  --title "tinytool v0.1.0 — First Release" \
  --notes "$(sed -n '/## \[0.1.0\]/,/## \[/p' CHANGELOG.md | head -n -1)" \
  --latest

# PyPI 배포 (선택 사항)
pip install build twine
python -m build
twine upload dist/*
```

### 6단계 — 공지하고 피드백 받기

프로젝트는 올리는 순간 끝나는 것이 아니라, 그다음 반응부터 본격적으로 시작됩니다.

**Show HN / Reddit 공지 템플릿:**

```text
Show HN: tinytool – collapse consecutive blank lines in text files

I wrote a small CLI tool that collapses consecutive blank lines
into a single blank line. Useful for cleaning up notes, logs, or
generated text files before further processing.

GitHub: https://github.com/yourname/tinytool
PyPI:   https://pypi.org/project/tinytool/

Feedback welcome — especially on edge cases I might have missed.
```

**Discussions 첫 스레드 열기:**

```bash
gh api repos/yourname/tinytool/discussions \
  --method POST \
  --field title="v0.1.0 출시 — 피드백을 환영합니다" \
  --field body="첫 릴리스를 공개했습니다. 사용 중 불편한 점이나 원하는 기능이 있으면 여기에 남겨 주세요." \
  --field category_id="DIC_kwDOA..."
```

## 운영 파일 체크리스트

공개에서 가장 많이 빠지는 것은 코드가 아니라 운영 파일입니다.

| 파일 | 역할 | 없을 때 생기는 문제 |
|---|---|---|
| `LICENSE` | 재사용 조건 | 사용자가 법적 불확실성으로 사용 기피 |
| `README.md` | 프로젝트 첫인상·사용법 | 설치조차 못 하고 이탈 |
| `CONTRIBUTING.md` | 참여 절차 | PR이 와도 어떻게 처리해야 할지 불명확 |
| `CHANGELOG.md` | 변경 이력 | 버전 간 차이를 릴리스 노트에서만 확인 가능 |
| `CODE_OF_CONDUCT.md` | 커뮤니티 경계 | 분쟁 발생 시 기준 없음 |

**PR 리뷰 체크리스트 (`.github/PULL_REQUEST_TEMPLATE.md`):**

```markdown
## PR 요약

<!-- 변경 사항을 한두 문장으로 설명해 주세요 -->

## 체크리스트

- [ ] 기능 동작 확인 (`pytest` 통과)
- [ ] 새로운 기능에 테스트 추가
- [ ] CHANGELOG.md의 `[Unreleased]` 섹션 업데이트
- [ ] 관련 문서 반영 (README 등)
- [ ] 커밋 메시지가 Conventional Commits 형식을 따름
```

## 브랜치 전략과 Git 워크플로

첫 프로젝트에 복잡한 브랜치 전략은 불필요합니다. 단순한 조합으로 시작하세요.

| 설정 | 방법 | 이유 |
|---|---|---|
| `main` 브랜치 보호 | Settings → Branch protection rules | 직접 push 방지 |
| 기능 브랜치 | `feat/collapse-blank-lines` 형식 | 변경 목적 명확화 |
| Squash Merge | PR merge 시 기본값으로 설정 | 커밋 히스토리 정리 |
| 태그 릴리스 | `v0.1.0`, `v0.1.1` 형식 | 사용자가 안정 버전 고정 가능 |

```bash
# 브랜치 보호 설정 (GitHub CLI)
gh api repos/yourname/tinytool/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["test"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null
```

## 메인테이너 번아웃 신호와 대응

첫 프로젝트를 공개하면 흥분되지만, 시간이 지나면서 유지보수 부담이 느껴집니다. 번아웃은 갑자기 오는 것이 아니라 신호가 있습니다.

| 신호 | 증상 | 대응 |
|---|---|---|
| 응답 지연 | 이슈·PR에 2주 이상 무응답 | 응답 주기 공표 또는 자동화 |
| 이슈 축적 | 미해결 이슈 100개+ | triage 루틴 강화, 라벨링 정리 |
| 동기 저하 | 코드 작성에 흥미 상실 | 서브 프로젝트 분리, 휴식 |
| 불명확한 방향 | 기능 추가를 계속 미룸 | 로드맵 작성, non-goals 재선언 |

번아웃을 느낀다면 부끄러운 것이 아니라 프로젝트 구조를 고쳐야 한다는 신호입니다. 메인테이너 역할을 나누거나, 자동화를 더하거나, 프로젝트 범위를 줄이는 것이 해결책입니다.

## 프로젝트 종료와 인수인계

첫 프로젝트를 시작하는 것만큼이나 끝내는 것도 중요합니다. 메인테이너가 더 이상 프로젝트를 지속할 수 없다면 인수인계 절차가 필요합니다.

**1단계: README에 상태 공지**

```markdown
## Status: Seeking New Maintainer

I can no longer maintain this project.
If you are a regular contributor and interested in taking over,
please open an issue tagged `maintainer-wanted`.

Read-only archive will happen on 2027-01-01 if no successor is found.
```

**2단계: 후임자를 찾지 못했다면 fork 권장**

```markdown
## Fork Recommended

This project is archived. Community members are encouraged to fork.
Notable forks:
- @alice/tinytool (active, maintained by @alice)
```

**3단계: GitHub Archive 설정**

```bash
# Repository Settings → Danger Zone → Archive this repository
# 이후 저장소는 읽기 전용, 새 이슈·PR 불가
```

프로젝트를 깨끗하게 마무리하는 것도 메인테이너의 책임입니다. 방치하기보다는 명시적으로 끝내고 후임자를 찾거나 fork를 권장하는 편이 커뮤니티에 훨씬 낫습니다.

## 자주 하는 실수 다섯 가지

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 완벽해질 때까지 공개를 미룸 | 기능 10개를 다 완성한 뒤 공개하려다 결국 포기 | MVP 1개 기능으로 `v0.1.0` 먼저 공개 |
| 라이선스 없이 저장소만 공개 | `git push` 후 LICENSE 파일 없이 방치 | `choosealicense.com`에서 MIT 선택 후 첫 커밋에 포함 |
| README가 모호해서 시작을 못 함 | "A tool for text processing"만 쓰고 설치법 누락 | 설치 → 실행 → 예시 출력을 복사 가능한 코드블록으로 제공 |
| 피드백 채널을 만들지 않음 | 이슈 탭 비활성화, Discussions 없음 | GitHub Discussions 활성화 후 첫 스레드 직접 개설 |
| 로드맵 없이 기능 요청 처리 | 들어오는 요청마다 반응해 방향이 흔들림 | `ROADMAP.md` 또는 GitHub Milestone으로 다음 버전 계획 공표 |

## 실무에서는 이렇게 생각한다

회사 내부 도구도 이 공개 절차를 닮을수록 온보딩이 쉬워집니다. 작은 도구라도 이름이 있고, README가 있고, 릴리스가 있고, 변경 이력이 있으면 다른 팀이 가져다 쓰기 훨씬 편해집니다. 결국 오픈소스 방식은 외부 공개 여부를 넘어, 소프트웨어를 공유 가능한 형태로 다듬는 습관입니다.

시니어 엔지니어는 첫 프로젝트를 대작으로 시작하지 않습니다. 작게 만들고, 빠르게 공개하고, 피드백을 받아 개선합니다. 공개가 곧 마무리가 아니라 학습의 다음 단계라는 사실을 알고 있기 때문입니다.

SemVer를 문서에 직접 넣어 두면 릴리스 판단 기준이 흔들리지 않습니다. `0.1.0`(첫 공개) → `0.1.1`(버그 수정) → `0.2.0`(기능 추가)처럼 작게 반복하면 유지보수 감각이 빠르게 붙습니다.

## 운영 체크리스트

- [ ] 프로젝트 목표와 non-goals를 한 문서에 정리했습니다.
- [ ] MVP가 로컬에서 동작합니다.
- [ ] 기본 문서 5종(LICENSE, README, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG)을 준비했습니다.
- [ ] CI 워크플로가 PR마다 자동으로 실행됩니다.
- [ ] `v0.1.0` 태그와 GitHub Release를 생성했습니다.
- [ ] 공지 메시지를 하나 이상의 채널에 올렸습니다.
- [ ] 피드백을 받을 채널(Discussions 또는 이슈)을 활성화했습니다.

## 정리

이번 글에서는 작은 아이디어를 실제 오픈소스 프로젝트로 공개하는 최소 절차를 정리했습니다. 핵심은 거대한 결과물이 아니라, 다른 사람이 써 볼 수 있는 상태까지 끝내는 경험입니다.

이 시리즈는 여기서 마칩니다. 이제 첫 풀 리퀘스트를 보내도 좋고, 작은 도구 하나를 첫 릴리스까지 밀어도 좋습니다. 중요한 것은 더 배우는 것이 아니라, 공개 가능한 단위로 한 번 끝까지 가 보는 일입니다.

## 처음 질문으로 돌아가기

- **첫 오픈소스 프로젝트는 어느 정도 크기여야 할까요?**
  - 기능 하나가 동작하고, 문서 5종이 갖춰지고, 릴리스 태그가 붙으면 충분합니다. `tinytool`처럼 CLI 도구 하나, 함수 하나, 테스트 몇 개 수준도 첫 오픈소스 프로젝트로서 완전합니다. 크기보다 끝까지 가 본 경험이 더 중요합니다.

- **아이디어, 범위, MVP, 문서, 릴리스는 어떤 순서로 준비하면 좋을까요?**
  - "목표 한 줄 + non-goals 목록 → MVP 구현 → 문서 5종 → CI → 릴리스 → 공지 → 피드백" 순서를 지키면 됩니다. 특히 non-goals를 먼저 적는 것이 완벽주의 함정을 막는 가장 효과적인 장치입니다. 범위가 확정되지 않으면 기능을 계속 추가하다 공개에 이르지 못합니다.

- **코드보다 문서와 라이선스가 왜 공개 직전에 더 중요해질까요?**
  - 코드가 아무리 좋아도 LICENSE가 없으면 사용자는 법적 불확실성 때문에 사용을 기피합니다. README가 설치법 없이 설명만 있으면 시작을 못 합니다. 문서는 "이 프로젝트를 써도 안전하고, 시작하기 어렵지 않다"는 신호를 동시에 주기 때문에, 코드 품질보다 첫 인상을 결정하는 데 더 큰 영향을 미칩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Open Source 101 (1/10): 오픈소스란 무엇인가](./01-what-is-open-source.md)
- [Open Source 101 (2/10): 라이선스 이해하기](./02-understanding-licenses.md)
- [Open Source 101 (3/10): 이슈 읽기](./03-reading-issues.md)
- [Open Source 101 (4/10): 풀 리퀘스트 만들기](./04-creating-pull-requests.md)
- [Open Source 101 (5/10): 좋은 리드미 문서](./05-good-readme.md)
- [Open Source 101 (6/10): 릴리스와 버전 관리](./06-release-and-versioning.md)
- [Open Source 101 (7/10): 커뮤니티 운영](./07-community-management.md)
- [Open Source 101 (8/10): 메인테이너의 역할](./08-maintainer-role.md)
- [Open Source 101 (9/10): 오픈소스 포트폴리오](./09-open-source-portfolio.md)
- **내 첫 오픈소스 프로젝트 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Open Source Guides — Starting a Project](https://opensource.guide/starting-a-project/)
- [Choose a License](https://choosealicense.com/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Show HN](https://news.ycombinator.com/showhn.html)
- [github/opensource.guide 저장소](https://github.com/github/opensource.guide)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, Project, Capstone, GitHub, Beginner
