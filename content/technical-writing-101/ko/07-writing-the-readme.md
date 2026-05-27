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
> README는 병녀 나뎲닉니다.

## 먼저 던지는 질문

- 처음 방문한 사람이 README만 보고 5분 안에 실행할 수 있을까요?
- README의 다섯 부분은 왜 거의 같은 순서로 반복될까요?
- Quick Start는 왜 짧을수록 더 강할까요?

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

## 전후 비교

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

## Contributing 가이드라인 작성법

오픈소스 프로젝트는 README에 Contributing 섹션을 추가해 외부 기여자가 프로젝트에 참여하는 방법을 명확히 해야 합니다.

### 기본 Contributing 템플릿

```markdown
## Contributing

We welcome contributions! Here's how you can help:

### 1. 저장소 포크하기

```bash
git clone https://github.com/username/my-api-project.git
cd my-api-project
```

### 2. 브랜치 생성하기

```bash
git checkout -b feature/your-feature-name
```

### 3. Make your changes

- Follow the code style in `.editorconfig`
- Add tests for new features
- Update documentation if needed

### 4. Run tests

```bash
pytest tests/
```

### 5. 풀 리퀘스트 제출하기

- Describe what you changed and why
- Link related issues
- Wait for review

## 행동 강령

Please be respectful and constructive in all interactions. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.
```

### Contributing을 별도 파일로 분리하는 기준

다음 경우 `CONTRIBUTING.md`로 분리합니다:

1. **기여 가이드가 README보다 긴 경우** (10줄 이상)
2. **코드 스타일이나 테스트 규칙이 복잡한 경우**
3. **팀 규모가 크고 프로세스가 정형화된 경우**

README에는 다음처럼 링크만 남깁니다:

```markdown
## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
```

## Troubleshooting 섹션 구성

README에 Troubleshooting 섹션을 추가하면 독자가 흔히 겪는 문제를 빠르게 해결할 수 있습니다.

### 템플릿

```markdown
## Troubleshooting

### 문제: `ModuleNotFoundError: No module named 'fastapi'`

**원인**: 가상 환경이 활성화되지 않았거나 패키지가 설치되지 않았습니다.

**해결**:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 문제: `Address already in use`

**원인**: 포트 8000이 이미 사용 중입니다.

**해결**:

```bash
fastapi dev main.py --port 8001
```

### 문제: 테스트가 실패합니다

**원인**: 의존성이 최신 버전이 아닐 수 있습니다.

**해결**:

```bash
pip install --upgrade -r requirements.txt
pytest tests/
```
```

### Troubleshooting을 별도 문서로 분리하는 기준

문제가 5개 이상이거나 해결 방법이 복잡하면 `docs/troubleshooting.md`로 분리하고 README에는 링크만 남깁니다.

```markdown
## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues and solutions.
```
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

## 실전 앵커: README를 첫 5분 온보딩 문서로 설계하기

README는 프로젝트 소개문이 아니라 실행 입구입니다. 첫 방문자가 5분 안에 성공 경험을 얻도록 작성 순서를 고정합니다.

### README 5분 루틴

1. 프로젝트 한 줄 설명
2. 왜 이 프로젝트가 필요한지 2문장
3. Quick Start 3-5명령
4. 기대 출력
5. 다음 링크

### Quick Start 교정 예시

| 교정 전 | 교정 후 |
| --- | --- |
| 설치 후 실행하세요 | `python3 -m venv .venv` → `source .venv/bin/activate` → `pip install -r requirements.txt` → `uvicorn app:app --reload` |
| 정상적으로 동작합니다 | `Uvicorn running on http://127.0.0.1:8000` 출력 확인 |

### README 품질 표

| 항목 | 기준 |
| --- | --- |
| What | 제목 아래 1-2문장 |
| Why | 문제 맥락과 대상 독자 명시 |
| How | 명령 복사-실행 가능 |
| Demo | 출력 또는 스크린샷 제공 |
| License | 라이선스 명시 |

### 흔한 이탈 지점과 해결

- 가상환경 누락: Quick Start 첫 줄에 명시
- 버전 불일치: requirements 버전 고정
- 포트 충돌: 대체 포트 명령 제공
- 문서 과다: 고급 내용은 별도 `docs/`로 분리

## README 검토 템플릿

- 5분 안에 첫 실행이 가능한가?
- 실행 실패 시 복구 명령이 있는가?
- 기여/문제해결 문서로 가는 링크가 있는가?

### 실전 보강 섹션 1

이 단락은 본문 원칙을 실제 작성 루틴으로 옮기기 위한 보강 섹션입니다. 팀 문서에서 품질 편차가 생기는 이유는 원칙을 모르는 것이 아니라, 원칙을 반복 적용할 고정 루틴이 없기 때문입니다. 그래서 작성자와 리뷰어가 같은 기준을 공유하는 문장, 표, 체크리스트를 함께 두는 편이 좋습니다.

