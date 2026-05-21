---
title: "Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv"
series: python-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Python
- virtual-environments
- environment-isolation
- python-installation
- package-management
- developer-setup
last_reviewed: '2026-05-12'
seo_description: Python은 한 대의 컴퓨터에 여러 개가 동시에 존재할 수 있고, 각 프로젝트는 자기만의 Python을 하나씩 들고
  있어야 합니다.
---

# Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv

Python은 한 대의 컴퓨터에 여러 개가 동시에 존재할 수 있고, 각 프로젝트는 자기만의 Python을 하나씩 들고 있어야 합니다.

이 글은 Python 101 시리즈의 첫 번째 글입니다.

## 먼저 던지는 질문

- 왜 Python인가, 그리고 설치와 venv를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- 왜 Python인가, 그리고 설치와 venv에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- 왜 Python인가, 그리고 설치와 venv를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 큰 그림

![Python 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-101/01/01-01-mental-model.ko.png)

*Python 101 1장 흐름 개요*

이 그림에서는 왜 Python인가, 그리고 설치와 venv를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 왜 Python인가, 그리고 설치와 venv의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 멘탈 모델

> Python은 한 대의 컴퓨터에 여러 개가 동시에 존재할 수 있고, 각 프로젝트는 자기만의 Python을 하나씩 들고 있어야 합니다.

이 한 문장이 이 글의 핵심입니다.

- system Python: OS가 쓰는 Python입니다. 건드리지 않습니다.
- project Python (venv): 프로젝트 폴더 안에 만든 사본입니다. 여기에만 패키지를 설치합니다.
- 프로젝트가 10개면 venv도 10개가 됩니다. 서로 영향을 주지 않습니다.

system Python은 OS의 영역, 각 venv는 프로젝트의 영역입니다. 개발자는 venv만 활성화해서 그 안에서 작업합니다.

## 핵심 개념

**1. Python의 종류**

- **CPython**: 공식 Python 구현체. python.org에서 받는 것이 이것이고, 거의 모든 자료가 CPython 기준으로 쓰여 있습니다. 이 글도 CPython 3.12를 가정합니다.
- **system Python**: OS에 미리 깔려 있는 Python. macOS와 Linux에 보통 있습니다. 버전이 낮고, 건드리면 OS가 영향을 받습니다.
- **user-installed Python**: python.org 설치 파일, Homebrew, pyenv, uv 등으로 직접 설치한 Python. 우리가 쓸 것은 이쪽입니다.

**2. `python` vs `python3`**

명령어가 두 개 있어서 처음에는 헷갈립니다. 규칙은 단순합니다.

- macOS와 Linux에서는 `python3`이 Python 3을 가리킵니다. `python`은 존재하지 않거나, 옛날 Python 2를 가리킬 수 있어서 위험합니다. 그래서 **shell에서는 항상 `python3`을 사용합니다.**
- Windows의 공식 설치 파일은 `python` (그리고 launcher인 `py`) 명령을 만듭니다. `python3`이 없을 수 있습니다.
- venv를 활성화한 뒤에는 어느 OS든 그냥 `python`을 써도 됩니다 — 활성화된 venv의 Python을 가리키기 때문입니다.

이 글에서는 venv 활성화 전에는 `python3` (Windows에서는 `py -3`), 활성화 후에는 `python`을 쓰겠습니다.

**3. venv (virtual environment)**

venv는 Python 표준 라이브러리에 내장된 도구입니다. `python3.12 -m venv .venv`처럼 버전을 명시해서 실행하면 `.venv/`라는 폴더가 생깁니다 (이 글에서는 일관되게 버전을 명시한 형태를 사용합니다 — 이유는 "자주 하는 실수 6" 참조). 그 안에는 Python 인터프리터의 사본 (혹은 링크), 그리고 비어 있는 `site-packages/` 폴더가 들어 있습니다. 활성화하면 `python`과 `pip` 명령이 그 venv 내부의 것을 가리키게 됩니다. 비활성화하면 system 환경으로 되돌아갑니다.

**4. pip와 requirements.txt**

