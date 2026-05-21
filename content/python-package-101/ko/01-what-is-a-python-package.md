---
title: "Python Package 101 (1/10): Python Package란 무엇인가?"
series: python-package-101
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
- Package
- Module
- Import
- pip
- Library
last_reviewed: '2026-05-15'
seo_description: Python 패키지는 재사용 가능한 코드를 묶어 다른 사람과 공유하는 단위입니다. import로 불러오는 모든 것이 패키지입니다.
---

# Python Package 101 (1/10): Python Package란 무엇인가?

프로젝트가 조금만 커져도 파일을 여러 개로 나누고, 다른 파일의 코드를 `import`해서 쓰게 됩니다. 여기서부터 Python 패키징의 기본 개념이 시작됩니다.

이 글은 Python Package 101 시리즈의 첫 번째 글입니다. 여기서는 모듈, 패키지, 배포판이 각각 무엇이고 `pip install`이 실제로 무엇을 설치하는지, 그리고 왜 여러분의 코드를 패키지로 만들어야 하는지를 먼저 정리하겠습니다.

![Python Package 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/01/01-01-mental-model.ko.png)
*Python Package 101 1장 흐름 개요*

## 먼저 던지는 질문

- 모듈과 패키지는 정확히 무엇이 다를까요?
- `import requests`를 실행하면 내부에서는 어떤 일이 일어날까요?
- `pip install`은 실제로 무엇을 설치할까요?

## 이 글에서 배우는 내용

- 모듈, 패키지, 라이브러리, 배포판의 차이
- Python이 `sys.path`를 따라 모듈을 찾는 방식
- `pip install`이 패키지를 설치하는 위치와 동작 방식
- 내 코드를 패키지로 묶어야 하는 시점

## 왜 중요한가

프로젝트가 커지면 파일을 여러 개로 나누고 서로 `import`하게 됩니다. 그것이 모듈이고, 모듈을 묶으면 패키지입니다. 문제는 공통 코드를 프로젝트마다 복사해서 쓰기 시작할 때 생깁니다. 버그 하나를 고치려면 모든 복사본을 다시 수정해야 하고, 한 군데라도 놓치면 운영에서 다른 결과가 나옵니다.

> 같은 유틸리티 함수를 프로젝트 세 개에 복사해서 쓰고 있다고 가정해 보겠습니다. 버그를 발견해 두 군데만 고쳤고, 세 번째 프로젝트는 그대로 배포되었습니다. 결국 수정하지 않은 복사본이 프로덕션 장애를 일으킵니다.

이 코드를 패키지로 만들면 고치는 곳은 한 군데로 줄어듭니다. 이후 각 프로젝트에서는 `pip install --upgrade`만 다시 실행하면 같은 수정 사항을 일관되게 반영할 수 있습니다.

## 멘탈 모델

Python 패키지는 레고 세트에 가깝습니다. 블록 하나는 특정 기능을 담은 모듈이고, 여러 블록을 묶은 세트가 패키지입니다. 그 세트를 매장(PyPI)에 올리면 다른 사람도 내려받아 그대로 쓸 수 있습니다.

```text
Module              Package                  Distribution
──────              ───────                  ────────────
utils.py    ->     mylib/               ->  mylib-1.0.0.tar.gz
                     __init__.py             (uploaded to PyPI)
                     utils.py
                     models.py
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 모듈(module) | 하나의 `.py` 파일 | `utils.py` |
| 패키지(package) | `__init__.py`가 있는 디렉터리 | `mylib/` |
| 라이브러리(library) | 패키지를 가리키는 비공식 표현 | `requests`, `flask` |
| 배포판(distribution) | 설치 가능한 아카이브 | `mylib-1.0.0.tar.gz` |
| PyPI | Python Package Index, 패키지 저장소 | pypi.org |

## 적용 전후 비교
**Before (복사-붙여넣기 코드)**

```text
project-a/utils.py   # copy 1
project-b/utils.py   # copy 2
project-c/utils.py   # copy 3
# -> Fix a bug? Edit all three.
```

**After (패키지화)**

```text
mylib/               # one package
  utils.py

project-a/           # pip install mylib
project-b/           # pip install mylib
project-c/           # pip install mylib
# -> Fix mylib once, pip install --upgrade everywhere
```

## 단계별 실습

### 단계 1. 모듈 만들기

```python
# ~/practice/python-pkg/calculator.py
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b
```

```python
# ~/practice/python-pkg/main.py
from calculator import add, subtract

