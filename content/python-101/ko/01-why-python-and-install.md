---
title: "왜 Python인가, 그리고 설치와 venv"
series: python-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
  - Python
  - install
  - venv
  - pip
  - version
  - beginner
last_reviewed: '2026-05-03'
---

# 왜 Python인가, 그리고 설치와 venv

## 이 글에서 배울 것

- Python이 입문 언어로 가장 많이 선택되는 이유
- macOS, Linux, Windows 환경별 Python 설치 방법
- system Python을 직접 건드리면 안 되는 이유와 venv의 역할
- venv를 만들고 활성화하는 표준 흐름
- pip으로 패키지를 설치하고 버전을 고정하는 방법

## 왜 중요한가

Python을 처음 설치할 때 가장 흔한 실수는 system이 사용하는 Python에 패키지를 마구 설치하는 것입니다. 처음에는 잘 동작하지만, 두 번째 프로젝트를 시작하면 패키지 버전이 충돌하고 결국 OS 도구가 깨집니다. 처음부터 venv 사용을 습관화하면 평생 이 문제를 겪지 않습니다. 입문자가 가장 먼저 익혀야 할 기술은 문법이 아니라 환경 격리입니다.

## Mental Model

> Python 환경은 "**system Python은 OS의 것, 내 프로젝트는 내 venv**"라는 한 줄로 외울 수 있습니다. system Python은 OS가 자기 도구를 돌리는 데 사용하는 인터프리터이고, 내가 작업하는 모든 프로젝트는 별도 디렉터리의 venv 안에 들어가야 합니다.

git에 비유하면 venv는 프로젝트 디렉터리 같은 것입니다. 프로젝트마다 별도 디렉터리를 두지 않고 한 디렉터리에 모든 코드를 섞지는 않듯이, Python 환경도 프로젝트마다 분리합니다.

## 핵심 개념

### Python을 입문 언어로 고르는 이유

- **읽기 쉬운 문법**: 들여쓰기 기반 블록 + 자연어에 가까운 키워드(`if`, `for`, `in`, `not`)
- **거대한 ecosystem**: 데이터, 웹, AI, 자동화 모든 영역에 라이브러리가 존재
- **즉시 실행 가능**: 컴파일 단계 없이 `python script.py`로 바로 실행
- **REPL**: `python` 명령으로 대화형 셸이 떠서 한 줄씩 시험 가능
- **취업 시장의 광범위함**: 데이터, 백엔드, ML, DevOps 어디서든 사용

### Python 버전: 3.x만 사용

Python 2는 2020년에 공식 지원이 끝났습니다. 새 코드는 Python 3.10 이상을 권장합니다. `python --version`으로 확인하고, 시스템에 2.x만 있다면 새로 설치합니다.

| OS | 권장 설치 방법 |
| --- | --- |
| macOS | `brew install python@3.12` |
| Ubuntu/Debian | `apt install python3.12 python3.12-venv` |
| Windows | python.org installer (PATH 추가 체크) 또는 `winget install Python.Python.3.12` |
| 모든 OS (대안) | `pyenv` (여러 버전을 한 머신에서 관리) |

### system Python을 건드리면 안 되는 이유

macOS와 Linux는 OS 자체가 Python을 사용합니다. `/usr/bin/python3`에 패키지를 직접 설치하면 OS 도구가 망가질 수 있습니다. 또한 두 프로젝트가 같은 패키지의 다른 버전을 요구하면 한 환경에서는 절대 동시에 만족할 수 없습니다.

해결책이 venv입니다. venv는 프로젝트별로 독립된 Python 환경을 만들어 주고, 그 안에서 설치한 패키지는 다른 프로젝트나 system에 전혀 영향을 주지 않습니다.

### venv의 동작 원리

`python -m venv .venv`를 실행하면 `.venv/` 디렉터리가 생기고 그 안에 Python interpreter 사본 또는 link가 들어갑니다. 활성화(`source .venv/bin/activate`)하면 `python`이 `.venv/bin/python`을 가리키도록 PATH가 바뀌고, `pip install`은 `.venv/lib/`에 패키지를 설치합니다. 비활성화(`deactivate`)하면 PATH가 원래대로 돌아옵니다.

### pip과 requirements.txt

`pip`은 Python의 기본 패키지 매니저입니다. `pip install requests`처럼 패키지를 설치하고, `pip freeze > requirements.txt`로 현재 설치된 모든 패키지 버전을 파일로 저장합니다. 다른 머신에서는 `pip install -r requirements.txt`로 같은 환경을 재현할 수 있습니다.

## Before-After

```bash
# Before: system Python에 직접 설치
$ pip install requests          # /usr/lib/python3 에 설치
$ pip install requests==2.20    # 다른 프로젝트에서 충돌
ERROR: Cannot uninstall 'requests'. It is a distutils installed project.
```

