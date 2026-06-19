---
series: open-source-101
episode: 5
title: "Open Source 101 (5/10): 좋은 리드미 문서"
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
  - README
  - Documentation
  - GitHub
  - Beginner
seo_description: 리드미 문서를 단순한 소개글이 아니라 첫 5분 온보딩을 책임지는 안내서로 보고 설치부터 라이선스까지의 필수 구성을 정리합니다.
last_reviewed: '2026-05-15'
---

# Open Source 101 (5/10): 좋은 리드미 문서

좋은 프로젝트라도 리드미 문서가 불친절하면 첫인상이 크게 나빠집니다. 특히 오픈소스에서는 리드미 문서가 제품 소개서이자 설치 안내서이고, 때로는 유지보수자의 태도를 보여 주는 문서이기도 합니다. 방문자는 코드를 열어 보기 전에 이 문서부터 읽습니다.

이 글은 오픈소스 101 시리즈의 5번째 글입니다.

여기서는 사용자가 5분 안에 프로젝트를 이해하고 실행할 수 있게 만드는 좋은 리드미 문서의 기본 구조를 정리하겠습니다.

![Open Source 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/open-source-101/05/05-01-follow-the-reader-s-order.ko.png)
*Open Source 101 5장 흐름 개요*
> 좋은 README는 기술 정보를 나열하는 문서가 아닙니다. **이 프로젝트가 뭐하는 것이고, 나는 언제 쓰고, 어떻게 시작할 수 있는지**를 5분 안에 이해시키는 프로젝트 대표입니다.

## 이 글에서 다룰 문제

- 처음 방문한 사용자가 리드미 문서에서 가장 먼저 찾는 정보는 무엇일까요?
- 제목, 한 줄 설명, 설치, 사용 예시, 라이선스는 왜 핵심 섹션일까요?
- 배지와 스크린샷은 언제 도움이 되고 언제 방해가 될까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 이 글이 중요한가

리드미 문서가 나쁘면 사용자는 설치 전 단계에서 이탈하고, 기여자는 규칙을 찾지 못해 헤매며, 메인테이너는 같은 질문에 반복 답변하게 됩니다.

좋은 리드미 문서는 지원 비용을 줄이고 신뢰를 높입니다. 특히 작은 프로젝트일수록 문서 품질이 프로젝트 성숙도를 대신 보여 주는 경우가 많습니다. 코드가 아무리 좋아도 시작 경로가 보이지 않으면 사용자는 떠납니다.

## 핵심 관점

사용자의 읽기 순서를 따라가는 것이 좋은 README의 핵심입니다.

```text
이 프로젝트가 뭔가? (한 줄 설명)
  → 내가 쓸 수 있나? (설치 방법)
  → 어떻게 쓰는 거야? (사용 예시)
  → 계속 써도 되나? (라이선스, CI 상태)
  → 기여할 수 있나? (CONTRIBUTING 링크)
```

> 좋은 README는 화려한 수사보다 **빠른 성공 경험**을 제공합니다. 사용자가 5분 안에 설치하고 한 번 실행해 볼 수 있다면, 이미 절반은 성공한 문서입니다.

## 핵심 개념

### README 필수 섹션과 역할

| 섹션 | 역할 | 없을 때 결과 |
|---|---|---|
| 프로젝트명 + 한 줄 설명 | 무엇인지 즉시 이해 | 이탈률 증가 |
| 배지 (CI, 버전) | 유지보수 상태 신호 | 신뢰도 하락 |
| 설치 방법 | 진입 장벽 제거 | 포기 또는 질문 폭주 |
| 사용 예시 (Quickstart) | 첫 성공 경험 제공 | 이해 없이 사용 |
| 기여 안내 링크 | 기여자 유입 경로 | 메인테이너에게 직접 질문 |
| 라이선스 | 법적 명확성 | 도입 불가 판단 |

### 배지 사용 기준

배지는 상태를 빠르게 보여 주는 장치이지만, 의미 없는 배지 남발은 오히려 시선을 분산시킵니다.

**권장 배지**:
```markdown
![CI](https://github.com/owner/repo/actions/workflows/ci.yml/badge.svg)
![PyPI version](https://badge.fury.io/py/my-package.svg)
![License](https://img.shields.io/github/license/owner/repo)
![Python versions](https://img.shields.io/pypi/pyversions/my-package)
```

**피해야 할 배지**:
```markdown
# 의미 없거나 항상 초록인 배지는 신뢰를 낮춤
![Made with love](https://img.shields.io/badge/made%20with-love-red)
![Stars](https://img.shields.io/github/stars/owner/repo)  # 초기 프로젝트엔 역효과
```

## 좋은 README vs 나쁜 README 비교

### 한 줄 설명

```markdown
# 나쁜 예시
# MyTool
A utility tool for developers.

# 좋은 예시
# MyTool
Convert Markdown files to PDF in one command — no LaTeX required.
```

차이: 좋은 설명은 **누가**, **무엇을**, **어떤 상황에서** 쓰는지 즉시 알 수 있습니다.

### 설치 방법

