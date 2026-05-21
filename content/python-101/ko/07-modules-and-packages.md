---
title: "Python 101 (7/10): 모듈과 패키지: import, __init__, __name__"
series: python-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- import-system
- module-vs-package
- init-py
- name-main-guard
- relative-imports
- namespace-packages
last_reviewed: '2026-05-12'
seo_description: Python에서 모듈은 "한 번 실행되면 캐시되는 namespace"이고, 패키지는 "__init__.py가 있는 디렉터리로
  묶인 모듈의…
---

# Python 101 (7/10): 모듈과 패키지: import, __init__, __name__

Python에서 모듈은 한 번 실행되면 캐시되는 namespace이고, 패키지는 관련 모듈을 디렉터리로 묶는 단위입니다. import가 실제로 무엇을 읽고 어디에 이름을 올리는지 이해하면 구조가 한결 단순해집니다.

이 글은 Python 101 시리즈의 일곱 번째 글입니다.


![Python 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-101/07/07-01-mental-model.ko.png)
*Python 101 7장 흐름 개요*
> 모듈과 패키지: import, __init__, __name__의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 같은 이름의 함수와 변수가 충돌합니다?
- 어떤 함수가 어디서 정의됐는지 찾기 어렵습니다?
- 다른 프로젝트에서 같은 코드를 재사용하기 힘듭니다?

## 멘탈 모델

> Python에서 모듈은 "한 번 실행되면 캐시되는 namespace"이고, 패키지는 "`__init__.py`가 있는 디렉터리로 묶인 모듈의 묶음"이라는 두 정의만 잡아 두면 import 동작 대부분이 같은 그림으로 설명됩니다.
모듈은 "한 번 실행되어 namespace를 만드는 `.py` 파일"입니다. 패키지는 "그런 모듈들을 담는 디렉터리"입니다. `import`는 그 namespace를 현재 코드에 연결하는 동작입니다.

여기서 먼저 잡아둘 점은 두 가지입니다. 첫째, **모듈 코드는 처음 import될 때 위에서 아래로 한 번 실행됩니다**. 둘째, **그 결과 만들어진 namespace 객체가 캐시되어 재사용됩니다**. 두 번째 import는 파일을 다시 읽지 않고 캐시된 객체만 가져옵니다.

*분할 결정 트리: 파일 크기와 책임 분리 기준으로 모듈/패키지 구조가 결정됩니다.*

## 핵심 개념

### 1. 모듈

`.py` 파일 하나가 모듈입니다. 파일 이름에서 `.py`를 뺀 것이 모듈 이름입니다. `math.py`라는 파일이 있다면 `import math`로 부릅니다.

### 2. 패키지

`__init__.py`가 들어 있는 디렉터리가 패키지입니다. 패키지 안에는 다른 모듈이나 하위 패키지를 둘 수 있습니다. `__init__.py`는 비어 있어도 되고, 패키지가 처음 로드될 때 실행할 코드를 담아도 됩니다.

```text
myapp/
    __init__.py
    cli.py
    db/
        __init__.py
        sqlite_store.py
        migrations.py
```

위 구조에서 `myapp.db.sqlite_store`는 `myapp` 패키지 안의 `db` 하위 패키지 안의 `sqlite_store` 모듈을 가리킵니다.

### 3. import 형태

```python
import math                # bring in the whole math namespace as 'math'
from math import sqrt      # bring just sqrt into the current namespace
import numpy as np         # use a short alias 'np' for numpy
from .sibling import foo   # import foo from a sibling module in the same package
```

`import x`는 `x` 자체를 가져옵니다. 호출은 `x.func()`로 합니다. `from x import y`는 `y`만 가져오므로 호출이 `y()`로 짧아지지만, `y`가 어디서 왔는지 호출부에서 보이지 않습니다. 작은 프로젝트라면 둘 다 괜찮고, 코드가 커질수록 `import x` 쪽이 출처를 따라가기 쉬운 편입니다.

### 4. `__name__`과 `__main__` 가드

여기서 다루는 일반적인 Python 모듈에는 `__name__`이라는 문자열이 자동으로 붙습니다. 다른 파일에서 import되어 실행될 때는 모듈 이름이 들어가고, `python file.py`처럼 직접 실행될 때는 `"__main__"`이 들어갑니다.

```python
def main():
    print("hello")

if __name__ == "__main__":
    main()
```

이 패턴은 같은 파일을 "스크립트로 실행할 때만 동작하는 부분"과 "라이브러리로 import될 때 노출할 부분"을 분리합니다.

### 5. relative import