| 점검 항목 | 질문 | 통과 기준 |
| --- | --- | --- |
| 대상 독자 | 이 문단이 누구를 위한 설명인가 | 독자가 한 문장으로 명시됨 |
| 실행 가능성 | 독자가 바로 따라 할 수 있는가 | 명령 또는 절차가 구체적으로 적힘 |
| 검증 가능성 | 성공 여부를 확인할 수 있는가 | 출력, 상태, 체크포인트가 제시됨 |
| 범위 통제 | 다루지 않는 항목이 명시되었는가 | 비목표 또는 한계가 적힘 |

- 작성 팁: 한 섹션 안에 새 개념을 1개만 두면 독자가 중간에 이탈할 확률이 줄어듭니다.
- 리뷰 팁: 문장 정확성보다 먼저 독자의 다음 행동이 보이는지 확인하면 실용성이 올라갑니다.
- 운영 팁: 반복되는 질문은 FAQ나 오류 해결 섹션으로 승격해 검색 비용을 낮춥니다.

다음 예시 문장은 실제로 수정 비용을 줄이는 데 유용합니다. "이 단계가 끝나면 터미널에 특정 메시지가 보입니다."처럼 눈으로 확인 가능한 결과를 붙이면, 독자는 추측 대신 확인으로 진행할 수 있습니다. 또한 "이 글은 여기까지만 다룹니다."라는 범위 문장을 넣으면 글이 과도하게 확장되는 문제를 막을 수 있습니다.

### 실전 보강 섹션 2

이 단락은 본문 원칙을 실제 작성 루틴으로 옮기기 위한 보강 섹션입니다. 팀 문서에서 품질 편차가 생기는 이유는 원칙을 모르는 것이 아니라, 원칙을 반복 적용할 고정 루틴이 없기 때문입니다. 그래서 작성자와 리뷰어가 같은 기준을 공유하는 문장, 표, 체크리스트를 함께 두는 편이 좋습니다.

| 점검 항목 | 질문 | 통과 기준 |
| --- | --- | --- |
| 대상 독자 | 이 문단이 누구를 위한 설명인가 | 독자가 한 문장으로 명시됨 |
| 실행 가능성 | 독자가 바로 따라 할 수 있는가 | 명령 또는 절차가 구체적으로 적힘 |
| 검증 가능성 | 성공 여부를 확인할 수 있는가 | 출력, 상태, 체크포인트가 제시됨 |
| 범위 통제 | 다루지 않는 항목이 명시되었는가 | 비목표 또는 한계가 적힘 |

- 작성 팁: 한 섹션 안에 새 개념을 1개만 두면 독자가 중간에 이탈할 확률이 줄어듭니다.
- 리뷰 팁: 문장 정확성보다 먼저 독자의 다음 행동이 보이는지 확인하면 실용성이 올라갑니다.
- 운영 팁: 반복되는 질문은 FAQ나 오류 해결 섹션으로 승격해 검색 비용을 낮춥니다.

다음 예시 문장은 실제로 수정 비용을 줄이는 데 유용합니다. "이 단계가 끝나면 터미널에 특정 메시지가 보입니다."처럼 눈으로 확인 가능한 결과를 붙이면, 독자는 추측 대신 확인으로 진행할 수 있습니다. 또한 "이 글은 여기까지만 다룹니다."라는 범위 문장을 넣으면 글이 과도하게 확장되는 문제를 막을 수 있습니다.

### 실전 보강 섹션 3

이 단락은 본문 원칙을 실제 작성 루틴으로 옮기기 위한 보강 섹션입니다. 팀 문서에서 품질 편차가 생기는 이유는 원칙을 모르는 것이 아니라, 원칙을 반복 적용할 고정 루틴이 없기 때문입니다. 그래서 작성자와 리뷰어가 같은 기준을 공유하는 문장, 표, 체크리스트를 함께 두는 편이 좋습니다.

| 점검 항목 | 질문 | 통과 기준 |
| --- | --- | --- |
| 대상 독자 | 이 문단이 누구를 위한 설명인가 | 독자가 한 문장으로 명시됨 |
| 실행 가능성 | 독자가 바로 따라 할 수 있는가 | 명령 또는 절차가 구체적으로 적힘 |
| 검증 가능성 | 성공 여부를 확인할 수 있는가 | 출력, 상태, 체크포인트가 제시됨 |
| 범위 통제 | 다루지 않는 항목이 명시되었는가 | 비목표 또는 한계가 적힘 |

- 작성 팁: 한 섹션 안에 새 개념을 1개만 두면 독자가 중간에 이탈할 확률이 줄어듭니다.
- 리뷰 팁: 문장 정확성보다 먼저 독자의 다음 행동이 보이는지 확인하면 실용성이 올라갑니다.
- 운영 팁: 반복되는 질문은 FAQ나 오류 해결 섹션으로 승격해 검색 비용을 낮춥니다.

다음 예시 문장은 실제로 수정 비용을 줄이는 데 유용합니다. "이 단계가 끝나면 터미널에 특정 메시지가 보입니다."처럼 눈으로 확인 가능한 결과를 붙이면, 독자는 추측 대신 확인으로 진행할 수 있습니다. 또한 "이 글은 여기까지만 다룹니다."라는 범위 문장을 넣으면 글이 과도하게 확장되는 문제를 막을 수 있습니다.

### 실전 보강 섹션 4

