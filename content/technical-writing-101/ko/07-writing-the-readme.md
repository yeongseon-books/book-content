---
series: technical-writing-101
episode: 7
title: "Technical Writing 101 (7/10): README 작성하기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - TechnicalWriting
  - README
  - OpenSource
  - Documentation
  - Beginner
seo_description: 프로젝트의 첫인상인 README를 효과적으로 구성하여 독자가 5분 안에 프로젝트를 실행할 수 있게 돕는 핵심 5단계 구조와 작성 팁을 다룹니다.
last_reviewed: '2026-05-15'
---

# Technical Writing 101 (7/10): README 작성하기

저장소를 처음 연 사람은 보통 코드보다 README를 먼저 읽습니다. 여기서 프로젝트의 목적이 흐리거나, 설치 명령이 깨지거나, 첫 실행까지의 경로가 길면 대부분은 바로 탭을 닫습니다. README는 소개문이라기보다 입구의 마찰을 줄이는 실행 문서에 가깝습니다.

이 글은 기술 글쓰기 101 시리즈의 7번째 글입니다.

좋은 README는 모든 것을 설명하려 하지 않습니다. 이 프로젝트가 무엇인지, 왜 필요한지, 가장 짧게 어떻게 돌려 보는지, 실제로 어떤 결과가 나와야 하는지부터 차례로 보여 주며 독자의 첫 5분을 설계합니다.

여기서는 처음 방문한 사람이 5분 안에 성공 경험을 얻도록 README를 구성하는 기준을 다룹니다.

![Technical Writing 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/07/07-01-concept-at-a-glance.ko.png)
*Technical Writing 101 7장 흐름 개요*
> README는 프로젝트의 첫 입구입니다. 독자가 5분 안에 실행 성공을 경험하도록 설계합니다.

## 이 글에서 다룰 문제

- 처음 방문한 사람이 README만 보고 5분 안에 실행할 수 있을까요?
- README의 다섯 부분은 왜 거의 같은 순서로 반복될까요?
- Quick Start는 왜 짧을수록 더 강할까요?
- FAQ, Troubleshooting, Contributing 섹션은 언제 추가해야 할까요?
- 배지와 스크린샷은 어떻게 활용하면 좋을까요?

## 이 글에서 배울 것

- README 다섯 부분 구조 (What / Why / How / Demo / License)
- Quick Start 작성 기준
- 배지 배치 원칙
- FAQ와 Troubleshooting 섹션 추가 기준
- Contributing 가이드라인 작성법

README는 프로젝트의 첫인상입니다. 저장소에 처음 들어온 사람은 코드보다 먼저 README를 읽고, 여기서 계속 볼지 떠날지를 결정합니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 좋은 README는 이 프로젝트가 무엇인지, 왜 만들었는지, 어떻게 써야 하는지, 실제로 돌아가는지, 법적으로 무엇이 허용되는지까지 한 흐름으로 답합니다.

- **What**: 이것이 무엇인지입니다.
- **Why**: 왜 만들었는지입니다.
- **How**: 어떻게 쓰는지입니다.
- **Demo**: 실제로 돌아간다는 증거입니다.
- **License**: 법적 조건입니다.

## README 5단계 흐름 구조

```
방문자가 저장소를 엽니다
          │
          ▼
  [What] 제목 아래 한 줄 설명
    ─ "이 프로젝트는 무엇인가"
          │
          ▼
  [Why] 왜 만들었는가
    ─ 동기, 배경, 대상 독자
          │
          ▼
  [How] Quick Start
    ─ 3-5개 명령, 5분 안에 실행
          │
          ▼
  [Demo] 기대 출력 / 스크린샷
    ─ 성공의 증거
          │
          ▼
  [License] 법적 조건
    ─ MIT / Apache 2.0 / GPL
```

이 순서는 독자가 프로젝트를 이해하고 실행하기까지 가장 빠른 경로를 형성합니다.

## Before / After 비교: README 작성 방식

### Before / After 예시 1: 목적 없는 소개 vs 한 줄 정의

**Before — 모호한 첫 문장**

```markdown
# my-api-project

This is a project I made to learn about APIs and databases.
```

독자는 이 프로젝트가 무엇을 하는지, 자기에게 유용한지 알 수 없습니다.

**After — 기능 중심 한 줄 정의**

```markdown
# my-api-project

A lightweight REST API for managing user profiles, built with FastAPI and SQLite.
```

한 문장에 무엇을(REST API), 무엇을 위해(user profiles), 어떻게(FastAPI + SQLite)가 모두 담겼습니다.

---

### Before / After 예시 2: 길고 불명확한 Quick Start vs 5분 안에 끝나는 Quick Start

**Before — 설명이 많고 명령이 흩어진 Quick Start**

```
먼저 Python이 설치되어 있어야 합니다. 그다음 가상 환경을 만들고 활성화합니다.
의존성을 설치한 다음 서버를 시작합니다. 서버가 시작되면 브라우저에서 확인합니다.
```

독자는 명령을 찾아 스크롤을 내려야 합니다.

**After — 복사-붙여넣기 가능한 Quick Start**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

설치, 실행, 검증이 한 화면 안에 모여 있습니다.

---

### Before / After 예시 3: 데모 없음 vs 기대 출력 제시

**Before — 명령만 있고 결과가 없음**

```
서버를 실행한 다음 API를 테스트합니다.
```

**After — 실행 결과를 직접 보여줌**

```bash
curl http://127.0.0.1:8000/
```

```json
{"message": "Hello World"}
```

독자는 자기 실행 결과가 정상인지 즉시 확인할 수 있습니다.