같은 패키지 안에서 형제 모듈을 부를 때 `.`를 씁니다. 점 하나는 같은 패키지, 점 두 개는 부모 패키지를 가리킵니다.

```python
# myapp/db/sqlite_store.py
from .migrations import latest_version       # migrations in the same db package
from ..cli import parse_args                 # cli one level up, in myapp
```

relative import는 패키지 안에서만 의미가 있습니다. 스크립트로 직접 실행하는 파일에서는 쓸 수 없습니다.

### 6. `sys.path`와 import 경로

`import x`가 실행되면 Python은 `sys.path`라는 디렉터리 리스트를 차례로 뒤져서 `x.py`나 `x/`를 찾습니다. `sys.path`에는 보통 다음이 포함됩니다.

- 실행한 스크립트가 있는 디렉터리
- `PYTHONPATH` 환경 변수에 있는 경로들
- 표준 라이브러리 위치
- 설치된 site-packages

같은 모듈 이름이 여러 곳에 있다면 `sys.path` 순서대로 먼저 발견된 쪽이 이깁니다.

## 전후 비교

같은 결제 처리 로직이 한 파일에 모여 있을 때와, 모듈과 패키지로 정리되었을 때를 비교합니다.

**Before — 한 파일에 모든 것이 섞임**

```python
# pay.py
import sqlite3

def connect():
    return sqlite3.connect("pay.db")

def insert_order(order):
    conn = connect()
    conn.execute("insert into orders(amount) values (?)", [order["amount"]])
    conn.commit()
    conn.close()

def calc_tax(amount):
    return round(amount * 0.1, 2)

def send_receipt(email, amount):
    print(f"sending receipt to {email}: {amount}")

def main():
    order = {"amount": 100, "email": "a@b.c"}
    insert_order(order)
    send_receipt(order["email"], order["amount"] + calc_tax(order["amount"]))

if __name__ == "__main__":
    main()
```

DB, 세금 계산, 이메일이 한 파일에 섞여 있어 테스트하거나 재사용하기 어렵습니다.

**After — 책임별 모듈, 패키지로 묶기**

```text
pay/
    __init__.py
    cli.py
    db.py
    tax.py
    notify.py
```

```python
# pay/db.py
import sqlite3

def connect():
    return sqlite3.connect("pay.db")

def insert_order(order):
    conn = connect()
    conn.execute("insert into orders(amount) values (?)", [order["amount"]])
    conn.commit()
    conn.close()
```

```python
# pay/tax.py
def calc_tax(amount):
    return round(amount * 0.1, 2)
```

```python
# pay/notify.py
def send_receipt(email, amount):
    print(f"sending receipt to {email}: {amount}")
```

```python
# pay/cli.py
from .db import insert_order
from .tax import calc_tax
from .notify import send_receipt

def main():
    order = {"amount": 100, "email": "a@b.c"}
    insert_order(order)
    send_receipt(order["email"], order["amount"] + calc_tax(order["amount"]))

if __name__ == "__main__":
    main()
```

각 모듈은 한 가지 책임만 갖고, `cli.py`는 그 모듈들을 조합합니다. `tax.py`는 DB와 무관하게 단독으로 테스트할 수 있고, `pay.tax`만 다른 프로젝트에서 가져다 쓸 수도 있습니다.

## 단계별 실습

REPL에서 직접 만들어 봅니다. `>>>` 프롬프트가 보이는 줄은 실제 입력이고, 그 아래 줄은 출력입니다.

### 1. 모듈 만들기

작업 디렉터리에 `greet.py`를 만듭니다.

```python
# greet.py
def hello(name):
    return f"hello, {name}"

print("greet module loaded")
```

같은 디렉터리에서 REPL을 띄우고 import해 봅니다.

```pycon
>>> import greet
greet module loaded
>>> greet.hello("ada")
'hello, ada'
>>> import greet
>>>
```

처음 import에서만 `print` 한 줄이 보입니다. 두 번째 `import greet`는 캐시를 재사용하므로 모듈 본문이 다시 실행되지 않습니다.

### 2. `__name__` 가드 확인하기

`greet.py` 마지막에 한 줄을 추가합니다.

```python
if __name__ == "__main__":
    print("running as a script")
```

이제 `python greet.py`로 직접 실행하면 두 줄이 보입니다.

```text
greet module loaded
running as a script
```

반면 다른 파일에서 `import greet`만 했을 때는 `running as a script` 줄이 보이지 않습니다. 이 차이가 라이브러리와 CLI를 한 파일에 함께 둘 수 있게 해 줍니다.

### 3. 패키지 만들기

