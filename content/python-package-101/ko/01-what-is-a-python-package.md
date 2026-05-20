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

## 먼저 던지는 질문

- 모듈과 패키지는 정확히 무엇이 다를까요?
- `import requests`를 실행하면 내부에서는 어떤 일이 일어날까요?
- `pip install`은 실제로 무엇을 설치할까요?

## 큰 그림

![Python Package 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/01/01-01-mental-model.ko.png)

*Python Package 101 1장 흐름 개요*

이 그림에서는 Python Package란 무엇인가?를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Python Package란 무엇인가?의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## Before / After

**Before (copy-paste code)**

```text
project-a/utils.py   # copy 1
project-b/utils.py   # copy 2
project-c/utils.py   # copy 3
# -> Fix a bug? Edit all three.
```

**After (packaged)**

```text
mylib/               # one package
  utils.py

project-a/           # pip install mylib
project-b/           # pip install mylib
project-c/           # pip install mylib
# -> Fix mylib once, pip install --upgrade everywhere
```

## 단계별 실습

### Step 1. 모듈 만들기

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

### Step 2. 패키지 구조 만들기

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

### Step 3. `sys.path` 확인

```python
import sys
for path in sys.path:
    print(path)
# '' (current directory)
# /usr/lib/python3.11
# /usr/lib/python3.11/lib-dynload
# /home/user/.local/lib/python3.11/site-packages
```

### Step 4. 설치된 패키지 확인

```bash
pip list                          # List installed packages
pip show requests                 # Details for requests
pip show requests | grep Location # Installation path
# Location: /home/user/.local/lib/python3.11/site-packages
```

### Step 5. 설치된 패키지 내부 확인

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
# If you create email.py
import email  # Your file shadows the standard library
```

`random.py`, `json.py`, `os.py`처럼 표준 라이브러리와 충돌하는 이름은 피하는 편이 좋습니다.

### 실수 3. 순환 임포트를 만든다

```python
# a.py: from b import func_b
# b.py: from a import func_a
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

## 처음 질문으로 돌아가기

- **모듈과 패키지는 정확히 무엇이 다를까요?**
  - 본문의 기준은 Python Package란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`import requests`를 실행하면 내부에서는 어떤 일이 일어날까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`pip install`은 실제로 무엇을 설치할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

- [Python Packaging User Guide](https://packaging.python.org/)
- [Python Modules Tutorial](https://docs.python.org/3/tutorial/modules.html)
- [Real Python - Python Packages](https://realpython.com/python-modules-packages/)
- [PyPI - Python Package Index](https://pypi.org/)

Tags: Python, Packaging, PyPI, pyproject.toml
