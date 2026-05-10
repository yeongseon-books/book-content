---
title: Python Package란 무엇인가?
series: python-package-101
episode: 1
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- Package
- Module
- Import
- pip
- Library
last_reviewed: '2026-05-04'
seo_description: Python 패키지는 재사용 가능한 코드를 묶어 다른 사람과 공유하는 단위입니다. import로 불러오는 모든 것이 패키지입니다.
---

# Python Package란 무엇인가?

> Python Package 101 시리즈 (1/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 모듈과 패키지의 차이는 무엇일까요?
- `import requests` 할 때 어떤 일이 일어날까요?
- `pip install`은 실제로 무엇을 설치할까요?
- 내 코드를 패키지로 만들면 무엇이 좋을까요?

> Python 패키지는 재사용 가능한 코드를 묶어 다른 사람과 공유하는 단위입니다. `import`로 불러오는 모든 것이 패키지입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 모듈, 패키지, 라이브러리의 정의와 관계
- `import`가 모듈을 찾는 경로(`sys.path`)
- `pip install`이 패키지를 설치하는 위치와 과정
- 왜 자기 코드를 패키지로 만들어야 하는지

## 왜 중요한가

프로젝트가 커지면 파일을 여러 개로 나누고 서로 `import`합니다. 이것이 모듈이고, 모듈을 묶으면 패키지입니다. 팀에서 공통 코드를 복사해서 쓰면 버그를 고칠 때 모든 곳을 수정해야 합니다.

> 같은 유틸리티 함수를 프로젝트 3개에 복사해서 쓰고 있습니다. 버그를 발견했는데 3곳을 모두 수정해야 합니다. 한 곳을 빼먹어 배포 후 장애가 났습니다.

패키지로 만들면 한 곳에서 고치고 `pip install --upgrade`로 모든 프로젝트에 반영됩니다.

## Mental Model

> Python 패키지는 레고 블록입니다. 블록 하나(모듈)는 특정 기능을 담고, 블록을 세트로 묶으면(패키지) 하나의 주제가 됩니다. 세트를 매장(PyPI)에 올리면 누구나 가져다 쓸 수 있습니다.

```text
모듈(module)      패키지(package)          배포(distribution)
──────────        ──────────────          ─────────────────
utils.py    →    mylib/                →  mylib-1.0.0.tar.gz
                   __init__.py             (PyPI에 업로드)
                   utils.py
                   models.py
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 모듈(module) | 하나의 `.py` 파일 | `utils.py` |
| 패키지(package) | `__init__.py`가 있는 디렉터리 | `mylib/` |
| 라이브러리(library) | 패키지의 비공식 별칭 | `requests`, `flask` |
| 배포판(distribution) | 설치 가능한 아카이브 | `mylib-1.0.0.tar.gz` |
| PyPI | Python Package Index, 패키지 저장소 | pypi.org |

## Before / After

**Before (코드 복사)**

```text
project-a/utils.py   # 복사본 1
project-b/utils.py   # 복사본 2
project-c/utils.py   # 복사본 3
# → 버그 수정 시 3곳 모두 수정 필요
```

**After (패키지화)**

```text
mylib/               # 패키지 하나
  utils.py

project-a/           # pip install mylib
project-b/           # pip install mylib
project-c/           # pip install mylib
# → mylib 한 곳만 수정 후 pip install --upgrade
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

### Step 3. sys.path 확인

```python
import sys
for path in sys.path:
    print(path)
# '' (현재 디렉터리)
# /usr/lib/python3.11
# /usr/lib/python3.11/lib-dynload
# /home/user/.local/lib/python3.11/site-packages
```

### Step 4. pip으로 설치된 패키지 확인

```bash
pip list                          # 설치된 패키지 목록
pip show requests                 # requests 패키지 정보
pip show requests | grep Location # 설치 위치
# Location: /home/user/.local/lib/python3.11/site-packages
```

### Step 5. 설치된 패키지의 실제 파일 확인

```bash
python -c "import requests; print(requests.__file__)"
# /home/user/.local/lib/python3.11/site-packages/requests/__init__.py

ls /home/user/.local/lib/python3.11/site-packages/requests/
# __init__.py  api.py  models.py  sessions.py  ...
```

## 이 코드에서 봐야 할 것

- `__init__.py`가 있어야 Python이 디렉터리를 패키지로 인식합니다
- `from .calculator import add`에서 `.`은 현재 패키지 내부를 가리키는 상대 임포트입니다
- `sys.path`의 순서가 곧 Python이 모듈을 찾는 우선순위입니다
- `pip install`은 결국 `site-packages/`에 파일을 복사하는 것입니다

## 자주 하는 실수

### 실수 1. __init__.py를 빼먹는다

`__init__.py`가 없으면 Python 3.3+ namespace package로 동작하지만, 명시적으로 넣는 것이 관례입니다. 없으면 일부 도구가 패키지를 인식하지 못합니다.

### 실수 2. 모듈 이름이 표준 라이브러리와 충돌한다

```python
# email.py 라는 파일을 만들면
import email  # 내 파일이 표준 라이브러리 대신 임포트됨
```

`random.py`, `json.py`, `os.py` 같은 이름을 쓰면 안 됩니다.

### 실수 3. 순환 임포트

```python
# a.py: from b import func_b
# b.py: from a import func_a
# → ImportError
```

의존 방향을 한쪽으로 정리하거나 공통 모듈로 분리합니다.

### 실수 4. site-packages를 직접 수정한다

설치된 패키지의 코드를 직접 수정하면, 다음 `pip install`에서 덮어씌워집니다.

### 실수 5. 패키지 이름에 하이픈과 언더스코어를 혼동한다

```bash
pip install my-package      # 설치 이름: 하이픈
import my_package           # 임포트 이름: 언더스코어
```

## 실무 적용

- **사내 공통 라이브러리**: 인증, 로깅, 설정 관리를 패키지로 통일합니다
- **마이크로서비스 공유 코드**: gRPC 스텁, 데이터 모델을 패키지로 배포합니다
- **CLI 도구**: `pip install`로 설치하면 터미널에서 바로 쓸 수 있는 명령어가 됩니다
- **오픈소스 기여**: PyPI에 올리면 `pip install`로 전 세계 누구나 설치합니다
- **테스트 픽스처 공유**: 여러 프로젝트에서 쓰는 테스트 유틸리티를 패키지로 묶습니다

## 실무에서는 이렇게 생각한다

"이 코드가 2개 이상의 프로젝트에서 쓰이나?" — 그렇다면 패키지로 만들 때입니다. 복사해서 쓰면 유지보수 비용이 프로젝트 수에 비례해서 늘어납니다. 패키지로 만들면 한 곳에서 관리하고, 버전으로 안정성을 보장합니다.

처음에는 "패키지 만드는 게 오버헤드 아닌가?"라고 생각하지만, 실제로는 `pyproject.toml` 하나면 됩니다. 이 시리즈에서 그 과정을 하나씩 다룹니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **배포 단위** — 패키지는 “배포 가능한 단위”의 정의입니다.
- **표준 도구** — pyproject.toml + build + twine이 사실상 표준입니다.
- **이름 정책** — 이름은 PyPI에서 미리 확보합니다.
- **배포 vs 사내** — 사내 배포는 private index로 분리합니다.
- **문서화** — README가 첫 사용자 경험입니다.

## 체크리스트

- [ ] 모듈, 패키지, 배포판의 차이를 설명할 수 있다
- [ ] `__init__.py`의 역할을 알고 있다
- [ ] `sys.path`로 모듈 검색 경로를 확인할 수 있다
- [ ] `pip show`로 패키지 설치 위치를 확인할 수 있다
- [ ] 코드를 패키지로 만들어야 하는 시점을 판단할 수 있다

## 연습 문제

1. `mymath/` 패키지를 만들고, `multiply`와 `divide` 함수를 추가한 뒤 `main.py`에서 임포트해보세요.
2. `sys.path`를 출력하고, `site-packages` 디렉터리에서 설치된 패키지 하나의 파일 구조를 확인해보세요.
3. `string.py`라는 파일을 만들고 `import string`을 실행했을 때 어떤 일이 일어나는지 확인해보세요.

## 정리 · 다음 글

- 모듈은 `.py` 파일, 패키지는 `__init__.py`가 있는 디렉터리입니다.
- Python은 `sys.path` 순서대로 모듈을 찾습니다.
- `pip install`은 `site-packages/`에 패키지 파일을 복사합니다.
- 2개 이상의 프로젝트에서 쓰이는 코드는 패키지로 만들 때입니다.
- 패키지 이름은 표준 라이브러리와 충돌하지 않아야 합니다.

다음 글에서는 **프로젝트 구조 잡기** — src layout과 pyproject.toml을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- **Python Package란 무엇인가? (현재 글)**
- 프로젝트 구조 잡기 — src layout과 pyproject.toml (예정)
- 의존성 관리 — venv, pip, uv, requirements (예정)
- 패키지 빌드하기 — wheel과 sdist (예정)
- PyPI에 배포하기 — TestPyPI부터 실제 배포까지 (예정)
- 버전 관리와 릴리스 (예정)
- CLI 패키지 만들기 (예정)
- 타입 힌트와 정적 검사 (예정)
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Packaging User Guide](https://packaging.python.org/)
- [Python Modules Tutorial](https://docs.python.org/3/tutorial/modules.html)
- [Real Python - Python Packages](https://realpython.com/python-modules-packages/)
- [PyPI - Python Package Index](https://pypi.org/)