작은 패키지 구조를 만듭니다.

```text
shop/
    __init__.py
    catalog.py
    cart.py
```

```python
# shop/catalog.py
PRICES = {"apple": 1000, "banana": 500}

def price_of(item):
    return PRICES.get(item, 0)
```

```python
# shop/cart.py
from .catalog import price_of

def total(items):
    return sum(price_of(i) for i in items)
```

`shop`이 보이는 디렉터리에서 REPL을 띄웁니다.

```pycon
>>> from shop.cart import total
>>> total(["apple", "banana", "apple"])
2500
```

`shop/cart.py`의 `from .catalog import price_of`가 같은 패키지 안의 `catalog`를 가리킵니다.

### 4. `sys.path` 들여다보기

```pycon
>>> import sys
>>> sys.path[:3]
['', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload']
```

가장 앞의 빈 문자열은 "현재 작업 디렉터리"를 뜻합니다. 그래서 같은 폴더의 `greet.py`를 바로 import할 수 있었던 것입니다.

## 이 코드에서 주목할 점

- **`pay/` 디렉터리에 `__init__.py`** — 빈 파일이라도 두면 일반 패키지로 명시되어 import 동작이 예측 가능해집니다. namespace package에 의존하지 않습니다.
- **`from .db import insert_order` relative import** — `pay` 패키지 안에서 형제 모듈을 부르므로 패키지 위치가 바뀌어도 깨지지 않습니다.
- **모듈별 한 책임** — `db.py`는 저장, `tax.py`는 계산, `notify.py`는 알림. 각 모듈이 단독으로 테스트 가능한 단위가 됩니다.
- **`cli.py`가 조립 책임** — 다른 모듈은 서로를 모르고, `cli.py`만 셋을 조합합니다. 의존성이 한 방향으로만 흐릅니다.
- **`python -m pay.cli`로 실행 가능** — `__main__` 가드와 패키지 구조가 결합되어 라이브러리이자 CLI인 패키지가 만들어집니다.

## 자주 하는 실수

1. **`__init__.py`가 없는 디렉터리를 패키지처럼 다루기.**
   `__init__.py`가 없어도 namespace package로 동작하는 경우가 있지만, 의도가 명확한 일반 패키지에서는 빈 `__init__.py`라도 두는 편이 import 경로를 따라가기 쉽습니다.

2. **`from x import *`를 본문에 쓰기.**
   어떤 이름이 들어왔는지 호출부에서 보이지 않아 충돌이 생겨도 추적이 어렵습니다. 라이브러리 본문에서는 피하고, REPL이나 짧은 노트북에서만 제한적으로 씁니다.

3. **스크립트로 실행하는 파일에서 relative import 사용.**
   `python pay/cli.py`처럼 단일 파일로 실행하면 `cli.py`는 패키지의 일부로 간주되지 않으므로 `from .db import ...`가 실패합니다. `python -m pay.cli`로 실행하거나, 진입점을 패키지 바깥에 두는 식으로 분리합니다.

4. **무거운 작업을 모듈 본문에 두기.**
   import 한 번에 네트워크 호출이나 큰 파일 로드가 일어나면 import만으로 시간이 늘어납니다. 무거운 작업은 함수 안으로 옮기고, 필요할 때 호출합니다.

5. **순환 import.**
   `a.py`가 `b`를 import하고, `b.py`가 다시 `a`를 import하면 한쪽이 완성되기 전에 다른 쪽이 그 namespace를 보게 됩니다. 공통 의존을 별도 모듈로 빼거나, 함수 안에서 import하는 방식으로 풀 수 있습니다.

6. **`sys.path`를 본문에서 직접 조작하기.**
   `sys.path.insert(0, "...")`을 본문 곳곳에 흩어두면 import가 어디서 어떻게 풀리는지 추적이 어려워집니다. 패키지 설치(`pip install -e .`)나 `PYTHONPATH` 설정으로 푸는 편이 훨씬 안전합니다.

## 실무에서는 이렇게 생각합니다

실제 프로젝트에서 모듈과 패키지가 만나는 모습은 다음과 같습니다.

- **계층 분리**: `myapp/api`, `myapp/db`, `myapp/services`처럼 책임별 하위 패키지로 나누고, 각 모듈은 자기 계층의 일만 합니다.
- **CLI 진입점**: `python -m myapp.cli`로 실행할 수 있게 만들면 패키지 안에서 relative import가 자연스럽게 동작합니다.
- **재사용 단위**: 외부에 공개할 함수만 `__init__.py`에서 다시 export하면 사용자는 `from myapp import do_something`처럼 짧게 쓸 수 있습니다.
- 테스트: 모듈 단위로 import해서 `pytest`가 함수만 골라 실행할 수 있게 합니다. 한 파일에 모든 것이 섞여 있으면 테스트도 함께 무거워집니다.
- **설정 분리**: 환경별 설정은 별도 모듈(`config_dev.py`, `config_prod.py`)로 두고 진입점에서 골라 import합니다.

