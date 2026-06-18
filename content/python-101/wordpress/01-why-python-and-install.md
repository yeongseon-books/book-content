---
title: "바이브코딩을 위한 Python 기초 (1/10): 왜 Python이고, 어떻게 설치할까?"
series: python-101
episode: 1
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- Python
- venv
- AI코딩
- 개발환경
seo_description: "바이브코딩 시대, AI에게 코드를 시키기 전에 Python 환경부터 제대로 잡아야 합니다. 설치, venv, pip의 핵심을 AI 코딩 관점에서 정리합니다."
---

# 바이브코딩을 위한 Python 기초 (1/10): 왜 Python이고, 어떻게 설치할까?

이 글은 바이브코딩을 위한 Python 기초 시리즈의 첫 번째 글입니다.

ChatGPT에게 "파이썬으로 웹 크롤러 만들어줘"라고 했더니 코드가 나왔습니다. 복사해서 터미널에 붙여넣었더니 `ModuleNotFoundError: No module named 'requests'`가 뜹니다. `pip install requests`를 했더니 이번엔 `Permission denied`. 결국 `sudo pip install`을 했더니 돌아가긴 하는데, 다음날 다른 프로젝트를 열었더니 패키지 버전이 꼬여서 둘 다 안 됩니다.

바이브코딩의 핵심은 AI가 코드를 생성하고 사람이 실행하는 것입니다. 그런데 **실행 환경이 망가져 있으면 AI가 아무리 좋은 코드를 줘도 돌아가지 않습니다.** 환경 설정은 AI가 대신 해줄 수 없는 영역이고, 한 번 잘 잡아두면 이후 모든 바이브코딩이 매끄러워집니다.

> AI가 생성한 코드를 실행하려면 Python 환경부터 격리해야 합니다. system Python에 직접 설치하는 순간 모든 프로젝트가 엮입니다.

---

## 이 글에서 다룰 문제

- AI가 만든 코드를 바로 실행했는데 왜 에러가 날까요?
- system Python과 venv를 분리해야 하는 진짜 이유는 무엇일까요?
- `sudo pip install`이 왜 위험하고, 대신 어떻게 해야 할까요?
- 프로젝트마다 다른 패키지 버전이 필요할 때 어떻게 관리할까요?
- AI에게 받은 requirements.txt를 안전하게 설치하는 방법은 무엇일까요?

---

## 바이브코딩에서 Python 환경이 중요한 이유

AI에게 코드를 받아서 실행하는 워크플로우는 대략 이렇습니다:

1. AI에게 프롬프트를 줍니다
2. AI가 코드를 생성합니다
3. **사람이 실행합니다** ← 여기서 터집니다
4. 에러가 나면 다시 AI에게 물어봅니다

3번에서 문제가 생기는 이유의 절반 이상은 환경 문제입니다. 패키지가 없거나, 버전이 안 맞거나, Python 자체가 다른 버전이거나. AI는 코드를 잘 만들어도 여러분 컴퓨터의 환경까지는 모릅니다.

그래서 바이브코딩을 제대로 하려면 **프로젝트마다 독립된 Python 환경**을 만드는 습관이 필수입니다.

---

## 멘탈 모델: 프로젝트 = 폴더 + 자기만의 Python

```
내 컴퓨터
├── system Python (OS용 — 건드리지 않음)
├── project-A/
│   └── .venv/  ← project-A만의 Python + 패키지
├── project-B/
│   └── .venv/  ← project-B만의 Python + 패키지
└── project-C/
    └── .venv/  ← project-C만의 Python + 패키지
```

프로젝트가 10개면 `.venv`도 10개. 서로 영향을 주지 않습니다. AI가 만든 코드를 시험해 볼 때도 새 폴더 + 새 venv를 만들면 기존 프로젝트가 깨질 걱정이 없습니다.

---

## Before / After

### Before — system Python에 직접 설치

```bash
$ pip install requests
ERROR: Permission denied
$ sudo pip install requests   # 위험!
# 되긴 되는데... 다른 프로젝트까지 영향받음
```

AI가 준 코드를 급하게 돌리려고 `sudo pip install`을 하면, OS가 사용하는 Python 환경이 오염됩니다. 나중에 brew 업데이트가 깨지거나, 다른 프로젝트의 패키지 버전이 덮어써집니다.

### After — venv로 격리

```bash
$ mkdir ai-project && cd ai-project
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install requests
Successfully installed requests-2.32.3
(.venv) $ python main.py  # AI가 만든 코드 실행
```

`(.venv)` 프롬프트가 보이면 안전 지대입니다. 여기서 뭘 설치하든 이 폴더 안에만 들어갑니다.

---

## 실습: 바이브코딩 환경 5분 만에 세팅하기

### Step 1 — Python 설치 확인

```bash
python3 --version
# Python 3.11.x 이상이면 OK
```