`pip`는 Python의 패키지 관리자입니다. `pip install requests`처럼 사용하면 활성화된 venv의 `site-packages/`에 패키지를 설치합니다. `pip freeze > requirements.txt`로 현재 설치 상태를 파일로 저장하고, 다른 사람은 `pip install -r requirements.txt`로 같은 환경을 재현합니다. 이것이 협업과 배포의 기본 단위입니다.

## 전후 비교

**Before — system Python에 직접 설치한 경우**

```bash
$ pip install requests
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
$ sudo pip install requests   # please don't
```

`sudo pip install`은 일시적으로 동작하는 듯 보이지만, system Python을 오염시킵니다. 다음 OS 업데이트나 brew 명령이 실패할 수 있습니다.

**After — venv 안에 설치한 경우**

```bash
$ python3.12 -m venv .venv
$ source .venv/bin/activate         # macOS/Linux
(.venv) $ pip install requests
Successfully installed requests-2.32.3
(.venv) $ which python
/Users/me/myproj/.venv/bin/python
```

`(.venv)` 프롬프트가 나타나고, `which python`이 프로젝트 폴더 안을 가리킵니다. 이 상태에서 설치한 모든 패키지는 `.venv/` 안에만 들어가고, 프로젝트를 지우면 깨끗하게 사라집니다.

## 단계별 실습

### 1) Python 3.12 설치

**macOS** (Homebrew 사용):

```bash
brew install python@3.12
python3.12 --version
# Python 3.12.x
```

**Windows** (python.org 설치 파일):

1. https://www.python.org/downloads/ 에서 Python 3.12 installer를 받습니다.
2. 설치 화면에서 **"Add python.exe to PATH"**를 반드시 체크합니다.
3. 설치 후 PowerShell에서:

```powershell
py -3.12 --version
# Python 3.12.x
```