이 구조는 프로젝트가 커져도 큰 틀은 비슷하게 유지되는 편입니다. 처음에 `myapp/__init__.py` 한 줄로 시작해도, 필요해지면 하위 패키지를 늘리는 방식으로 확장할 수 있습니다.

## 체크리스트

- [ ] `.py` 파일 하나를 모듈로 만들고 다른 파일에서 import할 수 있습니다.
- [ ] `__init__.py`를 둔 디렉터리를 패키지로 만들고, 안의 모듈을 `pkg.mod`로 부를 수 있습니다.
- [ ] `import x`, `from x import y`, `import x as alias`의 차이를 한 문장씩으로 설명할 수 있습니다.
- [ ] `if __name__ == "__main__":` 가드의 동작을 직접 실행과 import 두 경우로 나눠 설명할 수 있습니다.
- [ ] 같은 패키지 안에서 `from .sibling import ...`로 relative import를 쓸 수 있습니다.
- [ ] `sys.path`와 `PYTHONPATH`가 import 경로 탐색에 관여한다는 것을 한 줄로 설명할 수 있습니다.

## 정리·다음 글

- 모듈은 `.py` 파일 하나, 패키지는 `__init__.py`가 있는 디렉터리입니다.
- import는 모듈을 처음 가져올 때 본문을 한 번 실행하고, 그 결과를 `sys.modules`에 캐시해 둡니다.
- `import x`, `from x import y`, `as alias`, `from .sibling import ...`는 같은 import 시스템의 다른 사용 방식입니다.
- `if __name__ == "__main__":` 가드는 한 파일을 스크립트와 라이브러리로 동시에 쓸 수 있게 합니다.
- `sys.path`와 `PYTHONPATH`는 모듈 탐색 경로의 단일 출처이므로, 직접 조작하기보다 패키지 설치나 환경 변수로 다루는 편이 안전합니다.

다음 글에서는 파일 I/O와 예외 처리를 다룹니다. 모듈 단위로 정리한 코드가 외부 자원을 안전하게 다루는 방법을 살펴봅니다.

## 실전 앵커: import 경로, 패키지 구조, 배포 전 점검

모듈/패키지 파트의 핵심은 "내 코드가 어디에서 로드되는가"를 확실히 아는 것입니다. 아래 세 줄만으로도 대부분의 import 문제를 빠르게 좁힐 수 있습니다.

```python
import sys
import mypkg

print(sys.path)
print(mypkg.__file__)
```

`sys.path` 앞부분에 의도치 않은 경로가 있으면 같은 이름의 모듈이 그림자처럼 먼저 로드될 수 있습니다. 특히 파일명을 `random.py`, `json.py`로 짓는 실수가 자주 발생합니다.

```text
ImportError: cannot import name 'loads' from 'json' (/project/json.py)
```

이 에러는 표준 라이브러리 `json`이 아니라 프로젝트 파일 `json.py`를 먼저 읽은 경우입니다.

패키지 구조는 최소 단위부터 단정하게 시작하는 편이 좋습니다.

```text
myapp/
  pyproject.toml
  src/
    myapp/
      __init__.py
      cli.py
      service.py
```

`src/` 레이아웃은 테스트 중 우연한 상대경로 import를 줄여 줍니다. 설치된 패키지 기준으로 동작을 확인하기 쉬워 배포 안정성이 올라갑니다.

`pyproject.toml`의 가장 작은 예시는 다음처럼 유지할 수 있습니다.

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp"
version = "0.1.0"
description = "python-101 example"
requires-python = ">=3.11"
```

설치 후에는 엔트리포인트를 통해 import 경로를 검증합니다.

```bash
python -m pip install -e .
python -m myapp.cli
```

표준 라이브러리 `importlib`도 함께 익혀 두면 동적 로딩 코드의 디버깅이 쉬워집니다.

```python
import importlib

math_mod = importlib.import_module('math')
print(math_mod.sqrt(16))
```

성능 관점에서는 import 비용도 측정할 수 있습니다.

```python
import timeit

