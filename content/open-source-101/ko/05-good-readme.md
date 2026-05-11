---
series: open-source-101
episode: 5
title: 좋은 README
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - OpenSource
  - README
  - Documentation
  - GitHub
  - Beginner
seo_description: 사용자가 5분 안에 시작할 수 있는 좋은 README 작성 원칙을 정리한 글
last_reviewed: '2026-05-11'
---

# 좋은 README

좋은 프로젝트라도 README가 불친절하면 첫인상이 크게 나빠집니다. 특히 오픈소스에서는 README가 제품 소개서이자 설치 안내서이고, 때로는 유지보수자의 태도를 보여 주는 문서이기도 합니다. 방문자는 코드를 열어 보기 전에 README부터 읽습니다.

초보자가 README를 쓸 때 가장 자주 빠지는 함정은 두 가지입니다. 아무 정보도 없는 빈 문서이거나, 반대로 너무 많은 정보를 한 파일에 몰아넣는 경우입니다. 좋은 README는 모든 것을 설명하는 문서가 아니라, 사용자가 5분 안에 프로젝트를 이해하고 실행할 수 있게 만드는 입구 문서입니다.

## 이 글에서 다룰 문제

- 처음 방문한 사용자가 README에서 가장 먼저 찾는 정보는 무엇일까요?
- 제목, 한 줄 설명, 설치, 사용 예시, 라이선스는 왜 핵심 섹션일까요?
- 배지와 스크린샷은 언제 도움이 되고 언제 방해가 될까요?
- CONTRIBUTING.md 같은 별도 문서와 README의 경계는 어디일까요?
- 사용자가 5분 안에 시작할 수 있는 문서는 어떻게 설계할까요?

## 왜 중요한가

README는 프로젝트의 얼굴이라는 말이 흔하지만, 실제로는 그보다 더 실무적입니다. README가 나쁘면 사용자는 설치 전 단계에서 이탈하고, 기여자는 규칙을 찾지 못해 헤매며, 메인테이너는 같은 질문에 반복 답변하게 됩니다.

좋은 README는 지원 비용을 줄이고 신뢰를 높입니다. 특히 작은 프로젝트일수록 문서 품질이 프로젝트 성숙도를 대신 보여 주는 경우가 많습니다.

## 먼저 잡아둘 멘탈 모델

> README는 저장소 소개글이 아니라 첫 5분을 안내하는 온보딩 스크립트입니다.

```mermaid
flowchart LR
    T[제목] --> D[설명]
    D --> I[설치]
    I --> U[사용 예시]
    U --> L[라이선스]
```

이 흐름이 중요한 이유는 읽는 사람의 관심사가 이 순서로 움직이기 때문입니다. 먼저 이 프로젝트가 무엇인지 알고 싶고, 다음에는 설치 가능한지 보고, 그다음 실제로 어떻게 쓰는지 확인합니다. 라이선스와 기여 안내는 그 다음입니다.

## 핵심 개념

- README는 진입 문서입니다. 저장소의 전체 설계를 다 담는 곳이 아닙니다.
- badge는 상태를 빠르게 보여 주는 장치입니다. 의미 없는 배지 남발은 오히려 시선을 분산시킵니다.
- TOC는 문서가 길어질 때 이동 비용을 줄여 줍니다.
- quickstart는 가장 짧은 성공 경로입니다. 처음 읽는 사람에게는 전체 설명보다 이 경로가 더 중요합니다.
- CONTRIBUTING는 기여 규칙을 분리하는 문서입니다. README에 모든 규칙을 넣지 않아도 되는 이유가 여기 있습니다.

## 생각이 어떻게 바뀌는가

Before: README는 나중에 쓰는 장식 같은 문서다.

After: README는 사용자가 실제로 프로젝트를 시작하게 만드는 첫 번째 인터페이스다.

## 직접 따라해 보기: README 기본 뼈대 만들기

### 1단계 — 제목과 한 줄 설명 쓰기

제목은 프로젝트 정체성을, 한 줄 설명은 사용 가치를 압축합니다. 애매한 문구보다 누가 무엇을 왜 쓰는지 보이게 적는 편이 좋습니다.

```markdown
# my-project

> A tiny tool that does X in one command.
```

### 2단계 — 꼭 필요한 배지만 넣기