없으면 [python.org](https://www.python.org/downloads/)에서 설치합니다. Windows는 설치할 때 **"Add python.exe to PATH"** 반드시 체크.

### Step 2 — 프로젝트 폴더 + venv 생성

```bash
mkdir vibe-test && cd vibe-test
python3 -m venv .venv
```

### Step 3 — 활성화

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

프롬프트에 `(.venv)`가 보이면 성공입니다.

### Step 4 — AI가 준 패키지 설치

```bash
pip install requests beautifulsoup4
```

또는 AI가 `requirements.txt`를 만들어줬다면:

```bash
pip install -r requirements.txt
```

### Step 5 — 실행 & 검증

```bash
python main.py
```

끝났으면 `deactivate`로 빠져나옵니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `sudo pip install` | system Python 오염 | venv 안에서 설치 |
| venv 활성화 안 하고 실행 | 패키지 못 찾음 | `source .venv/bin/activate` 먼저 |
| `.venv/` 폴더를 git에 커밋 | 용량 폭발, OS별 호환 문제 | `.gitignore`에 추가 |
| AI가 준 버전 무시 | 호환성 깨짐 | `requirements.txt` 그대로 사용 |
| 하나의 venv로 모든 프로젝트 | 패키지 충돌 | 프로젝트마다 venv 분리 |

---

## AI에게 환경 관련 질문하는 팁

바이브코딩할 때 환경 에러가 나면 AI에게 이렇게 물어보세요:

```
이 에러가 났어:
[에러 메시지 붙여넣기]

내 환경:
- OS: macOS / Windows / Linux
- Python: python3 --version 결과
- venv 활성화 여부: (.venv) 프롬프트 보이는지
```

환경 정보를 함께 주면 AI가 훨씬 정확한 답을 줍니다.

---

## 운영 체크리스트

- [ ] Python 3.11 이상이 설치되어 있다
- [ ] 프로젝트마다 별도 venv를 만드는 습관이 있다
- [ ] `sudo pip install`을 쓰지 않는다
- [ ] `.venv/`가 `.gitignore`에 들어 있다
- [ ] AI가 준 코드를 실행하기 전에 venv 활성화부터 한다

---

## 처음 질문으로 돌아가기

- **AI가 만든 코드를 바로 실행했는데 왜 에러가 날까요?**
  - 대부분 패키지 미설치 또는 Python 버전 불일치입니다. venv를 만들고 필요한 패키지를 설치하면 해결됩니다.
- **system Python과 venv를 분리해야 하는 진짜 이유는 무엇일까요?**
  - system Python은 OS가 사용합니다. 여기에 패키지를 설치하면 OS 도구가 깨질 수 있고, 프로젝트 간 버전 충돌이 생깁니다.
- **`sudo pip install`이 왜 위험하고, 대신 어떻게 해야 할까요?**
  - root 권한으로 system Python에 설치하면 되돌리기 어렵습니다. venv 안에서는 `sudo` 없이도 설치됩니다.
- **프로젝트마다 다른 패키지 버전이 필요할 때 어떻게 관리할까요?**
  - 프로젝트마다 `.venv`를 별도로 만들면 각자 독립된 패키지 목록을 갖습니다.
- **AI에게 받은 requirements.txt를 안전하게 설치하는 방법은 무엇일까요?**
  - venv를 활성화한 상태에서 `pip install -r requirements.txt`를 실행하면 해당 프로젝트에만 설치됩니다.

---

## 정리

바이브코딩의 첫 단계는 AI에게 프롬프트를 잘 쓰는 것이 아니라, AI가 준 코드가 돌아갈 환경을 만드는 것입니다. `python3 -m venv .venv` → `source .venv/bin/activate` → `pip install` — 이 세 줄이 모든 바이브코딩 프로젝트의 시작점입니다. 한 번 습관이 되면 AI가 어떤 코드를 줘도 안전하게 실행할 수 있습니다.

다음 글에서는 변수, 타입, 연산자를 다룹니다. AI가 생성한 코드를 읽으려면 이 기초 문법을 알아야 합니다.

## 참고 자료

### 공식 문서
- [Python 공식 문서 (python.org)](https://docs.python.org/3/)
- [Python Tutorial (python.org)](https://docs.python.org/3/tutorial/)

### 관련 시리즈
- [Python DB-API 101](../../python-dbapi-101/ko/)
- [Pytest 101](../../pytest-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Python 기초 (1/10): 왜 Python이고, 어떻게 설치할까? (현재 글)**
- [바이브코딩을 위한 Python 기초 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [바이브코딩을 위한 Python 기초 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- [바이브코딩을 위한 Python 기초 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [바이브코딩을 위한 Python 기초 (5/10): 제어 흐름](./05-control-flow.md)
- [바이브코딩을 위한 Python 기초 (6/10): 함수와 인자](./06-functions-and-arguments.md)
- [바이브코딩을 위한 Python 기초 (7/10): 모듈과 패키지](./07-modules-and-packages.md)
- [바이브코딩을 위한 Python 기초 (8/10): 파일 I/O와 예외 처리](./08-file-io-and-exceptions.md)
- [바이브코딩을 위한 Python 기초 (9/10): 클래스와 객체](./09-classes-and-objects.md)
- [바이브코딩을 위한 Python 기초 (10/10): 표준 라이브러리 투어](./10-standard-library-tour.md)

<!-- toc:end -->
Tags: 바이브코딩, Python, venv, AI코딩, 개발환경