**Linux** (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install python3 python3-venv     # whichever Python 3 your distro ships
python3 --version
```

Debian 계열에서는 `python3-venv` 패키지를 같이 설치해야 venv를 만들 수 있습니다 (잊으면 venv 생성 시 오류가 납니다). 배포판이 제공하는 Python 버전이 3.12보다 낮다면, Ubuntu에서는 `deadsnakes` PPA를 추가해서 `python3.12`와 `python3.12-venv`를 설치하거나, pyenv·uv 같은 도구로 별도 설치하는 방법이 안전합니다. 시스템 Python 자체를 강제로 바꾸지 않는 점이 핵심입니다.

### 2) 프로젝트 폴더와 venv 만들기

```bash
mkdir hello-python && cd hello-python
python3.12 -m venv .venv
```

`.venv/` 폴더가 생깁니다. 이 폴더는 git에 커밋하지 않습니다 — 나중에 `.gitignore`에 `.venv/`를 추가하면 됩니다.

### 3) 활성화

**macOS / Linux**:

```bash
source .venv/bin/activate
```

**Windows PowerShell**:

```powershell
.\.venv\Scripts\Activate.ps1
```

만약 PowerShell에서 "이 시스템에서 스크립트를 실행할 수 없으므로..."라는 오류가 나면, 한 번만 다음 명령으로 사용자 정책을 풀어 주세요:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

활성화에 성공하면 프롬프트 앞에 `(.venv)`가 붙습니다.

### 4) 격리되었는지 검증

이 단계가 가장 중요합니다. 활성화만으로 끝내지 말고, **정말로 venv 안의 Python을 쓰고 있는지** 세 가지 명령으로 확인하세요.

macOS / Linux:

```bash
(.venv) $ which python
/Users/me/hello-python/.venv/bin/python

(.venv) $ python -c "import sys; print(sys.executable)"
/Users/me/hello-python/.venv/bin/python

(.venv) $ pip --version
pip 24.x from /Users/me/hello-python/.venv/lib/python3.12/site-packages/pip (python 3.12)
```

Windows:

```powershell
(.venv) PS> where python
C:\Users\me\hello-python\.venv\Scripts\python.exe

(.venv) PS> python -c "import sys; print(sys.executable)"
C:\Users\me\hello-python\.venv\Scripts\python.exe

(.venv) PS> pip --version
pip 24.x from C:\Users\me\hello-python\.venv\Lib\site-packages\pip (python 3.12)
```

세 명령 모두 `.venv` 안 경로를 가리키면 격리에 성공한 것입니다. 만약 system 경로(예: `/usr/bin/python`, `C:\Python312\python.exe`)가 나오면 활성화가 실패한 것이니, macOS/Linux는 `source .venv/bin/activate`로, Windows는 `.\.venv\Scripts\Activate.ps1`로 다시 시작하세요.

### 5) 첫 스크립트 (네트워크 없음)

처음에는 외부 패키지나 네트워크 없이, Python이 정말 동작하는지만 확인합니다. `hello.py`:

```python
import sys
import platform

print(f"Hello from Python {sys.version_info.major}.{sys.version_info.minor}")
print(f"Running on: {platform.system()} {platform.release()}")
print(f"Interpreter path: {sys.executable}")
```

실행:

```bash
(.venv) $ python hello.py
Hello from Python 3.12
Running on: Darwin 23.x.x
Interpreter path: /Users/me/hello-python/.venv/bin/python
```

이 출력이 나오면 venv 안의 Python이 정상적으로 코드를 실행하고 있습니다. 외부 의존성이 없으므로 Wi-Fi가 끊긴 상태에서도 동일하게 동작합니다.

### 6) 패키지 설치와 requirements.txt

이제 패키지를 하나 설치해 보겠습니다 (네트워크 필요):

```bash
(.venv) $ pip install requests
(.venv) $ pip freeze > requirements.txt
(.venv) $ cat requirements.txt
certifi==2024.x.x
charset-normalizer==3.x.x
idna==3.x
requests==2.32.3
urllib3==2.x.x
```

`requirements.txt`를 git에 커밋하면, 동료는 같은 명령으로 동일 환경을 재현할 수 있습니다:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 7) 비활성화

작업이 끝나면:

```bash
(.venv) $ deactivate
$
```

프롬프트에서 `(.venv)`가 사라지고 system 환경으로 돌아갑니다.

## 이 코드에서 주목할 점

- `python3.12 -m venv .venv` — 버전을 명시한 형태입니다. `python3 -m venv`만 쓰면 시스템에 여러 Python이 깔려 있을 때 어느 쪽을 가리키는지 모호해집니다.
- `which python` (Windows는 `where python`) — 활성화의 "진짜 검증"입니다. 프롬프트만 보고 안심하지 않고 명령으로 확인합니다.
- `pip freeze > requirements.txt` — 출력이 `requests==2.32.3`처럼 정확한 버전으로 박힙니다. 이것은 의도된 동작이며, 미래의 "갑자기 깨진다" 사고를 막는 첫 단계입니다.
- `import sys; print(sys.executable)` — venv 격리를 코드 수준에서 검증합니다. 셸이 거짓말할 수 있어도, Python 자체가 가리키는 인터프리터 경로는 거짓말할 수 없습니다.

## 자주 하는 실수

**1. `sudo pip install` 사용**
"권한이 없다"는 오류를 보면 `sudo`를 붙이고 싶어집니다. 절대 하지 마세요. 권한 오류 자체가 "지금 system Python을 건드리고 있다"는 신호입니다. 폴더로 들어가서 venv를 만들면 됩니다.

**2. `python` vs `python3` 혼용**
shell에서 `python`을 쳤을 때 어떤 Python이 나올지 예측할 수 없습니다. **venv 활성화 전에는 항상 `python3` (Windows에서는 `py -3`)** 을 쓰세요. 활성화 후에는 `python`을 써도 venv의 것을 가리킵니다.

**3. venv를 만들었는데 활성화하지 않음**
`python3.12 -m venv .venv`만 실행하고 `source .venv/bin/activate`를 잊는 경우가 흔합니다. 활성화 안 된 상태로 `pip install`을 하면 또다시 system Python에 설치됩니다. **`(.venv)` 프롬프트와 `which python` 결과를 항상 확인**하세요.

**4. PowerShell 활성화 실패를 "Python 문제"로 오해**
"스크립트를 실행할 수 없습니다" 오류는 Python 문제가 아니라 Windows 보안 정책입니다. `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`을 한 번 실행하면 해결됩니다.

**5. `.venv/`를 git에 커밋**
`.venv/`는 OS와 Python 버전에 의존하는 바이너리가 들어 있어서 다른 컴퓨터에서 그대로 쓸 수 없습니다. 반드시 `.gitignore`에 추가하고, 환경 재현은 `requirements.txt`로 합니다.

**6. `python3 -m venv` 대신 `python3.12 -m venv` 사용**
시스템에 Python 3.10과 3.12가 같이 깔려 있으면 `python3`이 어느 쪽을 가리키는지 모호합니다. **venv를 만들 때는 항상 버전을 명시**해서 `python3.12 -m venv .venv`처럼 쓰세요. 만들고 나면 그 venv는 영원히 그 버전에 묶입니다.

## 실무에서는 이렇게 생각합니다

**1. 프로젝트 폴더 표준 구조**

새 프로젝트를 시작할 때 항상 같은 모양으로 만듭니다:

```text
hello-python/
├── .venv/              # not committed
├── .gitignore          # includes .venv/ and __pycache__/
├── requirements.txt    # runtime dependencies
├── requirements-dev.txt # dev tools (pytest, ruff, etc.)
└── src/
    └── hello.py
```

이렇게 하면 어떤 프로젝트를 열어도 폴더 구조가 같아서 인지 부하가 줄어듭니다.

**2. requirements.txt를 두 개로 나누기**

`requirements.txt`에는 production에서도 필요한 패키지만 넣고, `requirements-dev.txt`에는 테스트와 lint 같은 개발용만 넣습니다. CI나 production 컨테이너에서 불필요한 패키지를 빼서 빌드를 가볍게 유지하기 위함입니다.

**3. 버전 고정 (pinning)**

`pip freeze`의 결과는 `requests==2.32.3`처럼 버전이 정확히 박혀 있습니다. 이것이 의도된 결과입니다. "어떤 버전이든 알아서"를 허용하면, 한 달 뒤 동일한 코드가 다른 버전으로 깔려서 갑자기 깨질 수 있습니다. 의존성은 명시적으로 고정하세요.

**4. Python 버전도 명시하기**

프로젝트 root에 `.python-version` 파일을 두고 `3.12`를 적어 두면, pyenv·uv·일부 IDE가 자동으로 그 버전을 선택합니다. 협업할 때 "Python 몇 버전 써요?"라는 질문이 사라집니다.

**5. uv·poetry는 나중에**

요즘 `uv`나 `poetry` 같은 더 빠르고 강력한 도구가 있습니다. 하지만 그 도구들도 내부적으로는 venv 개념 위에 동작합니다. 표준 venv + pip를 먼저 손에 익히면, 나중에 어떤 도구로 옮겨도 원리가 보입니다.

## 체크리스트

- [ ] Python 3.12를 설치하고 `python3.12 --version` (Windows는 `py -3.12 --version`)으로 확인했다
- [ ] 프로젝트 폴더에 `python3.12 -m venv .venv`로 venv를 만들었다
- [ ] 활성화 후 프롬프트에 `(.venv)`가 보인다
- [ ] `which python` (Windows는 `where python`)이 `.venv` 안 경로를 가리킨다
- [ ] `python -c "import sys; print(sys.executable)"`도 같은 경로를 출력한다
- [ ] `.gitignore`에 `.venv/`를 추가했다
- [ ] `pip install`로 설치한 뒤 `pip freeze > requirements.txt`로 저장했다
- [ ] 새 폴더에서 `pip install -r requirements.txt`로 환경을 재현해 보았다

## 정리

- system Python은 OS의 영역입니다. 절대 `pip install`하지 않습니다.
- 프로젝트마다 `python3.12 -m venv .venv`로 격리된 환경을 만듭니다.
- 활성화 후에는 `which python`으로 격리를 검증합니다 — 이 한 단계가 미래의 버그 절반을 막아줍니다.
- `pip freeze > requirements.txt`로 환경을 문서화하고, 동료는 `pip install -r requirements.txt`로 재현합니다.
- venv 안에서는 `python`을 그대로 써도 좋지만, 활성화 전에는 항상 `python3`을 사용합니다.

## 다음 글

다음 글에서는 변수, 타입, 연산자를 다룹니다. Python의 동적 타입이 무엇을 의미하는지, type hint가 왜 필요한지, 정수·실수·문자열·bool·None이 어떻게 다르게 동작하는지 짚어 봅니다.

## 실전 앵커: 설치 직후에 바로 보는 실행 환경과 인터프리터 내부

입문자가 가장 많이 겪는 문제는 문법이 아니라 실행 환경 불일치입니다. VS Code에서 실행한 결과와 터미널에서 실행한 결과가 다르면, 코드 자체보다 먼저 인터프리터 경로를 확인해야 합니다. 아래 점검 루틴을 팀 온보딩 문서에 넣어 두면 초반 시행착오를 크게 줄일 수 있습니다.

```bash
python --version
which python
python -c "import sys; print(sys.executable)"
python -c "import site; print(site.getsitepackages())"
```

실제 출력 예시는 다음처럼 해석합니다.

```text
$ python --version
Python 3.12.4

$ which python
~/.pyenv/shims/python

$ python -c "import sys; print(sys.executable)"
~/.pyenv/versions/3.12.4/bin/python
```

여기서 중요한 포인트는 `which python`과 `sys.executable`이 논리적으로 같은 런타임을 가리키는지입니다. 다르면 쉘 alias, IDE 인터프리터 설정, 가상환경 활성화 순서를 먼저 의심합니다.

CPython 관점에서도 설치 확인은 단순 버전 확인으로 끝나지 않습니다. 다음 한 줄은 현재 런타임의 구현체와 GIL 정보를 함께 확인하게 해 줍니다.

```python
import platform
import sys

print(platform.python_implementation())
print(sys.version)
print(sys.getswitchinterval())
```

`platform.python_implementation()`이 `CPython`이면, 우리가 이 시리즈에서 설명하는 참조 카운트(reference counting) 기반 메모리 관리 모델을 그대로 적용해서 이해할 수 있습니다. `sys.getswitchinterval()`은 스레드 전환 간격으로, GIL이 있는 CPython에서 CPU-bound 코드가 왜 선형 확장되지 않는지를 설명할 때 자주 쓰는 단서입니다.

REPL에서도 메모리 모델을 짧게 체험할 수 있습니다.

```pycon
>>> import sys
>>> a = []
>>> sys.getrefcount(a)
2
>>> b = a
>>> sys.getrefcount(a)
3
>>> del b
>>> sys.getrefcount(a)
2
```

`getrefcount` 값이 1씩 더 크게 보이는 이유는 함수 호출 인자 자체가 임시 참조를 만들기 때문입니다. 이런 작은 관찰이 나중에 함수 인자 전달, 얕은 복사/깊은 복사, 객체 수명 주기를 이해할 때 큰 차이를 만듭니다.

패키지 설치까지 확장하면 표준 점검표는 아래처럼 정리할 수 있습니다.

| 점검 항목 | 확인 명령 | 기대 결과 | 실패 시 대응 |
|---|---|---|---|
| 인터프리터 버전 | `python --version` | 3.11+ | pyenv/설치 버전 재선택 |
| pip 연결 | `python -m pip --version` | 같은 python 경로 | `python -m pip` 방식 고정 |
| venv 활성화 | `echo $VIRTUAL_ENV` | 경로 출력 | `source .venv/bin/activate` |
| 인코딩 | `python -c "import sys; print(sys.getdefaultencoding())"` | utf-8 | 쉘 locale/터미널 설정 점검 |

입문 단계에서 이 표를 귀찮아하면 이후 모든 디버깅 비용이 커집니다. 반대로 처음 한 번만 정확히 정렬해 두면, 시리즈 후반의 모듈/패키지, 테스트, 배포 주제를 훨씬 안정적으로 따라갈 수 있습니다.

### 추가 실습: 환경 불일치를 5분 안에 찾는 체크리스트

설치가 끝난 뒤 바로 프로젝트를 시작하기 전에, 아래 명령을 한 번 실행해 두면 이후 오류의 절반을 예방할 수 있습니다.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ipython
python -c "import sys, platform; print(sys.executable); print(platform.platform())"
```

출력으로 확보해야 하는 사실은 세 가지입니다. 첫째, 실행 파일 경로가 프로젝트 내부 가상환경인지. 둘째, pip가 같은 경로의 python에 연결되는지. 셋째, 운영체제/아키텍처 정보가 팀 문서와 일치하는지입니다.

```text
$ python -m pip --version
pip 25.0 from /project/.venv/lib/python3.12/site-packages/pip (python 3.12)
```

이런 확인을 루틴으로 만들면 "왜 제 컴퓨터에서만 안 돼요"라는 질문이 훨씬 줄어듭니다.

### 부록: 로컬 실습 로그 템플릿

아래 템플릿은 학습 단계에서 직접 실험한 결과를 남길 때 유용합니다. 중요한 점은 "코드 + 실행 환경 + 출력"을 한 세트로 기록하는 것입니다. 이렇게 남긴 로그는 나중에 문제가 다시 발생했을 때 가장 신뢰할 수 있는 재현 자료가 됩니다.

```text
[환경]
python: 3.12.x
platform: macOS/Linux
venv: .venv

[실험]
목표: 동작 확인 또는 성능 비교
입력: 샘플 데이터 1,000건
실행 명령: python script.py

[출력]
성공/실패 여부
핵심 숫자(timeit, 처리 건수, 예외 메시지)
```

실무 코드 리뷰에서는 결과 숫자만 공유하는 경우가 많지만, 학습 단계에서는 중간 가정까지 함께 적는 편이 더 효과적입니다. 예를 들어 "셋 포함 검사가 빠를 것이다"라는 가정이 맞았는지, "f-string이 항상 더 읽기 쉽다"라는 판단이 팀 컨벤션과 맞는지까지 기록하면 다음 의사결정이 빨라집니다.

디버깅 기록도 같은 형식을 쓰면 좋습니다.

1) 증상: 어떤 입력에서 실패했는가
2) 가설: 어떤 조건문/자료구조/경로가 원인인가
3) 검증: `pdb`, `print`, `timeit`, 단위 테스트 중 무엇으로 확인했는가
4) 결론: 수정 전후 동작 차이가 무엇인가