배지는 한눈에 상태를 보여 주는 장점이 있지만, 의미 없는 장식으로 늘리기 쉽습니다. 유지되는 지표만 두는 편이 낫습니다.

```markdown
![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)
```

### 3단계 — 설치 명령 적기

설치 명령이 빠진 README는 사용자를 추측에 맡기는 문서입니다. 가장 짧은 설치 경로를 명시해야 합니다.

```markdown
## Install

\`\`\`bash
pip install my-project
\`\`\`
```

### 4단계 — 바로 실행 가능한 사용 예시 넣기

예시는 설명보다 강합니다. 사용자가 복사해 실행했을 때 바로 동작하는 코드 한 개가 긴 문단보다 낫습니다.

```markdown
## Usage

\`\`\`bash
my-project --help
\`\`\`
```

### 5단계 — 라이선스 명시하기

사용 예시가 좋아도 라이선스가 비어 있으면 배포와 재사용 판단이 멈춥니다. 짧더라도 명확하게 적는 편이 좋습니다.

```markdown
## License

MIT © 2026 Author Name
```

## 이 예시에서 읽어야 할 포인트

- 제목은 프로젝트가 무엇인지 단번에 보여 줘야 합니다.
- 예시는 실제로 실행 가능해야 합니다.
- 설치와 사용 예시는 분리할수록 읽기 쉽습니다.
- 라이선스 표기는 맨 아래에 있어도 절대 빠지면 안 됩니다.

## 자주 하는 실수 5가지

1. 설치 명령을 적지 않습니다.
2. 오래되어 실행되지 않는 예시를 남겨 둡니다.
3. 스크린샷만 넣고 설명은 비워 둡니다.
4. 라이선스 섹션을 생략합니다.
5. README 하나에 모든 설계를 몰아넣습니다.

## 실무에서는 이렇게 봅니다

회사 내부 라이브러리도 README 품질에 따라 온보딩 속도가 크게 달라집니다. 새 팀원이 README만 보고 환경을 띄울 수 있으면 지원 비용이 줄고, 그렇지 않으면 메신저 질문이 README 역할을 대신하게 됩니다.

시니어 엔지니어는 README를 광고처럼 쓰되 과장하지 않습니다. 짧은 문장, 바로 실행되는 예시, 관련 문서 링크, 기여 문서 분리 같은 기본이 오히려 더 큰 신뢰를 만듭니다.

## 체크리스트

- [ ] 제목과 한 줄 설명이 있습니다.
- [ ] 설치 명령이 바로 보입니다.
- [ ] 실행 가능한 사용 예시가 있습니다.
- [ ] 라이선스 섹션이 있습니다.

## 연습 문제

1. quickstart의 목표 시간을 한 문장으로 적어 보세요.
2. badge의 목적을 한 문장으로 적어 보세요.
3. CONTRIBUTING.md를 README와 분리하는 이유를 한 문장으로 적어 보세요.

## 마무리

이번 글에서는 README를 저장소 소개글이 아니라 첫 5분 온보딩 문서로 보는 관점을 정리했습니다. 좋은 README는 프로젝트를 돋보이게 꾸미는 문서가 아니라, 사용자가 실제로 움직이게 만드는 문서입니다.

다음 글에서는 릴리스와 버전 관리를 다룹니다. 프로젝트를 쓰게 만드는 문서를 정리했다면, 이제는 사용자가 안심하고 업데이트할 수 있는 규칙도 필요합니다.

<!-- toc:begin -->
- [오픈소스란 무엇인가](./01-what-is-open-source.md)
- [라이선스 이해하기](./02-understanding-licenses.md)
- [Issue 읽기](./03-reading-issues.md)
- [PR 만들기](./04-creating-pull-requests.md)
- **좋은 README (현재 글)**
- Release 와 Versioning (예정)
- Community 관리 (예정)
- Maintainer 의 역할 (예정)
- 오픈소스 포트폴리오 (예정)
- 내 첫 오픈소스 프로젝트 (예정)
<!-- toc:end -->

## 참고 자료

- [Make a README](https://www.makeareadme.com/)
- [GitHub README guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Shields.io](https://shields.io/)

Tags: OpenSource, README, Documentation, GitHub, Beginner