```bash
# After: venv 사용
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install requests==2.20    # .venv/lib 에만 설치
(.venv) $ deactivate                    # 시스템에 영향 없음
```

After 패턴은 프로젝트가 100개로 늘어도 충돌이 발생하지 않습니다.

## 단계별 실습

### 1단계: Python 설치 확인

```bash
python3 --version
# Python 3.12.0 처럼 출력되면 OK
```

3.10 미만이면 위 표를 참고해 새로 설치합니다.

### 2단계: 프로젝트 디렉터리 생성

```bash
mkdir my-first-project
cd my-first-project
```

### 3단계: venv 생성과 활성화

```bash
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

활성화되면 prompt 앞에 `(.venv)`가 표시됩니다.

### 4단계: 패키지 설치

```bash
(.venv) $ pip install requests
(.venv) $ pip list
Package    Version
---------- -------
pip        24.0
requests   2.32.3
...
```

### 5단계: 버전 고정과 재현

```bash
(.venv) $ pip freeze > requirements.txt
(.venv) $ cat requirements.txt
requests==2.32.3
...

# 다른 머신에서
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```

### 6단계: 첫 스크립트 실행

```python
# hello.py
import requests
response = requests.get("https://httpbin.org/get")
print(response.status_code)
print(response.json()["url"])
```

```bash
(.venv) $ python hello.py
200
https://httpbin.org/get
```

## 자주 하는 실수

- **`sudo pip install`을 실행한다.** system Python을 변경하므로 OS 도구가 깨질 수 있습니다.
- **venv를 활성화하지 않고 `pip install`.** 의도와 다른 곳에 설치되어 추적이 어려워집니다.
- **`.venv`를 git에 커밋한다.** 수백 MB가 저장소에 들어갑니다. `.gitignore`에 `.venv/`를 추가하세요.
- **`requirements.txt`를 만들지 않는다.** 다른 머신에서 환경 재현이 불가능합니다.
- **Python 2를 새로 설치한다.** 2020년에 끝났습니다. 무조건 3.10+ 사용.

## 실무에서 쓰는 패턴

- **프로젝트 루트에 `.venv/` 고정 위치.** 모든 프로젝트가 같은 규칙이면 IDE 설정도 단순해집니다.
- **`.gitignore`에 `.venv/`, `__pycache__/`, `*.pyc` 기본 추가.**
- **버전 명시 (`pip install requests==2.32.3`).** 미래의 자기에게 친절합니다.
- **`pyproject.toml`로 점진적 이전.** 입문은 requirements.txt로 시작하고 익숙해지면 `pyproject.toml` + `uv` / `poetry`로 옮겨도 좋습니다.
- **여러 Python 버전이 필요하면 `pyenv`.** 프로젝트마다 다른 Python 버전을 강제할 수 있습니다.

## 체크리스트

- [ ] `python3 --version`이 3.10 이상이다
- [ ] 프로젝트마다 `.venv/`를 만든다
- [ ] 활성화 시 prompt에 `(.venv)`가 보인다
- [ ] `.venv/`가 `.gitignore`에 들어 있다
- [ ] `requirements.txt`가 저장소에 커밋되어 있다
- [ ] `sudo pip install`을 사용하지 않는다

## 연습 문제

1. 새 디렉터리에 venv를 만들고 `requests`를 설치한 뒤 `pip freeze > requirements.txt`로 저장하세요.
2. 같은 폴더에서 venv를 삭제하고 (`rm -rf .venv`), 다시 만들어 `requirements.txt`로 환경을 재현하세요.
3. 두 개의 폴더에 각각 venv를 만들고 한 곳에는 `requests==2.20`, 다른 곳에는 `requests==2.32`를 설치한 뒤 충돌 없이 동작함을 확인하세요.

## 정리, 다음 글

Python을 시작하는 데 필요한 것은 인터프리터 하나와 venv 습관입니다. system Python은 OS 도구로 두고, 내 모든 코드는 venv 안에서 돌립니다. 이 한 줄을 처음부터 지키면 환경 사고를 평생 겪지 않습니다.

다음 글에서는 Python의 변수, 타입, 연산자를 다룹니다. 동적 타입 언어가 어떻게 동작하는지, type hint가 왜 점점 표준이 되어 가는지를 살펴봅니다.

## 참고 자료

- Python 공식 문서: venv — https://docs.python.org/3/library/venv.html
- Python Packaging User Guide: pip — https://packaging.python.org/en/latest/tutorials/installing-packages/
- pyenv — https://github.com/pyenv/pyenv
- Real Python: Python Virtual Environments Primer — https://realpython.com/python-virtual-environments-a-primer/

<!-- toc:begin -->
<!-- toc:end -->

Tags: Python, install, venv, pip, version, beginner
