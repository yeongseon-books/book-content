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

좋은 README는 모든 것을 설명하려 하지 않습니다. 이 프로젝트가 무엇인지, 왜 필요한지, 가장 짧게 어떻게 돌려 보는지, 실제로 어떤 결과가 나와야 하는지부터 차례로 보여 주며 독자의 첫 5분을 설계합니다.

이 글은 Technical Writing 101 시리즈의 7번째 글입니다. 여기서는 처음 방문한 사람이 5분 안에 성공 경험을 얻도록 README를 구성하는 기준을 다룹니다.

## 먼저 던지는 질문

- 처음 방문한 사람이 README만 보고 5분 안에 실행할 수 있을까요?
- README의 다섯 부분은 왜 거의 같은 순서로 반복될까요?
- Quick Start는 왜 짧을수록 더 강할까요?

## 큰 그림

![Technical Writing 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/technical-writing-101/07/07-01-concept-at-a-glance.ko.png)

*Technical Writing 101 7장 흐름 개요*

단순 구조로 나눔닉니다.

> README는 병녀 나뎲닉니다.

## 이 글에서 배울 것

- 다섯 부분 구조
- Quick Start 쓰기
- 배지 쓰기
- FAQ 추가하기
- 라이선스 적기

## 왜 중요한가

README는 프로젝트의 첫인상입니다. 저장소에 처음 들어온 사람은 코드보다 먼저 README를 읽고, 여기서 계속 볼지 떠날지를 결정합니다.

## 한눈에 보는 멘탈 모델

> 멘탈 모델: 좋은 README는 이 프로젝트가 무엇인지, 왜 만들었는지, 어떻게 써야 하는지, 실제로 돌아가는지, 법적으로 무엇이 허용되는지까지 한 흐름으로 답합니다.

## 핵심 용어

- **What**: 이것이 무엇인지입니다.
- **Why**: 왜 만들었는지입니다.
- **How**: 어떻게 쓰는지입니다.
- **Demo**: 실제로 돌아간다는 증거입니다.
- **License**: 법적 조건입니다.

## Before / After

**Before**: "A Python package called Hello."

**After**: A README with all five parts.

## README는 5분 계약처럼 읽혀야 합니다

다음처럼 빠른 성공 경로를 본문 초반에 압축할 수 있습니다.

~~~markdown
## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```
~~~

**Expected output:**

```text
Uvicorn running on http://127.0.0.1:8000
```

이런 Quick Start가 강한 이유는 설치, 실행, 검증이 한 화면 안에 모여 있기 때문입니다. 저장소 설명을 길게 읽지 않아도 독자는 먼저 성공을 확인할 수 있고, 성공 뒤에야 아키텍처나 배경 설명을 더 읽을 이유가 생깁니다.

## README 필수 섹션 체크리스트

좋은 README는 다섯 부분이 거의 같은 순서로 반복됩니다. 이 순서는 독자가 프로젝트를 이해하고 실행하기까지 가장 빠른 경로를 형성하기 때문입니다.

| 섹션 | 목적 | 분량 가이드 | 위치 | 필수 여부 |
| --- | --- | --- | --- | --- |
| **What** | 프로젝트가 무엇인지 한 마디로 | 1-2문장 | 제목 바로 아래 | 필수 |
| **Why** | 왜 만들었는지 배경 | 2-3문장 | What 바로 다음 | 필수 |
| **How (Quick Start)** | 설치와 실행 명령 | 3-5 번의 커맨드 | Why 다음 | 필수 |
| **Demo** | 실행 결과 또는 스크린샷 | 결과 1개 이상 | Quick Start 바로 아래 | 필수 |
| **License** | 법적 조건 | 1줄 (MIT, Apache 2.0 등) | 문서 하단 | 필수 |
| Features | 주요 기능 목록 | 글머리 기호 3-5개 | Quick Start 전후 | 선택 |
| Contributing | 기여 방법 | 링크 또는 간단 안내 | License 전 | 선택 |
| FAQ | 자주 묻는 질문 | 3-5개 | License 전 | 선택 |