## 문서 템플릿: Python 프로젝트 README

```markdown
# [프로젝트 이름]

[한 문장 설명 — 무엇을, 무엇으로, 무엇을 위해]

## Why

[왜 만들었는지 2-3문장 — 동기와 대상 독자]

## Quick Start

```bash
git clone https://github.com/username/[프로젝트].git
cd [프로젝트]
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

**Expected output:**

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

## Demo

브라우저에서 `http://127.0.0.1:8000/docs`를 열면 대화형 API 문서가 보입니다.

## Features

- [기능 1]
- [기능 2]
- [기능 3]

## License

MIT
```

## README 필수 섹션 체크리스트

| 섹션 | 목적 | 분량 가이드 | 필수 여부 |
| --- | --- | --- | --- |
| **What** | 프로젝트가 무엇인지 한 마디로 | 1-2문장 | 필수 |
| **Why** | 왜 만들었는지 배경 | 2-3문장 | 필수 |
| **How (Quick Start)** | 설치와 실행 명령 | 3-5개 명령 | 필수 |
| **Demo** | 실행 결과 또는 스크린샷 | 출력 1개 이상 | 필수 |
| **License** | 법적 조건 | 1줄 | 필수 |
| Features | 주요 기능 목록 | 3-5개 | 선택 |
| Contributing | 기여 방법 | 링크 또는 간단 안내 | 선택 |
| FAQ | 자주 묻는 질문 | 3-5개 | 선택 |
| Troubleshooting | 흔한 오류 해결 | 3-5개 | 선택 |

## 배지와 상태 표시

README 상단에 배지를 달면 프로젝트 상태를 한눈에 전달할 수 있습니다.

```markdown
![CI](https://github.com/user/repo/workflows/CI/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Coverage](https://img.shields.io/codecov/c/github/user/repo)
```

배지 배치 원칙:
1. 제목 바로 아래 한 줄에 모읍니다
2. 3-5개 이하로 제한합니다
3. 중요도 순으로 배치합니다: CI 상태 → 라이선스 → 버전

## 흔한 README 실수와 해결

| 실수 | 왜 문제인가 | 바로 고치는 방법 |
| --- | --- | --- |
| Why가 없습니다 | 독자가 이 프로젝트가 자기에게 맞는지 판단하기 어렵습니다 | `## Why` 섹션을 추가하고 동기를 1-2문장으로 적습니다 |
| Quick Start가 너무 깁니다 | 독자가 첫 단계에서 이탈합니다 | 복잡한 설정은 별도 섹션으로 분리하고 Quick Start는 기본 실행만 담습니다 |
| 데모 결과가 없습니다 | 독자가 성공 여부를 알 수 없습니다 | 기대 출력 블록을 Quick Start 바로 아래 추가합니다 |
| 라이선스가 없습니다 | 상업적 사용 여부 등 법적 판단을 할 수 없습니다 | `## License` 섹션을 문서 하단에 추가합니다 |
| 스크린샷이 없습니다 | 독자가 결과를 상상해야 합니다 | CLI는 터미널 출력, 웹앱은 UI 스크린샷 한 장을 추가합니다 |
| 버전 정보가 없습니다 | 시간이 지나면 명령이 달라져 독자가 혼란을 겪습니다 | requirements.txt에 버전을 고정하고 README에 Python 버전을 명시합니다 |

## 운영 체크리스트

- [ ] What / Why / How / Demo / License 다섯 부분이 모두 있는가
- [ ] Quick Start가 5개 명령 이하인가
- [ ] 기대 출력이 명시되어 있는가
- [ ] 라이선스가 적혀 있는가
- [ ] 모든 명령이 복사-붙여넣기로 동작하는가
- [ ] 스크린샷 또는 기대 출력이 한 개 이상 있는가

## 연습 문제

1. 아래 첫 문장을 개선하세요: "This is my project for learning Python."
2. Quick Start에서 반드시 포함해야 할 세 가지 요소를 적어 보세요.
3. 다음 중 필수 섹션과 선택 섹션을 구분하세요: What / Features / Why / FAQ / License / Contributing

## 정리

좋은 README는 저장소 소개문이 아니라 친절한 입구입니다. 무엇인지, 왜 만들었는지, 어떻게 쓰는지, 실제로 돌아가는지, 어떤 조건으로 쓸 수 있는지까지 짧고 분명하게 보여 줘야 합니다. Quick Start는 5분 안에 첫 성공을 경험하게 하고, 기대 출력은 독자가 스스로 성공을 확인하게 합니다. 다음 글에서는 독자가 실제로 따라 하며 배울 수 있는 튜토리얼을 어떻게 설계할지 봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): 예제 코드 설명하기](./05-explaining-example-code.md)
- [Technical Writing 101 (6/10): 그림과 표 사용하기](./06-using-figures-and-tables.md)
- **Technical Writing 101 (7/10): README 작성하기 (현재 글)**
- [Technical Writing 101 (8/10): 튜토리얼 작성하기](./08-writing-tutorials.md)
- [Technical Writing 101 (9/10): 블로그와 문서 차이](./09-blog-vs-docs.md)
- [발행 전 체크리스트](./10-pre-publish-checklist.md)

<!-- toc:end -->

## 참고 자료

- [Make a README - GitHub](https://www.makeareadme.com/)
- [Standard README - RichardLitt](https://github.com/RichardLitt/standard-readme)
- [Awesome README - matiassingers](https://github.com/matiassingers/awesome-readme)
- [Choose a License](https://choosealicense.com/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/technical-writing-101/ko)

Tags: TechnicalWriting, README, OpenSource, Documentation, Beginner