```markdown
# 나쁜 예시
## Installation
Install the package using your preferred package manager.

# 좋은 예시
## Installation

Python 3.9+ required.

```bash
pip install mytool
```

For development:

```bash
git clone https://github.com/owner/mytool
cd mytool
pip install -e ".[dev]"
pre-commit install
```
```

### 사용 예시

```markdown
# 나쁜 예시
## Usage
Use the tool to convert files.

# 좋은 예시
## Usage

### Convert a single file

```bash
mytool convert README.md --output README.pdf
```

### Convert a directory

```bash
mytool convert docs/ --output build/pdf/ --recursive
```

### Python API

```python
from mytool import Converter

converter = Converter(theme="minimal")
converter.convert("README.md", "README.pdf")
```
```

## 실전 README 구조 예시

실제 프로젝트에서 쓸 수 있는 완성된 구조입니다.

```markdown
# mytool

> Convert Markdown files to PDF in one command — no LaTeX required.

[![CI](https://github.com/owner/mytool/actions/workflows/ci.yml/badge.svg)](https://github.com/owner/mytool/actions)
[![PyPI](https://badge.fury.io/py/mytool.svg)](https://pypi.org/project/mytool/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- Single command conversion
- Custom CSS themes
- Batch processing
- Python 3.9+ support

## Installation

```bash
pip install mytool
```

## Quickstart

```bash
# Convert a single file
mytool convert README.md

# Convert with custom theme
mytool convert README.md --theme minimal --output output.pdf
```

## Documentation

Full documentation: [https://mytool.readthedocs.io](https://mytool.readthedocs.io)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
# Development setup
pip install -e ".[dev]"
pre-commit install
pytest
```

## License

MIT © 2026 Your Name
```

## 섹션별 작성 가이드

### 한 줄 설명 공식

```text
[동사] + [무엇을] + [어디서/어떻게] + [차별점]

좋은 예시:
"Convert Markdown to PDF in one command — no LaTeX required."
"Detect memory leaks in Python applications with one import."
"Send Slack notifications from GitHub Actions without configuration."
```

### Quickstart 5분 원칙

첫 성공 경험까지 5분이 넘으면 이탈률이 급격히 높아집니다.

```markdown
## Quickstart

Install (30초):
```bash
pip install mytool
```

Run your first conversion (30초):
```bash
mytool convert README.md
# Output: README.pdf ✓
```

See result: Open README.pdf in your PDF viewer.

→ 전체 시간: 약 2분
```

### CONTRIBUTING 링크 패턴

```markdown
## Contributing