print(add(3, 5))        # 8
print(subtract(10, 4))  # 6
```

### 단계 2. 패키지 구조 만들기

```bash
mkdir -p ~/practice/python-pkg/mymath
cat > ~/practice/python-pkg/mymath/__init__.py << 'EOF'
from .calculator import add, subtract
EOF

cat > ~/practice/python-pkg/mymath/calculator.py << 'EOF'
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b
EOF
```

```python
# ~/practice/python-pkg/main.py
from mymath import add, subtract

print(add(3, 5))        # 8
```

### 단계 3. `sys.path` 확인

```python
import sys
for path in sys.path:
    print(path)
# '' (current directory)
# /usr/lib/python3.11
# /usr/lib/python3.11/lib-dynload
# /home/user/.local/lib/python3.11/site-packages
```

### 단계 4. 설치된 패키지 확인

```bash
pip list                          # List installed packages
pip show requests                 # Details for requests
pip show requests | grep Location # Installation path
# Location: /home/user/.local/lib/python3.11/site-packages
```

### 단계 5. 설치된 패키지 내부 확인

```bash
python -c "import requests; print(requests.__file__)"
# /home/user/.local/lib/python3.11/site-packages/requests/__init__.py

ls /home/user/.local/lib/python3.11/site-packages/requests/
# __init__.py  api.py  models.py  sessions.py  ...
```

## 이 코드에서 눈여겨볼 점

- `__init__.py`가 있으면 Python은 그 디렉터리를 패키지로 취급합니다.
- `from .calculator import add`에서 `.`은 현재 패키지를 가리키는 상대 임포트입니다.
- `sys.path`의 순서가 곧 모듈 검색 우선순위입니다.
- `pip install`은 결국 패키지 파일을 `site-packages/` 아래에 복사하는 작업입니다.

## 자주 하는 실수

### 실수 1. `__init__.py`를 빼먹는다

Python 3.3+에서는 `__init__.py`가 없어도 namespace package로 동작할 수 있습니다. 하지만 명시적으로 넣는 편이 여전히 가장 안전한 관례입니다. 일부 도구는 이 파일이 없으면 패키지를 제대로 인식하지 못합니다.

### 실수 2. 표준 라이브러리와 같은 이름을 쓴다

```python
# email.py를 생성하면
import email  # Your file shadows the standard library
```

`random.py`, `json.py`, `os.py`처럼 표준 라이브러리와 충돌하는 이름은 피하는 편이 좋습니다.

### 실수 3. 순환 임포트를 만든다

```python
# a.py: b에서 가져오기 func_b
# b.py: 가져오기 func_a에서
# -> ImportError
```

의존 방향을 한쪽으로 유지하거나, 공통 코드를 별도 모듈로 분리해야 합니다.

### 실수 4. `site-packages`를 직접 수정한다

설치된 패키지 파일을 직접 고쳐도 다음 `pip install`에서 쉽게 덮어써집니다. 수정이 필요하다면 원본 프로젝트를 고치고 다시 빌드·배포하는 흐름으로 가져가야 합니다.

### 실수 5. 하이픈과 언더스코어를 혼동한다

```bash
pip install my-package      # Install name: hyphen
import my_package           # Import name: underscore
```

설치 이름과 import 이름이 다를 수 있다는 점을 초반에 익혀 두는 편이 좋습니다.

## 실무 적용

- **사내 공통 라이브러리**: 인증, 로깅, 설정 관리를 하나의 패키지로 통일합니다.
- **마이크로서비스 공유 코드**: gRPC 스텁과 데이터 모델을 패키지로 배포합니다.
- **CLI 도구**: `pip install` 후 바로 실행되는 터미널 명령으로 배포할 수 있습니다.
- **오픈소스**: PyPI에 올리면 누구나 `pip install`로 설치할 수 있습니다.
- **테스트 유틸리티 공유**: 여러 프로젝트에서 쓰는 픽스처와 헬퍼를 공용 패키지로 묶습니다.

## 실무에서는 이렇게 생각합니다

실무에서는 보통 이렇게 질문합니다. “이 코드가 두 개 이상의 프로젝트에서 쓰이는가?” 그렇다면 패키지로 만들 시점이라고 보는 편이 맞습니다. 복사해서 쓰는 구조는 프로젝트 수만큼 유지보수 비용이 선형으로 증가하지만, 패키지는 변경 지점을 한곳으로 모으고 버전으로 안정성을 관리하게 해 줍니다.

처음에는 패키징이 과한 절차처럼 보일 수 있습니다. 하지만 실제로는 `pyproject.toml` 하나로 시작할 수 있고, 이후 빌드·배포 자동화까지 자연스럽게 확장됩니다. 이 시리즈는 그 흐름을 단계적으로 익히도록 구성되어 있습니다.

## 체크리스트

- [ ] 모듈, 패키지, 배포판의 차이를 설명할 수 있다
- [ ] `__init__.py`의 역할을 이해한다
- [ ] `sys.path`로 모듈 검색 경로를 확인할 수 있다
- [ ] `pip show`로 패키지 설치 위치를 찾을 수 있다
- [ ] 코드를 패키지로 묶어야 할 시점을 판단할 수 있다

## 연습 문제

1. `multiply`와 `divide` 함수를 가진 `mymath/` 패키지를 만들고, `main.py`에서 이를 import해 보세요.
2. `sys.path`를 출력하고, `site-packages` 안에 설치된 패키지 하나의 디렉터리 구조를 직접 살펴보세요.
3. `string.py`라는 파일을 만든 뒤 `import string`을 실행해 어떤 일이 일어나는지 확인해 보세요.

## 정리 · 다음 글

- 모듈은 `.py` 파일이고, 패키지는 `__init__.py`가 있는 디렉터리입니다.
- Python은 `sys.path` 순서대로 모듈을 찾습니다.
- `pip install`은 패키지 파일을 `site-packages/`에 설치합니다.
- 두 개 이상의 프로젝트에서 쓰이는 코드는 패키지로 만드는 편이 낫습니다.
- 패키지 이름은 표준 라이브러리와 충돌하지 않아야 합니다.

다음 글에서는 **프로젝트 구조** — src layout과 `pyproject.toml`을 다룹니다.

## import 시스템 내부 동작

`import requests`를 실행하면 Python 인터프리터는 다음 순서로 작업합니다.

### 1단계: sys.modules 캐시 확인

```python
import sys