이 표를 따르면 독자는 제목을 보고 1분 안에 프로젝트가 무엇인지, 5분 안에 어떻게 실행하는지 파악할 수 있습니다.

## Python 프로젝트용 README 템플릿

다음은 FastAPI 프로젝트를 가정한 구체적인 템플릿입니다.

```markdown
# my-api-project

A lightweight REST API for managing user profiles, built with FastAPI.

## Why

I needed a simple user management API for learning FastAPI deployment patterns. Existing examples were either too complex or lacked production-ready structure.

## Quick Start

```bash
# Clone and enter
git clone https://github.com/username/my-api-project.git
cd my-api-project

# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run dev server
fastapi dev main.py
```

**Expected output:**

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Demo

Open `http://127.0.0.1:8000/docs` to see interactive API documentation.

![API Documentation Screenshot](docs/screenshot-swagger.png)

## Features

- User CRUD operations
- JWT authentication
- SQLite database with SQLAlchemy ORM
- Input validation with Pydantic v2
- Automatic OpenAPI docs

## License

MIT
```

이 템플릿은 What, Why, How, Demo, License 다섯 부분을 모두 담고 있으며, 명령은 복사해 붙여 넣으면 바로 동작합니다.

## 흔한 README 실수 5가지

### 1. Why가 없습니다

프로젝트가 무엇인지만 적고 왜 만들었는지 빠뜨립니다. 독자는 배경 없이 Quick Start만 보면 이 프로젝트가 자기에게 맞는지 판단하기 어렵습니다.

**Fix**: `## Why` 섹션을 추가하고 한 두 문장으로 동기를 적습니다.

### 2. Quick Start가 깁니다

설치 명령이 열 줄 넘게 나열되면 독자는 이미 지쳤습니다. Quick Start는 5분 안에 끝날 수 있어야 합니다.

**Fix**: 복잡한 설정은 별도 섹션으로 분리하고, Quick Start는 기본 실행만 담습니다.

### 3. 데모 결과가 없습니다

명령을 실행했을 때 무엇이 나와야 하는지 보여 주지 않으면 독자는 성공했는지 실패했는지 모릉니다.

**Fix**: `**Expected output:**` 블록을 추가하고 실제 터미널 출력을 붙여 넣습니다.

### 4. 라이선스가 없습니다

라이선스가 없으면 독자는 이 코드를 상업적으로 쓸 수 있는지, 수정해도 되는지 모릅니다.

**Fix**: `## License` 섹션을 하단에 추가하고 `MIT`, `Apache 2.0`, `GPL-3.0` 등 명시합니다.

### 5. 스크린샷이 없습니다

CLI 도구라면 터미널 출력, 웹 앱이라면 UI 스크린샷을 한 장이라도 보여 주면 독자는 훨씬 빨리 이해합니다.

**Fix**: `Demo` 섹션에 스크린샷을 추가하고, 이미지에 대체 텍스트를 달아 접근성을 보장합니다.

## 배지와 상태 표시

README 상단에 배지를 달면 프로젝트 상태를 한눈에 전달할 수 있습니다.

### 주요 배지 종류

```markdown
![CI](https://github.com/user/repo/workflows/CI/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Coverage](https://img.shields.io/codecov/c/github/user/repo)
```

### 배지 배치 원칙

1. 제목 바로 아래 한 줄에 모음
2. 3-5개 이하로 제한
3. 중요도 순: CI 상태 → 라이선스 → 버전

## FAQ 섹션 추가 가이드

README를 발행한 뒤 동일한 질문이 반복되면 FAQ 섹션을 추가합니다.

```markdown
## FAQ

### Q: Windows에서 실행되나요?

A: 네, Python 3.11 이상이면 Windows/macOS/Linux 모두 동작합니다.

### Q: Docker로 실행할 수 있나요?

A: 네, `docker-compose up`으로 실행할 수 있습니다. 자세한 내용은 [docs/docker.md](docs/docker.md)를 참고하세요.

### Q: 상용 프로젝트에 사용해도 되나요?

A: 네, MIT 라이선스로 상업적 사용이 가능합니다.
```