이 단락은 본문 원칙을 실제 작성 루틴으로 옮기기 위한 보강 섹션입니다. 팀 문서에서 품질 편차가 생기는 이유는 원칙을 모르는 것이 아니라, 원칙을 반복 적용할 고정 루틴이 없기 때문입니다. 그래서 작성자와 리뷰어가 같은 기준을 공유하는 문장, 표, 체크리스트를 함께 두는 편이 좋습니다.

| 점검 항목 | 질문 | 통과 기준 |
| --- | --- | --- |
| 대상 독자 | 이 문단이 누구를 위한 설명인가 | 독자가 한 문장으로 명시됨 |
| 실행 가능성 | 독자가 바로 따라 할 수 있는가 | 명령 또는 절차가 구체적으로 적힘 |
| 검증 가능성 | 성공 여부를 확인할 수 있는가 | 출력, 상태, 체크포인트가 제시됨 |
| 범위 통제 | 다루지 않는 항목이 명시되었는가 | 비목표 또는 한계가 적힘 |

- 작성 팁: 한 섹션 안에 새 개념을 1개만 두면 독자가 중간에 이탈할 확률이 줄어듭니다.
- 리뷰 팁: 문장 정확성보다 먼저 독자의 다음 행동이 보이는지 확인하면 실용성이 올라갑니다.
- 운영 팁: 반복되는 질문은 FAQ나 오류 해결 섹션으로 승격해 검색 비용을 낮춥니다.

다음 예시 문장은 실제로 수정 비용을 줄이는 데 유용합니다. "이 단계가 끝나면 터미널에 특정 메시지가 보입니다."처럼 눈으로 확인 가능한 결과를 붙이면, 독자는 추측 대신 확인으로 진행할 수 있습니다. 또한 "이 글은 여기까지만 다룹니다."라는 범위 문장을 넣으면 글이 과도하게 확장되는 문제를 막을 수 있습니다.

### 실전 보강 섹션 5

이 단락은 본문 원칙을 실제 작성 루틴으로 옮기기 위한 보강 섹션입니다. 팀 문서에서 품질 편차가 생기는 이유는 원칙을 모르는 것이 아니라, 원칙을 반복 적용할 고정 루틴이 없기 때문입니다. 그래서 작성자와 리뷰어가 같은 기준을 공유하는 문장, 표, 체크리스트를 함께 두는 편이 좋습니다.

| 점검 항목 | 질문 | 통과 기준 |
| --- | --- | --- |
| 대상 독자 | 이 문단이 누구를 위한 설명인가 | 독자가 한 문장으로 명시됨 |
| 실행 가능성 | 독자가 바로 따라 할 수 있는가 | 명령 또는 절차가 구체적으로 적힘 |
| 검증 가능성 | 성공 여부를 확인할 수 있는가 | 출력, 상태, 체크포인트가 제시됨 |
| 범위 통제 | 다루지 않는 항목이 명시되었는가 | 비목표 또는 한계가 적힘 |

- 작성 팁: 한 섹션 안에 새 개념을 1개만 두면 독자가 중간에 이탈할 확률이 줄어듭니다.
- 리뷰 팁: 문장 정확성보다 먼저 독자의 다음 행동이 보이는지 확인하면 실용성이 올라갑니다.
- 운영 팁: 반복되는 질문은 FAQ나 오류 해결 섹션으로 승격해 검색 비용을 낮춥니다.

다음 예시 문장은 실제로 수정 비용을 줄이는 데 유용합니다. "이 단계가 끝나면 터미널에 특정 메시지가 보입니다."처럼 눈으로 확인 가능한 결과를 붙이면, 독자는 추측 대신 확인으로 진행할 수 있습니다. 또한 "이 글은 여기까지만 다룹니다."라는 범위 문장을 넣으면 글이 과도하게 확장되는 문제를 막을 수 있습니다.

## 정리

좋은 README는 저장소 소개문이 아니라 친절한 입구입니다. 무엇인지, 왜 만들었는지, 어떻게 쓰는지, 실제로 돌아가는지, 어떤 조건으로 쓸 수 있는지까지 짧고 분명하게 보여 줘야 합니다. 다음 글에서는 독자가 실제로 따라 하며 배울 수 있는 튜토리얼을 어떻게 설계할지 봅니다.

## 처음 질문으로 돌아가기

- **처음 방문한 사람이 README만 보고 5분 안에 실행할 수 있을까요?**
  블로그와 문서는 역할이 다르므로 섞지 않고 분리해 운영해야 신뢰를 유지할 수 있습니다.
- **README의 다섯 부분은 왜 거의 같은 순서로 반복될까요?**
  블로그는 작성 시점의 경험을, 문서는 현재 기준의 정본을 책임진다는 점에서 생명주기와 소유권이 다릅니다.
- **Quick Start는 왜 짧을수록 더 강할까요?**
  Diátaxis의 네 구역은 글의 목적을 학습, 문제 해결, 참조, 설명으로 나눠 채널 혼선을 줄여 줍니다.

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/technical-writing-101/ko)

Tags: TechnicalWriting, README, OpenSource, Documentation, Beginner