# 이미 import한 모듈은 캐시에 저장됩니다.
print("requests" in sys.modules)  # 첫 import 전: False

import requests
print("requests" in sys.modules)  # import 후: True

# 두 번째 import는 캐시에서 즉시 반환합니다.
import requests  # 파일을 다시 읽지 않음
```

Python은 `sys.modules` 딕셔너리에서 먼저 모듈을 찾습니다. 이미 있으면 파일 시스템을 탐색하지 않고 캐시된 모듈 객체를 그대로 반환합니다. 이 때문에 모듈 최상위에 있는 코드는 프로세스 생애에서 단 한 번만 실행됩니다.

### 2단계: Finder와 Loader

```python
import sys

for finder in sys.meta_path:
    print(type(finder).__name__)
# 내장 임포터(BuiltinImporter) - 내장 모듈(sys, 내장)
# FrozenImporter       - 프리즈된 모듈
# PathFinder - sys.path 기반 탐색
```

`sys.meta_path`에 등록된 finder가 순서대로 모듈을 찾습니다. `PathFinder`가 가장 마지막에 동작하며, `sys.path`의 각 경로를 순회하면서 `.py` 파일이나 패키지 디렉터리를 찾습니다.

### 3단계: 모듈 실행과 바인딩

```python
# Python이 내부적으로 수행하는 과정을 단순화하면:
# 1. 빈 모듈 객체 생성
# 2. sys.modules에 등록 (순환 임포트 방지)
# 3. 모듈 파일 실행 (.py의 최상위 코드)
# 4. 호출자의 네임스페이스에 이름 바인딩

# 이것이 의미하는 바:
import mylib          # mylib 이름이 현재 네임스페이스에 바인딩
from mylib import f   # f 이름만 바인딩, mylib은 바인딩되지 않음
```

### import 흐름 전체 다이어그램

```text
import mylib
    │
    ▼
sys.modules에 있는가? ──Yes──> 캐시된 객체 반환
    │ No
    ▼
sys.meta_path의 finder 순회
    │
    ▼
PathFinder: sys.path 각 경로 탐색
    │
    ▼
mylib/ 디렉터리 발견 (__init__.py 존재)
    │
    ▼
모듈 객체 생성 → sys.modules 등록
    │
    ▼
__init__.py 실행
    │
    ▼