이 습관은 초급 단계에서는 다소 느리게 느껴질 수 있습니다. 하지만 프로젝트 규모가 커질수록 "정확한 기록"이 가장 빠른 길이 됩니다. Python 문법을 익히는 것과 별개로, 실험을 재현 가능한 형태로 남기는 역량은 개발자로서의 성장 속도를 결정합니다.

## 처음 질문으로 돌아가기

- **왜 Python인가, 그리고 설치와 venv를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 왜 Python인가, 그리고 설치와 venv를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 Python인가, 그리고 설치와 venv에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 Python인가, 그리고 설치와 venv를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **왜 Python인가, 그리고 설치와 venv (현재 글)**
- 변수, 타입, 연산자 (예정)
- 문자열과 포매팅 (예정)
- list, tuple, set, dict (예정)
- 제어 흐름: if, for, while, comprehension (예정)
- 함수와 인자: def, args, kwargs, default, lambda (예정)
- 모듈과 패키지: import, __init__, __name__ (예정)
- 파일 I/O와 예외 처리 (예정)
- 클래스와 객체: 데이터와 동작을 함께 묶기 (예정)
- 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — venv](https://docs.python.org/3/library/venv.html) — `python -m venv`, 활성화 스크립트, 격리 원리를 직접 확인할 수 있습니다.
- [PEP 405 — Python Virtual Environments](https://peps.python.org/pep-0405/) — venv가 `sys.prefix`와 site-packages를 어떻게 분리하는지 배경 설명을 제공합니다.
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/) — `python -m pip`, `-r requirements.txt`, `pip freeze` 같은 실무 명령의 기준 문서입니다.
- [Python Packaging User Guide — Install packages in a virtual environment using pip and venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) — 프로젝트별 `.venv` 생성·활성화·설치 흐름을 단계별로 정리합니다.
- [Python.org Downloads](https://www.python.org/downloads/) — 공식 설치 경로와 지원 버전 확인에 적합합니다.
- [Python 공식 문서 — Using Python on Windows](https://docs.python.org/3/using/windows.html) — Windows에서 `python`/`py` 명령, 설치 관리자, venv 사용 규칙을 확인할 수 있습니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-101/ko)
Tags: Python, virtual-environments, environment-isolation, python-installation, package-management, developer-setup