cold = timeit.timeit("import json", number=1000)
print(cold)
```

대부분은 미미하지만 대규모 CLI에서 초기 체감 속도를 바꾸는 경우가 있어, 느린 의존성은 함수 내부 지연 import로 분리하기도 합니다.

디버깅 루틴으로는 `pdb`보다도 `python -X importtime -c "import myapp"`가 매우 유용합니다. 어떤 모듈 import가 느린지 계층별로 확인할 수 있습니다.

모듈/패키지 단원의 목표는 코드 재사용을 넘어서, 실행 환경이 바뀌어도 동일하게 로드되는 구조를 만드는 것입니다.

### 추가 실습: 배포 전 import 안정성 점검 절차

패키지 작업에서 "로컬에서는 되는데 서버에서 안 되는" 문제는 대부분 경로/설치 방식에서 발생합니다. 배포 전에는 아래 절차를 고정해서 확인합니다.

```bash
python -m pip uninstall -y myapp
python -m pip install .
python -c "import myapp, sys; print(myapp.__file__); print(sys.version)"
```

editable install(`-e`)과 일반 install 모두 테스트하면 경로 의존 버그를 빨리 찾을 수 있습니다.

네임스페이스 충돌 방지도 중요합니다. 표준 라이브러리와 같은 모듈명을 피하고, `__init__.py`에서 과도한 사이드이펙트 import를 줄여야 초기화 실패를 줄일 수 있습니다.

```python
# 불량: __init__.py에서 호출
# good: 최소 공개 심볼만 노출
from .service import run
```

마지막으로 `python -m package.module` 실행 습관을 들이면 상대 import 오류를 줄일 수 있습니다.

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

### 보강 메모: 실수 줄이는 운영 습관

학습 단계에서 만든 코드를 실제 프로젝트에 옮길 때는 세 가지를 같이 점검하는 편이 좋습니다. 첫째, 입력 검증 경계가 함수 시작 지점에 있는지 확인합니다. 둘째, 실패 시 사용자에게 보여 줄 메시지와 로그 메시지를 분리합니다. 셋째, 성능 판단은 추측이 아니라 `timeit` 또는 샘플 벤치마크로 남깁니다.

간단한 템플릿은 다음과 같습니다.

```python
def safe_run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        # 학습 단계에서는 원인 관찰을 우선
        raise RuntimeError(f'실행 실패: {fn.__name__}') from e
```

또한 표준 라이브러리 문서를 읽을 때는 "모듈 개요 -> 대표 함수 3개 -> 예외 종류" 순서로 훑는 습관을 들이면 기억이 오래갑니다. 기능을 전부 외우는 것보다, 어떤 상황에서 어떤 모듈을 열어봐야 하는지 아는 것이 더 중요합니다.

## 처음 질문으로 돌아가기

- **같은 이름의 함수와 변수가 충돌합니다?**
  - 본문의 기준은 모듈과 패키지: import, __init__, __name__를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **어떤 함수가 어디서 정의됐는지 찾기 어렵습니다?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **다른 프로젝트에서 같은 코드를 재사용하기 힘듭니다?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv](./01-why-python-and-install.md)
- [Python 101 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [Python 101 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- [Python 101 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [Python 101 (5/10): 제어 흐름: if, for, while, comprehension](./05-control-flow.md)
- [Python 101 (6/10): 함수와 인자: def, args, kwargs, default, lambda](./06-functions-and-arguments.md)
- **모듈과 패키지: import, __init__, __name__ (현재 글)**
- 파일 I/O와 예외 처리 (예정)
- 클래스와 객체: 데이터와 동작을 함께 묶기 (예정)
- 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (예정)

<!-- toc:end -->

## 참고 자료

- [Python 튜토리얼 — Modules](https://docs.python.org/3/tutorial/modules.html) — 모듈 실행, import 캐시, `sys.path` 탐색 순서를 입문 관점에서 설명합니다.
- [Python Language Reference — The import system](https://docs.python.org/3/reference/import.html) — import가 finder/loader와 module cache를 거쳐 동작하는 방식을 공식 정의합니다.
- [Python 공식 문서 — `__main__`](https://docs.python.org/3/library/__main__.html) — `if __name__ == "__main__"` 가드와 패키지 엔트리 포인트의 의미를 보완합니다.
- [PEP 328 — Imports: Multi-Line and Absolute/Relative](https://peps.python.org/pep-0328/) — 절대/상대 import와 leading dot 문법의 배경입니다.
- [PEP 420 — Implicit Namespace Packages](https://peps.python.org/pep-0420/) — `__init__.py` 없는 namespace package 개념을 확인할 수 있습니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-101/ko)
Tags: import-system, module-vs-package, init-py, name-main-guard, relative-imports, namespace-packages