We welcome contributions! To get started:

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Find an issue labeled [`good first issue`](https://github.com/owner/repo/issues?q=is%3Aopen+label%3A%22good+first+issue%22)
3. Fork the repo and create a branch
4. Make your changes and run tests
5. Submit a pull request

Questions? Open a [Discussion](https://github.com/owner/repo/discussions).
```

## README 분리 기준

README가 너무 길어지면 다른 파일로 분리합니다.

```text
README.md          ← 첫 5분 온보딩 (설치, 사용 예시, 링크)
CONTRIBUTING.md    ← 기여 규칙 (환경 설정, 브랜치, 커밋)
ARCHITECTURE.md    ← 설계 문서 (경험 있는 기여자용)
CHANGELOG.md       ← 버전별 변경 이력
docs/              ← 상세 API 문서, 튜토리얼
```

분리 기준: README가 1000줄을 넘거나, 스크롤 없이 설치 방법을 볼 수 없으면 분리를 고려합니다.

## 자동화로 README 최신 상태 유지

```yaml
# .github/workflows/readme-check.yml
name: README Link Check

on:
  push:
    paths: ['README.md']
  schedule:
    - cron: '0 0 * * 1'  # 매주 월요일

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Check links
      uses: lycheeverse/lychee-action@v1
      with:
        args: README.md
        fail: true
```

```yaml
# .github/workflows/readme-contributors.yml
# 기여자 목록 자동 업데이트
name: Update Contributors

on:
  push:
    branches: [main]

jobs:
  contributors:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: minicli/action-contributors@v3
      with:
        repo: '${{ github.repository }}'
        output: 'CONTRIBUTORS.md'
```

## 다국어 README 전략

글로벌 프로젝트라면 영어와 함께 주요 언어 README를 제공합니다.

```markdown
# 영어 README.md 상단에 언어 링크 추가
Available in: [한국어](README.ko.md) | [中文](README.zh.md) | [日本語](README.ja.md)
```

```text
파일 구조:
README.md      ← 영어 (기본)
README.ko.md   ← 한국어
README.zh.md   ← 중국어
```

번역은 커뮤니티 기여로 받되, 핵심 섹션(설치, 사용 예시, 라이선스)은 메인테이너가 직접 관리합니다.

## 직접 따라해 보기: 리드미 문서 기본 뼈대 만들기

### 1단계 — 제목과 한 줄 설명 쓰기

```markdown
# my-project

> A tiny tool that does X in one command.
```

### 2단계 — 꼭 필요한 배지만 넣기

```markdown
[![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)](https://github.com/user/repo/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

### 3단계 — 설치 명령 적기

```markdown
## Installation

```bash
pip install my-project
```
```

### 4단계 — 바로 실행 가능한 사용 예시 넣기

```markdown
## Usage

```bash
my-project --input data.csv --output result.pdf
```
```

### 5단계 — 라이선스 명시하기

```markdown
## License

MIT © 2026 Author Name
```

## 자주 하는 실수

| 실수 | 구체적 상황 | 올바른 접근 |
|---|---|---|
| 설치 명령 없음 | "소스에서 빌드하세요" 한 줄만 있음 | `pip install`, `npm install` 등 복사 가능한 명령어 제공 |
| 오래된 예시 | 실행하면 오류나는 코드 블록 방치 | CI에서 README 코드 블록 테스트 자동화 |
| 스크린샷만 있음 | 스크린샷만 있고 텍스트 설명 없음 | 스크린샷 + 접근성 고려한 alt text + 텍스트 설명 병행 |
| 라이선스 섹션 생략 | README에 라이선스 언급 없음 | LICENSE 파일 + README 하단 라이선스 섹션 필수 |
| 모든 설계를 README에 | 아키텍처 다이어그램부터 API 문서까지 | README는 진입 문서, 나머지는 별도 파일로 분리 |

## 실무에서는 이렇게 생각한다

회사 내부 라이브러리도 리드미 문서 품질에 따라 온보딩 속도가 크게 달라집니다. 새 팀원이 문서만 보고 환경을 띄울 수 있으면 지원 비용이 줄고, 그렇지 않으면 메신저 질문이 문서 역할을 대신하게 됩니다.

시니어 엔지니어는 리드미 문서를 광고처럼 쓰되 과장하지 않습니다. 짧은 문장, 바로 실행되는 예시, 관련 문서 링크, 기여 문서 분리 같은 기본이 오히려 더 큰 신뢰를 만듭니다.

**README 갱신 습관** — README는 한 번 쓰고 끝나는 문서가 아닙니다. 다음 시점에 반드시 갱신합니다:
- 주요 기능 추가 시
- 설치 방법 변경 시 (Python 버전 요구사항 변경 포함)
- 라이선스 변경 시
- Breaking change 발생 시
- 기여 가이드 추가·수정 시

## 운영 체크리스트

- [ ] 제목과 한 줄 설명이 있습니다.
- [ ] 설치 명령이 바로 보입니다.
- [ ] 실행 가능한 사용 예시가 있습니다.
- [ ] 라이선스 섹션이 있습니다.
- [ ] CI 배지가 있습니다.
- [ ] CONTRIBUTING.md 링크가 있습니다.

## 연습 문제

1. quickstart의 목표 시간을 한 문장으로 적어 보세요.
2. badge의 목적을 한 문장으로 적어 보세요.
3. `CONTRIBUTING.md`를 리드미 문서와 분리하는 이유를 한 문장으로 적어 보세요.

## 정리

이번 글에서는 리드미 문서를 저장소 소개글이 아니라 첫 5분 온보딩 문서로 보는 관점을 정리했습니다. 좋은 문서는 프로젝트를 멋져 보이게 만드는 문서가 아니라, 사용자가 실제로 움직이게 만드는 문서입니다.

다음 글에서는 릴리스와 버전 관리를 다룹니다. 프로젝트를 쓰게 만드는 문서를 정리했다면, 이제는 사용자가 안심하고 업데이트할 수 있는 규칙도 필요합니다.

## 처음 질문으로 돌아가기

- **처음 방문한 사용자가 리드미 문서에서 가장 먼저 찾는 정보는 무엇일까요?**
  - 가장 먼저 찾는 것은 "이 프로젝트가 내 문제를 해결해 주는가"입니다. 한 줄 설명과 사용 예시가 여기에 답합니다. 그 다음이 설치 방법입니다. 이 세 가지가 5분 안에 보이지 않으면 사용자는 이탈합니다.
- **제목, 한 줄 설명, 설치, 사용 예시, 라이선스는 왜 핵심 섹션일까요?**
  - 이 다섯 섹션은 사용자가 프로젝트를 평가하는 순서와 일치합니다. 무엇인지 → 쓸 수 있는지 → 어떻게 쓰는지 → 계속 써도 되는지. 이 흐름이 끊기면 사용자는 다음 단계로 넘어가지 못합니다.
- **배지와 스크린샷은 언제 도움이 되고 언제 방해가 될까요?**
  - CI 통과, 최신 버전, 라이선스 배지는 신뢰 신호로 도움이 됩니다. 스크린샷은 GUI 도구나 시각적 결과물을 보여줄 때 유용합니다. 하지만 의미 없는 장식 배지가 5개 이상이거나 스크린샷이 오래되어 실제와 다르면 오히려 신뢰를 낮춥니다.

<!-- toc:end -->

## 참고 자료

- [Make a README](https://www.makeareadme.com/)
- [GitHub README guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Shields.io](https://shields.io/)
- [GitHub Docs 저장소](https://github.com/github/docs)

- [이 시리즈 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/open-source-101/ko)

Tags: OpenSource, README, Documentation, GitHub, Beginner