호출자 네임스페이스에 'mylib' 바인딩
```

## 네임스페이스 패키지 대 일반 패키지

Python 3.3부터 `__init__.py`가 없어도 디렉터리를 패키지로 인식하는 namespace package가 도입되었습니다. 하지만 두 방식은 동작이 다릅니다.

| 구분 | Regular Package | Namespace Package |
|---|---|---|
| `__init__.py` | 필수 | 없음 |
| `__path__` | 단일 디렉터리 | 여러 디렉터리 가능 |
| 초기화 코드 | `__init__.py`에 작성 | 불가 |
| 도구 호환성 | 모든 도구 지원 | 일부 도구 미지원 |
| 용도 | 일반 패키지 | 플러그인, 분산 패키지 |

```python
# 일반 패키지: mylib/__init__.py 존재
import mylib
print(mylib.__file__)
# /home/user/.local/lib/python3.11/site-packages/mylib/__init__.py

# 네임스페이스 패키지: __init__.py 없음
import google.cloud  # google은 namespace package
print(google.__path__)
# _NamespacePath(['/path/to/site-packages/google'])
# 여러 배포판이 google/ 아래 하위 패키지를 각각 설치
```

실무에서 namespace package를 사용하는 대표 사례는 `google-cloud-*` 패키지 군입니다. `google.cloud.storage`와 `google.cloud.bigquery`는 별도 배포판이지만 동일한 `google.cloud` namespace를 공유합니다.

**권장**: 대부분의 프로젝트에서는 Regular Package(`__init__.py` 포함)를 사용하는 것이 명확합니다. Namespace Package는 여러 독립 배포판이 하나의 최상위 네임스페이스를 공유해야 할 때만 선택합니다.

## `__init__.py` 활용 패턴

`__init__.py`는 단순히 "이 디렉터리는 패키지입니다"를 선언하는 것 이상의 역할을 합니다.

### 패턴 1: Public API 정의

```python
# mylib/__init__.py
from .core import Engine
from .config import Settings
from .exceptions import MyLibError

__all__ = ["Engine", "Settings", "MyLibError"]
```

사용자는 `from mylib import Engine`으로 바로 접근할 수 있고, 내부 구현 파일(`core.py`, `config.py`)은 숨겨집니다. `__all__`을 명시하면 `from mylib import *` 시 노출되는 이름을 제어합니다.

### 패턴 2: 버전 정보 제공

```python
# mylib/__init__.py
__version__ = "1.2.0"
```

```python
import mylib
print(mylib.__version__)  # "1.2.0"
```

### 패턴 3: 빈 파일로 두기

```python
# mylib/__init__.py
# (비어 있음)
```

패키지가 깊은 구조를 가지고 있고, 사용자가 하위 모듈을 직접 import하는 경우에는 `__init__.py`를 비워 두는 것이 가장 단순합니다. Django의 `migrations/` 패키지가 이 패턴을 사용합니다.

### 패턴 4: Lazy Import

```python
# mylib/__init__.py
def __getattr__(name):
    if name == "HeavyModule":
        from .heavy import HeavyModule
        return HeavyModule
    raise AttributeError(f"module 'mylib' has no attribute {name}")