FAQ는 3-5개를 권장하며, 각 질문은 Q&A 형식으로 적습니다.
## 실습: README 다섯 부분 만들기

### 1단계 — What

```markdown
# greeter
A small greeting library.
```

### 2단계 — Why

```markdown
## Why
I wanted multilingual greetings in a single line.
```

### 3단계 — How

```bash
pip install greeter
python3 -c "from greeter import hello; print(hello('en'))"
```

### 4단계 — Demo

```text
Hello!
```

### 5단계 — License

```markdown
## License
MIT
```

## 이 코드에서 먼저 볼 점

- 다섯 부분이 모두 있습니다.
- 명령은 복사해 붙여 넣을 수 있습니다.
- 결과가 눈에 보입니다.

## 자주 하는 실수 5가지

1. **Why가 없습니다.**
2. **Quick Start가 깁니다.**
3. **데모 결과가 없습니다.**
4. **라이선스가 없습니다.**
5. **스크린샷이 없습니다.**

## 실무에서는 이렇게 드러납니다

GitHub에서 주목받는 프로젝트 대부분은 거의 같은 다섯 부분 패턴을 따릅니다. 독자가 가장 빨리 프로젝트를 이해하고 실행할 수 있는 구조이기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 5분 안에 실행돼야 합니다.
- Why는 한 줄이어야 합니다.
- 명령은 적힌 그대로 돌아가야 합니다.
- 라이선스는 명시해야 합니다.
- 스크린샷은 하나 이상 있어야 합니다.

## 체크리스트

- [ ] 다섯 부분이 모두 있는가
- [ ] Quick Start가 다섯 줄 이하인가
- [ ] 데모 결과를 보여 주는가
- [ ] 라이선스를 적었는가

## 연습 문제

1. What의 뜻을 한 줄로 적어 보세요.
2. Demo의 뜻을 한 줄로 적어 보세요.
3. License의 예시를 한 줄로 적어 보세요.

## 정리

좋은 README는 저장소 소개문이 아니라 친절한 입구입니다. 무엇인지, 왜 만들었는지, 어떻게 쓰는지, 실제로 돌아가는지, 어떤 조건으로 쓸 수 있는지까지 짧고 분명하게 보여 줘야 합니다. 다음 글에서는 독자가 실제로 따라 하며 배울 수 있는 튜토리얼을 어떻게 설계할지 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **처음 방문한 사람이 README만 보고 5분 안에 실행할 수 있을까요?**
  단띄닉니다.
- **README의 다섯 부분은 왜 거의 같은 순서로 반복될까요?**
  단렷닉니다.
- **Quick Start는 왜 짧을수록 더 강할까요?**
  늨륹 낸말니다.

<!-- toc:begin -->
## 시리즈 목차

- [Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가](./01-what-is-technical-writing.md)
- [Technical Writing 101 (2/10): 독자 정의하기](./02-defining-the-reader.md)
- [Technical Writing 101 (3/10): 제목과 구조 잡기](./03-title-and-structure.md)
- [Technical Writing 101 (4/10): 개념 설명하기](./04-explaining-concepts.md)
- [Technical Writing 101 (5/10): 예제 코드 설명하기](./05-explaining-example-code.md)
- [Technical Writing 101 (6/10): 그림과 표 사용하기](./06-using-figures-and-tables.md)
- **README 작성하기 (현재 글)**
- 튜토리얼 작성하기 (예정)
- 블로그와 문서 차이 (예정)
- 발행 전 체크리스트 (예정)

<!-- toc:end -->

## 참고 자료

- [Make a README - GitHub](https://www.makeareadme.com/)
- [Standard README - RichardLitt](https://github.com/RichardLitt/standard-readme)
- [Awesome README - matiassingers](https://github.com/matiassingers/awesome-readme)
- [Choose a License](https://choosealicense.com/)

Tags: TechnicalWriting, README, OpenSource, Documentation, Beginner