```

무거운 의존성을 가진 하위 모듈을 실제로 접근할 때까지 로드를 미루는 방식입니다. `import mylib`만으로는 `heavy.py`가 실행되지 않습니다.

## Wheel 내부 구조

`pip install`이 설치하는 대상은 대부분 wheel(`.whl`) 파일입니다. wheel은 단순한 ZIP 파일이며 내부 구조가 정해져 있습니다.

```bash
# wheel 파일의 실체 확인
pip download requests --no-deps -d /tmp/wheels
unzip -l /tmp/wheels/requests-2.32.3-py3-none-any.whl | head -20
```

```text
requests-2.32.3-py3-none-any.whl 내부:
├── requests/
│   ├── __init__.py
│   ├── api.py
│   ├── sessions.py
│   ├── models.py
│   └── ...
├── requests-2.32.3.dist-info/
│   ├── METADATA        # 패키지 메타데이터 (이름, 버전, 의존성)
│   ├── WHEEL           # wheel 형식 정보
│   ├── RECORD          # 설치될 파일 목록 + 해시
│   ├── top_level.txt   # 최상위 패키지 이름
│   └── LICENSE
```

### Wheel 파일 이름 규칙

```text
{distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl

예시:
requests-2.32.3-py3-none-any.whl
├── distribution: requests
├── version: 2.32.3
├── python: py3 (Python 3)
├── abi: none (순수 Python)
└── platform: any (모든 플랫폼)

numpy-1.26.4-cp312-cp312-manylinux_2_17_x86_64.whl
├── distribution: numpy
├── version: 1.26.4
├── python: cp312 (CPython 3.12)
├── abi: cp312 (CPython 3.12 ABI)
└── platform: manylinux_2_17_x86_64 (Linux x86_64)
```

순수 Python 패키지는 `py3-none-any`로 모든 환경에서 동일한 wheel을 사용합니다. C 확장을 포함하는 패키지는 플랫폼별로 별도 wheel이 필요합니다.

## Editable Install 동작 원리

개발 중에는 `pip install -e .`(editable install)을 사용합니다. 이 모드에서는 소스 코드를 `site-packages`에 복사하지 않고, 원본 디렉터리를 직접 참조합니다.

```bash
# 일반 설치: 파일이 site-packages로 복사됨
pip install .
# site-packages/mylib/__init__.py (복사본)

# Editable 설치: 원본을 참조하는 링크가 생성됨
pip install -e .
# site-packages/mylib.egg-link 또는
# site-packages/__editable__.mylib-0.1.0.pth
```

```python
# editable install 후
import mylib
print(mylib.__file__)
# /home/user/projects/mylib/src/mylib/__init__.py (원본 번역!)
```

editable install의 장점은 소스를 수정하면 다시 설치하지 않아도 변경이 즉시 반영된다는 것입니다. 개발-테스트 사이클이 빨라집니다.

### 모던 Editable Install (PEP 660)

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

```bash
pip install -e .
# setuptools >= 64는 .pth 파일 방식으로 editable install 수행
# import hook 없이도 src/ 레이아웃을 정상 인식
```

## 패키지 이름 짓기: 충돌을 피하는 전략

PyPI에는 50만 개 이상의 패키지가 등록되어 있습니다. 이름 충돌을 피하면서도 찾기 쉬운 이름을 짓는 것이 중요합니다.

### 이름 규칙

| 규칙 | 예시 |
|---|---|
| 소문자 + 하이픈 (배포 이름) | `my-utils` |
| 소문자 + 언더스코어 (import 이름) | `my_utils` |
| PyPI에서 정규화 | `my-utils` == `my_utils` == `My.Utils` |
| 3글자 이상 권장 | `io`보다 `fileio` |

### 사내 패키지 네이밍 패턴

```text
{회사/조직}-{도메인}-{기능}
예: acme-auth-client, acme-logging, acme-config
```

접두사를 통일하면 `pip list | grep acme-`로 사내 패키지를 한눈에 파악할 수 있습니다.

### PyPI 이름 선점 확인

```bash
# 이름이 사용 가능한지 확인
pip index versions my-desired-name
# ERROR: No matching distribution found -> 사용 가능

# 또는 API로 확인
curl -s https://pypi.org/pypi/my-desired-name/json | python -m json.tool
# 404 -> 사용 가능
```

## pip install 전체 흐름

`pip install requests`를 실행하면 실제로 어떤 단계를 거치는지 살펴보겠습니다.

```text
pip install requests
    │
    ▼
1. PyPI API 호출: GET https://pypi.org/simple/requests/
    │
    ▼
2. 호환 wheel 선택 (Python 버전, 플랫폼 기준)
    │
    ▼
3. wheel 다운로드 + 해시 검증
    │
    ▼
4. 의존성 해결 (urllib3, certifi, charset-normalizer, idna)
    │
    ▼
5. 의존성도 같은 과정으로 설치
    │
    ▼
6. wheel 압축 해제 → site-packages/에 파일 배치
    │
    ▼
7. .dist-info/ 디렉터리 생성 (METADATA, RECORD 등)
```

### 의존성 해결기 (Resolver)

pip 20.3부터 새로운 의존성 해결기가 기본으로 동작합니다. 이 해결기는 모든 패키지의 버전 요구 사항이 동시에 만족되는 조합을 찾습니다.

```bash
# 의존성 트리 확인
pip install pipdeptree
pipdeptree -p requests
```

```text
requests==2.32.3
├── certifi [required: >=2017.4.17, installed: 2024.7.4]
├── charset-normalizer [required: >=2,<4, installed: 3.3.2]
├── idna [required: >=2.5,<4, installed: 3.7]
└── urllib3 [required: >=1.21.1,<3, installed: 2.2.2]
```

### site-packages 설치 후 디렉터리 상태

```bash
ls site-packages/ | grep -E "requests|urllib3"
```

```text
requests/
requests-2.32.3.dist-info/
urllib3/
urllib3-2.2.2.dist-info/
```

각 패키지마다 두 개의 디렉터리가 생깁니다. 하나는 실제 코드가 담긴 패키지 디렉터리이고, 다른 하나는 메타데이터를 담는 `.dist-info/` 디렉터리입니다.

### RECORD 파일: 설치된 파일 목록

```bash
head -5 site-packages/requests-2.32.3.dist-info/RECORD
```

```text
requests/__init__.py,sha256=abc123...,4567
requests/api.py,sha256=def456...,2345
requests/sessions.py,sha256=ghi789...,12345
requests/models.py,sha256=jkl012...,23456
requests/adapters.py,sha256=mno345...,8901
```

`pip uninstall requests`를 실행하면 pip은 이 RECORD 파일을 읽어서 설치된 모든 파일을 정확히 제거합니다.

## 모듈 검색 순서가 만드는 함정

`sys.path`의 순서는 실질적인 우선순위입니다. 이 순서를 이해하지 못하면 의도치 않은 모듈이 import될 수 있습니다.

```python
import sys
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")
```

```text
0:                          # 빈 문자열 = 현재 디렉터리 (최우선)
1: /usr/lib/python3.11
2: /usr/lib/python3.11/lib-dynload
3: /home/user/.local/lib/python3.11/site-packages
4: /usr/lib/python3.11/site-packages
```

### Shadow Import 문제

```bash
# 현재 디렉터리에 random.py를 만들면:
echo "print('This is NOT the stdlib random!')" > random.py
python -c "import random; print(random.randint(1, 10))"
# This is NOT the stdlib random!
# AttributeError: module 'random' has no attribute 'randint'
```

현재 디렉터리(`sys.path[0]`)가 표준 라이브러리보다 먼저 탐색되기 때문입니다. 이 문제는 파일명만 바꾸면 해결됩니다.

### 권장 확인 습관

```python
# 어떤 모듈이 실제로 로드되었는지 확인
import json
print(json.__file__)  # /usr/lib/python3.11/json/__init__.py 이면 정상

# 의심스러우면 spec 확인
import importlib.util
spec = importlib.util.find_spec("json")
print(spec.origin)
```

## 처음 질문으로 돌아가기

- **모듈과 패키지는 정확히 무엇이 다를까요?**
  - 모듈은 하나의 `.py` 파일이고, 패키지는 `__init__.py`가 있는 디렉터리입니다. 패키지는 여러 모듈을 하나의 네임스페이스로 묶어서 계층 구조를 만들 수 있게 합니다. `import json`은 모듈 하나를 가져오는 것이고, `import requests`는 패키지 전체(디렉터리)를 가져오는 것입니다.

- **`import requests`를 실행하면 내부에서는 어떤 일이 일어날까요?**
  - Python은 먼저 `sys.modules` 캐시를 확인합니다. 없으면 `sys.meta_path`의 finder들이 순서대로 모듈을 탐색하고, `PathFinder`가 `sys.path`의 각 경로에서 `requests/` 디렉터리를 찾습니다. 디렉터리를 발견하면 모듈 객체를 생성하고, `__init__.py`를 실행한 뒤, 호출자의 네임스페이스에 `requests`라는 이름을 바인딩합니다.

- **`pip install`은 실제로 무엇을 설치할까요?**
  - `pip install`은 PyPI에서 wheel(`.whl`) 파일을 다운로드하고, 그 안에 들어 있는 패키지 파일을 `site-packages/` 디렉터리에 풀어 놓습니다. 동시에 `.dist-info/` 디렉터리를 생성하여 메타데이터, 설치된 파일 목록, 의존성 정보를 기록합니다. 이후 `import`할 때 `site-packages/`는 `sys.path`에 포함되어 있으므로 바로 찾을 수 있게 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- **Python Package 101 (1/10): Python Package란 무엇인가? (현재 글)**
- Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml (예정)
- Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements (예정)
- Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist (예정)
- Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- Python Package 101 (6/10): 버전 관리와 릴리스 (예정)
- Python Package 101 (7/10): CLI 패키지 만들기 (예정)
- Python Package 101 (8/10): 타입 힌트와 정적 검사 (예정)
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Python Modules Tutorial](https://docs.python.org/3/tutorial/modules.html)
- [Real Python - Python Packages](https://realpython.com/python-modules-packages/)
- [PyPI - Python Package Index](https://pypi.org/)

Tags: Python, Packaging, PyPI, pyproject.toml
